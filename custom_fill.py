import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the app's resource directory.

    When running as a PyInstaller one-file executable, resources are extracted
    to a temporary directory stored in sys._MEIPASS. When running from source,
    resources are found relative to this file's directory.
    """
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return base / relative


env = Environment(loader=FileSystemLoader(str(resource_path('templates'))))

# Retreive templates
template_1 = env.get_template('Page1.HTML')
template_2 = env.get_template('Page2.HTML')
template_3 = env.get_template('Page3.HTML')

# Render outputs
def render_output(dictionary):
    # Clean up old output files
    for old_file in Path('.').glob('output_*.html'):
        old_file.unlink()

    # Absolute file:// URI so wkhtmltopdf can find styles.css and images/
    # regardless of where the user's cwd is or where the exe was extracted.
    resource_dir = resource_path('.').as_uri()

    HTML_FILES = []
    # create list of reviewer names & remove from main dictionary 
    remaining_distribution_emails = [
        value for key, value in dictionary.items() if key.startswith('Reviewer_Name')
    ]
    # Always ensure at least one blank reviewer slot before any pages consume names
    remaining_distribution_emails.append('')
    dictionary = {
        key: value for key, value in dictionary.items() if not key.startswith('Reviewer_Name')
    }

    # Render page 1
    output_page1 = template_1.render(**dictionary, resource_dir=resource_dir)
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

        output_page2 = template_2.render(**consultant_review_dict, resource_dir=resource_dir)
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

        output_page3 = template_3.render(**reviewer_xmtl_dict, resource_dir=resource_dir)
        with open(f'output_page3_{reviewer_xmtl_pages}.html', 'w') as f:
            f.write(output_page3)
        HTML_FILES.append(f'output_page3_{reviewer_xmtl_pages}.html')
    
    return HTML_FILES
    


