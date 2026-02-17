import rich
from rich.console import Console
from rich.table import Table
import click
from html_to_pdf import create_final_pdf
from custom_fill import render_output
from datetime import datetime, timedelta
import yaml

date = datetime.now() + timedelta(weeks=2)

def check_defaults(default_key):
    #open and read the yaml file
    with open("default_values.yaml", "r") as file:
        defaults = yaml.safe_load(file)

    #check if the default key exists in the yaml file & put into dictionary
    if default_key in defaults:
        default_keys = defaults.get(default_key, [])
    else:
        console.print(f"\nNo default values found for key: {default_key}", style="red")
        return None
    
    reviewer_names = default_keys.pop('reviewer_list')
    reviewer_names = [name.strip() for name in reviewer_names.split(";")]

    #insert date review ends into dictionary & add reviewer names  as a list to dictionary
    items = list(default_keys.items())
    items.insert(3,('Date_Review_Ends', date.strftime("%m/%d/%Y")))
    items.append(('Reviewer_Names', reviewer_names))
    default_keys = dict(items)
    
    return default_keys
    

def review_dictionary(dictionary):
    #print out summary of inputs into a table
    table = Table(title="Submittal Details")
    table.add_column("Field", style="#333FFF", no_wrap=True)
    table.add_column("Input", style="#8691F6")
    for key, value in dictionary.items():
        # If value is a list → iterate through it
        if isinstance(value, list):
            for i, item in enumerate(value, start=1):
                table.add_row(f"{key} {i}", str(item))
        else:
            table.add_row(key, str(value))

    console.print(table)

    #confirm with user that inputs are correct before proceeding
    if click.confirm("Does everything look correct?", default=True):
        console.print("[green]✔ Confirmed[/green]")
    else:
        console.print("✖ Process Cancelled", style="bold red")
        return False
    return True

def fill_dictionary(project_number, project_title, submittal_no, rev_no, specification, description, contractor_name, edp_line1, edp_line2, edp_line3, reviewer_names):
    #read inputs into dictionary    
    dictionary = {
        'Project_Title': project_number+", "+ project_title,
        'Submittal_No': submittal_no,
        'Revision_No': rev_no,
        'Date_Review_Ends': date.strftime("%m/%d/%Y"),
        'Specification': specification,
        'Description': description,
        'Contractor': contractor_name,
        'EDP_Address_Line_1': edp_line1,
        'EDP_Address_Line_2': edp_line2,
        'EDP_Address_Line_3': edp_line3,
        'Reviewer_Names': reviewer_names.split(";")
    }

    return dictionary

def get_inputs_manual(): #manually gather inputs for project and submittal details
    project_number = click.prompt("Input Project Number")
    project_title = click.prompt("Input Project Title")
    submittal_no = click.prompt("Input Submittal Number")
    rev_no = click.prompt("Input Revision Number")
    specification = click.prompt("Input Specification")
    description = click.prompt("Input Description")
    contractor_name = click.prompt("Input Contractor Name")

    if click.confirm("Does this submittal have an Executive Design Professional (EDP)?", default=False):
        edp_line1 = click.prompt("Input Executive Design Professional Name")
        edp_line2 = click.prompt("Input EDP Address (e.g. 1 Pier Ste 2)")
        edp_line3 = click.prompt("Input EDP City, State, & Zip (e.g. San Francisco, CA 94111-2028)")
    else:
        console.print("No EDP information will be included in the submittal.", style="green")
        edp_line1 = ""
        edp_line2 = ""
        edp_line3 = ""
    
    # gather input for reviewer names
    console.print("\nTO input reviewer names, please input a semicolon delimited list of the reviewer names WITHOUT SPACES", style="bold green")
    console.print("Example: 'David Jessen, UCSC PP;Jeff Clothier, UCSC PP'", style="green")
    reviewer_names = click.prompt("Input Reviewer Names", default='')
    
    return fill_dictionary(project_number, project_title, submittal_no, rev_no, specification, description, contractor_name, edp_line1, edp_line2, edp_line3, reviewer_names)


if __name__ == "__main__":
    console = Console()
    console.print("Welcome to the Submittal Generator!\n", style="bold green")
    console.print("Project & Submittal Details", style="green")

    #ask user if they want to use default values 
    default_key = str(click.prompt("To use default values, input the default key (e.g. 3238), otherwise just hit enter to input values manually", default="").strip())
    if default_key: 
        default_dict = check_defaults(default_key)
        if default_dict:
            console.print(f"\nSummary of Default Values for key {default_key}:", style="bold green")
            if review_dictionary(default_dict):
                dictionary = default_dict       
    else:
        console.print("\nProceeding with manual input", style="green")
        dictionary = get_inputs_manual()
        print(dictionary)

    console.print("\nSummary of Submittal Inputs", style="bold green")
    if review_dictionary(dictionary):
        render_output(dictionary)
        final_pdf_name = click.prompt("Input name for final submittal file")
        create_final_pdf(final_pdf_name)





# gather inputs for project and submittal details
'''@click.command()
@click.option('--project_number', prompt='Input Project Number', help='Project Number, e.g. 3239')
@click.option('--project_title', prompt='Input Project Title', help='Project Title, e.g. Kresege COllege - Non-academic Renovation Project')
@click.option('--submittal_no', prompt='Input Submittal Number', help='Submittal Number, e.g. 4-073113-03')
@click.option('--rev_no', prompt='Input Revison Number', help='Revison Number, e.g. 0')
@click.option('--specification', prompt='Input Specification', help='Specification, e.g. 07 31 13 Asphalt Shingles')
@click.option('--description', prompt='Input Description', help='Description, e.g. G3 Provost Shingle Sample')
@click.option('--contractor_name', prompt='Input Contractor Name', help='Contractor Name, e.g. Nathan Jenson')
@click.option('--edp_line1', prompt='Input Executive Design Professional Name', help='EDP Address, e.g. EHDD Architecture')
@click.option('--edp_line2', prompt='Input EDP Address (e.g. 1 Pier Ste 2)', help='EDP Address, e.g. 1 Pier Ste 2')
@click.option('--edp_line3', prompt='Input EDP City, State, & Zip (e.g. San Francisco, CA 94111-2028)', help='EDP Address, e.g. San Francisco, CA 94111-2028')
#project_number, project_title, submittal_no, rev_no, specification, description, contractor_name, edp_line1, edp_line2, edp_line3
'''




