"""Input parsing and range checks."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from odia_panji import MAX_SUPPORTED_YEAR, OdiaCalendarError, parse_date, utkalabda_year


@pytest.mark.parametrize(
    "raw", ["23-09-2026", "23/09/2026", "23.09.2026", " 23-09-2026 "]
)
def test_parse_date_accepts_separators(raw: str) -> None:
    assert parse_date(raw) == date(2026, 9, 23)


def test_parse_date_accepts_date_and_datetime() -> None:
    assert parse_date(date(2026, 9, 23)) == date(2026, 9, 23)
    assert parse_date(datetime(2026, 9, 23, 18, 30)) == date(2026, 9, 23)


@pytest.mark.parametrize("raw", ["2026-09-23", "31-02-2026", "hello", ""])
def test_parse_date_rejects_bad_strings(raw: str) -> None:
    with pytest.raises(OdiaCalendarError):
        parse_date(raw)


@pytest.mark.parametrize("raw", [20260923, None, 3.5])
def test_parse_date_rejects_bad_types(raw: object) -> None:
    with pytest.raises(OdiaCalendarError):
        parse_date(raw)  # type: ignore[arg-type]


def test_year_beyond_supported_range_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError, match="supported range"):
        utkalabda_year(date(MAX_SUPPORTED_YEAR + 1, 1, 1))
