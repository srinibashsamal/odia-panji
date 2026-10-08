# Odia Panji

A pure-Python library for converting between **Gregorian dates** and the **traditional Odia calendar**: Utkalabda, Anka, tithi, solar month and Shakabda.

It converts in both directions across three Odia calendar systems:

- **Odia solar calendar**
- **Odia lunar calendar**
- **Anka / Gajapati regnal year**

Sunia, tithis and sankrantis are **computed** from the positions of the Sun and Moon, not read from hard-coded tables. The code therefore works for any year in its supported range.

> **Scope:** this is a date-conversion library, not a full Panchanga/Panji. It does not cover Nakshatra, Yoga, Karana, Muhurta, festival rules or other daily Panchanga details.

## Features

| Direction                              | What you get                                                                                                                       |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Gregorian → Odia**                   | Utkalabda, Anka, reigning Gajapati, lunar date (month, paksha, tithi, adhika), solar date (rashi and day), Shakabda, Odia numerals |
| **Utkalabda + solar date → Gregorian** | e.g. 21 Kanya 1434 → 07-10-2026                                                                                                    |
| **Utkalabda + lunar date → Gregorian** | e.g. Aswina Krushna Dwadasi 1434 → 07-10-2026                                                                                      |
| **Anka + solar date → Gregorian**      | e.g. Anka 71, 21 Kanya → 07-10-2026                                                                                                |
| **Anka + lunar date → Gregorian**      | e.g. Anka 71, Bhadraba Shukla Dwadasi → 23-09-2026                                                                                 |
| **Anka → Gregorian range**             | e.g. Anka 71 → 23-09-2026 to 11-09-2027                                                                                            |

There are no external dependencies; it uses only the Python standard library.

## Requirements

Python 3.8 or later.

## Getting started

```bash
git clone https://github.com/srinibashsamal/odia-panji.git
cd odia-panji
python call.py
```

Pass your own dates in `dd-mm-yyyy` format (`/` and `.` separators also work):

```bash
python call.py 23-09-2026 07-10-2026
```

Sample output:

```text
=== English -> Odia ===
23-09-2026  ->  1434 Utkalabda | 71 Anka (Divyasingha Deva IV) | Acce: 56 | Bhadraba Shukla Dwadasi | 7 Kanya | Sunia: 23-09-2026 | Shakabda: 1948
07-10-2026  ->  1434 Utkalabda | 71 Anka (Divyasingha Deva IV) | Acce: 56 | Aswina Krushna Dwadasi | 21 Kanya | Sunia: 23-09-2026 | Shakabda: 1948

=== Odia (Utkalabda) -> English ===
solar: 13 Simha 1406 -> 1999-08-29
solar: 1 Mesha 1433 -> 2026-04-14
solar: 21 Kanya 1434 -> 2026-10-07

lunar: Bhadraba Krushna Trutiya 1406 -> 1999-08-29
lunar: Bhadraba Shukla Dwadasi 1434 -> 2026-09-23
lunar: Aswina Krushna Dwadasi 1434 -> 2026-10-07

=== Odia (Anka) -> English ===
solar: 21 Kanya, Anka 71 -> 2026-10-07
solar: 31 Karkata, Anka 25 -> 1947-08-15

lunar: Bhadraba Shukla Dwadasi, Anka 71 -> 2026-09-23
lunar: Jyestha Krushna Amabasya, Anka 39 -> 2002-06-11
```

## Usage

### Gregorian → Odia

```python
from odia_calendar import (
    anka_year, convert, format_odia_date, lunar_date,
    odia_solar_date, shaka_year, sunia_date, utkalabda_year,
)

utkalabda_year("23-09-2026")   # 1434
anka_year("23-09-2026")        # 71
shaka_year("23-09-2026")       # 1948
sunia_date(2026)               # datetime.date(2026, 9, 23)

lunar_date("07-10-2026")
# LunarDate(month='Aswina', paksha='Krushna', tithi='Dwadasi', adhika=False)

odia_solar_date("07-10-2026")
# SolarDate(rashi='Kanya', month='Kanya', day=21, lunar_equivalent='Aswina')

print(format_odia_date("23-09-2026"))   # one-line summary
convert("23-09-2026")                   # everything, as a dict
```

`convert()` returns:

