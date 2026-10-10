"""Constants for :mod:`odia_calendar` and its helper modules.

Calendar epochs, the Gajapati reign table, observer location, month and
tithi name tables, and the numerical tuning parameters used by the
astronomical routines.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, FrozenSet, List, Tuple

from .calendar_types import Reign

# --------------------------------------------------------------------------
# eras
# --------------------------------------------------------------------------

# Utkalabda = CE year - 592, counted from Sunia.
UTKALABDA_EPOCH: int = 592

# Shaka = CE year - 78, counted from Chaitra Shukla Pratipada.
SHAKA_EPOCH: int = 78


# --------------------------------------------------------------------------
# Gajapati reigns
# --------------------------------------------------------------------------

GAJAPATI_REIGNS: List[Reign] = [
    Reign("Ramachandra Deba IV", date(1926, 2, 14)),
    Reign("Birakisore Deva III", date(1956, 11, 15), predecessor_died_same_day=True),
    Reign("Divyasingha Deva IV", date(1970, 7, 7), predecessor_died_same_day=True),
]
"""Gajapati Maharajas of Puri, in ascending order of accession.

The Anka year is a *regnal* count: it restarts at each accession, so
converting a date to an Anka year requires knowing who reigned then.  Each
reign runs from its own accession up to (but excluding) the next one, which
is why the table stores only accession dates -- a reign's end is the
successor's beginning.

Succession at Puri is immediate: the heir takes the throne on the day the
reigning Gajapati dies, so that single date belongs to both reigns.
``predecessor_died_same_day`` marks those shared days; by default they are
credited to the incoming monarch, which is the usual panji convention.

