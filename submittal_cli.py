import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
import click
from html_to_pdf import create_final_pdf
from custom_fill import render_output
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
import yaml
from pathlib import Path
import sys

console = Console()


def _default_templates_path() -> Path:
    cwd_path = Path("xmtl_templates.yaml")
    if cwd_path.exists():
        return cwd_path

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled_path = Path(sys._MEIPASS) / "xmtl_templates.yaml"
        if bundled_path.exists():
            return bundled_path

    local_path = Path(__file__).resolve().parent / "xmtl_templates.yaml"
    return local_path


def _parse_review_date(value: str) -> str:
    """Parse a user-supplied date string and return it formatted as MM/DD/YYYY.

    Accepts any format recognised by dateutil.parser (e.g. '03/15/2025',
    'March 15 2025', '2025-03-15'). Returns a date two weeks from today
    if value is blank or cannot be parsed.
    """
    if value.strip():
        try:
            return dateutil_parser.parse(value.strip()).strftime("%m/%d/%Y")
        except (ValueError, OverflowError):
            console.print(f"Could not parse date '{value}' — defaulting to two weeks from today.", style="yellow")
    return (datetime.now() + timedelta(weeks=2)).strftime("%m/%d/%Y")


class XmtlBuildField:
    """A single data field on a transmittal build.

    Holds the field's name, current value, and CLI prompt text. Optionally
    enforces a non-empty value at prompt time and applies a processor function
    to transform the raw value before it is used in rendering.
    """

    def __init__(self, name, value, prompt, required=False, processor=None, max_length=None):
        """Initialise the field.

        Args:
            name:      Key used in the render dictionary (e.g. 'Submittal_Number').
            value:     Initial value, typically loaded from a template or left empty.
            prompt:    Text shown to the user when prompting for input.
            required:  If True, fill_field will loop until a non-empty value is entered.
            processor: Optional callable (value: str) -> Any applied by processed_value.
        """
        self.name = name
        self.value = value
        self.prompt = prompt
        self.required = required
        self._processor = processor
        self.max_length = max_length

    @property
    def processed_value(self):
        """Return processor(value) if a processor is defined, otherwise return raw value.

        The processor is called even when value is empty, allowing it to supply
        a default (e.g. returning '0' for a blank revision number).
        """
        if self._processor:
            return self._processor(self.value)
        return self.value

    def fill_field(self):
        """Prompt the user for a value if the field is currently empty.

        Always prompts once. The user may press Enter to leave optional fields
        blank. Required field validation and retry logic is handled by
        XmtlBuild.fill_all_fields().
        """
        if not self.value:
            self.value = click.prompt(self.prompt, default="")
            #console.print(f"{self.name} set to: {self.processed_value} \n", style="green")

