"""Command-line entry point (formerly ``call.py``).

Usage::

    odia-panji                         # built-in samples, every direction
    odia-panji 23-09-2026 07-10-2026   # your own dates (English -> Odia)
    python -m odia_panji 23-09-2026    # same, without the console script
"""

from __future__ import annotations

import sys
from typing import List, Optional, Tuple

from . import __version__
from .anka_to_english import english_date_from_anka_lunar, english_date_from_anka_solar
from .calendar_types import OdiaCalendarError
from .odia_calendar import format_odia_date
from .odia_to_english import english_date_from_lunar, english_date_from_solar

_SAMPLE_DATES: List[str] = [
    "17-03-1961",
    "07-07-1970",
    "08-07-1970",
    "12-09-1970",
    "13-09-1970",
    "23-09-2026",
    "11-06-2002",
    "07-10-2026",
]


def english_to_odia(dates: List[str]) -> int:
    """Print the Odia conversion of each date; return 1 if any failed."""
    exit_code = 0
    for raw_date in dates:
        try:
            print(format_odia_date(raw_date))
        except OdiaCalendarError as exc:
            print(f"{raw_date}: {exc}")
            exit_code = 1
    return exit_code


def odia_to_english() -> int:
    """Utkalabda + solar/lunar date -> English samples."""
    solar_dates: List[Tuple[int, str, int]] = [
        (1406, "Simha", 13),
        (1433, "Mesha", 1),
        (1434, "Kanya", 21),
    ]
    lunar_dates: List[Tuple[int, str, str, str]] = [
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
            result = english_date_from_lunar(utkalabda, month, paksha, tithi)
            print(f"lunar: {query} -> {result}")
        except OdiaCalendarError as exc:
            print(f"lunar: {query} -> {exc}")
            exit_code = 1
    return exit_code


def anka_to_english() -> int:
    """Anka + solar/lunar date -> English samples (None = current reign)."""
    solar_dates: List[Tuple[int, str, int, Optional[str]]] = [
        (71, "Kanya", 21, None),
        (25, "Karkata", 31, "Ramachandra Deba IV"),
    ]
    lunar_dates: List[Tuple[int, str, str, str, Optional[str]]] = [
        (71, "Bhadraba", "Shukla", "Dwadasi", None),
        (39, "Jyestha", "Krushna", "Amabasya", None),
    ]
    exit_code = 0
    for anka, month, day, gajapati in solar_dates:
        query = f"{day} {month}, Anka {anka}"
        try:
            result = english_date_from_anka_solar(anka, month, day, gajapati)
            print(f"solar: {query} -> {result}")
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


def main(argv: Optional[List[str]] = None) -> int:
    """Run the conversions; return 1 if any of them reported a failure.

    With dates on the command line, only English -> Odia is run for them.
    Without arguments, built-in samples are run in every direction.
    """
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in ("-V", "--version"):
        print(f"odia-panji {__version__}")
        return 0
    if args:
        return english_to_odia(args)

    print("=== English -> Odia ===")
    statuses = [english_to_odia(_SAMPLE_DATES)]
    print("\n=== Odia (Utkalabda) -> English ===")
    statuses.append(odia_to_english())
    print("\n=== Odia (Anka) -> English ===")
    statuses.append(anka_to_english())
    return 1 if any(statuses) else 0


if __name__ == "__main__":
    sys.exit(main())