```json
{
  "english_date": "23-09-2026",
  "utkalabda": 1434,
  "utkalabda_odia": "୧୪୩୪",
  "gajapati": "Divyasingha Deva IV",
  "gajapati_accession": "07-07-1970",
  "is_accession_day": false,
  "anka": 71,
  "anka_odia": "୭୧",
  "anka_index": 57,
  "years_since_accession": 56,
  "odia_year_start": "23-09-2026",
  "odia_year_end": "11-09-2027",
  "sunia_of_year": "23-09-2026",
  "lunar_month": "Bhadraba",
  "adhika": false,
  "paksha": "Shukla",
  "tithi": "Dwadasi",
  "solar_rashi": "Kanya",
  "solar_month": "Kanya",
  "solar_day": 7,
  "solar_month_lunar_equivalent": "Aswina",
  "shakabda": 1948
}
```

### Utkalabda + Odia date → Gregorian

```python
from odia_to_english import english_date_from_lunar, english_date_from_solar

english_date_from_solar(1434, "Kanya", 21)                      # datetime.date(2026, 10, 7)
english_date_from_lunar(1434, "Aswina", "Krushna", "Dwadasi")   # datetime.date(2026, 10, 7)
```

### Anka + Odia date → Gregorian

An Anka is a regnal **year**, not a day, so it is combined with a solar or lunar date:

```python
from anka_to_english import (
    anka_year_span, english_date_from_anka_lunar, english_date_from_anka_solar,
)

english_date_from_anka_solar(71, "Kanya", 21)                      # datetime.date(2026, 10, 7)
english_date_from_anka_lunar(71, "Bhadraba", "Shukla", "Dwadasi")  # datetime.date(2026, 9, 23)

# An earlier reign: pass the Gajapati's name
english_date_from_anka_solar(25, "Karkata", 31, "Ramachandra Deba IV")  # datetime.date(1947, 8, 15)

# First and last Gregorian date of an Anka year
anka_year_span(71)  # (datetime.date(2026, 9, 23), datetime.date(2027, 9, 11))
```

The Anka count restarts with every Gajapati, so the same number recurs in each reign. `gajapati` defaults to the current (latest) reign.

All names are case-insensitive. For an intercalary month, pass `adhika=True` to the lunar functions.

### Accession days

At Puri the heir accedes on the day the reigning Gajapati dies, so a handover date belongs to two reigns. The `inclusive_end` option decides who gets it, in both directions:

| `inclusive_end`   | Handover day is credited to |
| ----------------- | --------------------------- |
| `False` (default) | the incoming Gajapati       |
| `True`            | the outgoing Gajapati       |

```python
anka_year("07-07-1970")                      # 2  (Divyasingha Deva IV)
anka_year("07-07-1970", inclusive_end=True)  # 15 (Birakisore Deva III)
```

### Errors

Every invalid input raises `OdiaCalendarError`, a subclass of `ValueError`. Reverse conversions raise it when no date matches, or when several do. They list the matching dates rather than guess.

## Calendar systems

### Utkalabda / Utkaliya San

The Odia era year begins on **Sunia** (Bhadra Shukla Dwadashi). Utkalabda is CE year − 592 on or after that year's Sunia, otherwise CE year − 593.

### Odia solar calendar

Solar months are named after the sidereal sign (Lahiri ayanamsa) the Sun has entered. Each starts on the civil day of its Sankranti. Almanacs pair each with a lunar month name:

| Rashi     | Lunar month pairing |
| --------- | ------------------- |
| Mesha     | Baisakha            |
| Vrusha    | Jyestha             |
| Mithuna   | Asadha              |
| Karkata   | Srabana             |
| Simha     | Bhadraba            |
| Kanya     | Aswina              |
| Tula      | Kartika             |
| Bruschika | Margasira           |
| Dhanu     | Pausa               |
| Makara    | Magha               |
| Kumbha    | Phalguna            |
| Meena     | Chaitra             |

### Odia lunar calendar

Lunar months are **Purnimanta** (full moon to full moon), so the Krushna paksha takes the name of the following month. The date is the tithi in force at **sunrise in Puri**. A _kshaya_ tithi, which contains no sunrise, goes to the day it begins. Adhika (intercalary) months are detected.

### Anka and Gajapati

The Anka is counted from the Gajapati's accession and advances at every Sunia. Valid Anka numbers skip 1, numbers ending in 6, and numbers ending in 0 (except 10):

```text
2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, ...
```