class XmtlBuild:
    """Represents all data needed to generate a submittal transmittal PDF.

    Each piece of data is stored as an XmtlBuildField, which carries its own
    prompt text, required flag, and optional processor. The class supports
    loading pre-filled data from an xmtl_templates.yaml entry and interactively
    prompting the user for any fields that are still empty.
    """

    def __init__(self, project_number="", project_title="", submittal_number="", revision_number="",
                 specification_section="", submittal_name="", date_review_ends="",
                 project_manager_name="", edp_line1="", edp_line2="", edp_line3="", reviewer_names=""):
        """Initialise all fields. All arguments are optional and default to empty string.

        Required fields (project_number, project_title, submittal_number, revision_number,
        specification_section, submittal_name) must be non-empty before to_render_dict()
        is called — validate() or fill_all_fields() will surface any gaps.
        """
        self.project_number        = XmtlBuildField("Project_Number",        project_number,        "Input Project Number (e.g. 3238)",        required=True)
        self.project_title         = XmtlBuildField("Project_Title",         project_title,         "Input Project Title (e.g. Bay Tree Bookstore - Building Renovation for Student Services)",         required=True)
        self.submittal_number      = XmtlBuildField("Submittal_Number",      submittal_number,      "Input Submittal Number (e.g. 321313-01)",      required=True)
        self.revision_number       = XmtlBuildField(
            "Revision_Number",
            revision_number,
            "Input Revision Number, if left blank auto-populated with 0",
            required=True,
            processor=lambda v: v.strip() if v.strip() else "0"
        )
        self.specification_section = XmtlBuildField("Specification_Section", specification_section, "Input Specification Section (e.g. 32 13 13 Concrete Pavement)", required=True)
        self.submittal_name        = XmtlBuildField("Submittal_Name",        submittal_name,        "Input Submittal Name (e.g. Engine Generator Product Data)",        required=True)
        self.date_review_ends      = XmtlBuildField(
            "Date_Review_Ends",
            date_review_ends,
            "Input review end date (MM/DD/YYYY, leave blank to default to two weeks from today)",
            processor=_parse_review_date
        )
        self.project_manager_name  = XmtlBuildField("Project_Manager",       project_manager_name,  "Input Project Manager Name (e.g. John Doe)")
        self.edp_line1             = XmtlBuildField("EDP_Address_Line_1",    edp_line1,             "Input EDP Name (e.g. EDP Inc.)")
        self.edp_line2             = XmtlBuildField("EDP_Address_Line_2",    edp_line2,             "Input EDP Address Line (e.g. 123 Main St.)")
        self.edp_line3             = XmtlBuildField("EDP_Address_Line_3",    edp_line3,             "Input EDP City, State, Zip (e.g. City, ST 12345)")
        self.reviewer_names        = XmtlBuildField(
            "Reviewer_Names",
            reviewer_names,
            "Input Reviewer Names (semicolon-delimited) (e.g. 'David Jessen, UCSC PP; Jeff Clothier, UCSC PP')",
            processor=lambda v: [name.strip() for name in v.split(";") if name.strip()],
            max_length=540
        )

    @classmethod
    def empty(cls):
        """Create an XmtlBuild with all fields empty, ready for manual prompting."""
        return cls()

    @classmethod
    def from_yaml(cls, yaml_path, key):
        """Load an XmtlBuild from a keyed entry in an xmtl_templates.yaml file.

        Args:
            yaml_path: Path to the YAML templates file.
            key:       Top-level key identifying the template entry (e.g. '3238').

        Raises:
            KeyError: If the key is not present in the file.

        Note:
            Project_Title in the YAML is stored as "number, title" and is split
            back into project_number and project_title on load.
        """
        with open(yaml_path, "r") as f:
            defaults = yaml.safe_load(f)
        if key not in defaults:
            raise KeyError(f"Key '{key}' not found in {yaml_path}\n")
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
            date_review_ends     = d.get("Date_Review_Ends", ""),
            project_manager_name = d.get("Project_Manager", ""),
            edp_line1            = d.get("EDP_Address_Line_1", ""),
            edp_line2            = d.get("EDP_Address_Line_2", ""),
            edp_line3            = d.get("EDP_Address_Line_3", ""),
            reviewer_names       = d.get("reviewer_list", ""),
        )

    def validate(self):
        """Return a list of required field names whose processed_value is still empty.

        Uses processed_value rather than raw value so that a processor which
        generates a default (e.g. revision_number defaulting to '0') is
        considered satisfied without re-prompting the user.
        """
        return [
            field.name for field in vars(self).values()
            if isinstance(field, XmtlBuildField) and field.required and not field.processed_value
        ]

    @property
    def has_edp(self):
        """True if an Executive Design Professional name has been provided."""
        return bool(self.edp_line1.value)

    def fill_all_fields(self, using_defaults=False):
        """Prompt for any fields that are still empty, then retry any required fields
        that remain unresolved after the first pass.

        Required field validation is owned here rather than inside fill_field,
        so that processor-generated defaults (e.g. revision_number defaulting
        to '0') can satisfy a required field without user input.
        """
        for field in [self.project_number, self.project_title, self.submittal_number,
                      self.revision_number, self.specification_section, self.submittal_name,
                      self.date_review_ends, self.project_manager_name]:
            field.fill_field()

        if not using_defaults:
            if click.confirm("Does this submittal have an Executive Design Professional (EDP)?", default=False):
                console.print("\nExample for how to input EDP information: ", style="yellow")
                console.print("\tEHDD Architecture\n\t1 Pier Ste 2\n\tSan Francisco, CA 94111-2028", style="yellow")
                self.edp_line1.fill_field()
                self.edp_line2.fill_field()
                self.edp_line3.fill_field()
            else:
                console.print("No EDP information will be included in the submittal.", style="green")

            console.print("\nInput reviewer names as a semicolon-delimited list", style="bold green")
            console.print("Example: 'David Jessen, UCSC PP;Jeff Clothier, UCSC PP'", style="green")
            console.print("\nNOTE: Reviewer names must not exceed 2 lines so in total reviewer names must not exceed 540 characters", style="red")
        #self.reviewer_names.fill_field()
        
            # enforce max length of reviewer names 
            while True:
                self.reviewer_names.fill_field()
                value = self.reviewer_names.value

                if len(value) > self.reviewer_names.max_length:
                    console.print(
                        f"Reviewer names are {len(value)} characters. "
                        f"Maximum allowed is {self.reviewer_names.max_length} (about 6 lines in PDF).",
                        style="bold red"
                        )
                    self.reviewer_names.value = ""  # reset so it reprompts
                    continue
                break


        # Retry loop — re-prompt only fields still failing validation after the first pass
        while missing := self.validate():
            console.print(f"\nThe following required fields are still missing: {missing}", style="red")
            for field in vars(self).values():
                if isinstance(field, XmtlBuildField) and field.name in missing:
                    field.value = ""
                    field.fill_field()

    def to_render_dict(self):
        """Produce the flat dictionary that render_output() expects.

        Uses processed_value for all fields so that any processor-generated
        defaults or transformations are reflected in the output.
        """
        d = {
            "Project_Title":        f"{self.project_number.value}, {self.project_title.value}",
            "Submittal_Number":     self.submittal_number.value,
            "Revision_Number":      self.revision_number.processed_value,
            "Date_Review_Ends":     self.date_review_ends.processed_value,
            "Specification_Section": self.specification_section.value,
            "Submittal_Name":       self.submittal_name.value,
            "Project_Manager":      self.project_manager_name.value,
            "EDP_Address_Line_1":   self.edp_line1.value,
            "EDP_Address_Line_2":   self.edp_line2.value,
            "EDP_Address_Line_3":   self.edp_line3.value,
        }
        for i, name in enumerate(self.reviewer_names.processed_value or [], start=1):
            d[f"Reviewer_Name_{i}"] = name
        return d


