"""Odia -> English: Utkalabda and Anka, solar and lunar, plus round trips."""

from __future__ import annotations

from datetime import date
from typing import Callable

import pytest

from odia_panji import (
    OdiaCalendarError,
    anka_year,
    english_date_from_anka_lunar,
    english_date_from_anka_solar,
    english_date_from_lunar,
    english_date_from_solar,
    lunar_date,
    odia_solar_date,
    utkalabda_year,
)

from .helpers import daterange

# ---------------------------------------------------------------------------
# Utkalabda + solar / lunar -> English
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("utkalabda", "month", "day", "expected"),
    [
        (1406, "Simha", 13, date(1999, 8, 29)),
        (1433, "Mesha", 1, date(2026, 4, 14)),
        (1434, "Kanya", 21, date(2026, 10, 7)),
        (1431, "Kumbha", 17, date(2024, 2, 29)),  # leap day
    ],
)
def test_solar_to_english(utkalabda: int, month: str, day: int, expected: date) -> None:
    assert english_date_from_solar(utkalabda, month, day) == expected


@pytest.mark.parametrize(
    ("utkalabda", "month", "paksha", "tithi", "expected"),
    [
        (1406, "Bhadraba", "Krushna", "Trutiya", date(1999, 8, 29)),
        (1434, "Bhadraba", "Shukla", "Dwadasi", date(2026, 9, 23)),
        (1434, "Aswina", "Krushna", "Dwadasi", date(2026, 10, 7)),
    ],
)
def test_lunar_to_english(
    utkalabda: int, month: str, paksha: str, tithi: str, expected: date
) -> None:
    assert english_date_from_lunar(utkalabda, month, paksha, tithi) == expected


def test_names_are_case_insensitive() -> None:
    assert english_date_from_solar(1434, "kAnYa", 21) == date(2026, 10, 7)
    assert english_date_from_lunar(1434, "aswina", "KRUSHNA", "dwadasi") == date(
        2026, 10, 7
    )


def test_tithi_spanning_two_sunrises_returns_first_day() -> None:
    assert english_date_from_lunar(1431, "Phalguna", "Krushna", "Panchami") == date(
        2024, 2, 29
    )


def test_adhika_lunar_date() -> None:
    result = english_date_from_lunar(1433, "Jyestha", "Shukla", "Dasami", adhika=True)
    assert lunar_date(result).adhika is True


def test_ambiguous_solar_date_lists_both_matches() -> None:
    with pytest.raises(OdiaCalendarError, match="1927-09-08, 1928-09-08"):
        english_date_from_solar(1335, "Simha", 24)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((1433, "Simha", 40), "day must be 1-32"),
        ((1433, "Nowhere", 1), "unknown rashi"),
        ((99999, "Simha", 1), "outside the supported range"),
    ],
)
def test_invalid_solar_queries(args: tuple, message: str) -> None:
    with pytest.raises(OdiaCalendarError, match=message):
        english_date_from_solar(*args)


def test_purnima_needs_shukla_paksha() -> None:
    with pytest.raises(OdiaCalendarError, match="only in Shukla"):
        english_date_from_lunar(1434, "Aswina", "Krushna", "Purnima")


@pytest.mark.xfail(
    reason="Known limitation: kshaya tithis contain no sunrise", strict=True
)
def test_kshaya_tithi_reverse_lookup() -> None:
    assert english_date_from_lunar(1433, "Chaitra", "Shukla", "Pratipada") == date(
        2026, 3, 19
    )


# ---------------------------------------------------------------------------
# Anka + solar / lunar -> English
# ---------------------------------------------------------------------------


def test_anka_solar_to_english() -> None:
    assert english_date_from_anka_solar(71, "Kanya", 21) == date(2026, 10, 7)
    assert english_date_from_anka_solar(
        25, "Karkata", 31, "Ramachandra Deba IV"
    ) == date(1947, 8, 15)


def test_anka_lunar_to_english() -> None:
    assert english_date_from_anka_lunar(71, "Bhadraba", "Shukla", "Dwadasi") == date(
        2026, 9, 23
    )
    assert english_date_from_anka_lunar(39, "Jyestha", "Krushna", "Amabasya") == date(
        2002, 6, 11
    )


# ---------------------------------------------------------------------------
# Round trips: English -> Odia -> English must return the starting date
# ---------------------------------------------------------------------------

ROUND_TRIP_DAYS = list(daterange(date(2025, 9, 4), date(2027, 9, 11), 9))


def assert_round_trip(convert_back: Callable[[], date], day: date) -> None:
    """``convert_back()`` must return ``day``, or report it as one of several
    matches: in a long (adhika) year a few solar dates near Sunia occur twice,
    which the library reports instead of guessing."""
    try:
        assert convert_back() == day
    except OdiaCalendarError as exc:
        assert "ambiguous" in str(exc)
        assert day.isoformat() in str(exc)


@pytest.mark.parametrize("day", ROUND_TRIP_DAYS, ids=str)
def test_solar_round_trip(day: date) -> None:
    solar = odia_solar_date(day)
    assert_round_trip(
        lambda: english_date_from_solar(utkalabda_year(day), solar.month, solar.day),
        day,
    )


@pytest.mark.parametrize("day", ROUND_TRIP_DAYS, ids=str)
def test_lunar_round_trip(day: date) -> None:
    lunar = lunar_date(day)
    result = english_date_from_lunar(
        utkalabda_year(day), lunar.month, lunar.paksha, lunar.tithi, lunar.adhika
    )
    # A tithi spanning two sunrises maps back to the first of the two days.
    assert result in (day, date.fromordinal(day.toordinal() - 1))
    assert lunar_date(result) == lunar


@pytest.mark.parametrize("day", ROUND_TRIP_DAYS[::4], ids=str)
def test_anka_solar_round_trip(day: date) -> None:
    solar = odia_solar_date(day)
    assert_round_trip(
        lambda: english_date_from_anka_solar(anka_year(day), solar.month, solar.day),
        day,
    )


def test_long_year_repeats_solar_dates_near_sunia() -> None:
    """Utkalabda 1433 (04-09-2025 to 22-09-2026) is 384 days long, so a short
    run of Simha/Kanya days appears at both ends of it."""
    with pytest.raises(OdiaCalendarError, match="2025-09-04, 2026-09-04"):
        english_date_from_solar(1433, "Simha", 19)
