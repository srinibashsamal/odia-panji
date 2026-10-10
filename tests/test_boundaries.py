"""New-year transitions: the day before and the day of each rollover."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from odia_panji import (
    convert,
    odia_year_start,
    shaka_new_year,
    shaka_year,
    sunia_date,
    utkalabda_year,
)

YEARS = [1947, 1970, 1999, 2011, 2022, 2023, 2024, 2025, 2026, 2027]


@pytest.mark.parametrize("year", YEARS)
def test_utkalabda_rolls_over_on_sunia(year: int) -> None:
    sunia = sunia_date(year)
    assert utkalabda_year(sunia - timedelta(days=1)) == year - 593
    assert utkalabda_year(sunia) == year - 592


@pytest.mark.parametrize("year", YEARS)
def test_shakabda_rolls_over_on_chaitra_shukla_pratipada(year: int) -> None:
    new_year = shaka_new_year(year)
    assert shaka_year(new_year - timedelta(days=1)) == year - 79
    assert shaka_year(new_year) == year - 78


@pytest.mark.parametrize("year", YEARS)
def test_odia_year_runs_sunia_to_day_before_next_sunia(year: int) -> None:
    start, end = odia_year_start(sunia_date(year))
    assert start == sunia_date(year)
    assert end == sunia_date(year + 1) - timedelta(days=1)
    assert 354 <= (end - start).days + 1 <= 385


def test_anka_rolls_over_on_sunia() -> None:
    sunia = sunia_date(2026)
    assert convert(sunia - timedelta(days=1))["anka"] == 69
    assert convert(sunia)["anka"] == 71


def test_gregorian_new_year_does_not_change_odia_years() -> None:
    before, after = convert(date(2026, 12, 31)), convert(date(2027, 1, 1))
    for key in ("utkalabda", "anka", "shakabda"):
        assert before[key] == after[key]
