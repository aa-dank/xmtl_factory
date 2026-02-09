import rich
from rich.console import Console
import click

@click.command()

@click.option('--project_number', prompt='Input Project Number', help='The project number for the submittal')


def fill_dictionary(project_number):
    
    '''dictionary = {
        'Project_Title': project_title,
        'Submittal_No': submittal_no,
        'Revision_No': rev_no,
        'Specification': specification,
        'Description': description,
        'Contractor': contractor_name,
        'EDP_Address_Line_1': EDP_line1,
        'EDP_Address_Line_2': EDP_line2,
        'EDP_Address_Line_3': EDP_line3,
        'Reviewer_Name_1': 'David Jessen, UCSC PP',
    }'''

    
    # gather inputs for project and submittal details

    console.print("\nTO input reviewer names, please input a semicolon delimited list of the reviewer names", style="bold green")
    console.print("Example: 'David Jessen, UCSC PP; Jeff Clothier, UCSC PP'", style="green")
    # gather input for reviewer names
    for reviewer in  reviewer_names.split(";"):
        dictionary[f'Reviewer_Name_{reviewer_names.split(";").index(reviewer)+1}'] = reviewer.strip()

    '''submittal_no = click.prompt("Input Submittal Number")
rev_no = click.prompt("Input Revision Number")
specification = click.prompt("Input Specification (e.g. '07 31 13 Asphalt Shingles')")
description = click.prompt("Input Description (e.g. 'G3 Provost Shingle Sample')")
contractor_name = click.prompt("Input Contractor Name")
EDP_line1 = click.prompt("Input Eexecutive Design Professional (e.g. 'EHDD Architecture')")
EDP_line2 = click.prompt("Input EDP Address (e.g. '1 Pier Ste 2')")
    EDP_line3 = click.prompt("Input EDP City, State, & Zip (e.g. 'San Francisco, CA 94111-2028')")'''

if __name__ == "__main__":
    console = Console()
    console.print("Welcome to the Submittal Generator!", style="bold green")
    console.print("Project & Submittal Details", style="green")
    fill_dictionary()



