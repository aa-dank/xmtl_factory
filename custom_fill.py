from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta

env = Environment(loader=FileSystemLoader('templates'))

# Retreive templates
template_1 = env.get_template('Page1.HTML')
template_2 = env.get_template('Page2.HTML')
template_3 = env.get_template('Page3.HTML')

# BASE Input dictionary
dictionary = {
    'Project_Title': '',            #Project 3239, Kresge College - Non-academic Renovation Project
    'Submittal_No': '',             #4-073113-03
    'Revision_No': '',              #0
    'Date_Review_Ends': datetime.now() + timedelta(weeks=2),
    'Specification': '',            #07 31 13 Asphalt Shingles
    'Description': '',              #G3 Provost Shingle Sample
    #'Contractor': '',               #Nathan Jensen
    'EDP_Address_Line_1': 'dddd',       #EHDD Architecture
    'EDP_Address_Line_2': '',       #1 Pier Ste 2
    'EDP_Address_Line_3': '',       #San Francisco, CA 94111-2028
    'Reviewer_Name_1': 'Ken Rector, UCSC PPC', 
    'Reviewer_Name_2': 'Met DeMonner, UCSC PPC',
}
HTML_FILES = []

# Render outputs
def render_output(dictionary):
    HTML_FILES = []
    consultant_review_dict = {}
    # create list of reviewer names & remove from main dictionary 
    remaining_distribution_emails = [
        value for key, value in dictionary.items() if key.startswith('Reviewer_Name')
    ]
    remaining_distribution_emails.append('')  # Ensure there's always a blank slot for the last reviewer
    dictionary = {
        key: value for key, value in dictionary.items()if not (key.startswith('Reviewer_Name'))
    }

    # Render page 1 
    output_page1 = template_1.render(**dictionary, **consultant_review_dict)
    with open('output_page1.html', 'w') as f:
        f.write(output_page1)
    HTML_FILES.append('output_page1.html')

    # Render page 2 only if EDP information is included
    if dictionary['EDP_Address_Line_1']:
        consultant_review_dict = {
            'EDP_Address_Line_1': dictionary['EDP_Address_Line_1'],       
            'EDP_Address_Line_2': dictionary['EDP_Address_Line_2'],      
            'EDP_Address_Line_3': dictionary['EDP_Address_Line_3'],  
        }

        if remaining_distribution_emails:
        # if there are remaining distribution emails, add them to the consultant review dict
            consultant_review_dict['Reviewer_Name_1'] = remaining_distribution_emails.pop(0)
        if remaining_distribution_emails:
            # if there are still remaining distribution emails, add them to the consultant review dict
            consultant_review_dict['Reviewer_Name_2'] = remaining_distribution_emails.pop(0)
        if remaining_distribution_emails:
            # if there are still remaining distribution emails, add them to the consultant review dict
            consultant_review_dict['Reviewer_Name_3'] = remaining_distribution_emails.pop(0)

        output_page2 = template_2.render(consultant_review_dict)
        with open('output_page2.html', 'w') as f:
            f.write(output_page2)
        HTML_FILES.append('output_page2.html')

    #while there are still emails in the distribution list, create a reviewers transmittals ensuring there is
    # at least one additional blank reviewer review slot
    
    reviewer_xmtl_pages = 0
    while len(remaining_distribution_emails) > 0:
        reviewer_xmtl_dict = {}
        reviewer_xmtl_pages += 1
        if remaining_distribution_emails:
            reviewer_xmtl_dict['Reviewer_Name_1'] = remaining_distribution_emails.pop(0)
        if remaining_distribution_emails:
            reviewer_xmtl_dict['Reviewer_Name_2'] = remaining_distribution_emails.pop(0)
        if remaining_distribution_emails:
            reviewer_xmtl_dict['Reviewer_Name_3'] = remaining_distribution_emails.pop(0)
        if remaining_distribution_emails:
            reviewer_xmtl_dict['Reviewer_Name_4'] = remaining_distribution_emails.pop(0)

        output_page3 = template_3.render(**reviewer_xmtl_dict)
        with open(f'output_page3_{reviewer_xmtl_pages}.html', 'w') as f:
            f.write(output_page3)
        HTML_FILES.append(f'output_page3_{reviewer_xmtl_pages}.html')
    
    return HTML_FILES
    