def review_dictionary(dictionary, title):
    """Print a Rich table summarising a render dictionary then ask the user to confirm.

    Args:
        dictionary: The key/value pairs to display.
        title:      Table heading shown to the user.

    Returns:
        True if the user confirms, False if they cancel.
    """
    table = Table(title=title)
    table.add_column("Field", style="#333FFF", no_wrap=True)
    table.add_column("Input", style="#8691F6")
    for key, value in dictionary.items():
        table.add_row(key, str(value))
    console.print(table)

    if click.confirm("Does everything look correct?", default=True):
        console.print("[green]✔ Confirmed[/green]")
    else:
        console.print("✖ Process Cancelled\n", style="bold red")
        return False
    return True

def submittal_filename(project_number: str, revision: str, submittal_number: str, submittal_title: str) -> str:
    """
    Generates a submittal filename based on the project number, revision, submittal number, and title.
    The format is: {project_number}_{revision}_{submittal_number}_{submittal_title}.pdf
    :param project_number: The project number.
    :param revision: The revision number.
    :param submittal_number: The submittal number.
    :param submittal_title: The title of the submittal.
    :return: A formatted filename string.
    """
    revision = "0" if not revision else revision
    filename_str = f"{project_number}_-_{submittal_number}_R{revision}_-_{submittal_title}.pdf"
    
    # replace spaces with underscores
    filename_str = filename_str.replace(" ", "_")
    # replace '&' with 'and'
    filename_str = filename_str.replace("&", "and")
    # replace '%' with 'percent'
    filename_str = filename_str.replace("%", "percent")
    # replace ' - ' with '-'
    filename_str = filename_str.replace(" - ", "-")
    # remove other illegal characters
    filename_str = re.sub(r'[\\/:*?"<>|]', '', filename_str)
    
    return filename_str

