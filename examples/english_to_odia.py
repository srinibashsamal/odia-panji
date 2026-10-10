"""English (Gregorian) date -> Odia calendar.

Run:  python examples/english_to_odia.py
"""

from odia_panji import (
    anka_year,
    convert,
    format_odia_date,
    lunar_date,
    odia_solar_date,
    shaka_year,
    utkalabda_year,
)

DATE = "07-10-2026"  # dd-mm-yyyy; "/" and "." separators also work

# One line, ready to print
print(format_odia_date(DATE))

# Individual pieces
print("Utkalabda :", utkalabda_year(DATE))
print("Anka      :", anka_year(DATE))
print("Shakabda  :", shaka_year(DATE))
print("Lunar     :", lunar_date(DATE))
print("Solar     :", odia_solar_date(DATE))

# Everything at once, as a dict
for key, value in convert(DATE).items():
    print(f"  {key:<30} {value}")
