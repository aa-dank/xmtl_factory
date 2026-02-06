from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta

env = Environment(loader=FileSystemLoader('templates'))

# Retreive templates
template_1 = env.get_template('Page1.HTML')
template_2 = env.get_template('Page2.HTML')
template_3 = env.get_template('Page3.HTML')

# Input dictionary
dictionary = {
    'Project_Title': 'Project 3239, Kresge College - Non-academic Renovation Project',
    'Submittal_No': '4-073113-03',
    'Revision_No': '0',
    'Date_Review_Ends': datetime.now() + timedelta(weeks=2),
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

# Render outputs
output_page1 = template_1.render(dictionary)
output_page2 = template_2.render(dictionary)
output_page3 = template_3.render(dictionary)

# Write outputs
with open('output_page1.html', 'w') as f:
    f.write(output_page1)
with open('output_page2.html', 'w') as f:
    f.write(output_page2)
with open('output_page3.html', 'w') as f:
    f.write(output_page3)

print("Render Complete!")