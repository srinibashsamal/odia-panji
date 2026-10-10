"""Anka numbering, Gajapati reigns and English -> Anka."""

from __future__ import annotations

from datetime import date

import pytest

from odia_panji import (
    OdiaCalendarError,
    anka_from_index,
    anka_year,
    anka_year_span,
    gajapati_reign,
    index_from_anka,
    is_valid_anka,
)

# ---------------------------------------------------------------------------
# Numbering rules
# ---------------------------------------------------------------------------


def test_first_valid_ankas() -> None:
    expected = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21]
    assert [n for n in range(-5, 22) if is_valid_anka(n)] == expected


@pytest.mark.parametrize("number", [0, 1, 6, 16, 20, 26, 30, 100, 106])
def test_skipped_numbers_are_invalid(number: int) -> None:
    assert not is_valid_anka(number)
    with pytest.raises(OdiaCalendarError):
        index_from_anka(number)


def test_index_and_anka_round_trip() -> None:
    for index in range(1, 500):
        assert index_from_anka(anka_from_index(index)) == index


def test_index_below_one_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError):
        anka_from_index(0)


def test_anka_71_is_index_57() -> None:
    assert index_from_anka(71) == 57


# ---------------------------------------------------------------------------
# English -> Anka
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("22-09-2026", 69),  # day before Sunia 2026
        ("23-09-2026", 71),  # Sunia 2026 (70 is skipped)
        ("07-10-2026", 71),
        ("11-06-2002", 39),
        ("15-08-1947", 25),  # earlier reign, resolved automatically
    ],
)
def test_anka_year(raw: str, expected: int) -> None:
    assert anka_year(raw) == expected


def test_accession_day_goes_to_incoming_gajapati_by_default() -> None:
    assert gajapati_reign("07-07-1970").name == "Divyasingha Deva IV"
    assert anka_year("07-07-1970") == 2


def test_accession_day_goes_to_outgoing_gajapati_on_request() -> None:
    assert gajapati_reign("07-07-1970", inclusive_end=True).name == (
        "Birakisore Deva III"
    )
    assert anka_year("07-07-1970", inclusive_end=True) == 15


def test_date_before_earliest_reign_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError, match="earliest known reign"):
        anka_year("01-01-1900")


def test_explicit_accession_before_date_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError, match="precedes the accession"):
        anka_year("01-01-1970", accession=date(1970, 7, 7))


# ---------------------------------------------------------------------------
# Anka -> date span
# ---------------------------------------------------------------------------


def test_anka_year_span_current_reign() -> None:
    assert anka_year_span(71) == (date(2026, 9, 23), date(2027, 9, 11))


def test_first_anka_runs_from_accession_to_second_sunia() -> None:
    assert anka_year_span(2) == (date(1970, 7, 7), date(1971, 9, 1))


def test_last_anka_of_past_reign_is_cut_short() -> None:
    assert anka_year_span(15, "Birakisore Deva III") == (
        date(1969, 9, 23),
        date(1970, 7, 6),
    )


def test_gajapati_name_is_case_insensitive() -> None:
    assert anka_year_span(25, "ramachandra deba iv") == anka_year_span(
        25, "Ramachandra Deba IV"
    )


def test_unknown_gajapati_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError, match="unknown Gajapati"):
        anka_year_span(10, "Nobody")


def test_anka_never_reached_in_reign_is_rejected() -> None:
    with pytest.raises(OdiaCalendarError, match="never reached"):
        anka_year_span(99, "Birakisore Deva III")


def test_every_day_of_an_anka_span_maps_back_to_that_anka() -> None:
    start, end = anka_year_span(71)
    assert anka_year(start) == 71
    assert anka_year(end) == 71
