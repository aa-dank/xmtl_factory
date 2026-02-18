from rich.console import Console
from rich.table import Table
import click
from html_to_pdf import create_final_pdf
from custom_fill import render_output
from datetime import datetime, timedelta
import yaml

console = Console()


class XmtlBuildField:
    def __init__(self, name, value, prompt, required = False):
        self.name = name
        self.value = value
        self.prompt = prompt
        self.required = required

    def fill_field(self):
        if not self.value:
            if self.required:
                while not self.value:
                    self.value = click.prompt(self.prompt)
                    if not self.value:
                        console.print(f"'{self.name}' is required. Please enter a value.", style="red")
            else:
                self.value = click.prompt(self.prompt, default="")

class XmtlBuild:
    def __init__(self, project_number="", project_title="", submittal_number="", revision_number="",
                 specification_section="", submittal_name="",
                 project_manager_name="", edp_line1="", edp_line2="", edp_line3="", reviewer_names=""):
        self.project_number        = XmtlBuildField("Project_Number",        project_number,        "Input Project Number",        required=True)
        self.project_title         = XmtlBuildField("Project_Title",         project_title,         "Input Project Title",         required=True)
        self.submittal_number      = XmtlBuildField("Submittal_Number",      submittal_number,      "Input Submittal Number",      required=True)
        self.revision_number       = XmtlBuildField("Revision_Number",       revision_number,       "Input Revision Number",       required=True)
        self.specification_section = XmtlBuildField("Specification_Section", specification_section, "Input Specification Section", required=True)
        self.submittal_name        = XmtlBuildField("Submittal_Name",        submittal_name,        "Input Submittal Name",        required=True)
        self.project_manager_name  = XmtlBuildField("Project_Manager",       project_manager_name,  "Input Project Manager Name")
        self.edp_line1             = XmtlBuildField("EDP_Address_Line_1",    edp_line1,             "Input EDP Name")
        self.edp_line2             = XmtlBuildField("EDP_Address_Line_2",    edp_line2,             "Input EDP Address")
        self.edp_line3             = XmtlBuildField("EDP_Address_Line_3",    edp_line3,             "Input EDP City, State, Zip")
        self.reviewer_names        = XmtlBuildField("Reviewer_Names",        reviewer_names,        "Input Reviewer Names (semicolon-delimited)")

    @classmethod
    def empty(cls):
        """Create an XmtlBuild with all fields empty, ready for manual prompting."""
        return cls()

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
            project_number       = project_number,
            project_title        = project_title,
            submittal_number     = d.get("Submittal_Number", ""),
            revision_number      = d.get("Revision_Number", ""),
            specification_section = d.get("Specification_Section", ""),
            submittal_name       = d.get("Submittal_Name", ""),
            project_manager_name = d.get("Project_Manager", ""),
            edp_line1            = d.get("EDP_Address_Line_1", ""),
            edp_line2            = d.get("EDP_Address_Line_2", ""),
            edp_line3            = d.get("EDP_Address_Line_3", ""),
            reviewer_names       = d.get("reviewer_list", ""),
        )

    def validate(self):
        """Return a list of required field names that are still empty."""
        return [
            field.name for field in vars(self).values()
            if isinstance(field, XmtlBuildField) and field.required and not field.value
        ]

    @property
    def has_edp(self):
        return bool(self.edp_line1.value)

    def fill_all_fields(self):
        """Prompt for any fields that are still empty."""
        for field in [self.project_number, self.project_title, self.submittal_number,
                      self.revision_number, self.specification_section, self.submittal_name, self.project_manager_name]:
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
            "Project_Title":        f"{self.project_number.value}, {self.project_title.value}",
            "Submittal_Number":     self.submittal_number.value,
            "Revision_Number":      self.revision_number.value,
            "Date_Review_Ends":     (datetime.now() + timedelta(weeks=2)).strftime("%m/%d/%Y"),
            "Specification_Section": self.specification_section.value,
            "Submittal_Name":       self.submittal_name.value,
            "Project_Manager":      self.project_manager_name.value,
            "EDP_Address_Line_1":   self.edp_line1.value,
            "EDP_Address_Line_2":   self.edp_line2.value,
            "EDP_Address_Line_3":   self.edp_line3.value,
        }
        names = [] if not self.reviewer_names.value else [name.strip() for name in self.reviewer_names.value.split(";")]
        for i, name in enumerate(names, start=1):
            d[f"Reviewer_Name_{i}"] = name
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
    console.print("Welcome to the Submittal Generator!\n", style="bold green")
    console.print("Project & Submittal Details", style="green")

    default_key = str(click.prompt(
        "To use an xmtl template, input the template key (e.g. 3238), otherwise just hit enter to input values manually",
        default=""
    ).strip())

    if default_key:
        try:
            build = XmtlBuild.from_yaml("xmtl_templates.yaml", default_key)
            console.print(f"\nXmtl template '{default_key}' loaded. You will be prompted for any missing values.\n", style="bold green")
            build.fill_all_fields()
            console.print("\nSummary of Submittal Inputs", style="bold green")
        except KeyError as e:
            console.print(str(e), style="red")
            exit()
    else:
        console.print("\nProceeding with manual input", style="green")
        build = XmtlBuild.empty()
        build.fill_all_fields()
        console.print("\nSummary of Submittal Inputs", style="bold green")

    missing = build.validate()
    if missing:
        console.print(f"Cannot render — missing required fields: {missing}", style="bold red")
        exit()

    dictionary = build.to_render_dict()
    if not review_dictionary(dictionary, "Submittal Details"):
        exit()

    HTML_FILES = render_output(dictionary)
    final_pdf_name = click.prompt("Input name for final submittal file")
    create_final_pdf(final_pdf_name, HTML_FILES)







