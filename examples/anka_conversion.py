"""Anka (Gajapati regnal year) conversions in both directions.

Run:  python examples/anka_conversion.py
"""

from odia_panji import (
    anka_year,
    anka_year_span,
    english_date_from_anka_lunar,
    english_date_from_anka_solar,
    gajapati_reign,
    is_valid_anka,
)

# English -> Anka
print(anka_year("23-09-2026"), gajapati_reign("23-09-2026").name)  # 71

# Which numbers are valid Anka years (1, x6 and x0 except 10 are skipped)
print([n for n in range(1, 30) if is_valid_anka(n)])

# First and last English date of an Anka year
print(anka_year_span(71))

# Anka + Odia date -> English (defaults to the current Gajapati)
print(english_date_from_anka_solar(71, "Kanya", 21))
print(english_date_from_anka_lunar(71, "Bhadraba", "Shukla", "Dwadasi"))

# An earlier reign: pass the Gajapati's name
print(english_date_from_anka_solar(25, "Karkata", 31, "Ramachandra Deba IV"))

# Accession day: credited to the incoming Gajapati unless inclusive_end=True
print(anka_year("07-07-1970"), anka_year("07-07-1970", inclusive_end=True))