def list_template_keys(yaml_path):
    """Return a list of available template keys from an xmtl_templates.yaml file."""
    with open(yaml_path, "r") as f:
        defaults = yaml.safe_load(f)

    table = Table(border_style="yellow")
    table.add_column("Template Keys", style="yellow", header_style="bold yellow", no_wrap=True) 
    for key in defaults.keys():
        if key!="KEY": table.add_row(key)
    console.print((table))
    #return list(defaults.keys())


if __name__ == "__main__":
    console.print(r"""
 __  __     __    __     ______   __            ______   ______     ______     ______   ______     ______     __  __    
/\_\_\_\   /\ "-./  \   /\__  _\ /\ \          /\  ___\ /\  __ \   /\  ___\   /\__  _\ /\  __ \   /\  == \   /\ \_\ \   
\/_/\_\/_  \ \ \-./\ \  \/_/\ \/ \ \ \____     \ \  __\ \ \  __ \  \ \ \____  \/_/\ \/ \ \ \/\ \  \ \  __<   \ \____ \  
  /\_\/\_\  \ \_\ \ \_\    \ \_\  \ \_____\     \ \_\    \ \_\ \_\  \ \_____\    \ \_\  \ \_____\  \ \_\ \_\  \/\_____\ 
  \/_/\/_/   \/_/  \/_/     \/_/   \/_____/      \/_/     \/_/\/_/   \/_____/     \/_/   \/_____/   \/_/ /_/   \/_____/ 
""", style="bold green", highlight=False)
    console.print(Align.center("Submittal transmittal PDF generator", style="italic dim"))
    console.rule(style="green")
    console.print(Panel(
        "[green]This tool streamlines the creation of submittal transmittal PDFs.[/green]\n"
        "Use a [bold yellow]pre-defined template[/bold yellow] or [bold yellow]input values manually[/bold yellow].",
        title="[bold yellow]How to use[/bold yellow]",
        border_style="yellow",
        padding=(0, 2),
    ))
    console.print()

    while True:
        console.print(Align.center("Press [bold red][CTRL+C][/bold red] at any time to exit.", style="dim"))
        console.rule("[bold yellow]Project & Submittal Details[/bold yellow]", style="yellow")
        list_template_keys(_default_templates_path())

        default_key = str(click.prompt(
            "\nTo use an xmtl template, input the template key from the table above (e.g. 3238), otherwise just hit enter to input values manually",
            default=""
        ).strip())

        if default_key:
            try:
                build = XmtlBuild.from_yaml(str(_default_templates_path()), default_key)
                console.print(f"\nXmtl template '{default_key}' loaded. You will be prompted for any missing values.\n", style="bold green")
                build.fill_all_fields(True)
                console.print("\nSummary of Submittal Inputs", style="bold green")
            except KeyError as e:
                console.print(str(e), style="red")
                continue
        else:
            console.print("\nProceeding with manual input...", style="green")
            build = XmtlBuild.empty()
            build.fill_all_fields(False)
            console.print("\nSummary of Submittal Inputs", style="bold yellow")

        dictionary = build.to_render_dict()
        if not review_dictionary(dictionary, "Submittal Details"):
            console.print("\nStarting new submittal generation...", style="green")
            continue

        HTML_FILES = render_output(dictionary)
        #final_pdf_name = click.prompt("Input name for final submittal file")
        final_pdf_name = submittal_filename(
            project_number=build.project_number.value,
            revision=build.revision_number.processed_value,
            submittal_number=build.submittal_number.value,
            submittal_title=build.submittal_name.value
        )
        console.print(f"\nGenerated submittal filename: {final_pdf_name}\n", style="green")
        create_final_pdf(final_pdf_name, HTML_FILES)

        console.rule(style="green")
        console.print(f"[bold green]✔ Submittal PDF '[cyan]{final_pdf_name}[/cyan]' generated successfully![/bold green]\n")
        if not click.confirm("Would you like to generate another submittal?", default=False):
            console.rule(style="dim")
            console.print(Align.center("Thank you for using XMTL Factory! Goodbye!", style="bold green"))
            console.rule(style="dim")
            break
        console.rule(style="dim")
        console.print(Align.center("Starting new submittal...", style="italic green"))
        console.print()









