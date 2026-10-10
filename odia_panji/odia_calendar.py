"""Odia calendar conversion: Gregorian date -> Utkalabda and Anka year.

Convert an English (Gregorian) date given as ``"dd-mm-yyyy"`` into the Odia
era year -- Utkalabda / Utkaliya San -- together with the Anka year of the
Gajapati Maharaja of Puri.

Rules implemented
-----------------
See Wikipedia: https://en.wikipedia.org/wiki/Odia_calendar
and https://en.wikipedia.org/wiki/Anka_year

1. The Utkaliya era begins in 592 CE and the era year rolls over on
   **Sunia** = Bhadra Shukla Dwadashi (12th tithi of the bright fortnight
   of the lunar month Bhadrapada), which falls in Aug/Sept::

       Utkalabda = CE_year - 592   (on/after Sunia of that CE year)
                 = CE_year - 593   (before Sunia)

   e.g. 23-Sep-2026 -> 1434 Utkalabda (2026 - 592).

2. The Anka year also rolls over on Sunia.  Valid Anka numbers skip 1,
   every number ending in 6, and every number ending in 0 except 10::

       2,3,4,5,7,8,9,10,11,12,13,14,15,17,18,19,21,...

   The Anka is a *regnal* count, restarting at each accession, so a date
   is only meaningful relative to a named monarch -- see
   :func:`gajapati_reign` and :data:`~constants.GAJAPATI_REIGNS`.  The
   *index* (1, 2, 3, ...) advances by one at every Sunia; under the
   present Gajapati (acceded 07-Jul-1970) Sunia 2011 gives Anka 52 and
   Sunia 2026 gives Anka 71.

   Succession at Puri is immediate -- the heir accedes on the day the
   reigning Gajapati dies -- so a handover date belongs to both reigns.
   By default it is credited to the incoming monarch; pass
   ``inclusive_end=True`` to credit it to the outgoing one.

3. Odia lunar months are **Purnimanta** (month runs full moon -> full
   moon), the way the panji labels religious dates.  Sunia itself is a
   Shukla-paksha date, so it is the same in Amanta and Purnimanta.

4. Odia **solar** months are named for the sign the Sun has entered
   (Mesha, Vrusha, ..., Simha, Kanya) and change at Sankranti.  See :data:`~constants.ODIA_SOLAR_MONTHS`.

5. A tithi belongs to the civil day whose *sunrise* falls inside it.  A
   *kshaya* tithi, with no sunrise inside it, goes to the day it begins
   (Chaitra Shukla Pratipada 2026: the new moon is at 06:56 IST on
   19 March, after sunrise, so the Shaka new year is 19 March).

Because Sunia is a *lunar* date, its Gregorian date is computed
astronomically (Meeus sun & moon, Lahiri ayanamsa, tithi at Puri sunrise)
instead of being hard-coded.  The results match the published dates
checked -- Sunia 2011 and 2022-2026, and Chaitra Shukla Pratipada
2019-2027 -- but not every year has been verified against a printed
panji; where one differs, pin it via :data:`~constants.SUNIA_OVERRIDES` or
:data:`~constants.CHAITRA_OVERRIDES` rather than editing the astronomy.

Range
-----
Years 1 to 6782 CE (:data:`~constants.MIN_SUPPORTED_YEAR` ..
:data:`~constants.MAX_SUPPORTED_YEAR`).  The sidereal calendar drifts
against the Gregorian one (Chaitra Shukla Pratipada reaches June by 6782),
and from 6783 Chaitra can leave the fixed February-May search window.
Later years are therefore rejected up front, even though a few happen to
resolve.  :func:`sunia_date` also accepts 6783, so that the last supported
Odia year can be closed.

The Anka functions have a tighter bound: they cannot reach before the
earliest reign in :data:`~constants.GAJAPATI_REIGNS` (14-Feb-1926).
Utkalabda, Shaka, lunar and solar dates are unaffected, since none of
them is regnal.

Accuracy is separate: :func:`ayanamsa` is a *linear* approximation and the
Meeus series are truncated, so trust results only for roughly **1800-2100**.

Module layout
-------------
This module is the public entry point and re-exports every helper below,
so ``from odia_panji.odia_calendar import ...`` keeps working.  The
most-used names are also re-exported from the package root, so
``from odia_panji import convert`` is the recommended import.

    calendar_types  DateLike, OdiaCalendarError, Reign, LunarDate, ...
    constants       every constant and lookup table
    validation      parsing and argument checks
    julian_day      Gregorian <-> Julian Day
    math_helpers    angle normalisation and bisection
    astronomy       Sun, Moon, ayanamsa, sunrise, sankranti
    lunation        tithis, lunations and lunar-month naming
    anka            Anka number rules

Public functions
----------------
Dates & astronomy
    parse_date, to_jd, date_to_jd, jd_to_date,
    sun_longitude, moon_longitude, ayanamsa, sidereal_sun_longitude,
    tithi_at, tithi_span, sunrise_jd
Calendar logic
    sunia_date, shaka_new_year, odia_year_start,
    utkalabda_year, shaka_year,
    gajapati_reign, gajapati_accession,
    is_valid_anka, anka_from_index, index_from_anka,
    anka_index, years_since_accession, anka_year,
    lunar_date, odia_solar_date
Presentation
    to_odia_numerals, convert, format_odia_date
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from typing import Optional, Tuple, Union

from .anka import anka_from_index, index_from_anka, is_valid_anka
from .astronomy import (
    ayanamsa,
    moon_longitude,
    sidereal_sun_longitude,
    solar_ingress_jd,
    sun_longitude,
    sunrise_jd,
)
from .calendar_types import (
    DateLike,
    LunarDate,
    OdiaCalendarError,
    OdiaConversion,
    Reign,
    SolarDate,
)
from .constants import (
    BHADRA_MONTH_INDEX,
    CHAITRA_MONTH_INDEX,
    CHAITRA_OVERRIDES,
    DEGREES_PER_RASHI,
    GAJAPATI_REIGNS,
    IST_OFFSET,
    LUNAR_MONTHS,
    MAX_SUPPORTED_YEAR,
    MIN_SUPPORTED_YEAR,
    ODIA_DIGITS,
    ODIA_SOLAR_MONTHS,
    PAKSHA_KRUSHNA,
    PRATIPADA_TITHI,
    PURI_LAT,
    PURI_LON,
    RASHI,
    SHAKA_EPOCH,
    SOLAR_MONTH_LUNAR_EQUIVALENTS,
    SUNIA_OVERRIDES,
    SUNIA_TITHI,
    UTKALABDA_EPOCH,
    _CHAITRA_SEARCH_WINDOW,
    _END_OF_DAY_EPSILON_DAYS,
    _INPUT_DATE_FORMAT,
    _SUNIA_SEARCH_WINDOW,
)
from .julian_day import date_to_jd, jd_to_date, to_jd
from .lunation import (
    amanta_month_of_lunation,
    find_month_start_day,
    lunation_containing,
    tithi_at,
    tithi_name,
    tithi_span,
)
from .validation import parse_date, validate_supported_date, validate_year

__all__ = [
    "DateLike",
    "OdiaCalendarError",
    "OdiaConversion",
    "LunarDate",
    "SolarDate",
    "Reign",
    "MIN_SUPPORTED_YEAR",
    "MAX_SUPPORTED_YEAR",
    "GAJAPATI_REIGNS",
    "SUNIA_OVERRIDES",
    "CHAITRA_OVERRIDES",
    "parse_date",
    "to_jd",
    "date_to_jd",
    "jd_to_date",
    "sun_longitude",
    "moon_longitude",
    "ayanamsa",
    "sidereal_sun_longitude",
    "tithi_at",
    "tithi_span",
    "sunrise_jd",
    "sunia_date",
    "shaka_new_year",
    "odia_year_start",
    "utkalabda_year",
    "shaka_year",
    "gajapati_reign",
    "gajapati_accession",
    "is_valid_anka",
    "anka_from_index",
    "index_from_anka",
    "anka_index",
    "years_since_accession",
    "anka_year",
    "lunar_date",
    "odia_solar_date",
    "to_odia_numerals",
    "convert",
    "english_to_odia",
    "format_odia_date",
]


# --------------------------------------------------------------------------
# 1. Sunia -- Bhadra Shukla Dwadashi
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _compute_sunia_date(year: int, latitude: float, longitude: float) -> date:
    """Compute the astronomical Sunia date; see :func:`sunia_date`."""
    return find_month_start_day(
        year,
        BHADRA_MONTH_INDEX,
        SUNIA_TITHI,
        _SUNIA_SEARCH_WINDOW,
        latitude,
        longitude,
        "Bhadraba",
    )


def sunia_date(
    year: int, latitude: float = PURI_LAT, longitude: float = PURI_LON
) -> date:
    """Return the Gregorian date of Sunia (Bhadra Shukla Dwadashi) in ``year``.

    The Utkalabda and the Anka year both roll over on this day.

    Args:
        year (int): Gregorian year, 1 to ``MAX_SUPPORTED_YEAR + 1``.  The
            extra year lets :func:`odia_year_start` close the last
            supported Odia year.
        latitude (float, optional): Observer latitude. Defaults to PURI_LAT.
        longitude (float, optional): Observer longitude. Defaults to PURI_LON.

    Returns:
        date: The civil date (IST) whose sunrise falls in Bhadra Shukla
        Dwadashi, or -- if that tithi is kshaya -- the day on which it begins.

    Raises:
        OdiaCalendarError: if ``year`` is unsupported or the month cannot be
            located.

    Note:
        :data:`~constants.SUNIA_OVERRIDES` is consulted first.

    Examples:
        >>> sunia_date(2026)
        datetime.date(2026, 9, 23)
    """
    validate_year(year, MAX_SUPPORTED_YEAR + 1)
    if year in SUNIA_OVERRIDES:
        return SUNIA_OVERRIDES[year]
    return _compute_sunia_date(year, latitude, longitude)


def _era_year_starting_on_or_before(calendar_date: date) -> int:
    """Return the CE year of the most recent Sunia on or before ``calendar_date``."""
    return (
        calendar_date.year
        if calendar_date >= sunia_date(calendar_date.year)
        else calendar_date.year - 1
    )


# --------------------------------------------------------------------------
# 2. Utkalabda and Shaka years
# --------------------------------------------------------------------------


def utkalabda_year(date_like: DateLike) -> int:
    """Return the Utkalabda / Utkaliya San year for an English date.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"``, ``date`` or ``datetime``.

    Returns:
        int: The Utkalabda year: CE year - 592 on or after that year's Sunia,
        CE year - 593 before it.

    Raises:
        OdiaCalendarError: if the date cannot be parsed or is unsupported.

    Examples:
        >>> utkalabda_year("23-09-2026")  # Sunia day itself
        1434
        >>> utkalabda_year("22-09-2026")  # the day before
        1433
    """
    parsed = validate_supported_date(date_like)
    return _era_year_starting_on_or_before(parsed) - UTKALABDA_EPOCH


def odia_year_start(date_like: DateLike) -> Tuple[date, date]:
    """Return the first and last day of the Odia era year containing ``date_like``.

    The year runs from Sunia to the day before the following Sunia.

    Raises:
        OdiaCalendarError: if the date cannot be parsed or is unsupported.
    """
    parsed = validate_supported_date(date_like)
    era_start_year = _era_year_starting_on_or_before(parsed)
    return (
        sunia_date(era_start_year),
        sunia_date(era_start_year + 1) - timedelta(days=1),
    )


@lru_cache(maxsize=None)
def _compute_chaitra_pratipada(year: int, latitude: float, longitude: float) -> date:
    """Compute Chaitra Shukla Pratipada date; see :func:`shaka_new_year`."""
    return find_month_start_day(
        year,
        CHAITRA_MONTH_INDEX,
        PRATIPADA_TITHI,
        _CHAITRA_SEARCH_WINDOW,
        latitude,
        longitude,
        "Chaitra",
    )


def shaka_new_year(
    year: int, latitude: float = PURI_LAT, longitude: float = PURI_LON
) -> date:
    """Return the date of Chaitra Shukla Pratipada (Shaka new year) in ``year``.

    Args:
        year (int): Gregorian year, 1 to :data:`~constants.MAX_SUPPORTED_YEAR`.
        latitude (float, optional): Observer latitude. Defaults to PURI_LAT.
        longitude (float, optional): Observer longitude. Defaults to PURI_LON.

    Returns:
        date: The civil date (IST) of Chaitra Shukla Pratipada.

    Raises:
        OdiaCalendarError: if ``year`` is unsupported or Chaitra cannot be
            located.

    Note:
        :data:`~constants.CHAITRA_OVERRIDES` is consulted first.  The kshaya
        rule applies, hence 19 March for 2026.

    Examples:
        >>> shaka_new_year(2026)
        datetime.date(2026, 3, 19)
    """
    validate_year(year)
    if year in CHAITRA_OVERRIDES:
        return CHAITRA_OVERRIDES[year]
    return _compute_chaitra_pratipada(year, latitude, longitude)


def shaka_year(date_like: DateLike) -> int:
    """Return the Shaka (Śakābda) year, which begins at Chaitra Shukla Pratipada.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"``, ``date`` or ``datetime``.

    Returns:
        int: CE year - 78 on or after :func:`shaka_new_year`, else
        CE year - 79.

    Examples:
        >>> shaka_year("20-09-2026")
        1948
        >>> shaka_year("18-03-2026")
        1947
    """
    parsed = validate_supported_date(date_like)
    if parsed >= shaka_new_year(parsed.year):
        return parsed.year - SHAKA_EPOCH
    return parsed.year - SHAKA_EPOCH - 1


# --------------------------------------------------------------------------
# 3. Gajapati reigns and the Anka year
# --------------------------------------------------------------------------


def gajapati_reign(date_like: DateLike, inclusive_end: bool = False) -> Reign:
    """Return the Gajapati reigning on ``date_like``.

    The Anka is a regnal count, so this needs the monarch who held the
    throne on ``date_like``.  Reigns come from
    :data:`~constants.GAJAPATI_REIGNS`, each running from its own
    accession up to (but excluding) the next.

    Succession at Puri is immediate, so an accession date can belong to
    two reigns.  Such dates are flagged with
    :attr:`~constants.Reign.predecessor_died_same_day`; ``inclusive_end``
    decides who gets credited for them.

    Args:
        date_like (DateLike): Date to resolve.
        inclusive_end (bool, optional): On a flagged accession day,
            ``False`` (default) credits the incoming monarch, the usual
            panji convention; ``True`` credits the outgoing one. No effect
            elsewhere.

    Returns:
        Reign: The reign in force, with its name and accession date.

    Raises:
        OdiaCalendarError: if ``date_like`` precedes the earliest known reign,
            since no Anka count can be established for it.

    Examples:
        >>> gajapati_reign("15-08-1947").name
        'Ramachandra Deba IV'
        >>> gajapati_reign("07-07-1970").name  # handover day, incoming king
        'Divyasingha Deva IV'
        >>> gajapati_reign("07-07-1970", inclusive_end=True).name
        'Birakisore Deva III'
    """
    parsed = validate_supported_date(date_like)

    # Scan newest first and take the first reign already begun; this needs
    # no end dates, because each reign ends where the next one starts.
    for position in range(len(GAJAPATI_REIGNS) - 1, -1, -1):
        reign = GAJAPATI_REIGNS[position]
        if parsed < reign.accession:
            continue

        # Hand the shared day back to the outgoing monarch when asked.  The
        # earliest reign in the table has no predecessor to hand it to, so
        # `position > 0` guards the lookup.
        if (
            inclusive_end
            and parsed == reign.accession
            and reign.predecessor_died_same_day
            and position > 0
        ):
            return GAJAPATI_REIGNS[position - 1]
        return reign

    earliest = GAJAPATI_REIGNS[0]
    raise OdiaCalendarError(
        f"{parsed.isoformat()} precedes the earliest known reign "
        f"({earliest.name}, acceded {earliest.accession.isoformat()}); "
        "add the earlier monarch to GAJAPATI_REIGNS, or pass an explicit "
        "accession date"
    )


def gajapati_accession(date_like: DateLike, inclusive_end: bool = False) -> date:
    """Return the accession date of the Gajapati reigning on ``date_like``.

    Thin wrapper over :func:`gajapati_reign` for callers that need only
    the accession date, e.g. as the ``accession`` argument below.

    Args:
        date_like (DateLike): Date to resolve.
        inclusive_end (bool, optional): See
            :func:`gajapati_reign`.

    Raises:
        OdiaCalendarError: if ``date_like`` precedes the earliest known reign.

    Examples:
        >>> gajapati_accession("15-08-1947")
        datetime.date(1926, 2, 14)
        >>> gajapati_accession("07-07-1970", inclusive_end=True)
        datetime.date(1956, 11, 15)
    """
    return gajapati_reign(date_like, inclusive_end).accession


def _resolve_accession(
    calendar_date: date, accession: Optional[date], inclusive_end: bool
) -> date:
    """Return the accession to count from, resolving ``None`` from the reign table."""
    if accession is None:
        return gajapati_reign(calendar_date, inclusive_end).accession
    return accession


def anka_index(
    date_like: DateLike,
    accession: Optional[date] = None,
    inclusive_end: bool = False,
) -> int:
    """Return the Anka counting index (1, 2, 3, ...) in force on ``date_like``.

    The index advances by one at every Sunia.  The stretch from accession
    to the first Sunia and the year starting at that Sunia both carry
    index 1, which is Anka 2 (Anka 1 is never used).  Under Dibyasingha
    Deb IV Sunia 2011 gives Anka 52 and Sunia 2026 gives Anka 71.

    Args:
        date_like (DateLike): Date to evaluate.
        accession (date, optional): Accession date to count from.
            Defaults to the reign resolved from
            :data:`~constants.GAJAPATI_REIGNS`. Pass a date explicitly
            for a monarch not in the table.
        inclusive_end (bool, optional): See :func:`gajapati_reign`.
            Ignored when ``accession`` is given explicitly.

    Raises:
        OdiaCalendarError: if ``date_like`` precedes ``accession`` (the
            Anka is a regnal count, undefined before a reign begins).

    Returns:
        int: The counting index.
    """
    parsed = validate_supported_date(date_like)
    accession = _resolve_accession(parsed, accession, inclusive_end)

    if parsed < accession:
        raise OdiaCalendarError(
            f"{parsed.isoformat()} precedes the accession "
            f"({accession.isoformat()}); pass the accession of the monarch "
            "reigning at the time"
        )

    first_sunia = sunia_date(accession.year)
    if first_sunia <= accession:
        # The monarch acceded after that year's Sunia, so the first rollover
        # of the reign is the following year's.
        first_sunia = sunia_date(accession.year + 1)

    if parsed < first_sunia:
        return 1
    return _era_year_starting_on_or_before(parsed) - first_sunia.year + 1


def years_since_accession(
    date_like: DateLike,
    accession: Optional[date] = None,
    inclusive_end: bool = False,
) -> int:
    """Return ``anka_index - 1``, the "regnal year" Wikipedia prints.

    Wikipedia shows regnal year 56 next to Anka 71 for 2026; that is this
    value, while Anka 71 is the 57th valid number (:func:`anka_index`).
    """
    return anka_index(date_like, accession, inclusive_end) - 1


def anka_year(
    date_like: DateLike,
    accession: Optional[date] = None,
    inclusive_end: bool = False,
) -> int:
    """Return the Anka year for an English date.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"``, ``date`` or ``datetime``.
        accession (date, optional): Accession date to count from; defaults
            to the reign resolved from :data:`~constants.GAJAPATI_REIGNS`.
        inclusive_end (bool, optional): See
            :func:`gajapati_reign`.

    Returns:
        int: The Anka year.

    Raises:
        OdiaCalendarError: if ``date_like`` precedes the reign counted from.

    Examples:
        >>> anka_year("23-09-2026")
        71
        >>> anka_year("22-09-2026")
        69
        >>> anka_year("15-08-1947")  # Ramachandra Deba IV, resolved automatically
        25
        >>> anka_year("07-07-1970")  # first day of the new reign
        2
        >>> anka_year("07-07-1970", inclusive_end=True)
        15
    """
    return anka_from_index(anka_index(date_like, accession, inclusive_end))


# --------------------------------------------------------------------------
# 4. Lunar date (Purnimanta), solar date, and presentation helpers
# --------------------------------------------------------------------------


def lunar_date(
    date_like: DateLike, latitude: float = PURI_LAT, longitude: float = PURI_LON
) -> LunarDate:
    """Return the Purnimanta lunar date prevailing at sunrise on ``date_like``.

    Shukla-paksha days carry the Amanta month name; Krushna-paksha days
    carry the *next* month's name, since the panji runs full moon to full
    moon (so Mahalaya falls in Aswina).

    Returns:
        LunarDate: The month, paksha, tithi name and whether the month is
        intercalary.

    Note:
        The tithi is the one at sunrise, so 19-03-2026 reports Chaitra
        Krushna Amabasya although :func:`shaka_year` has already rolled to
        1948 (Pratipada is kshaya and goes to the day it begins).
    """
    parsed = validate_supported_date(date_like)
    sunrise = sunrise_jd(parsed, latitude, longitude)
    tithi_number, paksha = tithi_at(sunrise)

    lunation = lunation_containing(sunrise)
    # Purnimanta naming: the dark fortnight belongs to the following month.
    naming_lunation = lunation + 1 if paksha == PAKSHA_KRUSHNA else lunation
    month_index, is_adhika = amanta_month_of_lunation(naming_lunation)

    return LunarDate(
        LUNAR_MONTHS[month_index], paksha, tithi_name(tithi_number), is_adhika
    )


def odia_solar_date(date_like: DateLike) -> SolarDate:
    """Return the Odia solar date for ``date_like``.

    Odia solar months take the name of the sign the Sun has entered, so a
    date in mid-August is ``13 Simha``, not the *lunar* ``13 Bhadraba``
    reported by :func:`lunar_date`.  The paired lunar month name is
    returned as :attr:`SolarDate.lunar_equivalent`.

    A solar month begins on the civil (IST) day the Sun enters the sign,
    whatever the hour.  This puts the Odia year on 14 April, or 13 April
    in Gregorian leap years.

    Returns:
        SolarDate: ``(rashi, month, day, lunar_equivalent)``.

    Examples:
        >>> odia_solar_date("14-04-2026")
        SolarDate(rashi='Mesha', month='Mesha', day=1, lunar_equivalent='Baisakha')
        >>> odia_solar_date("29-08-1999")
        SolarDate(rashi='Simha', month='Simha', day=13, lunar_equivalent='Bhadraba')
    """
    parsed = validate_supported_date(date_like)

    # Evaluate at the final instant of the IST day: the sign in force then
    # is the one that names the day.
    end_of_ist_day_jd = date_to_jd(parsed) + 1.0 - IST_OFFSET - _END_OF_DAY_EPSILON_DAYS
    rashi_index = int(sidereal_sun_longitude(end_of_ist_day_jd) // DEGREES_PER_RASHI)

    ingress_jd = solar_ingress_jd(rashi_index, end_of_ist_day_jd)
    month_start, _ = jd_to_date(ingress_jd + IST_OFFSET)
    day_of_month = (parsed - month_start).days + 1

    return SolarDate(
        RASHI[rashi_index],
        ODIA_SOLAR_MONTHS[rashi_index],
        day_of_month,
        SOLAR_MONTH_LUNAR_EQUIVALENTS[rashi_index],
    )


def to_odia_numerals(number: Union[int, str]) -> str:
    """Render ASCII digits as Odia digits, leaving other characters intact.

    Examples:
        >>> to_odia_numerals(2026)
        '୨୦୨୬'
    """
    return "".join(
        ODIA_DIGITS[int(char)] if char.isdigit() else char for char in str(number)
    )


def convert(date_like: DateLike, inclusive_end: bool = False) -> OdiaConversion:
    """Convert an English date to every supported Odia calendar quantity.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"``, ``date`` or ``datetime``.
        inclusive_end (bool, optional): See
            :func:`gajapati_reign`.  Only affects dates falling exactly on a
            same-day handover.

    Returns:
        OdiaConversion: A mapping with the Utkalabda and Anka years (in ASCII
        and Odia digits), the reigning Gajapati, whether the date is that
        monarch's accession day, the Odia year's start and end dates, the
        Purnimanta lunar date, the Odia solar date and the Shaka year.

    Raises:
        OdiaCalendarError: if the date is unsupported, or precedes the
            earliest known reign.
    """
    parsed = validate_supported_date(date_like)

    utkalabda = utkalabda_year(parsed)
    reign = gajapati_reign(parsed, inclusive_end)
    anka = anka_year(parsed, None, inclusive_end)
    counting_index = anka_index(parsed, None, inclusive_end)
    era_start, era_end = odia_year_start(parsed)
    lunar = lunar_date(parsed)
    solar = odia_solar_date(parsed)

    return {
        "english_date": parsed.strftime(_INPUT_DATE_FORMAT),
        "utkalabda": utkalabda,
        "utkalabda_odia": to_odia_numerals(utkalabda),
        "gajapati": reign.name,
        "gajapati_accession": reign.accession.strftime(_INPUT_DATE_FORMAT),
        "is_accession_day": parsed == reign.accession,
        "anka": anka,
        "anka_odia": to_odia_numerals(anka),
        "anka_index": counting_index,
        "years_since_accession": counting_index - 1,
        "odia_year_start": era_start.strftime(_INPUT_DATE_FORMAT),  # Sunia
        "odia_year_end": era_end.strftime(_INPUT_DATE_FORMAT),
        "sunia_of_year": sunia_date(parsed.year).strftime(_INPUT_DATE_FORMAT),
        "lunar_month": lunar.month,
        "adhika": lunar.adhika,
        "paksha": lunar.paksha,
        "tithi": lunar.tithi,
        "solar_rashi": solar.rashi,
        "solar_month": solar.month,
        "solar_day": solar.day,
        "solar_month_lunar_equivalent": solar.lunar_equivalent,
        "shakabda": shaka_year(parsed),
    }


def english_to_odia(date_like: DateLike, inclusive_end: bool = False) -> OdiaConversion:
    """Convert an English date to its Odia calendar details.

    Friendly alias of :func:`convert`, named to mirror the reverse
    functions in :mod:`odia_panji.odia_to_english`.

    Examples:
        >>> english_to_odia("23-09-2026")["utkalabda"]
        1434
    """
    return convert(date_like, inclusive_end)


def format_odia_date(date_like: DateLike, inclusive_end: bool = False) -> str:
    """Return a one-line human-readable summary of :func:`convert`."""
    converted = convert(date_like, inclusive_end)

    adhika_prefix = "Adhika " if converted["adhika"] else ""
    return (
        f"{converted['english_date']}  ->  {converted['utkalabda']} Utkalabda | "
        # f"({converted['utkalabda_odia']} ଉତ୍କଳାବ୍ଦ), "
        f"{converted['anka']} Anka ({converted['gajapati']}) | "
        f"Acce: {converted['years_since_accession']} | "
        f"{adhika_prefix}{converted['lunar_month']} {converted['paksha']} "
        f"{converted['tithi']} | "
        f"{converted['solar_day']} {converted['solar_month']} | "
        f"Sunia: {converted['sunia_of_year']} | Shakabda: {converted['shakabda']}"
    )