The first Anka of a reign runs from the accession to the second Sunia, so it can last more than a year. Reign data lives in `GAJAPATI_REIGNS` in `constants.py`, separate from the astronomy.

### Shakabda

CE year − 78 on or after Chaitra Shukla Pratipada, otherwise CE year − 79.

## Astronomy

Implemented from scratch, with no astronomy packages:

- Julian Day conversion (proleptic Gregorian)
- Solar longitude (Meeus, _Astronomical Algorithms_, ch. 25)
- Lunar longitude (Meeus, ch. 47, all 60 periodic terms)
- Lahiri / Chitrapaksha ayanamsa (linear approximation)
- Sunrise (NOAA algorithm, ~1 minute accuracy)
- Sankranti, tithi boundaries and new moons (by bisection)

Reverse conversions first work out the date range of the requested year (Utkalabda or Anka). They then scan that range day by day for the matching solar or lunar date.

## Accuracy and conventions

| Item           | Convention                                  |
| -------------- | ------------------------------------------- |
| Civil calendar | Proleptic Gregorian                         |
| Location       | Puri, Odisha (configurable where supported) |
| Time zone      | IST                                         |
| Lunar month    | Purnimanta                                  |
| Ayanamsa       | Lahiri, linear approximation                |
| Tithi          | At local sunrise                            |
| Solar month    | Sidereal sign, from Sankranti               |

- **Supported range:** 1 to 6782 CE. Anka years are available only from **14-02-1926**, the earliest reign in the table.
- **Trusted range:** roughly **1800–2100**. The ayanamsa is linear and the series are truncated, so error grows outside this window.
- **Checked against published dates:** Sunia 2011 and 2022–2026, and Chaitra Shukla Pratipada 2019–2027. Not every year has been compared with a printed panji.
- **Differences from printed panjis** can come from different constants, ayanamsa, sunrise definitions or location. If your panji differs for a year, pin the date in `constants.py` rather than editing the astronomy:

  ```python
  SUNIA_OVERRIDES[2031] = date(2031, 9, 4)
  ```

- **Earlier reigns:** to cover dates before 1926, add the earlier Gajapatis at the start of `GAJAPATI_REIGNS`.
- **Kshaya tithis in reverse lookups:** the lunar reverse functions cannot yet find a kshaya tithi (e.g. Chaitra Shukla Pratipada 1433 = 19-03-2026), because no sunrise falls inside it.

## Project structure

```text
odia-panji/
├── odia_calendar.py      # Gregorian → Odia (main entry point)
├── odia_to_english.py    # Utkalabda + solar/lunar date → Gregorian
├── anka_to_english.py    # Anka + solar/lunar date → Gregorian
├── call.py               # demo / command-line runner
├── constants.py          # constants, name tables, Gajapati reigns
├── calendar_types.py     # result types and OdiaCalendarError
├── validation.py         # parsing and input checks
├── julian_day.py         # Gregorian ↔ Julian Day
├── math_helpers.py       # angle normalisation, bisection
├── astronomy.py          # Sun, Moon, ayanamsa, sunrise, sankranti
├── lunation.py           # tithis, new moons, lunar-month naming
├── anka.py               # Anka numbering rules
├── LICENSE
└── README.md
```

## Testing

The docstring examples act as tests:

```bash
python -m doctest odia_calendar.py odia_to_english.py anka_to_english.py lunation.py anka.py validation.py
```

No output means every example passed. Boundary dates matter most here, because dates come from astronomical events: Sunia, Sankranti, accession days and adhika months.

## Design principles

1. **Calculation over lookup tables**
2. **Conversion in both directions**
3. **Calendar systems kept separate**
4. **No external dependencies**
5. **Explicit, documented assumptions**
6. **Simple, reusable functions**

## References

- [Odia calendar, Wikipedia](https://en.wikipedia.org/wiki/Odia_calendar)
- [Anka year, Wikipedia](https://en.wikipedia.org/wiki/Anka_year)
- Jean Meeus, _Astronomical Algorithms_, 2nd ed.
- NOAA Solar Calculator

## License

Released under the [MIT License](LICENSE).

## Author

**Srinibash Samal**: [github.com/srinibashsamal](https://github.com/srinibashsamal)

## Project status

Actively developed. Current focus:

- Gregorian ↔ Odia solar date
- Gregorian ↔ Odia lunar date
- Gregorian ↔ Anka / Gajapati year
