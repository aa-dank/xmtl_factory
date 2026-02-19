import pytest
from submittal_cli import XmtlBuild


@pytest.fixture
def full_build():
    """An XmtlBuild with all fields populated, including EDP and two reviewers."""
    return XmtlBuild(
        project_number="3238",
        project_title="Westside Research Park",
        submittal_number="4-073113-03",
        revision_number="0",
        specification_section="07 31 13 Asphalt Shingles",
        submittal_name="G3 Provost Shingle Sample",
        date_review_ends="03/15/2025",
        project_manager_name="Nathan Jensen",
        edp_line1="EHDD Architecture",
        edp_line2="1 Pier Ste 2",
        edp_line3="San Francisco, CA 94111",
        reviewer_names="David Jessen, UCSC PP;Jeff Clothier, UCSC PP",
    )


@pytest.fixture
def no_edp_build():
    """An XmtlBuild with all required fields but no EDP information."""
    return XmtlBuild(
        project_number="3238",
        project_title="Westside Research Park",
        submittal_number="4-073113-03",
        revision_number="0",
        specification_section="07 31 13 Asphalt Shingles",
        submittal_name="G3 Provost Shingle Sample",
        reviewer_names="Matt DeMonner, UCSC PPC",
    )
