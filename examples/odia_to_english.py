"""Utkalabda + Odia solar or lunar date -> English date.

Run:  python examples/odia_to_english.py
"""

from odia_panji import (
    OdiaCalendarError,
    english_date_from_lunar,
    english_date_from_solar,
)

# Solar date: Utkalabda year, rashi (solar month), day of month
print(english_date_from_solar(1434, "Kanya", 21))  # 2026-10-07

# Lunar date: Utkalabda year, Purnimanta month, paksha, tithi
print(english_date_from_lunar(1434, "Aswina", "Krushna", "Dwadasi"))  # 2026-10-07

# Intercalary (adhika) month
print(english_date_from_lunar(1433, "Jyestha", "Shukla", "Dasami", adhika=True))

# Invalid or ambiguous input raises OdiaCalendarError, never a silent guess
try:
    english_date_from_solar(1433, "Simha", 19)
except OdiaCalendarError as exc:
    print("Error:", exc)
