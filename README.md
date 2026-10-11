# Odia Panji

[![CI](https://github.com/srinibashsamal/odia-panji/actions/workflows/python.yml/badge.svg)](https://github.com/srinibashsamal/odia-panji/actions/workflows/python.yml)
[![PyPI version](https://img.shields.io/pypi/v/odia-panji.svg)](https://pypi.org/project/odia-panji/)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Source-black?logo=github)](https://github.com/srinibashsamal/odia-panji)

A pure-Python library for converting between **Gregorian dates** and the
**traditional Odia calendar**: Utkalabda, Anka, tithi, solar month and Shakabda.

Sunia, tithis and sankrantis are **computed** from the positions of the Sun and
Moon, not read from hard-coded tables, so the code works for any year in its
supported range. There are no external dependencies.

> **Scope:** this is a date-conversion library, not a full Panchanga/Panji. It
> does not cover Nakshatra, Yoga, Karana, Muhurta or festival rules.

## Installation

```bash
pip install odia-panji
```

Requires Python 3.9 or later. On Windows, use `py -m pip install odia-panji`
if `pip` is not recognised.

## Quick start

```python
from odia_panji import convert, format_historical, to_english

# English -> Odia
convert("07-10-2026")["utkalabda"]  # 1434

# Odia -> English
to_english("Kanya", 21, utkalabda=1434)  # datetime.date(2026, 10, 7)

# Citation-style output
print(format_historical("07-10-2026"))
# 7 October 2026 = 1434 Utkalabda, Anka 71 of Divyasingha Deva IV
# Aswina Krushna Dwadasi | 21 Kanya | Shakabda 1948
```

## English → Odia

Dates are written `dd-mm-yyyy` (`/` and `.` separators also work), or passed as
`datetime.date` / `datetime.datetime`.

```python
from odia_panji import convert, format_odia_date

print(format_odia_date("07-10-2026"))
# 07-10-2026  ->  1434 Utkalabda | 71 Anka (Divyasingha Deva IV) | Acce: 56 |
# Aswina Krushna Dwadasi | 21 Kanya | Sunia: 23-09-2026 | Shakabda: 1948

result = convert("07-10-2026")  # returns a dict; english_to_odia() is an alias
result["utkalabda"]  # 1434
result["anka"]  # 71
result["tithi"]  # 'Dwadasi'
```

Individual values:

```python
from odia_panji import (
    anka_year,
    lunar_date,
    odia_solar_date,
    shaka_year,
    sunia_date,
    utkalabda_year,
)

utkalabda_year("23-09-2026")  # 1434
anka_year("23-09-2026")  # 71
shaka_year("23-09-2026")  # 1948
sunia_date(2026)  # datetime.date(2026, 9, 23)
lunar_date("07-10-2026")
# LunarDate(month='Aswina', paksha='Krushna', tithi='Dwadasi', adhika=False)
odia_solar_date("07-10-2026")
# SolarDate(rashi='Kanya', month='Kanya', day=21, lunar_equivalent='Aswina')
```

<details>
<summary>Full output of <code>convert()</code></summary>

```python
{
    "english_date": "23-09-2026",
    "utkalabda": 1434,
    "utkalabda_odia": "୧୪୩୪",
    "gajapati": "Divyasingha Deva IV",
    "gajapati_accession": "07-07-1970",
    "is_accession_day": False,
    "anka": 71,
    "anka_odia": "୭୧",
    "anka_index": 57,
    "years_since_accession": 56,
    "odia_year_start": "23-09-2026",
    "odia_year_end": "11-09-2027",
    "sunia_of_year": "23-09-2026",
    "lunar_month": "Bhadraba",
    "adhika": False,
    "paksha": "Shukla",
    "tithi": "Dwadasi",
    "solar_rashi": "Kanya",
    "solar_month": "Kanya",
    "solar_day": 7,
    "solar_month_lunar_equivalent": "Aswina",
    "shakabda": 1948,
}
```

</details>

### Citation-style output

For historical and archival work (land grants, palm-leaf records, Madala Panji
style citations):

```python
from odia_panji import format_historical

print(format_historical("07-10-2026"))
# 7 October 2026 = 1434 Utkalabda, Anka 71 of Divyasingha Deva IV
# Aswina Krushna Dwadasi | 21 Kanya | Shakabda 1948

print(format_historical("07-10-2026", style="compact"))
# 7 October 2026 / 1434 Utkalabda / Anka 71 of Divyasingha Deva IV / Aswina Krushna Dwadasi / 21 Kanya

print(format_historical("07-10-2026", style="lunar"))
# Aswina Krushna Dwadasi, 1434 Utkalabda (Anka 71 of Divyasingha Deva IV)
# = 7 October 2026

print(format_historical("15-08-1947", style="solar"))
# 31 Karkata, 1354 Utkalabda (Anka 25 of Ramachandra Deba IV)
# = 15 August 1947
```

| `style`            | Layout                                                               |
| ------------------ | -------------------------------------------------------------------- |
| `"full"` (default) | Two lines: English = Utkalabda, Anka; then lunar, solar and Shakabda |
| `"compact"`        | One line, separated by `/`                                           |
| `"lunar"`          | Lunar date first, English date below                                 |
| `"solar"`          | Solar date first, English date below                                 |

Pass `include_english=False` to leave out the Gregorian date. Dates in an
intercalary month are prefixed with `Adhika`.

## Odia → English

`to_english()` is the reverse of `convert()`: one function for every Odia date.
Give the year as `utkalabda=` **or** `anka=`, and the date as a solar month +
day **or** a lunar month + `paksha=` + `tithi=`.

```python
from odia_panji import convert, to_english

to_english("Kanya", 21, utkalabda=1434)  # date(2026, 10, 7)
to_english(
    "Aswina", paksha="Krushna", tithi="Dwadasi", utkalabda=1434
)  # date(2026, 10, 7)
to_english("Kanya", 21, anka=71)  # date(2026, 10, 7)
to_english("Karkata", 31, anka=25, gajapati="Ramachandra Deba IV")  # date(1947, 8, 15)

# Intercalary (adhika) month
to_english("Jyestha", paksha="Shukla", tithi="Dasami", adhika=True, utkalabda=1433)

# Chain the two for the full Odia details of an Odia date
convert(to_english("Kanya", 21, anka=71))
```

Names are case-insensitive. The Anka count restarts with every Gajapati;
`gajapati` defaults to the current reign.

<details>
<summary>Specialised functions (one per case)</summary>

`to_english()` calls these; they remain available for direct use.

```python
from odia_panji import (
    anka_year_span,
    english_date_from_anka_lunar,
    english_date_from_anka_solar,
    english_date_from_lunar,
    english_date_from_solar,
)

# Utkalabda + Odia date
english_date_from_solar(1434, "Kanya", 21)  # date(2026, 10, 7)
english_date_from_lunar(1434, "Aswina", "Krushna", "Dwadasi")  # date(2026, 10, 7)

# Anka + Odia date
english_date_from_anka_solar(71, "Kanya", 21)  # date(2026, 10, 7)
english_date_from_anka_lunar(71, "Bhadraba", "Shukla", "Dwadasi")  # date(2026, 9, 23)

# First and last English date of an Anka year
anka_year_span(71)  # (date(2026, 9, 23), date(2027, 9, 11))
```

</details>

### Errors

Every invalid input raises `OdiaCalendarError` (a subclass of `ValueError`).
Reverse conversions raise it when no date matches, or when several do; they
list the matching dates instead of guessing.

## Command line

```bash
odia-panji                         # sample conversions in every direction
odia-panji 23-09-2026 07-10-2026   # your own dates
python -m odia_panji --version
```

More in the
[`examples/`](https://github.com/srinibashsamal/odia-panji/tree/main/examples)
folder.

## Supported calendars

| Calendar                     | What it is                                                                        | Year starts on                  |
| ---------------------------- | --------------------------------------------------------------------------------- | ------------------------------- |
| **Utkalabda** (Utkaliya San) | Odia era year: CE − 592 / − 593                                                   | Sunia (Bhadraba Shukla Dwadasi) |
| **Shakabda**                 | Shaka era year: CE − 78 / − 79                                                    | Chaitra Shukla Pratipada        |
| **Solar month**              | Sidereal sign the Sun is in (Lahiri ayanamsa); day 1 = Sankranti day              | 1 Mesha (13/14 April)           |
| **Lunar month**              | Purnimanta (full moon to full moon), with adhika months detected                  | —                               |
| **Tithi**                    | Lunar day in force at sunrise in Puri; a _kshaya_ tithi goes to the day it begins | —                               |
| **Anka**                     | Gajapati regnal year; skips 1, numbers ending in 6, and ending in 0 except 10     | Sunia                           |

Solar months pair with lunar month names as almanacs print them:
Mesha–Baisakha, Vrusha–Jyestha, Mithuna–Asadha, Karkata–Srabana,
Simha–Bhadraba, Kanya–Aswina, Tula–Kartika, Bruschika–Margasira,
Dhanu–Pausa, Makara–Magha, Kumbha–Phalguna, Meena–Chaitra.

### Accession days

At Puri the heir accedes on the day the reigning Gajapati dies, so a handover
date belongs to two reigns. By default it is credited to the incoming Gajapati;
pass `inclusive_end=True` to credit the outgoing one:

```python
anka_year("07-07-1970")  # 2  (Divyasingha Deva IV)
anka_year("07-07-1970", inclusive_end=True)  # 15 (Birakisore Deva III)
```

## Limitations

**Astronomical assumptions**

- Sun: Meeus, _Astronomical Algorithms_, ch. 25. Moon: Meeus ch. 47 (60 periodic terms).
- Ayanamsa: Lahiri / Chitrapaksha, **linear approximation**.
- Sunrise: NOAA algorithm (~1 minute accuracy), observer at **Puri**, times in **IST**.
- Civil calendar: proleptic Gregorian at every epoch.

**Historical date support range**

- Utkalabda, Shakabda, solar and lunar dates: **1 CE to 6782 CE**.
- Anka: only from **14-02-1926** (earliest reign in `GAJAPATI_REIGNS`).
  Add earlier Gajapatis at the start of that list to go further back.

**Accuracy expectations**

- **Trusted range: roughly 1800–2100.** Error grows outside it because the
  ayanamsa is linear and the series are truncated.
- Checked against published dates: Sunia 2011 and 2022–2026; Chaitra Shukla
  Pratipada 2019–2027. Not every year has been compared with a printed panji.
- Printed panjis can differ by a day near a boundary (different constants,
  ayanamsa, sunrise definition or location). Pin such dates rather than
  editing the astronomy:

  ```python
  from datetime import date
  from odia_panji import SUNIA_OVERRIDES

  SUNIA_OVERRIDES[2031] = date(2031, 9, 4)
  ```

**Known gaps**

- A _kshaya_ tithi (no sunrise inside it) cannot yet be found by the lunar
  reverse functions, e.g. Chaitra Shukla Pratipada 1433 = 19-03-2026.
- In a long (adhika) Odia year, a few Simha/Kanya solar dates near Sunia occur
  twice, e.g. 19 Simha in Utkalabda 1433 is both 04-09-2025 and 04-09-2026.
  The reverse functions report both instead of picking one.
- Kshaya _months_ are not modelled.

## Project structure

```
odia-panji/
├── odia_panji/
│   ├── __init__.py          # public API and __version__
│   ├── __main__.py          # `python -m odia_panji`
│   ├── odia_calendar.py     # Gregorian -> Odia
│   ├── formatting.py        # format_odia_date, format_historical
│   ├── reverse.py           # to_english(): any Odia date -> Gregorian
│   ├── odia_to_english.py   # Utkalabda + solar/lunar date -> Gregorian
│   ├── anka_to_english.py   # Anka + solar/lunar date -> Gregorian
│   ├── anka.py              # Anka numbering rules
│   ├── astronomy.py         # Sun, Moon, ayanamsa, sunrise, sankranti
│   ├── lunation.py          # tithis, new moons, lunar-month naming
│   ├── julian_day.py        # Gregorian <-> Julian Day
│   ├── math_helpers.py      # angle normalisation, bisection
│   ├── constants.py         # constants, name tables, Gajapati reigns
│   ├── calendar_types.py    # result types and OdiaCalendarError
│   ├── validation.py        # parsing and input checks
│   ├── cli.py               # `odia-panji` command
│   └── py.typed
├── tests/
├── examples/
├── .github/workflows/
│   ├── python.yml           # CI: tests, lint, build
│   └── publish.yml          # GitHub Release -> PyPI
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Development

```bash
git clone https://github.com/srinibashsamal/odia-panji.git
cd odia-panji
pip install -e ".[dev]"

pytest                  # unit tests + every docstring example
ruff check . && ruff format --check .
mypy
```

Boundary dates matter most here, because dates come from astronomical events:
Sunia, Sankranti, accession days and adhika months. Please add a test for any
date you correct.

## Versioning

The project follows [Semantic Versioning](https://semver.org/). The version
lives in one place, `odia_panji/__init__.py`, and `pyproject.toml` reads it from
there. Changes are listed in the
[CHANGELOG](https://github.com/srinibashsamal/odia-panji/blob/main/CHANGELOG.md).

## Design principles

- Calculation over lookup tables
- Conversion in both directions
- Calendar systems kept separate
- No external dependencies
- Explicit, documented assumptions
- Simple, reusable functions

## References

- [Odia calendar, Wikipedia](https://en.wikipedia.org/wiki/Odia_calendar)
- [Anka year, Wikipedia](https://en.wikipedia.org/wiki/Anka_year)
- Jean Meeus, _Astronomical Algorithms_, 2nd ed.
- NOAA Solar Calculator

## License

Released under the
[MIT License](https://github.com/srinibashsamal/odia-panji/blob/main/LICENSE).

## Author

**Srinibash Samal** — [github.com/srinibashsamal](https://github.com/srinibashsamal)
