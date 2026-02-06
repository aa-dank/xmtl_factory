import rich
import click

project_title = click.prompt("Input Project Title")
submittal_no = click.prompt("Input Submittal Number")

dictionary = {
    'Project_Title': project_title,
    'Submittal_No': submittal_no,
    'Revision_No': '0',
    'Specification': '07 31 13 Asphalt Shingles',
    'Description': 'G3 Provost Shingle Sample',
    'Contractor': 'Nathan Jensen',
    'EDP_Address_Line_1': 'EHDD Architecture',
    'EDP_Address_Line_2': '1 Pier Ste 2',
    'EDP_Address_Line_3': 'San Francisco, CA 94111-2028',
    'Reviewer_Name_1': 'David Jessen, UCSC PP',
    'Reviewer_Name_2': 'Jeff Clothier, UCSC PP',
    'Reviewer_Name_3': '',
    'Reviewer_Name_4': '',
    'Reviewer_Name_5': '',
    'Reviewer_Name_6': '',
    'Reviewer_Name_7': ''
}

