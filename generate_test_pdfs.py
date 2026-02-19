"""Manual visual test script — generates PDFs for known edge cases.

Run from the project root:
    python generate_test_pdfs.py

Output PDFs are written to ./test_output/.
Intermediate HTML files are written to the project root (cwd) by render_output()
and are cleaned up automatically on each run.

Review each PDF manually to verify layout, spacing, page breaks, and that
reviewer names and EDP blocks render as expected.
"""

import os
from pathlib import Path

from custom_fill import render_output
from html_to_pdf import create_final_pdf
from submittal_cli import XmtlBuild

OUT_DIR = Path("test_output")
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Test cases: (output_filename_stem, XmtlBuild kwargs)
# ---------------------------------------------------------------------------
CASES = [
    (
        "no_edp_no_reviewers",
        dict(
            reviewer_names="",
        ),
    ),
    (
        "no_edp_one_reviewer",
        dict(
            reviewer_names="Alice Smith, Engineering",
        ),
    ),
    (
        "no_edp_four_reviewers",
        dict(
            reviewer_names="Alice Smith, Engineering;Bob Jones, Architecture;Carol Lee, Civil;Dave Kim, Mechanical",
        ),
    ),
    (
        "no_edp_five_reviewers",
        dict(
            reviewer_names="Alice Smith, Engineering;Bob Jones, Architecture;Carol Lee, Civil;Dave Kim, Mechanical;Eve Brown, Electrical",
        ),
    ),
    (
        "edp_no_reviewers",
        dict(
            edp_line1="EHDD Architecture",
            edp_line2="1 Pier Ste 2",
            edp_line3="San Francisco, CA 94111-2028",
            reviewer_names="",
        ),
    ),
    (
        "edp_one_reviewer",
        dict(
            edp_line1="EHDD Architecture",
            edp_line2="1 Pier Ste 2",
            edp_line3="San Francisco, CA 94111-2028",
            reviewer_names="Alice Smith, Engineering",
        ),
    ),
    (
        "edp_three_reviewers",
        dict(
            edp_line1="EHDD Architecture",
            edp_line2="1 Pier Ste 2",
            edp_line3="San Francisco, CA 94111-2028",
            reviewer_names="Alice Smith, Engineering;Bob Jones, Architecture;Carol Lee, Civil",
        ),
    ),
    (
        "edp_five_reviewers",
        dict(
            edp_line1="EHDD Architecture",
            edp_line2="1 Pier Ste 2",
            edp_line3="San Francisco, CA 94111-2028",
            reviewer_names="Alice Smith, Engineering;Bob Jones, Architecture;Carol Lee, Civil;Dave Kim, Mechanical;Eve Brown, Electrical",
        ),
    ),
    (
        "blank_revision_number",
        dict(
            revision_number="",
            reviewer_names="Alice Smith, Engineering",
        ),
    ),
    (
        "high_revision_number",
        dict(
            revision_number="5",
            reviewer_names="Alice Smith, Engineering",
        ),
    ),
    (
        "long_names",
        dict(
            edp_line1="Gordon Prill Consulting Engineers, Inc.",
            edp_line2="310 East Caribbean Drive, Suite 200",
            edp_line3="Sunnyvale, CA 94089-1100",
            reviewer_names=(
                "A Very Long Reviewer Name, Department of Structural Engineering;"
                "Another Quite Long Reviewer Name, Department of Mechanical and Electrical;"
                "Yet Another Name With A Long Title, UCSC Physical Planning and Development"
            ),
            submittal_name="Extra Long Submittal Description That Tests Name Wrapping on Page 1",
        ),
    ),
    (
        "from_yaml_3238",
        None,  # loaded from yaml — see special handling below
    ),
]

# Common base kwargs applied to all programmatic cases
BASE_KWARGS = dict(
    project_number="9999",
    project_title="Visual Test Project",
    submittal_number="001",
    revision_number="0",
    specification_section="07 31 13 Asphalt Shingles",
    submittal_name="Test Submittal Item",
    project_manager_name="Jane Smith",
    date_review_ends="03/15/2026",
)

# ---------------------------------------------------------------------------
# Generate PDFs
# ---------------------------------------------------------------------------
print(f"Writing test PDFs to ./{OUT_DIR}/\n")

for name, overrides in CASES:
    print(f"  Generating: {name}.pdf ...", end=" ", flush=True)

    if overrides is None:
        # Special case: load from yaml template
        try:
            build = XmtlBuild.from_yaml("xmtl_templates.yaml", "3238")
        except KeyError as e:
            print(f"SKIPPED ({e})")
            continue
    else:
        kwargs = {**BASE_KWARGS, **overrides}
        build = XmtlBuild(**kwargs)

    render_dict = build.to_render_dict()
    html_files = render_output(render_dict)

    output_path = OUT_DIR / f"{name}.pdf"
    create_final_pdf(str(output_path), html_files)

    print("done")

# Clean up the output_*.html files left behind by the final render_output() call
for leftover in Path(".").glob("output_*.html"):
    leftover.unlink()

print(f"\nAll PDFs written to ./{OUT_DIR}/")
print("\nWhat to check in each PDF:")
print("  - Page count matches expectation (see README for page generation rules)")
print("  - Reviewer names are not clipped or overflowing their sections")
print("  - EDP block appears on Page 2 only when edp_line1 is set")
print("  - Blank reviewer slots appear at the end of the last reviewer page")
print("  - Revision number shows 'R0' when left blank")
print("  - Long names and descriptions wrap gracefully without breaking layout")
