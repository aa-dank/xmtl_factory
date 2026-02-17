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
    'Contractor': '',               #Nathan Jensen
    'has_EDP': 'True',              #True or False for whether to include EDP information
    'EDP_Address_Line_1': '',       #EHDD Architecture
    'EDP_Address_Line_2': '',       #1 Pier Ste 2
    'EDP_Address_Line_3': '',       #San Francisco, CA 94111-2028
    'Reviewer_Names': ['David Jessen, UCSC PP', 'Jeff Clothier, UCSC PP'] #List of reviewer names to be included in the submittal
}

# Render outputs
def render_output(dictionary):

    output_page1 = template_1.render(dictionary)
    output_page2 = template_2.render(dictionary)
    output_page3 = template_3.render(dictionary)

    with open('output_page1.html', 'w') as f:
        f.write(output_page1)
    with open('output_page2.html', 'w') as f:
        f.write(output_page2)
    with open('output_page3.html', 'w') as f:
        f.write(output_page3)
    

HTML_FILES = [
    "output_page1.html",
    "output_page2.html",
    "output_page3.html",
]
