from datetime import datetime, timedelta

import pytest
from submittal_cli import _parse_review_date


def two_weeks_from_today():
    return (datetime.now() + timedelta(weeks=2)).strftime("%m/%d/%Y")


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

def test_parses_us_slash_format():
    assert _parse_review_date("03/15/2025") == "03/15/2025"


def test_parses_iso_format():
    assert _parse_review_date("2025-03-15") == "03/15/2025"


def test_parses_natural_language():
    assert _parse_review_date("March 15 2025") == "03/15/2025"


def test_parses_abbreviated_month():
    assert _parse_review_date("Mar 15, 2025") == "03/15/2025"


def test_leading_and_trailing_whitespace_is_stripped():
    assert _parse_review_date("  03/15/2025  ") == "03/15/2025"


# ---------------------------------------------------------------------------
# Default fallback behaviour
# ---------------------------------------------------------------------------

def test_blank_string_returns_two_weeks_from_today():
    assert _parse_review_date("") == two_weeks_from_today()


def test_whitespace_only_returns_two_weeks_from_today():
    assert _parse_review_date("   ") == two_weeks_from_today()


def test_garbage_input_returns_two_weeks_from_today():
    assert _parse_review_date("not-a-date") == two_weeks_from_today()


def test_partial_garbage_returns_two_weeks_from_today():
    # dateutil may partially parse some strings; truly unparseable falls back
    assert _parse_review_date("99/99/9999") == two_weeks_from_today()
