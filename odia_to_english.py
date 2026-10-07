"""Convert an Utkalabda year plus an Odia solar or lunar date to English.

This is the inverse of :func:`odia_calendar.odia_solar_date` and
:func:`odia_calendar.lunar_date`: given the Utkalabda year and either a
solar date (rashi/month + day) or a Purnimanta lunar date (month, paksha,
tithi), it returns the matching Gregorian :class:`~datetime.date`.

All astronomy lives in :mod:`odia_calendar` and its helper modules, name
tables in :mod:`constants` and shared checks in :mod:`validation`; this
module only searches the Utkalabda year's date range for the day whose
forward conversion matches what was asked for.
That search is a plain day-by-day scan rather than a closed-form inverse,
since a scan is far simpler to get right and only has to cover the ~354 to
385 days of one Odia year.

A solar rashi+day can genuinely match two different English dates in a
rare long Utkalabda year (see :func:`english_date_from_solar`); a lunar
tithi can span two sunrises, in which case the earlier day is returned
(see :func:`english_date_from_lunar`). Both are documented, not silently
resolved.

Public functions
-----------------
    english_date_from_solar
    english_date_from_lunar
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from typing import List, Optional, Tuple

from calendar_types import OdiaCalendarError
from constants import (
    AMABASYA,
    LUNAR_MONTHS,
    MAX_SUPPORTED_YEAR,
    MIN_SUPPORTED_YEAR,
    PAKSHA_KRUSHNA,
    PAKSHA_SHUKLA,
    PURNIMA,
    RASHI,
    TITHI_NAMES,
    UTKALABDA_EPOCH,
)
from odia_calendar import lunar_date, odia_solar_date, sunia_date
from validation import lookup_name, validate_int

__all__ = ["english_date_from_solar", "english_date_from_lunar"]

_RASHI_BY_NAME = {name.lower(): name for name in RASHI}
_LUNAR_MONTH_BY_NAME = {name.lower(): name for name in LUNAR_MONTHS}
_PAKSHA_BY_NAME = {name.lower(): name for name in (PAKSHA_SHUKLA, PAKSHA_KRUSHNA)}
_TITHI_BY_NAME = {name.lower(): name for name in TITHI_NAMES}
_TITHI_BY_NAME[PURNIMA.lower()] = PURNIMA
_TITHI_BY_NAME[AMABASYA.lower()] = AMABASYA

_PAKSHA_OF_TERMINAL_TITHI = {PURNIMA: PAKSHA_SHUKLA, AMABASYA: PAKSHA_KRUSHNA}

_MAX_SOLAR_MONTH_DAYS = 32

_MIN_UTKALABDA = MIN_SUPPORTED_YEAR - UTKALABDA_EPOCH
_MAX_UTKALABDA = (MAX_SUPPORTED_YEAR - 1) - UTKALABDA_EPOCH


def _validate_utkalabda(utkalabda: int) -> int:
    """Return ``utkalabda`` if supported, else raise in Utkalabda terms.

    Validated here rather than through the Gregorian year check, so that
    the error names the Utkalabda year the caller passed, not the
    Gregorian year it maps to.
    """
    validate_int(utkalabda, "utkalabda")
    if not _MIN_UTKALABDA <= utkalabda <= _MAX_UTKALABDA:
        raise OdiaCalendarError(
            f"Utkalabda {utkalabda} is outside the supported range "
            f"{_MIN_UTKALABDA}-{_MAX_UTKALABDA}"
        )
    return utkalabda


def _utkalabda_year_span(utkalabda: int) -> Tuple[date, date]:
    """First and last Gregorian day of the given Utkalabda year."""
    era_year = _validate_utkalabda(utkalabda) + UTKALABDA_EPOCH
    start = sunia_date(era_year)
    end = sunia_date(era_year + 1) - timedelta(days=1)
    return start, end


def english_date_from_solar(utkalabda: int, month: str, day: int) -> date:
    """Return the English date of an Odia solar date in a given Utkalabda year.

    Args:
        utkalabda (int): Utkalabda / Utkaliya San year.
        month (str): Rashi/solar month name (e.g. ``"Simha"``),
            case-insensitive.
        day (int): Day of that solar month, counting Sankranti as day 1.

    Returns:
        date: The matching English date.

    Raises:
        OdiaCalendarError: if ``month`` is not a rashi name, ``day`` is not
            1-32, ``utkalabda`` is out of range, no day in the year matches
            (``day`` is too high for that month's length), or the
            combination is ambiguous (see Note).

    Note:
        Sunia falls inside Simha or Kanya, so in a long (adhika) Utkalabda
        year the window can span over 365 days and briefly repeat a low
        day number of that straddling rashi: once as the tail of the
        previous solar year, again days later as the start of the next.
        Such a query raises :class:`OdiaCalendarError` naming both
        matching dates instead of guessing.

    Examples:
        >>> english_date_from_solar(1406, "Simha", 13)
        datetime.date(1999, 8, 29)
        >>> english_date_from_solar(1433, "Mesha", 1)
        datetime.date(2026, 4, 14)
        >>> english_date_from_solar(1335, "Simha", 24)
        Traceback (most recent call last):
            ...
        calendar_types.OdiaCalendarError: 24 Simha is ambiguous in Utkalabda 1335: matches 1927-09-08, 1928-09-08
        >>> english_date_from_solar(1433, "Simha", 40)
        Traceback (most recent call last):
            ...
        calendar_types.OdiaCalendarError: day must be 1-32, got 40
    """
    target_rashi = lookup_name(month, _RASHI_BY_NAME, "rashi/solar month")
    validate_int(day, "day")
    if not 1 <= day <= _MAX_SOLAR_MONTH_DAYS:
        raise OdiaCalendarError(f"day must be 1-{_MAX_SOLAR_MONTH_DAYS}, got {day}")
    start, end = _utkalabda_year_span(utkalabda)

    matches = []
    candidate = start
    while candidate <= end:
        solar = odia_solar_date(candidate)
        if solar.rashi == target_rashi and solar.day == day:
            matches.append(candidate)
        candidate += timedelta(days=1)

    if not matches:
        raise OdiaCalendarError(
            f"no day in Utkalabda {utkalabda} matches {day} {target_rashi}"
        )
    if len(matches) > 1:
        options = ", ".join(d.isoformat() for d in matches)
        raise OdiaCalendarError(
            f"{day} {target_rashi} is ambiguous in Utkalabda {utkalabda}: "
            f"matches {options}"
        )
    return matches[0]


def english_date_from_lunar(
    utkalabda: int, month: str, paksha: str, tithi: str, adhika: bool = False
) -> date:
    """Return the English date of a Purnimanta lunar date in a given Utkalabda year.

    Args:
        utkalabda (int): Utkalabda / Utkaliya San year.
        month (str): Purnimanta lunar month name (e.g. ``"Bhadraba"``),
            case-insensitive.
        paksha (str): ``"Shukla"`` or ``"Krushna"``, case-insensitive.
        tithi (str): Tithi name (e.g. ``"Trutiya"``), or ``"Purnima"``
            (Shukla only) / ``"Amabasya"`` (Krushna only).
        adhika (bool, optional): Whether the month is the intercalary
            repeat rather than the ordinary (nija) month. Defaults to
            ``False``.

    Returns:
        date: The matching English date.  A tithi long enough to span two
        sunrises is reported on the first of those two days.

    Raises:
        OdiaCalendarError: if any name is unrecognised, Purnima or Amabasya
            is paired with the wrong paksha, ``utkalabda`` is out of range,
            or no day in the year matches.

    Note:
        The search compares against :func:`~odia_calendar.lunar_date`,
        which reports the tithi in force at *sunrise*.  A *kshaya* tithi
        begins and ends between two sunrises, so no day ever reports it,
        and asking for one currently raises "no day matches" even though
        the date exists -- e.g. Chaitra Shukla Pratipada of Utkalabda 1433
        (19-03-2026).  Fixing this needs a direct lunation-based lookup
        rather than this day-by-day scan.

    Examples:
        >>> english_date_from_lunar(1406, "Bhadraba", "Krushna", "Trutiya")
        datetime.date(1999, 8, 29)
        >>> english_date_from_lunar(1434, "Bhadraba", "Shukla", "Dwadasi")
        datetime.date(2026, 9, 23)
        >>> english_date_from_lunar(1434, "Bhadraba", "Shukla", "Amabasya")
        Traceback (most recent call last):
            ...
        calendar_types.OdiaCalendarError: Amabasya occurs only in Krushna paksha, not Shukla
    """
    target_month = lookup_name(month, _LUNAR_MONTH_BY_NAME, "lunar month")
    target_paksha = lookup_name(paksha, _PAKSHA_BY_NAME, "paksha")
    target_tithi = lookup_name(tithi, _TITHI_BY_NAME, "tithi")

    required_paksha = _PAKSHA_OF_TERMINAL_TITHI.get(target_tithi)
    if required_paksha is not None and required_paksha != target_paksha:
        raise OdiaCalendarError(
            f"{target_tithi} occurs only in {required_paksha} paksha, "
            f"not {target_paksha}"
        )

    start, end = _utkalabda_year_span(utkalabda)

    candidate = start
    while candidate <= end:
        lunar = lunar_date(candidate)
        if (
            lunar.month == target_month
            and lunar.paksha == target_paksha
            and lunar.tithi == target_tithi
            and lunar.adhika == adhika
        ):
            return candidate
        candidate += timedelta(days=1)

    raise OdiaCalendarError(
        f"no day in Utkalabda {utkalabda} matches "
        f"{target_month} {target_paksha} {target_tithi}"
        f"{' (adhika)' if adhika else ''}"
    )


def _main(argv: Optional[List[str]] = None) -> int:
    """Print a few sample conversions; return a non-zero exit code on failure."""
    del argv  # no command-line interface yet; kept for a uniform signature

    # (utkalabda, rashi/solar month, day)
    solar_dates = [
        (1406, "Simha", 13),
        (1433, "Mesha", 1),
        (1434, "Kanya", 21),
    ]

    # (utkalabda, lunar month, paksha, tithi)
    lunar_dates = [
        (1406, "Bhadraba", "Krushna", "Trutiya"),
        (1434, "Bhadraba", "Shukla", "Dwadasi"),
        (1434, "Aswina", "Krushna", "Dwadasi"),
    ]

    exit_code = 0

    for utkalabda, month, day in solar_dates:
        query = f"{day} {month} {utkalabda}"
        try:
            print(f"solar: {query} -> {english_date_from_solar(utkalabda, month, day)}")
        except OdiaCalendarError as exc:
            print(f"solar: {query} -> {exc}")
            exit_code = 1

    print("")

    for utkalabda, month, paksha, tithi in lunar_dates:
        query = f"{month} {paksha} {tithi} {utkalabda}"
        try:
            print(
                f"lunar: {query} -> "
                f"{english_date_from_lunar(utkalabda, month, paksha, tithi)}"
            )
        except OdiaCalendarError as exc:
            print(f"lunar: {query} -> {exc}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
