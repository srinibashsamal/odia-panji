"""English -> Odia lunar date (Purnimanta month, paksha, tithi, adhika)."""

from __future__ import annotations

from datetime import date

import pytest

from odia_panji import LunarDate, lunar_date, shaka_new_year, sunia_date

# Dates the README lists as checked against published panjis.
PUBLISHED_SUNIA = {
    2011: date(2011, 9, 9),
    2022: date(2022, 9, 7),
    2023: date(2023, 9, 26),
    2024: date(2024, 9, 15),
    2025: date(2025, 9, 4),
    2026: date(2026, 9, 23),
}

PUBLISHED_CHAITRA_SHUKLA_PRATIPADA = {
    2019: date(2019, 4, 6),
    2020: date(2020, 3, 25),
    2021: date(2021, 4, 13),
    2022: date(2022, 4, 2),
    2023: date(2023, 3, 22),
    2024: date(2024, 4, 9),
    2025: date(2025, 3, 30),
    2026: date(2026, 3, 19),  # kshaya Pratipada, see test below
    2027: date(2027, 4, 7),
}


@pytest.mark.parametrize(("year", "expected"), sorted(PUBLISHED_SUNIA.items()))
def test_sunia_matches_published_dates(year: int, expected: date) -> None:
    assert sunia_date(year) == expected


@pytest.mark.parametrize(
    ("year", "expected"), sorted(PUBLISHED_CHAITRA_SHUKLA_PRATIPADA.items())
)
def test_chaitra_shukla_pratipada_matches_published_dates(
    year: int, expected: date
) -> None:
    assert shaka_new_year(year) == expected


@pytest.mark.parametrize("year", sorted(PUBLISHED_SUNIA))
def test_sunia_is_bhadraba_shukla_dwadasi(year: int) -> None:
    assert lunar_date(sunia_date(year)) == LunarDate(
        "Bhadraba", "Shukla", "Dwadasi", False
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("23-09-2026", LunarDate("Bhadraba", "Shukla", "Dwadasi", False)),
        ("07-10-2026", LunarDate("Aswina", "Krushna", "Dwadasi", False)),
        ("29-08-1999", LunarDate("Bhadraba", "Krushna", "Trutiya", False)),
        ("11-06-2002", LunarDate("Jyestha", "Krushna", "Amabasya", False)),
    ],
)
def test_known_lunar_dates(raw: str, expected: LunarDate) -> None:
    assert lunar_date(raw) == expected


def test_krushna_paksha_takes_next_months_name() -> None:
    """Purnimanta: the dark fortnight after Bhadraba Purnima is Aswina."""
    assert lunar_date("07-10-2026").month == "Aswina"
    assert lunar_date("07-10-2026").paksha == "Krushna"


def test_kshaya_pratipada_2026() -> None:
    """New moon falls just after sunrise on 19-03-2026, so no sunrise lies in
    Chaitra Shukla Pratipada. The Shaka new year still falls on that day, while
    the tithi at sunrise is Amabasya."""
    assert shaka_new_year(2026) == date(2026, 3, 19)
    assert lunar_date("19-03-2026").tithi == "Amabasya"


def test_tithi_spanning_two_sunrises() -> None:
    """A vriddhi tithi is reported on both days (29 Feb and 1 Mar 2024)."""
    assert lunar_date("29-02-2024") == lunar_date("01-03-2024")


@pytest.mark.parametrize(
    ("raw", "month"),
    [("25-07-2023", "Srabana"), ("25-05-2026", "Jyestha")],
)
def test_adhika_months(raw: str, month: str) -> None:
    result = lunar_date(raw)
    assert result.adhika is True
    assert result.month == month


def test_ordinary_month_is_not_adhika() -> None:
    assert lunar_date("23-09-2026").adhika is False
