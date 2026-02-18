# xmtl-factory

A CLI tool for generating construction submittal transmittal PDFs for UCSC Physical Planning & Development Operations. Each transmittal is a multi-page PDF containing project details, review action checkboxes, and signature lines for the project manager, Executive Design Professional (EDP), and individual reviewers.

## Requirements

- Python 3.13+
- Microsoft Edge installed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

## Installation

```bash
# Create and activate a virtual environment (uv recommended)
uv sync

# Or with pip
pip install .
```

## Usage

Run the CLI from the project root:

```bash
python submittal_cli.py
```

You will be prompted to either load a saved template from `xmtl_templates.yaml` by key, or enter all values manually. After confirming the inputs, the final PDF is written to the current directory.

### Example session

```
To use an xmtl template, input the template key (e.g. 3238), otherwise just hit enter: 3238

Xmtl template '3238' loaded. You will be prompted for any missing values.

...

Input name for final submittal file: 3238_07-31-13_R0
```

## Output structure

| Page | Content | Generated when |
|------|---------|----------------|
| Page 1 | Project header, submittal details, official response box | Always |
| Page 2 | EDP review section + up to 3 reviewers | EDP address is provided |
| Page 3+ | Up to 4 additional reviewers per page | More reviewers than Page 2 can hold |

## xmtl_templates.yaml

Pre-fill project data by adding entries to `xmtl_templates.yaml`. Each top-level key is used as the template key at the CLI prompt.

```yaml
"my-project-key":
  Project_Title: "12345, My Project Title"
  Submittal_Number: "001"
  Revision_Number: "0"
  Specification_Section: "07 31 13 Asphalt Shingles"
  Submittal_Name: "Shingle Sample"
  Project_Manager: "Jane Smith"        # optional
  EDP_Address_Line_1: "Firm Name"      # optional — omit to skip Page 2
  EDP_Address_Line_2: "123 Main St"
  EDP_Address_Line_3: "City, CA 90000"
  reviewer_list: "Reviewer A, Dept;Reviewer B, Dept"  # semicolon-delimited, optional
```

**Required fields:** `Project_Title`, `Submittal_Number`, `Revision_Number`, `Specification_Section`, `Submittal_Name`

**Optional fields:** `Project_Manager`, `EDP_Address_Line_1/2/3`, `reviewer_list`

Any fields left blank in the template will be prompted for at runtime.

## Project structure

```
submittal_cli.py        # Entry point — XmtlBuild class and CLI logic
custom_fill.py          # Jinja2 rendering and HTML output logic
html_to_pdf.py          # Edge headless PDF conversion and merging
xmtl_templates.yaml     # Saved project templates
templates/
    Page1.HTML          # Cover page template
    Page2.HTML          # EDP + reviewer template
    Page3.HTML          # Additional reviewer pages template
styles.css              # Shared stylesheet for all pages
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `click` | CLI prompts |
| `jinja2` | HTML template rendering |
| `pypdf` | PDF merging |
| `pyyaml` | Template file parsing |
| `rich` | Formatted terminal output |
| `pyinstaller` *(dev)* | Standalone executable packaging |
