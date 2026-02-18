import rich
from rich.console import Console
from rich.table import Table
import click
from html_to_pdf import create_final_pdf
from custom_fill import render_output
from datetime import datetime, timedelta
import yaml


class XmtlBuildField:
    def __init__(self, name, value, prompt):
        self.name = name
        self.value = value
        self.prompt = prompt

    def fill_field(self):
        if not self.value:
            self.value = click.prompt(self.prompt)

class XmtlBuild:
    def __init__(self, project_number, project_title, submittal_no, rev_no, specification, description,
                 contractor_name="", edp_line1="", edp_line2="", edp_line3="", reviewer_names=""):
        self.project_number = XmtlBuildField("Project_Number", project_number, "Input Project Number")
        self.project_title = XmtlBuildField("Project_Title", project_title, "Input Project Title")
        self.submittal_no = XmtlBuildField("Submittal_No", submittal_no, "Input Submittal Number")
        self.rev_no = XmtlBuildField("Revision_No", rev_no, "Input Revision Number")
        self.specification = XmtlBuildField("Specification", specification, "Input Specification")
        self.description = XmtlBuildField("Description", description, "Input Description")
        self.contractor_name = XmtlBuildField("Contractor", contractor_name, "Input Contractor Name")
        self.edp_line1 = XmtlBuildField("EDP_Address_Line_1", edp_line1, "Input EDP Address Line 1")
        self.edp_line2 = XmtlBuildField("EDP_Address_Line_2", edp_line2, "Input EDP Address Line 2")
        self.edp_line3 = XmtlBuildField("EDP_Address_Line_3", edp_line3, "Input EDP Address Line 3")
        self.reviewer_names = XmtlBuildField("Reviewer_Names", reviewer_names, "Input Reviewer Names")

    @classmethod
    def empty(cls):
        """Create an XmtlBuild with all fields empty, ready for manual prompting."""
        return cls("", "", "", "", "", "")

    @classmethod
    def from_yaml(cls, yaml_path, key):
        with open(yaml_path, "r") as f:
            defaults = yaml.safe_load(f)
        if key not in defaults:
            raise KeyError(f"Key '{key}' not found in {yaml_path}")
        d = defaults[key]
        # yaml stores combined "number, title" — split them back out
        title_parts = d.get("Project_Title", "").split(", ", 1)
        project_number = title_parts[0] if len(title_parts) > 1 else ""
        project_title  = title_parts[1] if len(title_parts) > 1 else title_parts[0]
        return cls(
            project_number  = project_number,
            project_title   = project_title,
            submittal_no    = d.get("Submittal_No", ""),
            rev_no          = d.get("Revision_No", ""),
            specification   = d.get("Specification", ""),
            description     = d.get("Description", ""),
            contractor_name = d.get("Contractor", ""),
            edp_line1       = d.get("EDP_Address_Line_1", ""),
            edp_line2       = d.get("EDP_Address_Line_2", ""),
            edp_line3       = d.get("EDP_Address_Line_3", ""),
            reviewer_names  = d.get("reviewer_list", ""),
        )

    @property
    def has_edp(self):
        return bool(self.edp_line1.value)

    def fill_all_fields(self):
        """Prompt for any fields that are still empty."""
        for field in [self.project_number, self.project_title, self.submittal_no,
                      self.rev_no, self.specification, self.description, self.contractor_name]:
            field.fill_field()

        if click.confirm("Does this submittal have an Executive Design Professional (EDP)?", default=False):
            self.edp_line1.fill_field()
            self.edp_line2.fill_field()
            self.edp_line3.fill_field()
        else:
            console.print("No EDP information will be included in the submittal.", style="green")

        console.print("\nInput reviewer names as a semicolon-delimited list", style="bold green")
        console.print("Example: 'David Jessen, UCSC PP;Jeff Clothier, UCSC PP'", style="green")
        self.reviewer_names.fill_field()

    def to_render_dict(self):
        """Produce the flat dictionary that render_output() expects."""
        d = {
            "Project_Title":      f"{self.project_number.value}, {self.project_title.value}",
            "Submittal_No":       self.submittal_no.value,
            "Revision_No":        self.rev_no.value,
            "Date_Review_Ends":   (datetime.now() + timedelta(weeks=2)).strftime("%m/%d/%Y"),
            "Specification":      self.specification.value,
            "Description":        self.description.value,
            "Contractor":         self.contractor_name.value,
            "EDP_Address_Line_1": self.edp_line1.value,
            "EDP_Address_Line_2": self.edp_line2.value,
            "EDP_Address_Line_3": self.edp_line3.value,
        }
        for i, name in enumerate(self.reviewer_names.value.split(";"), start=1):
            d[f"Reviewer_Name_{i}"] = name.strip()
        return d


def review_dictionary(dictionary, title):
    table = Table(title=title)
    table.add_column("Field", style="#333FFF", no_wrap=True)
    table.add_column("Input", style="#8691F6")
    for key, value in dictionary.items():
        table.add_row(key, str(value))
    console.print(table)

    if click.confirm("Does everything look correct?", default=True):
        console.print("[green]✔ Confirmed[/green]")
    else:
        console.print("✖ Process Cancelled", style="bold red")
        return False
    return True


if __name__ == "__main__":
    console = Console()
    console.print("Welcome to the Submittal Generator!\n", style="bold green")
    console.print("Project & Submittal Details", style="green")

    default_key = str(click.prompt(
        "To use default values, input the default key (e.g. 3238), otherwise just hit enter to input values manually",
        default=""
    ).strip())

    if default_key:
        try:
            build = XmtlBuild.from_yaml("default_values.yaml", default_key)
            console.print(f"\nSummary of Default Values for key {default_key}:", style="bold green")
        except KeyError as e:
            console.print(str(e), style="red")
            exit()
    else:
        console.print("\nProceeding with manual input", style="green")
        build = XmtlBuild.empty()
        build.fill_all_fields()
        console.print("\nSummary of Submittal Inputs", style="bold green")

    dictionary = build.to_render_dict()
    if not review_dictionary(dictionary, "Submittal Details"):
        exit()

    HTML_FILES = render_output(dictionary)
    final_pdf_name = click.prompt("Input name for final submittal file")
    create_final_pdf(final_pdf_name, HTML_FILES)







