# xmtl-factory

A CLI tool for generating construction submittal transmittal PDFs for UCSC Physical Planning & Development Operations. Each transmittal is a multi-page PDF containing project details, review action checkboxes, and signature lines for the project manager, Executive Design Professional (EDP), and individual reviewers.

## Requirements

- Python 3.13+
- Microsoft Edge installed (detected from `EDGE_PATH`, `PATH`, registry, or common install locations)

If Edge is installed in a non-standard location, set `EDGE_PATH` to the full path of `msedge.exe`.

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

The number of pages in the final PDF depends on whether an EDP is provided and how many reviewers are listed.

**Page 1** is always generated. It contains the project header, submittal details, and the official response box with the project manager's name.

**Page 2** is generated only when an EDP address is provided. It contains the EDP's review section followed by review action slots for the first 3 reviewers from `reviewer_list`.

**Page 3+** are generated for any reviewers not consumed by Page 2, with 4 reviewer slots per page. These pages are added in sequence until all reviewers are placed.

Regardless of how many reviewers are listed, there is always at least one blank reviewer slot at the end of the document — ensuring there is room for a reviewer not listed on the transmittal.

### Examples

| EDP | Reviewers | Pages generated |
|-----|-----------|-----------------|
| No | 0 | Page 1, Page 3 (1 blank slot) |
| No | 2 | Page 1, Page 3 (2 named + 1 blank) |
| No | 5 | Page 1, Page 3 (4 named), Page 3_2 (1 named + 1 blank) |
| Yes | 0 | Page 1, Page 2 (EDP + 1 blank slot) |
| Yes | 3 | Page 1, Page 2 (EDP + 3 named), Page 3 (1 blank slot) |
| Yes | 5 | Page 1, Page 2 (EDP + 3 named), Page 3 (2 named + 1 blank) |

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

## Build executable (PyInstaller)

Use the included spec file to package templates, images, CSS, and default YAML:

```bash
pyinstaller --clean xmtl_factory.spec
```

The executable is generated at `dist/xmtl_factory.exe`.

If Edge is installed in a non-standard location on the target machine, set `EDGE_PATH` before running the executable.
