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
    
    #insert date review ends into dictionary & add reviewer names into dictionary with correct formatting
    reviewer_names = default_keys.pop('reviewer_list')
    items = list(default_keys.items())
    items.insert(3,('Date_Review_Ends', date.strftime("%m/%d/%Y")))
    
    for reviewer in  reviewer_names.split(";"):
        items.insert(len(items), (f'Reviewer_Name_{reviewer_names.split(";").index(reviewer)+1}', reviewer.strip()))
    default_keys = dict(items)
    
    return default_keys

def review_dictionary(dictionary, title): #print out summary of inputs into a table
    table = Table(title=title)
    table.add_column("Field", style="#333FFF", no_wrap=True)
    table.add_column("Input", style="#8691F6")

    #add rows to table for each key and print it out
    for key, value in dictionary.items():
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
    }

    # add reviewer names into dictionary as separate key value pairs
    for reviewer in  reviewer_names.split(";"):
        dictionary[f'Reviewer_Name_{reviewer_names.split(";").index(reviewer)+1}'] = reviewer.strip()

    return dictionary

def get_inputs_manual(): #manually gather inputs for project and submittal details
    project_number = click.prompt("Input Project Number")
    project_title = click.prompt("Input Project Title")
    submittal_no = click.prompt("Input Submittal Number")
    rev_no = click.prompt("Input Revision Number")
    specification = click.prompt("Input Specification")
    description = click.prompt("Input Description")
    contractor_name = click.prompt("Input Contractor Name")

    # check if submittal has EDP information and gather inputs if so
    if click.confirm("Does this submittal have an Executive Design Professional (EDP)?", default=False):
        edp_line1 = click.prompt("Input Executive Design Professional Name")
        edp_line2 = click.prompt("Input EDP Address (e.g. 1 Pier Ste 2)")
        edp_line3 = click.prompt("Input EDP City, State, & Zip (e.g. San Francisco, CA 94111-2028)")
    else: # otherwise leave EDP fields blank 
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
        #check if default key exists in yaml file 
        default_dict = check_defaults(default_key) 
        if default_dict: 
            # if input key exists, print out summary of default values and confirm with user before proceeding
            console.print(f"\nSummary of Default Values for key {default_key}:", style="bold green")
            if review_dictionary(default_dict, "Default Values"):
                dictionary = default_dict

            else: exit()     
    else: # if user does not want to use default values, proceed with manual input 
        console.print("\nProceeding with manual input", style="green")
        dictionary = get_inputs_manual()
        
        # print out summary of manual inputs and confirm with user before proceeding
        console.print("\nSummary of Submittal Inputs", style="bold green")
        if review_dictionary(dictionary, "Submittal Details"):
            pass
        else: exit()

    # render outputs and create final pdf
    HTML_FILES = render_output(dictionary)
    final_pdf_name = click.prompt("Input name for final submittal file")
    create_final_pdf(final_pdf_name, HTML_FILES)







