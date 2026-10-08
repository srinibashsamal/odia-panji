"""Run sample conversions in every direction.

* English -> Odia via :func:`odia_calendar.format_odia_date`
* Odia (Utkalabda) -> English via :mod:`odia_to_english`
* Odia (Anka) -> English via :mod:`anka_to_english`

Usage::

    python call.py                       # built-in samples
    python call.py 23-09-2026 07-10-2026 # your own dates (English -> Odia)
"""

from __future__ import annotations

import sys
from typing import List, Optional

from anka_to_english import english_date_from_anka_lunar, english_date_from_anka_solar
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
    """Utkalabda + solar/lunar date -> English."""
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


def anka_to_english() -> int:
    """Anka + solar/lunar date -> English (gajapati=None means current reign)."""
    # (anka, rashi/solar month, day, gajapati)
    solar_dates = [
        (71, "Kanya", 21, None),
        (25, "Karkata", 31, "Ramachandra Deba IV"),
    ]

    # (anka, lunar month, paksha, tithi, gajapati)
    lunar_dates = [
        (71, "Bhadraba", "Shukla", "Dwadasi", None),
        (39, "Jyestha", "Krushna", "Amabasya", None),
    ]

    exit_code = 0

    for anka, month, day, gajapati in solar_dates:
        query = f"{day} {month}, Gajapati {gajapati} - Anka {anka}"
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
        query = f"{month} {paksha} {tithi}, Gajapati {gajapati} - Anka {anka}"
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
    """Run every direction; return 1 if any of them reported a failure."""
    print("=== English -> Odia ===")
    statuses = [english_to_odia(argv)]

    print("\n=== Odia (Utkalabda) -> English ===")
    statuses.append(odia_to_english())

    print("\n=== Odia (Anka) -> English ===")
    statuses.append(anka_to_english())

    return 1 if any(statuses) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
