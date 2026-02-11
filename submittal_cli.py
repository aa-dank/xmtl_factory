import rich
from rich.console import Console
import click
from html_to_pdf import create_final_pdf
from custom_fill import render_output
from datetime import datetime, timedelta

@click.command()

# gather inputs for project and submittal details
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


def cli(project_number, project_title, submittal_no, rev_no, specification, description, contractor_name, edp_line1, edp_line2, edp_line3):
    #read inputs into dictionary
    dictionary = {
        'Project_Title': project_number+", "+ project_title,
        'Submittal_No': submittal_no,
        'Revision_No': rev_no,
        'Date_Review_Ends': datetime.now() + timedelta(weeks=2),
        'Specification': specification,
        'Description': description,
        'Contractor': contractor_name,
        'EDP_Address_Line_1': edp_line1,
        'EDP_Address_Line_2': edp_line2,
        'EDP_Address_Line_3': edp_line3,
    }
    
    # gather input for reviewer names
    console.print("\nTO input reviewer names, please input a semicolon delimited list of the reviewer names", style="bold green")
    console.print("Example: 'David Jessen, UCSC PP; Jeff Clothier, UCSC PP'", style="green")
    reviewer_names = click.prompt("Input Reviewer Names")
    for reviewer in  reviewer_names.split(";"):
        dictionary[f'Reviewer_Name_{reviewer_names.split(";").index(reviewer)+1}'] = reviewer.strip()

    for x, y in dictionary.items():
        print(f'{x}: {y}')
    
    render_output(dictionary)
    final_pdf_name = click.prompt("Input name for final submittal file")
    create_final_pdf(final_pdf_name)

if __name__ == "__main__":
    console = Console()
    console.print("Welcome to the Submittal Generator!", style="bold green")
    console.print("Project & Submittal Details", style="green")
    cli()


    




