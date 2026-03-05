# xmtl-factory Documentation

This text file gives a user-visible overview of using the xmtl-factory CLI program. It’s meant for people who just want to run the tool and don’t care about the internals; the full README.md has technical details.

**Notes:**

- Make sure a suitable Python environment is active (Python 3.13+)  
- To close program: \*\*CTR \+ C\*\*  
- Refer to DEMO.mp4 to show video of usage

## RUNNING PROGRAM

**START:** Open the "xmtl\_factory.exe" file 

**WORKFLOW:**

Program will start by asking if you want to use a template or manually input values.

**Manual Entry**

If using manual entry, press “ENTER”

For manual entry, the program will ask for the following values: (\\\* fields are required)

1. Project Number\\\*  
2. Project Title\\\*  
3. Submittal Number\\\*  
4. Revision Number\\\*  
5. Specification Section\\\*  
6. Submittal Name\\\*  
7. Review End Date  
8. Project Manager Name  
9. Executive Design Professional Name  
10. EDP Address  
11. EDP City, State, & Zip  
12. Reviewer Names \- NOTE: reviewer names need to be semi-colon delimited

**Template Usage**

If using templates, look in “xmtl\_templates.yaml” file for templates to use

When program asks for a template enter key. Each time the programs runs, it will print out all the available keys. 

If any values from the template chosen are empty, the program will ask to fill those in

- Program will always ask to input review end date

**Verification**

Once all the data is filled in, a summary of inputs will be printed.

Users will be prompted if summary is correct. 

- If not, the process will be canceled, and program will start from top.  
- If summary is correct, then a filename will be generated including the project number, revision & submittal number, and the submittal title    
  * Output file will be written to the current working directory  
  * Once output file is created, it can be renamed if need be

When the run completes the CLI prints the path of the new PDF. Open it in any PDF viewer and print or email as needed.

## 

## USING xmtl\_templates.yaml FILE

Templates let you reuse common project settings without retyping them, if creating many submittals with the same information. 

When you are preparing a submittal for a project you work on often, create an entry with a unique key (typically the project number or another short identifier). At the prompt the CLI will ask for this key; if it finds a matching section the values are loaded, and you're only asked to supply any missing fields.  

Only five fields are required; everything else is optional. (Refer to Manual Entry to see which fields are required). Even if a field is required it does not have to be filled in for the yaml file, as the program will ask to fill in all required fields anyway like in a manual run. 

**Entering New Templates:**

Syntax is very important\!

1. Pick a unique string that will serve as the key (e.g. "3238")  
2. Copy the reference block below and paste it after the existing entries (shown in Template Usage, should be at top of the file).  
3. Fill in as many of the fields as you know.    
4. Save the file.  The next time you run \`submittal\_cli.py\` you can enter the key at the prompt instead of typing all the values.

## OTHER NOTES

**Keep in mind when entering information:**

- The template can only handle a certain amount of information, so if you are entering information that takes up too much space it will lead to extra pages being generated unnecessarily. This is most important for specifically reviewer names and submittal names.  
  * Reviewer Names can be at a maximum 2 lines   
  * Submittal Name can be at a maximum of 10 extra lines   
  * Overall, page 1 can have 10 extra lines, page 2 has 5, and page 3 has 7  
- If you want to have line breaks in the input, use ”**\<br\>**” 

**Page Generation:** 

1. PAGE 1 will always be generated; it includes most required fields like project header, submittal details, and manager response box.  
2. PAGE 2 is added only if an EDP address is supplied; it holds the EDP review block and up to three reviewer slots.  
3. PAGE 3 and on are  additional pages for reviewers beyond the first three (four per page).

A blank reviewer slot is always appended so you can add an unlisted reviewer.

**Where to look for more info:**

\`README.md\` – full documentation, project design, dependencies, etc.

‘DEMO.mp4’ – video demonstrating manual entry and template usage

