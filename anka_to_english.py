"""Convert an Anka year plus an Odia solar or lunar date to English.

This is the Anka counterpart of :mod:`odia_to_english`.  There, the year is
given as an Utkalabda; here it is given as the **Anka** (regnal) year of a
Gajapati Maharaja of Puri, e.g. "Anka 71, 21 Kanya" or
"Anka 71, Bhadraba Shukla Dwadasi".

How an Anka year maps to dates
------------------------------
The Anka is a regnal count, so the same Anka number recurs under every
Gajapati.  The monarch is therefore part of the query; it defaults to the
latest reign in :data:`~constants.GAJAPATI_REIGNS`.

Within a reign the counting *index* (see :func:`anka.index_from_anka`)
advances at every Sunia, exactly as :func:`odia_calendar.anka_index`
counts forward:

* index 1 -- from the accession up to the day before the **second** Sunia
  of the reign (the short stretch before the first Sunia *and* the full
  year after it both carry index 1);
* index k >= 2 -- one Sunia-to-Sunia year, the one starting on the Sunia
  ``k - 1`` years after the first.

Every span is clipped to the reign, so the final Anka of a past reign is
only as long as the monarch actually reigned.

Because index 1 can cover well over a year, a solar or lunar date may
occur twice inside it.  That is reported as an ambiguity error listing
both dates instead of guessing -- the same policy as
:func:`odia_to_english.english_date_from_solar`.

Public functions
----------------
    anka_year_span
    english_date_from_anka_solar
    english_date_from_anka_lunar
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from typing import List, Optional, Tuple

from anka import index_from_anka
from calendar_types import OdiaCalendarError, Reign
from constants import GAJAPATI_REIGNS, MAX_SUPPORTED_YEAR
from odia_calendar import sunia_date
from odia_to_english import (
    lunar_matches,
    normalize_lunar_query,
    normalize_solar_query,
    solar_matches,
)
from validation import lookup_name, validate_int

__all__ = [
    "anka_year_span",
    "english_date_from_anka_solar",
    "english_date_from_anka_lunar",
]

_REIGN_POSITION_BY_NAME = {
    reign.name.lower(): position for position, reign in enumerate(GAJAPATI_REIGNS)
}
_REIGN_NAME_BY_NAME = {reign.name.lower(): reign.name for reign in GAJAPATI_REIGNS}

# Last day any forward conversion accepts.
_LAST_SUPPORTED_DAY = date(MAX_SUPPORTED_YEAR, 12, 31)


# --------------------------------------------------------------------------
# Reign and Anka-year span
# --------------------------------------------------------------------------


def _resolve_reign(gajapati: Optional[str]) -> Tuple[int, Reign]:
    """Return ``(position, reign)`` for a Gajapati name, or the latest reign.

    Raises:
        OdiaCalendarError: if ``gajapati`` is not a name in the reign table.
    """
    if gajapati is None:
        position = len(GAJAPATI_REIGNS) - 1
    else:
        canonical = lookup_name(gajapati, _REIGN_NAME_BY_NAME, "Gajapati")
        position = _REIGN_POSITION_BY_NAME[canonical.lower()]
    return position, GAJAPATI_REIGNS[position]


def _reign_bounds(position: int, inclusive_end: bool) -> Tuple[date, date]:
    """Return the first and last day credited to the reign at ``position``.

    A same-day handover belongs to the incoming monarch by default; with
    ``inclusive_end=True`` it goes to the outgoing one instead, matching
    :func:`odia_calendar.gajapati_reign`.
    """
    reign = GAJAPATI_REIGNS[position]

    first_day = reign.accession
    if inclusive_end and reign.predecessor_died_same_day and position > 0:
        first_day += timedelta(days=1)

    if position + 1 < len(GAJAPATI_REIGNS):
        successor = GAJAPATI_REIGNS[position + 1]
        last_day = successor.accession
        if not (inclusive_end and successor.predecessor_died_same_day):
            last_day -= timedelta(days=1)
    else:
        last_day = _LAST_SUPPORTED_DAY

    return first_day, last_day


def anka_year_span(
    anka: int, gajapati: Optional[str] = None, inclusive_end: bool = False
) -> Tuple[date, date]:
    """Return the first and last English date of an Anka year.

    Args:
        anka (int): Anka year (must be a valid Anka number, e.g. not 16).
        gajapati (str, optional): Reigning monarch's name, case-insensitive.
            Defaults to the latest reign in
            :data:`~constants.GAJAPATI_REIGNS`.
        inclusive_end (bool, optional): Who gets a same-day handover; see
            :func:`odia_calendar.gajapati_reign`. Defaults to ``False``
            (incoming monarch).

    Returns:
        Tuple[date, date]: ``(start, end)``, both inclusive.

    Raises:
        OdiaCalendarError: if ``anka`` is invalid, ``gajapati`` is unknown, or
            the reign never reached that Anka year.

    Examples:
        >>> anka_year_span(71)
        (datetime.date(2026, 9, 23), datetime.date(2027, 9, 11))
        >>> anka_year_span(2)  # index 1: accession to second Sunia
        (datetime.date(1970, 7, 7), datetime.date(1971, 9, 1))
        >>> anka_year_span(15, "Birakisore Deva III")  # cut short by the reign
        (datetime.date(1969, 9, 23), datetime.date(1970, 7, 6))
    """
    validate_int(anka, "anka")
    index = index_from_anka(anka)
    position, reign = _resolve_reign(gajapati)
    reign_first, reign_last = _reign_bounds(position, inclusive_end)

    first_sunia = sunia_date(reign.accession.year)
    if first_sunia <= reign.accession:
        first_sunia = sunia_date(reign.accession.year + 1)

    end_sunia_year = first_sunia.year + index
    if end_sunia_year > MAX_SUPPORTED_YEAR + 1:
        raise OdiaCalendarError(
            f"Anka {anka} of {reign.name} lies beyond the supported range "
            f"(years up to {MAX_SUPPORTED_YEAR})"
        )

    start = reign.accession if index == 1 else sunia_date(end_sunia_year - 1)
    end = sunia_date(end_sunia_year) - timedelta(days=1)

    start, end = max(start, reign_first), min(end, reign_last)
    if start > end:
        raise OdiaCalendarError(
            f"Anka {anka} was never reached in the reign of {reign.name} "
            f"({reign_first.isoformat()} to {reign_last.isoformat()})"
        )
    return start, end


# --------------------------------------------------------------------------
# Anka-based reverse conversion
# --------------------------------------------------------------------------


def _single_match(matches: List[date], description: str, context: str) -> date:
    """Return the only match, or raise for none / several."""
    if not matches:
        raise OdiaCalendarError(f"no day in {context} matches {description}")
    if len(matches) > 1:
        options = ", ".join(d.isoformat() for d in matches)
        raise OdiaCalendarError(
            f"{description} is ambiguous in {context}: matches {options}"
        )
    return matches[0]


def _context(anka: int, gajapati: Optional[str]) -> str:
    """Human-readable "Anka N (Gajapati)" label for error messages."""
    return f"Anka {anka} ({_resolve_reign(gajapati)[1].name})"


def english_date_from_anka_solar(
    anka: int,
    month: str,
    day: int,
    gajapati: Optional[str] = None,
    inclusive_end: bool = False,
) -> date:
    """Return the English date of an Odia solar date in a given Anka year.

    Args:
        anka (int): Anka year.
        month (str): Rashi/solar month name (e.g. ``"Kanya"``),
            case-insensitive.
        day (int): Day of that solar month, counting Sankranti as day 1.
        gajapati (str, optional): Reigning monarch; defaults to the latest
            reign.
        inclusive_end (bool, optional): See :func:`anka_year_span`.

    Returns:
        date: The matching English date.

    Raises:
        OdiaCalendarError: for invalid input, if no day matches, or if the
            date occurs twice in the Anka year (possible only in the long
            first Anka of a reign).

    Examples:
        >>> english_date_from_anka_solar(71, "Kanya", 21)
        datetime.date(2026, 10, 7)
        >>> english_date_from_anka_solar(25, "Karkata", 31, "Ramachandra Deba IV")
        datetime.date(1947, 8, 15)
    """
    target_rashi, day = normalize_solar_query(month, day)
    start, end = anka_year_span(anka, gajapati, inclusive_end)
    return _single_match(
        solar_matches(start, end, target_rashi, day),
        f"{day} {target_rashi}",
        _context(anka, gajapati),
    )


def english_date_from_anka_lunar(
    anka: int,
    month: str,
    paksha: str,
    tithi: str,
    adhika: bool = False,
    gajapati: Optional[str] = None,
    inclusive_end: bool = False,
) -> date:
    """Return the English date of a Purnimanta lunar date in a given Anka year.

    Args:
        anka (int): Anka year.
        month (str): Purnimanta lunar month name, case-insensitive.
        paksha (str): ``"Shukla"`` or ``"Krushna"``, case-insensitive.
        tithi (str): Tithi name, or ``"Purnima"`` / ``"Amabasya"``.
        adhika (bool, optional): ``True`` for the intercalary month.
        gajapati (str, optional): Reigning monarch; defaults to the latest
            reign.
        inclusive_end (bool, optional): See :func:`anka_year_span`.

    Returns:
        date: The matching English date.  A tithi spanning two sunrises is
        reported on the first of the two days.

    Raises:
        OdiaCalendarError: for invalid input, if no day matches (including
            a *kshaya* tithi, as in :func:`odia_to_english.english_date_from_lunar`),
            or if the date occurs twice in the Anka year.

    Examples:
        >>> english_date_from_anka_lunar(71, "Bhadraba", "Shukla", "Dwadasi")
        datetime.date(2026, 9, 23)
        >>> english_date_from_anka_lunar(71, "Aswina", "Krushna", "Dwadasi")
        datetime.date(2026, 10, 7)
    """
    target_month, target_paksha, target_tithi = normalize_lunar_query(
        month, paksha, tithi
    )
    start, end = anka_year_span(anka, gajapati, inclusive_end)
    description = (
        f"{'Adhika ' if adhika else ''}{target_month} {target_paksha} {target_tithi}"
    )
    return _single_match(
        lunar_matches(start, end, target_month, target_paksha, target_tithi, adhika),
        description,
        _context(anka, gajapati),
    )


def _main(argv: Optional[List[str]] = None) -> int:
    """Print a few sample conversions; return a non-zero exit code on failure."""
    del argv  # no command-line interface yet; kept for a uniform signature

    # (anka, rashi/solar month, day, gajapati)
    solar_dates = [
        (71, "Kanya", 21, None),
        (71, "Kanya", 7, None),
        (25, "Karkata", 31, "Ramachandra Deba IV"),
    ]

    # (anka, lunar month, paksha, tithi, gajapati)
    lunar_dates = [
        (71, "Bhadraba", "Shukla", "Dwadasi", None),
        (71, "Aswina", "Krushna", "Dwadasi", None),
        (39, "Jyestha", "Krushna", "Amabasya", None),
    ]

    exit_code = 0

    for anka, month, day, gajapati in solar_dates:
        query = f"{day} {month}, Anka {anka}"
        try:
            print(
                f"solar: {query} -> "
                f"{english_date_from_anka_solar(anka, month, day, gajapati)}"
            )
        except OdiaCalendarError as exc:
            print(f"solar: {query} -> {exc}")
            exit_code = 1

    print("")

    for anka, month, paksha, tithi, gajapati in lunar_dates:
        query = f"{month} {paksha} {tithi}, Anka {anka}"
        try:
            result = english_date_from_anka_lunar(
                anka, month, paksha, tithi, gajapati=gajapati
            )
            print(f"lunar: {query} -> {result}")
        except OdiaCalendarError as exc:
            print(f"lunar: {query} -> {exc}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
