import textwrap

import pytest
from submittal_cli import XmtlBuild, XmtlBuildField


# ===========================================================================
# XmtlBuildField
# ===========================================================================

class TestXmtlBuildField:
    def test_raw_value_returned_when_no_processor(self):
        field = XmtlBuildField("MyField", "hello", "Prompt")
        assert field.processed_value == "hello"

    def test_processor_is_applied_to_value(self):
        field = XmtlBuildField("MyField", "  trimmed  ", "Prompt", processor=str.strip)
        assert field.processed_value == "trimmed"

    def test_processor_called_even_when_value_is_empty(self):
        field = XmtlBuildField("MyField", "", "Prompt", processor=lambda v: v or "default")
        assert field.processed_value == "default"


# ===========================================================================
# XmtlBuild — revision number processor
# ===========================================================================

class TestRevisionNumberProcessor:
    def test_blank_revision_defaults_to_zero_string(self):
        build = XmtlBuild(revision_number="")
        assert build.revision_number.processed_value == "0"

    def test_whitespace_revision_defaults_to_zero_string(self):
        build = XmtlBuild(revision_number="   ")
        assert build.revision_number.processed_value == "0"

    def test_non_zero_revision_is_preserved(self):
        build = XmtlBuild(revision_number="2")
        assert build.revision_number.processed_value == "2"

    def test_revision_whitespace_is_stripped(self):
        build = XmtlBuild(revision_number="  3  ")
        assert build.revision_number.processed_value == "3"


# ===========================================================================
# XmtlBuild — reviewer name processor
# ===========================================================================

class TestReviewerNameProcessor:
    def test_semicolon_delimited_names_split_into_list(self):
        build = XmtlBuild(reviewer_names="Alice;Bob;Charlie")
        assert build.reviewer_names.processed_value == ["Alice", "Bob", "Charlie"]

    def test_names_are_stripped(self):
        build = XmtlBuild(reviewer_names=" Alice ; Bob ")
        assert build.reviewer_names.processed_value == ["Alice", "Bob"]

    def test_blank_reviewer_names_returns_empty_list(self):
        build = XmtlBuild(reviewer_names="")
        assert build.reviewer_names.processed_value == []

    def test_trailing_semicolon_ignored(self):
        build = XmtlBuild(reviewer_names="Alice;Bob;")
        assert build.reviewer_names.processed_value == ["Alice", "Bob"]


# ===========================================================================
# XmtlBuild — validate()
# ===========================================================================

class TestValidate:
    def test_no_missing_fields_when_all_required_are_set(self, full_build):
        assert full_build.validate() == []

    def test_returns_names_of_all_missing_required_fields(self):
        build = XmtlBuild()  # everything empty
        missing = build.validate()
        assert "Project_Number" in missing
        assert "Project_Title" in missing
        assert "Submittal_Number" in missing
        assert "Specification_Section" in missing
        assert "Submittal_Name" in missing

    def test_revision_number_not_missing_when_processor_supplies_default(self):
        # revision_number="" → processor returns "0" → should not appear in missing
        build = XmtlBuild(
            project_number="001",
            project_title="Test",
            submittal_number="S-001",
            revision_number="",          # blank, but processor gives "0"
            specification_section="01 00 00",
            submittal_name="Test Sub",
        )
        assert "Revision_Number" not in build.validate()


# ===========================================================================
# XmtlBuild — has_edp
# ===========================================================================

class TestHasEdp:
    def test_true_when_edp_line1_is_set(self, full_build):
        assert full_build.has_edp is True

    def test_false_when_edp_line1_is_empty(self, no_edp_build):
        assert no_edp_build.has_edp is False

    def test_false_on_empty_build(self):
        assert XmtlBuild().has_edp is False


# ===========================================================================
# XmtlBuild — to_render_dict()
# ===========================================================================

class TestToRenderDict:
    def test_project_title_combines_number_and_title(self, full_build):
        d = full_build.to_render_dict()
        assert d["Project_Title"] == "3238, Westside Research Park"

    def test_reviewer_names_are_numbered_from_one(self, full_build):
        d = full_build.to_render_dict()
        assert d["Reviewer_Name_1"] == "David Jessen, UCSC PP"
        assert d["Reviewer_Name_2"] == "Jeff Clothier, UCSC PP"
        assert "Reviewer_Name_3" not in d

    def test_no_reviewer_name_keys_when_empty(self, no_edp_build):
        build = XmtlBuild(
            project_number="001", project_title="P", submittal_number="S",
            revision_number="0", specification_section="01", submittal_name="N",
            reviewer_names="",
        )
        d = build.to_render_dict()
        assert not any(k.startswith("Reviewer_Name_") for k in d)

    def test_expected_keys_present(self, full_build):
        d = full_build.to_render_dict()
        for key in ("Project_Title", "Submittal_Number", "Revision_Number",
                    "Date_Review_Ends", "Specification_Section", "Submittal_Name",
                    "Project_Manager", "EDP_Address_Line_1", "EDP_Address_Line_2",
                    "EDP_Address_Line_3"):
            assert key in d, f"Missing key: {key}"


# ===========================================================================
# XmtlBuild — from_yaml()
# ===========================================================================

class TestFromYaml:
    YAML_CONTENT = textwrap.dedent("""\
        "TESTKEY":
          Project_Title: "9999, My Test Project"
          Submittal_Number: "001"
          Revision_Number: "1"
          Specification_Section: "07 31 13"
          Submittal_Name: "Shingle Sample"
          Project_Manager: "Jane Smith"
          EDP_Address_Line_1: "Firm LLC"
          EDP_Address_Line_2: "123 Main St"
          EDP_Address_Line_3: "City, CA 00000"
          reviewer_list: "Alice;Bob"
    """)

    def test_loads_project_number_and_title(self, tmp_path):
        yaml_file = tmp_path / "xmtl_templates.yaml"
        yaml_file.write_text(self.YAML_CONTENT)
        build = XmtlBuild.from_yaml(str(yaml_file), "TESTKEY")
        assert build.project_number.value == "9999"
        assert build.project_title.value == "My Test Project"

    def test_loads_submittal_fields(self, tmp_path):
        yaml_file = tmp_path / "xmtl_templates.yaml"
        yaml_file.write_text(self.YAML_CONTENT)
        build = XmtlBuild.from_yaml(str(yaml_file), "TESTKEY")
        assert build.submittal_number.value == "001"
        assert build.specification_section.value == "07 31 13"
        assert build.submittal_name.value == "Shingle Sample"

    def test_loads_edp_fields(self, tmp_path):
        yaml_file = tmp_path / "xmtl_templates.yaml"
        yaml_file.write_text(self.YAML_CONTENT)
        build = XmtlBuild.from_yaml(str(yaml_file), "TESTKEY")
        assert build.edp_line1.value == "Firm LLC"
        assert build.edp_line2.value == "123 Main St"

    def test_loads_reviewer_list(self, tmp_path):
        yaml_file = tmp_path / "xmtl_templates.yaml"
        yaml_file.write_text(self.YAML_CONTENT)
        build = XmtlBuild.from_yaml(str(yaml_file), "TESTKEY")
        assert build.reviewer_names.value == "Alice;Bob"

    def test_raises_key_error_for_unknown_key(self, tmp_path):
        yaml_file = tmp_path / "xmtl_templates.yaml"
        yaml_file.write_text(self.YAML_CONTENT)
        with pytest.raises(KeyError, match="missing-key"):
            XmtlBuild.from_yaml(str(yaml_file), "missing-key")
