# **xmtl-factory Quick Start Guide**



This text file gives a user-visible overview of using the xmtl-factory CLI

program. It’s meant for people who just want to run the tool and don’t care

about the internals; the full README.md has technical details.



Notes:

Make sure a suitable Python environment is active (Python 3.13+)

To close program: **CTR + C**



##### RUNNING PROGRAM

**START**: Open the "xmtl\_factory.exe" file 



The program will prompt you step by step. Refer to DEMO.mp4 to show video of usage



###### Workflow:

Program will start by asking if you want to use a template or manually input values.



**Manual Entry**

If using manual entry the program will ask for the following values: (\* fields are not required)

&nbsp;	

1. Project Number
2. Project Title
3. Submittal Number
4. Revision Number\*
5. Specification Section
6. Submittal Name
7. Review End Date\*
8. Project Manager Name
9. Executive Design Professional Name\*
10. EDP Address\*
11. EDP City, State, \& Zip\*
12. Reviewer Names\* - NOTE: reviewer names need to be semi-colon delimited





**Template** 





**Verification**

Once all the data is filled in, a summary of inputs will be printed.

User will be prompted if summary is correct. 



If not the process will be canceled and program will start from top.

If summary is correct, then user will be prompted for xtml name - NOTE name MUST end in ".pdf"









##### USING .YAML FILE

































\* \*\*Load a template\*\* – enter a key from `xmtl\_templates.yaml` or hit return to

&nbsp; answer questions manually.

\* \*\*Choose output filename\*\* – name of the generated PDF, written to the

&nbsp; current directory.



> Tip: templates let you reuse common project settings without retyping them.

> An example template (`3238`) is shown during the first run.



When the run completes the CLI prints the path of the new PDF. Open it in any

PDF viewer and print or email as needed.



---

\# Making the program easier to run



\* \*\*Edge requirement:\*\* the utility uses Headless Edge to convert HTML into

&nbsp; PDF. It usually finds your Edge installation automatically, but if it fails

&nbsp; set the environment variable `EDGE\_PATH` to the full path of `msedge.exe`.

\* \*\*Python environment:\*\* the `pyproject.toml` lists required packages. Run

&nbsp; `uv sync` (with the uv environment manager) or `pip install .` to install

&nbsp; them.

\* \*\*Executable option:\*\* to avoid installing Python on a workstation, build a

&nbsp; standalone executable with PyInstaller using the provided spec file:



&nbsp;     pyinstaller --clean xmtl\_factory.spec



&nbsp; The bundled program (`dist/xmtl\_factory.exe`) runs like the script and

&nbsp; already contains the HTML templates and default YAML.



---

\# Templates and data entry



Templates reside in `xmtl\_templates.yaml`. Each entry has a key you type at

startup and a set of fields that prefill the CLI prompts. Only five fields are

required; everything else is optional:



&nbsp; \* \*\*Required:\*\* `Project\_Title`, `Submittal\_Number`, `Revision\_Number`,

&nbsp;   `Specification\_Section`, `Submittal\_Name`.

&nbsp; \* \*\*Optional:\*\* `Project\_Manager`, `EDP\_Address\_Line\_1/2/3`,

&nbsp;   `reviewer\_list` (semicolon-separated list of "Name, Dept").



Any field left blank during template creation will trigger a prompt when you

run the CLI.



---

\# Output summary (for reference)



\* \*\*Page 1:\*\* always generated; includes project header and manager response

&nbsp; box.

\* \*\*Page 2:\*\* added only if an EDP address is supplied; it holds the EDP review

&nbsp; block and up to three reviewer slots.

\* \*\*Page 3+\*\*: additional pages for reviewers beyond the first three (four per

&nbsp; page). A blank slot is always appended so you can add an unlisted reviewer.



---

\# Where to look for more info



\* `README.md` – full documentation, project design, dependencies, etc.

\* `templates/` – HTML source for each page.

\* `submittal\_cli.py` – the CLI logic and data model.



The quick guide above should get most users started in seconds.