The first entry cannot carry the flag meaningfully, having no predecessor
in the table.  The list must stay sorted by accession;
:func:`~odia_calendar.gajapati_reign` relies on that to scan backwards for
the reign in force.  To cover earlier dates, prepend further reigns rather
than editing existing entries.
"""


# --------------------------------------------------------------------------
# observer
# --------------------------------------------------------------------------

# Observer: Puri, where Sunia and tithis are reckoned.
PURI_LAT: float = 19.8135
PURI_LON: float = 85.8312

# Indian Standard Time offset from UT, in days.
IST_OFFSET: float = 5.5 / 24.0


# --------------------------------------------------------------------------
# supported range
# --------------------------------------------------------------------------

# Inclusive CE years; later years fall outside the fixed search windows below.
MIN_SUPPORTED_YEAR: int = 1
MAX_SUPPORTED_YEAR: int = 6782


# --------------------------------------------------------------------------
# panji overrides
# --------------------------------------------------------------------------

# Verified panji dates, used instead of the computed value:
# ``SUNIA_OVERRIDES[2031] = date(2031, 9, 4)``.
SUNIA_OVERRIDES: Dict[int, date] = {}

# Same rule for Chaitra Shukla Pratipada:
# ``CHAITRA_OVERRIDES[2026] = date(2026, 3, 19)``.
CHAITRA_OVERRIDES: Dict[int, date] = {}


# --------------------------------------------------------------------------
# name tables
# --------------------------------------------------------------------------

# Periodic terms for the Moon's longitude: multipliers of the four
# fundamental arguments (D, M, M', F) and the coefficient in 1e-6 degree.
MOON_LONGITUDE_TERMS: List[Tuple[int, int, int, int, int]] = [
    (0, 0, 1, 0, 6288774),
    (2, 0, -1, 0, 1274027),
    (2, 0, 0, 0, 658314),
    (0, 0, 2, 0, 213618),
    (0, 1, 0, 0, -185116),
    (0, 0, 0, 2, -114332),
    (2, 0, -2, 0, 58793),
    (2, -1, -1, 0, 57066),
    (2, 0, 1, 0, 53322),
    (2, -1, 0, 0, 45758),
    (0, 1, -1, 0, -40923),
    (1, 0, 0, 0, -34720),
    (0, 1, 1, 0, -30383),
    (2, 0, 0, -2, 15327),
    (0, 0, 1, 2, -12528),
    (0, 0, 1, -2, 10980),
    (4, 0, -1, 0, 10675),
    (0, 0, 3, 0, 10034),
    (4, 0, -2, 0, 8548),
    (2, 1, -1, 0, -7888),
    (2, 1, 0, 0, -6766),
    (1, 0, -1, 0, -5163),
    (1, 1, 0, 0, 4987),
    (2, -1, 1, 0, 4036),
    (2, 0, 2, 0, 3994),
    (4, 0, 0, 0, 3861),
    (2, 0, -3, 0, 3665),
    (0, 1, -2, 0, -2689),
    (2, 0, -1, 2, -2602),
    (2, -1, -2, 0, 2390),
    (1, 0, 1, 0, -2348),
    (2, -2, 0, 0, 2236),
    (0, 1, 2, 0, -2120),
    (0, 2, 0, 0, -2069),
    (2, -2, -1, 0, 2048),
    (2, 0, 1, -2, -1773),
    (2, 0, 0, 2, -1595),
    (4, -1, -1, 0, 1215),
    (0, 0, 2, 2, -1110),
    (3, 0, -1, 0, -892),
    (2, 1, 1, 0, -810),
    (4, -1, -2, 0, 759),
    (0, 2, -1, 0, -713),
    (2, 2, -1, 0, -700),
    (2, 1, -2, 0, 691),
    (2, -1, 0, -2, 596),
    (4, 0, 1, 0, 549),
    (0, 0, 4, 0, 537),
    (4, -1, 0, 0, 520),
    (1, 0, -2, 0, -487),
    (2, 1, 0, -2, -399),
    (0, 0, 2, -2, -381),
    (1, 1, 1, 0, 351),
    (3, 0, -2, 0, -340),
    (4, 0, -3, 0, 330),
    (2, -1, 2, 0, 327),
    (0, 2, 1, 0, -323),
    (1, 1, -1, 0, 299),
    (2, 0, 3, 0, 294),
    (2, 0, -1, -2, 0),
]


# Odia digits 0-9, indexed by the corresponding ASCII digit value.
ODIA_DIGITS: str = "୦୧୨୩୪୫୬୭୮୯"

# Sidereal zodiac signs; index 0 = Mesha (Aries).
RASHI: List[str] = [
    "Mesha",
    "Vrusha",
    "Mithuna",
    "Karkata",
    "Simha",
    "Kanya",
    "Tula",
    "Bruschika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
]

# Solar months take the name of the sign the Sun enters on Sankranti.
ODIA_SOLAR_MONTHS: List[str] = list(RASHI)

# Lunar month traditionally paired with each solar month (Mesha ~ Baisakha).
SOLAR_MONTH_LUNAR_EQUIVALENTS: List[str] = [
    "Baisakha",
    "Jyestha",
    "Asadha",
    "Srabana",
    "Bhadraba",
    "Aswina",
    "Kartika",
    "Margasira",
    "Pausa",
    "Magha",
    "Phalguna",
    "Chaitra",
]

# Lunar month names; index 0 = Chaitra.
LUNAR_MONTHS: List[str] = [
    "Chaitra",
    "Baisakha",
    "Jyestha",
    "Asadha",
    "Srabana",
    "Bhadraba",
    "Aswina",
    "Kartika",
    "Margasira",
    "Pausa",
    "Magha",
    "Phalguna",
]

# Tithis 1-14 of a paksha; 15 and 30 are Purnima and Amabasya.
TITHI_NAMES: List[str] = [
    "Pratipada",
    "Dwitiya",
    "Trutiya",
    "Chaturthi",
    "Panchami",
    "Sasthi",
    "Saptami",
    "Astami",
    "Nabami",
    "Dasami",
    "Ekadasi",
    "Dwadasi",
    "Trayodasi",
    "Chaturdasi",
]


# --------------------------------------------------------------------------
# calendar indices
# --------------------------------------------------------------------------

BHADRA_MONTH_INDEX: int = 5  # LUNAR_MONTHS[5] == "Bhadraba"
CHAITRA_MONTH_INDEX: int = 0  # LUNAR_MONTHS[0] == "Chaitra"
SUNIA_TITHI: int = 12  # Shukla Dwadashi
PRATIPADA_TITHI: int = 1  # Shukla Pratipada

TITHIS_PER_LUNATION: int = 30
DEGREES_PER_TITHI: float = 12.0  # 360 / 30
DEGREES_PER_RASHI: float = 30.0  # 360 / 12
SIGNS_IN_ZODIAC: int = 12


# --------------------------------------------------------------------------
# astronomical reference values
# --------------------------------------------------------------------------

# Mean new moon to new moon, in days.
MEAN_SYNODIC_MONTH: float = 29.530588861

# A known new moon (JD); origin of the lunation numbering.
REFERENCE_NEW_MOON_JD: float = 2451550.09766

# JD of J2000.0; time origin of the Meeus series.
J2000_JD: float = 2451545.0

DAYS_PER_JULIAN_CENTURY: float = 36525.0

# Sun's zenith angle at sunrise (refraction + semidiameter, NOAA).
_SUNRISE_ZENITH_DEGREES: float = 90.833

# Earth's orbital eccentricity at J2000, for the equation of time.
_EARTH_ECCENTRICITY: float = 0.016708634


# --------------------------------------------------------------------------
# numerical tuning
# --------------------------------------------------------------------------

_BISECTION_STEPS: int = 80
_BISECTION_TOLERANCE_DAYS: float = 1e-7

# Root-finding brackets around the mean position.  A tithi averages ~0.98 day
# and varies by about +/-0.3 day, so +/-2 days always holds the true boundary.
_TITHI_BRACKET_DAYS: float = 2.0
_NEW_MOON_BRACKET_DAYS: float = 2.0

# The Sun stays in a sign for at most ~31.5 days; keep this above 32.
_SANKRANTI_LOOKBACK_DAYS: float = 35.0

# ((month, day), (month, day)) windows that contain the target lunar month
# for every supported year.
_SUNIA_SEARCH_WINDOW: Tuple[Tuple[int, int], Tuple[int, int]] = ((6, 1), (11, 15))
_CHAITRA_SEARCH_WINDOW: Tuple[Tuple[int, int], Tuple[int, int]] = ((2, 1), (5, 20))


# --------------------------------------------------------------------------
# input parsing and validation
# --------------------------------------------------------------------------
_INPUT_DATE_FORMAT: str = "%d-%m-%Y"
# Alternative separators accepted in input dates; normalised to "-".
DATE_SEPARATORS: Tuple[str, ...] = ("/", ".")
# Inclusive geographic bounds for an observer, in degrees.
LATITUDE_RANGE: Tuple[float, float] = (-90.0, 90.0)
LONGITUDE_RANGE: Tuple[float, float] = (-180.0, 360.0)


# --------------------------------------------------------------------------
# angles and time units
# --------------------------------------------------------------------------
FULL_CIRCLE_DEGREES: float = 360.0
HALF_CIRCLE_DEGREES: float = 180.0
ARCSECONDS_PER_DEGREE: float = 3600.0
MINUTES_PER_DAY: float = 1440.0
# The Earth turns 1 degree every 4 minutes.
MINUTES_PER_DEGREE: float = MINUTES_PER_DAY / FULL_CIRCLE_DEGREES
DAYS_PER_JULIAN_YEAR: float = 365.25
# Table 47.A coefficients are expressed in units of 1e-6 degree.
MOON_TERM_SCALE: float = 1_000_000.0


# --------------------------------------------------------------------------
# sunrise / civil-day tuning
# --------------------------------------------------------------------------
# Fixed-point refinements of the sunrise time; 3 converges well below 1 min.
_SUNRISE_ITERATIONS: int = 3
# Day offsets probed around a tithi's start when finding its civil day.
_CIVIL_DAY_PROBE_OFFSETS: Tuple[int, ...] = (0, 1, -1, 2)
# Steps back from midnight so the "end of day" instant stays in that day.
_END_OF_DAY_EPSILON_DAYS: float = 1e-6


# --------------------------------------------------------------------------
# paksha and tithi labels
# --------------------------------------------------------------------------
PAKSHA_SHUKLA: str = "Shukla"
PAKSHA_KRUSHNA: str = "Krushna"
PURNIMA: str = "Purnima"
AMABASYA: str = "Amabasya"
TITHIS_PER_PAKSHA: int = 15
PURNIMA_TITHI: int = 15  # last tithi of Shukla paksha
AMABASYA_TITHI: int = 30  # last tithi of Krushna paksha
MAX_SOLAR_MONTH_DAYS: int = 32  # Longest possible solar month, in days.

# --------------------------------------------------------------------------
# Anka numbering rules
# --------------------------------------------------------------------------
# Anka 1 is never used; counting starts at 2.
MIN_ANKA: int = 2
# Anka numbers ending in these digits are skipped ...
ANKA_SKIPPED_LAST_DIGITS: FrozenSet[int] = frozenset({0, 6})
# ... except for these explicit exceptions.
ANKA_ALLOWED_EXCEPTIONS: FrozenSet[int] = frozenset({10})
