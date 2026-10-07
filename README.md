# odia-panji
Converts English dates to the Odia calendar (Utkalabda, Anka, tithi, solar month, Shakabda) and back, using astronomical calculation.

Sunia, tithis and sankrantis are **computed** from the positions of the Sun and Moon. They are not hard-coded tables, so the code works for any year in its supported range.

## Features

- **Utkalabda / Utkaliya San:** era year that rolls over on Sunia (Bhadra Shukla Dwadashi).
- **Anka year:** regnal year of the Gajapati Maharaja of Puri. It skips 1, numbers ending in 6, and numbers ending in 0 (except 10).
- **Gajapati reign:** resolved automatically from a reign table, including same-day handovers.
- **Lunar date:** Purnimanta month, paksha and tithi at sunrise in Puri, with adhika (intercalary) months.
- **Solar date:** Odia solar month (Mesha, Vrusha, …) and day, counted from Sankranti.
- **Shakabda:** Shaka year, which begins at Chaitra Shukla Pratipada.
- **Reverse conversion:** turns an Odia solar or lunar date back into an English date.
- **Odia numerals:** e.g. `1434` → `୧୪୩୪`.
- **No dependencies:** pure Python standard library.

## Requirements

Python 3.8 or later.

## Getting started

```bash
git clone https://github.com/<your-username>/odia-panji.git
cd odia-panji
python call.py
```

Pass your own dates in `dd-mm-yyyy` format (`/` and `.` separators also work):

```bash
python call.py 23-09-2026 07-10-2026
```

Sample output:

```
=== English -> Odia ===
23-09-2026  ->  1434 Utkalabda | 71 Anka (Divyasingha Deva IV) | Acce: 56 | Bhadraba Shukla Dwadasi | 7 Kanya | Sunia: 23-09-2026 | Shakabda: 1948
07-10-2026  ->  1434 Utkalabda | 71 Anka (Divyasingha Deva IV) | Acce: 56 | Aswina Krushna Dwadasi | 21 Kanya | Sunia: 23-09-2026 | Shakabda: 1948

=== Odia -> English ===
solar: 13 Simha 1406 -> 1999-08-29
solar: 1 Mesha 1433 -> 2026-04-14
solar: 21 Kanya 1434 -> 2026-10-07

lunar: Bhadraba Krushna Trutiya 1406 -> 1999-08-29
lunar: Bhadraba Shukla Dwadasi 1434 -> 2026-09-23
lunar: Aswina Krushna Dwadasi 1434 -> 2026-10-07
```

## Usage

### English → Odia

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

### Odia → English

```python
from odia_to_english import english_date_from_lunar, english_date_from_solar

english_date_from_solar(1406, "Simha", 13)                     # datetime.date(1999, 8, 29)
english_date_from_lunar(1434, "Bhadraba", "Shukla", "Dwadasi")  # datetime.date(2026, 9, 23)
```

Names are case-insensitive. For an intercalary month, pass `adhika=True` to `english_date_from_lunar`.

### Accession days

At Puri the heir accedes on the day the reigning Gajapati dies, so a handover date belongs to two reigns. By default it is credited to the **incoming** monarch. Pass `inclusive_end=True` to credit it to the outgoing one:

```python
anka_year("07-07-1970")                      # 2  (Divyasingha Deva IV)
anka_year("07-07-1970", inclusive_end=True)  # 15 (Birakisore Deva III)
```

### Errors

Every invalid input raises `OdiaCalendarError`. It is a subclass of `ValueError`, so existing `except ValueError` blocks still catch it.

## Project structure

```
odia-panji/
├── odia_calendar.py      # main entry point: English → Odia
├── odia_to_english.py    # Odia → English
├── call.py               # sample runner
├── constants.py          # all constants and lookup tables
├── calendar_types.py     # DateLike, OdiaCalendarError, Reign, LunarDate, SolarDate, OdiaConversion
├── validation.py         # parsing and argument checks
├── julian_day.py         # Gregorian ↔ Julian Day
├── math_helpers.py       # angle normalisation, bisection
├── astronomy.py          # Sun, Moon, ayanamsa, sunrise, sankranti
├── lunation.py           # tithis, new moons, lunar-month naming
├── anka.py               # Anka number rules
├── LICENSE
└── README.md
```

## How it works

| Quantity    | Rule                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------- |
| Utkalabda   | CE year − 592 on or after that year's Sunia, otherwise CE year − 593                      |
| Shakabda    | CE year − 78 on or after Chaitra Shukla Pratipada, otherwise CE year − 79                 |
| Anka        | Counted from the Gajapati's accession, advancing at every Sunia, skipping invalid numbers |
| Tithi       | The tithi in force at sunrise in Puri; a _kshaya_ tithi goes to the day it begins         |
| Lunar month | Purnimanta: the Krushna paksha takes the name of the following month                      |
| Solar month | Named after the sidereal sign the Sun has entered (Lahiri ayanamsa)                       |

The astronomy uses Meeus's _Astronomical Algorithms_ (Sun: ch. 25, Moon: ch. 47) and the NOAA sunrise algorithm.

## Accuracy and limits

- **Supported range:** 1 to 6782 CE. Anka years are available only from **14-02-1926**, the earliest reign in the table.
- **Trusted range:** roughly **1800–2100**. The ayanamsa is a linear approximation and the series are truncated, so error grows outside this window.
- **Checked against published dates:** Sunia 2011 and 2022–2026, and Chaitra Shukla Pratipada 2019–2027. Not every year has been compared with a printed panji.
- **Fixing a wrong date:** if your panji differs for a year, pin the correct date in `constants.py` instead of editing the astronomy:

  ```python
  SUNIA_OVERRIDES[2031] = date(2031, 9, 4)
  ```

- **Earlier reigns:** to cover dates before 1926, add the earlier Gajapatis at the start of `GAJAPATI_REIGNS` in `constants.py`.
- **Kshaya tithis in reverse lookups:** `english_date_from_lunar` cannot yet find a kshaya tithi (e.g. Chaitra Shukla Pratipada 1433 = 19-03-2026), because no sunrise falls inside it.

## Running the tests

The docstring examples act as tests:

```bash
python -m doctest odia_calendar.py odia_to_english.py lunation.py anka.py validation.py
```

No output means every example passed.

## References

- [Odia calendar, Wikipedia](https://en.wikipedia.org/wiki/Odia_calendar)
- [Anka year, Wikipedia](https://en.wikipedia.org/wiki/Anka_year)
- Jean Meeus, _Astronomical Algorithms_, 2nd ed.
- NOAA Solar Calculator

## License

Released under the [MIT License](LICENSE).

## Author

**Srinibash Samal**
