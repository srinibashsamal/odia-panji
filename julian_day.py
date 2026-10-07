"""Julian Day conversions for the proleptic Gregorian calendar."""

from __future__ import annotations

import math
from datetime import date
from typing import Tuple

from calendar_types import OdiaCalendarError
from constants import DAYS_PER_JULIAN_CENTURY, J2000_JD

__all__ = ["to_jd", "date_to_jd", "jd_to_date", "julian_centuries_since_j2000"]


def to_jd(year: int, month: int, day: float) -> float:
    """Convert a proleptic-Gregorian calendar date to a Julian Day.

    Args:
        year (int): Calendar year.
        month (int): Month, 1-12.
        day (float): Day of month; may carry a fraction (``0.5`` = noon UT).

    Raises:
        OdiaCalendarError: if ``month`` is not in 1-12.

    Returns:
        float: The Julian Day number.
    """
    if not 1 <= month <= 12:
        raise OdiaCalendarError(f"month must be 1-12, got {month}")

    # January and February are treated as months 13 and 14 of the previous
    # year so that the leap day always falls at the end of the "year".
    if month <= 2:
        year, month = year - 1, month + 12

    century = year // 100
    gregorian_correction = 2 - century + century // 4
    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + gregorian_correction
        - 1524.5
    )


def date_to_jd(calendar_date: date, fraction: float = 0.0) -> float:
    """Return the Julian Day of 00:00 UT on ``calendar_date`` plus ``fraction`` of a day."""
    return to_jd(calendar_date.year, calendar_date.month, calendar_date.day + fraction)


def jd_to_date(jd: float) -> Tuple[date, float]:
    """Convert a Julian Day to ``(date, day_fraction)``.

    The proleptic Gregorian calendar is used throughout.  Meeus' algorithm
    switches to the Julian calendar below JD 2299161, but that branch is
    deliberately omitted here: mixing the two would stop results from
    round-tripping with :func:`date_to_jd` and ``datetime.date``, which are
    proleptic Gregorian at every epoch.

    Args:
        jd (float): Julian Day number.

    Raises:
        OdiaCalendarError: if ``jd`` falls outside the representable range of
            ``datetime.date``.

    Returns:
        Tuple[date, float]: The calendar date and the elapsed fraction of
        that day.
    """
    jd += 0.5
    julian_day_number = int(jd)
    day_fraction = jd - julian_day_number

    century = int((julian_day_number - 1867216.25) / 36524.25)
    adjusted = julian_day_number + 1 + century - century // 4
    shifted = adjusted + 1524
    approx_year = int((shifted - 122.1) / 365.25)
    days_in_years = int(365.25 * approx_year)
    approx_month = int((shifted - days_in_years) / 30.6001)

    day = shifted - days_in_years - int(30.6001 * approx_month)
    # approx_month runs 1-14; months 13 and 14 are January and February of
    # the following year, mirroring the shift applied in `to_jd`.
    month = approx_month - 1 if approx_month < 14 else approx_month - 13
    year = approx_year - 4716 if month > 2 else approx_year - 4715

    try:
        return date(year, month, day), day_fraction
    except ValueError as exc:
        raise OdiaCalendarError(
            f"Julian Day {jd - 0.5} maps to {year}-{month:02d}-{day:02d}, "
            "which datetime.date cannot represent"
        ) from exc


def julian_centuries_since_j2000(jd: float) -> float:
    """Return the time argument ``T`` used by the Meeus polynomials."""
    return (jd - J2000_JD) / DAYS_PER_JULIAN_CENTURY
