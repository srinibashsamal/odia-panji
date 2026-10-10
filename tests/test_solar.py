"""English -> Odia solar date (rashi + day)."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from odia_panji import odia_solar_date
from odia_panji.constants import RASHI, SOLAR_MONTH_LUNAR_EQUIVALENTS

from .helpers import daterange


@pytest.mark.parametrize(
    ("raw", "rashi", "day"),
    [
        ("14-04-2026", "Mesha", 1),
        ("29-08-1999", "Simha", 13),
        ("23-09-2026", "Kanya", 7),
        ("07-10-2026", "Kanya", 21),
        ("11-06-2002", "Vrusha", 28),
        ("15-08-1947", "Karkata", 31),
    ],
)
def test_known_solar_dates(raw: str, rashi: str, day: int) -> None:
    solar = odia_solar_date(raw)
    assert (solar.rashi, solar.day) == (rashi, day)
    assert solar.month == solar.rashi


def test_every_rashi_has_its_lunar_equivalent() -> None:
    pairing = dict(zip(RASHI, SOLAR_MONTH_LUNAR_EQUIVALENTS))
    for day in daterange(date(2026, 1, 1), date(2026, 12, 31), 10):
        solar = odia_solar_date(day)
        assert solar.lunar_equivalent == pairing[solar.rashi]


@pytest.mark.parametrize(
    "new_year",
    [
        date(2023, 4, 14),
        date(2024, 4, 13),  # Gregorian leap year
        date(2025, 4, 14),
        date(2026, 4, 14),
        date(2027, 4, 14),
        date(2028, 4, 13),  # Gregorian leap year
    ],
)
def test_odia_solar_new_year(new_year: date) -> None:
    """1 Mesha (Pana Sankranti): 14 April, or 13 April in leap years."""
    first = odia_solar_date(new_year)
    assert (first.rashi, first.day) == ("Mesha", 1)
    last = odia_solar_date(new_year - timedelta(days=1))
    assert last.rashi == "Meena"
    assert 29 <= last.day <= 32


def test_leap_day_is_counted() -> None:
    """29 Feb sits between 28 Feb and 1 Mar with no gap in the day count."""
    days = [odia_solar_date(d) for d in ("28-02-2024", "29-02-2024", "01-03-2024")]
    assert [s.rashi for s in days] == ["Kumbha"] * 3
    assert [s.day for s in days] == [16, 17, 18]


def test_day_count_is_continuous_over_two_years() -> None:
    """Each day either advances by one or starts the next rashi at day 1,
    and every completed month is 29-32 days long."""
    previous = odia_solar_date(date(2025, 1, 1))
    for day in daterange(date(2025, 1, 2), date(2026, 12, 31)):
        current = odia_solar_date(day)
        if current.rashi == previous.rashi:
            assert current.day == previous.day + 1
        else:
            assert current.day == 1
            assert current.rashi == RASHI[(RASHI.index(previous.rashi) + 1) % 12]
            assert 29 <= previous.day <= 32
        previous = current
