"""Run sample conversions in both directions.

Gregorian -> Odia via :func:`odia_calendar.format_odia_date`, and
Odia -> Gregorian via :mod:`odia_to_english`.

Usage::

    python call.py                       # built-in samples
    python call.py 23-09-2026 07-10-2026 # your own dates (English -> Odia)
"""

from __future__ import annotations

import sys
from typing import List, Optional

from calendar_types import OdiaCalendarError
from odia_calendar import format_odia_date
from odia_to_english import english_date_from_lunar, english_date_from_solar


def english_to_odia(argv: Optional[List[str]] = None) -> int:
    """Print the conversion for each date given on the command line."""
    dates = argv or [
        # "23-09-2026",
        # "14-04-2026",
        # "29-08-1999",
        # "07-07-1970",
        # "15-08-1947",
        "17-03-1961",
        "07-07-1970",
        "08-07-1970",
        "12-09-1970",
        "13-09-1970",
        # "22-09-2026",
        "23-09-2026",
        "11-06-2002",
        "07-10-2026",
    ]

    exit_code = 0

    for raw_date in dates:
        try:
            # print(format_odia_date(raw_date, True))
            print(format_odia_date(raw_date))
        except OdiaCalendarError as exc:
            print(f"{raw_date}: {exc}")
            exit_code = 1

    return exit_code


def odia_to_english() -> int:
    """Print a few sample conversions; return a non-zero exit code on failure."""
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


def main(argv: Optional[List[str]] = None) -> int:
    """Run both directions; return 1 if either reported a failure."""
    print("=== English -> Odia ===")
    forward_status = english_to_odia(argv)

    print("\n=== Odia -> English ===")
    reverse_status = odia_to_english()

    return forward_status or reverse_status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
