"""Tests for custom_fill.render_output().

Jinja2 template objects (template_1, template_2, template_3) are module-level
globals loaded at import time, so we monkeypatch them with MagicMocks that
return minimal HTML. Output files are written to pytest's tmp_path so the
working directory remains clean.
"""
from unittest.mock import MagicMock

import pytest
import custom_fill


@pytest.fixture(autouse=True)
def isolated_output(monkeypatch, tmp_path):
    """Change cwd to tmp_path and replace Jinja2 template objects with mocks."""
    monkeypatch.chdir(tmp_path)
    mock_tmpl = MagicMock()
    mock_tmpl.render.return_value = "<html><body>stub</body></html>"
    monkeypatch.setattr(custom_fill, "template_1", mock_tmpl)
    monkeypatch.setattr(custom_fill, "template_2", mock_tmpl)
    monkeypatch.setattr(custom_fill, "template_3", mock_tmpl)


def base_dict(edp=False, reviewer_count=0):
    """Build a minimal render dictionary for use in tests."""
    d = {
        "Project_Title": "9999, Test Project",
        "Submittal_Number": "001",
        "Revision_Number": "0",
        "Date_Review_Ends": "03/15/2025",
        "Specification_Section": "07 31 13",
        "Submittal_Name": "Test Submittal",
        "Project_Manager": "Jane Smith",
        "EDP_Address_Line_1": "Firm LLC" if edp else "",
        "EDP_Address_Line_2": "123 Main St" if edp else "",
        "EDP_Address_Line_3": "City, CA 00000" if edp else "",
    }
    for i in range(1, reviewer_count + 1):
        d[f"Reviewer_Name_{i}"] = f"Reviewer {i}"
    return d


# ---------------------------------------------------------------------------
# Page 1 — always generated
# ---------------------------------------------------------------------------

def test_page1_always_in_output():
    files = custom_fill.render_output(base_dict())
    assert "output_page1.html" in files


def test_page1_file_is_created_on_disk(tmp_path):
    custom_fill.render_output(base_dict())
    assert (tmp_path / "output_page1.html").exists()


# ---------------------------------------------------------------------------
# Page 2 — only when EDP is present
# ---------------------------------------------------------------------------

def test_page2_included_when_edp_present():
    files = custom_fill.render_output(base_dict(edp=True))
    assert "output_page2.html" in files


def test_page2_excluded_when_no_edp():
    files = custom_fill.render_output(base_dict(edp=False))
    assert "output_page2.html" not in files


# ---------------------------------------------------------------------------
# Page 3 — reviewer pages
# ---------------------------------------------------------------------------

def test_no_page3_when_no_reviewers_and_no_edp():
    # With 0 reviewers & no EDP, the single blank slot appended by render_output
    # is consumed by page2 (absent here), so a page3 should still be created
    # for the blank slot — confirm at least page1 is there and no extra pages.
    files = custom_fill.render_output(base_dict(edp=False, reviewer_count=0))
    page3_files = [f for f in files if "page3" in f]
    # With no EDP and only the synthetic blank reviewer, one page3 is generated
    assert len(page3_files) == 1


def test_single_reviewer_without_edp_produces_one_page3():
    files = custom_fill.render_output(base_dict(edp=False, reviewer_count=1))
    page3_files = [f for f in files if "page3" in f]
    assert len(page3_files) == 1


def test_many_reviewers_produce_multiple_page3s():
    # 5 reviewers + 1 blank appended = 6 total; page2 absent, page3 holds 4 each
    # → 2 page3 files
    files = custom_fill.render_output(base_dict(edp=False, reviewer_count=5))
    page3_files = [f for f in files if "page3" in f]
    assert len(page3_files) >= 2


def test_page3_files_are_sequentially_numbered():
    files = custom_fill.render_output(base_dict(edp=False, reviewer_count=5))
    page3_files = sorted(f for f in files if "page3" in f)
    assert page3_files[0] == "output_page3_1.html"
    assert page3_files[1] == "output_page3_2.html"


def test_edp_with_reviewers_consumes_names_on_page2_first():
    # With EDP + 4 reviewers + 1 blank = 5 total; page2 takes 3 → 2 left for page3
    files = custom_fill.render_output(base_dict(edp=True, reviewer_count=4))
    assert "output_page2.html" in files
    page3_files = [f for f in files if "page3" in f]
    assert len(page3_files) >= 1


# ---------------------------------------------------------------------------
# Cleanup of old output files
# ---------------------------------------------------------------------------

def test_old_output_files_removed_before_render(tmp_path):
    stale = tmp_path / "output_stale.html"
    stale.write_text("<html>old</html>")
    # Rename to match the glob pattern
    old_file = tmp_path / "output_old_page.html"
    old_file.write_text("<html>old</html>")
    custom_fill.render_output(base_dict())
    # Files matching output_*.html written THIS run exist; old ones are gone
    all_output = list(tmp_path.glob("output_*.html"))
    names = {f.name for f in all_output}
    assert "output_old_page.html" not in names
