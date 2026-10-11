"""Lunar-calendar machinery: tithis, lunations and lunar-month naming.

Everything here is driven by the Moon-minus-Sun elongation, which is 0 deg
at new moon, 180 deg at full moon and advances 12 deg per tithi.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from functools import cache
from typing import Tuple

from .astronomy import moon_longitude, sidereal_sun_longitude, sun_longitude, sunrise_jd
from .calendar_types import OdiaCalendarError
from .constants import (
    _CIVIL_DAY_PROBE_OFFSETS,
    _NEW_MOON_BRACKET_DAYS,
    _TITHI_BRACKET_DAYS,
    AMABASYA,
    AMABASYA_TITHI,
    DEGREES_PER_RASHI,
    DEGREES_PER_TITHI,
    FULL_CIRCLE_DEGREES,
    IST_OFFSET,
    MEAN_SYNODIC_MONTH,
    PAKSHA_KRUSHNA,
    PAKSHA_SHUKLA,
    PURI_LAT,
    PURI_LON,
    PURNIMA,
    PURNIMA_TITHI,
    REFERENCE_NEW_MOON_JD,
    SIGNS_IN_ZODIAC,
    TITHI_NAMES,
    TITHIS_PER_LUNATION,
    TITHIS_PER_PAKSHA,
)
from .julian_day import date_to_jd, jd_to_date
from .math_helpers import find_angle_crossing, normalize_degrees

__all__ = [
    "moon_sun_elongation",
    "tithi_at",
    "tithi_name",
    "solve_elongation_crossing",
    "new_moon_jd",
    "lunation_containing",
    "amanta_month_of_lunation",
    "tithi_span",
    "civil_day_bearing_tithi",
    "find_month_start_day",
]


def moon_sun_elongation(jd: float) -> float:
    """Return the Moon-minus-Sun tropical longitude in [0, 360).

    This single angle drives the whole lunar calendar: it is 0 deg at new
    moon, 180 deg at full moon, and advances 12 deg per tithi.
    """
    return normalize_degrees(moon_longitude(jd) - sun_longitude(jd))


def tithi_at(jd: float) -> Tuple[int, str]:
    """Return the lunar tithi that is current at the given instant.

    Args:
        jd (float): Julian Day (UT).

    Returns:
        Tuple[int, str]: ``(tithi_number, paksha)`` with the number
        in 1-30; 15 is Purnima and 30 is Amabasya.
    """
    tithi_number = int(moon_sun_elongation(jd) / DEGREES_PER_TITHI) + 1
    paksha = PAKSHA_SHUKLA if tithi_number <= TITHIS_PER_PAKSHA else PAKSHA_KRUSHNA
    return tithi_number, paksha


def tithi_name(tithi_number: int) -> str:
    """Return the name of a tithi numbered 1-30 from Shukla Pratipada.

    Examples:
        >>> tithi_name(12), tithi_name(15), tithi_name(18), tithi_name(30)
        ('Dwadasi', 'Purnima', 'Trutiya', 'Amabasya')
    """
    if tithi_number == PURNIMA_TITHI:
        return PURNIMA
    if tithi_number == AMABASYA_TITHI:
        return AMABASYA
    tithi_in_paksha = (tithi_number - 1) % TITHIS_PER_PAKSHA + 1
    return TITHI_NAMES[tithi_in_paksha - 1]


def solve_elongation_crossing(
    target_degrees: float, jd_low: float, jd_high: float
) -> float:
    """Find the instant in ``[jd_low, jd_high]`` where the elongation hits a target.

    Args:
        target_degrees (float): Desired Moon-minus-Sun elongation.
        jd_low (float): Start of the bracket; must precede the crossing.
        jd_high (float): End of the bracket; must follow the crossing.

    Returns:
        float: The Julian Day of the crossing.
    """
    return find_angle_crossing(moon_sun_elongation, target_degrees, jd_low, jd_high)


@cache
def new_moon_jd(lunation: int) -> float:
    """Return the JD (UT) of the true new moon of the given lunation number.

    Lunations are numbered from :data:`~constants.REFERENCE_NEW_MOON_JD`; the
    mean position is refined to the true conjunction by root finding.  Cached
    because the month-naming and tithi searches request the same lunations
    repeatedly.
    """
    mean_new_moon = REFERENCE_NEW_MOON_JD + MEAN_SYNODIC_MONTH * lunation
    return solve_elongation_crossing(
        0.0,
        mean_new_moon - _NEW_MOON_BRACKET_DAYS,
        mean_new_moon + _NEW_MOON_BRACKET_DAYS,
    )


def lunation_containing(jd: float) -> int:
    """Return the lunation ``k`` with ``new_moon(k) <= jd < new_moon(k + 1)``.

    The mean-motion estimate can be off by one near a conjunction, so the
    neighbouring lunations are checked explicitly.
    """
    estimated = math.floor((jd - REFERENCE_NEW_MOON_JD) / MEAN_SYNODIC_MONTH)
    for candidate in (estimated + 1, estimated, estimated - 1):
        if new_moon_jd(candidate) <= jd:
            return candidate
    return estimated - 1  # pragma: no cover - unreachable for sane inputs


@cache
def amanta_month_of_lunation(lunation: int) -> Tuple[int, bool]:
    """Return the Amanta month of a lunation and whether it is intercalary.

    The month is named for the sign the Sun is in at its starting new moon
    (Meena -> Chaitra, Mesha -> Baisakha, ..., Simha -> Bhadraba).  If the
    Sun is still in that sign at the next new moon, no sankranti fell inside
    the month, so it is *adhika* (intercalary).

    Returns:
        ``(index into LUNAR_MONTHS, is_adhika)``.  Rare *kshaya* months,
        where two sankrantis fall in one lunation, are not modelled.
    """
    sign_at_start = int(
        sidereal_sun_longitude(new_moon_jd(lunation)) // DEGREES_PER_RASHI
    )
    sign_at_next = int(
        sidereal_sun_longitude(new_moon_jd(lunation + 1)) // DEGREES_PER_RASHI
    )
    month_index = (sign_at_start + 1) % SIGNS_IN_ZODIAC
    return month_index, sign_at_start == sign_at_next


def tithi_span(new_moon_jd: float, tithi: int) -> Tuple[float, float]:
    """Return the start and end instants (JD) of a tithi within one lunation.

    Args:
        new_moon_jd (float): JD of the new moon that starts the lunation.
        tithi (int): Tithi number 1-30, counted from Shukla Pratipada.

    Returns:
        Tuple[float, float]: ``(start_jd, end_jd)`` of the tithi.

        A tithi
        lasts roughly 0.984 day; the search window of +/-2 days around the
        mean position is more than enough to locate the true boundaries.

    Raises:
        OdiaCalendarError: if ``tithi`` is outside 1-30.
    """
    if not 1 <= tithi <= TITHIS_PER_LUNATION:
        raise OdiaCalendarError(f"tithi must be 1-{TITHIS_PER_LUNATION}, got {tithi}")

    mean_tithi_length = MEAN_SYNODIC_MONTH / TITHIS_PER_LUNATION
    approx_start = new_moon_jd + (tithi - 1) * mean_tithi_length
    approx_end = new_moon_jd + tithi * mean_tithi_length

    # The 30th tithi ends at 360 deg, which must wrap to 0 for the solver.
    start_jd = solve_elongation_crossing(
        ((tithi - 1) * DEGREES_PER_TITHI) % FULL_CIRCLE_DEGREES,
        approx_start - _TITHI_BRACKET_DAYS,
        approx_start + _TITHI_BRACKET_DAYS,
    )
    end_jd = solve_elongation_crossing(
        (tithi * DEGREES_PER_TITHI) % FULL_CIRCLE_DEGREES,
        approx_end - _TITHI_BRACKET_DAYS,
        approx_end + _TITHI_BRACKET_DAYS,
    )
    return start_jd, end_jd


def civil_day_bearing_tithi(
    lunation_start_jd: float,
    tithi: int,
    latitude: float = PURI_LAT,
    longitude: float = PURI_LON,
) -> date:
    """Return the civil (IST) day that carries a given tithi.

    A tithi belongs to the day whose *sunrise* falls inside it.  A tithi is
    shorter than a solar day, so it can begin and end between two
    consecutive sunrises and contain none at all; such a *kshaya* tithi is
    assigned by convention to the day on which it begins.

    Chaitra Shukla Pratipada 2026 is exactly this case: the new moon lands
    at 06:56 IST on 19 March, minutes after sunrise, so Pratipada holds no
    sunrise and the Shaka new year falls on 19 March rather than 20 March.
    """
    start_jd, end_jd = tithi_span(lunation_start_jd, tithi)
    first_candidate, _ = jd_to_date(start_jd + IST_OFFSET)

    # Probe the day the tithi starts on and its immediate neighbours; the
    # IST conversion can place the start either side of local midnight.
    for day_offset in _CIVIL_DAY_PROBE_OFFSETS:
        candidate = first_candidate + timedelta(days=day_offset)
        if start_jd <= sunrise_jd(candidate, latitude, longitude) < end_jd:
            return candidate
    return first_candidate  # kshaya tithi: the day on which it begins


def find_month_start_day(
    year: int,
    target_month_index: int,
    tithi: int,
    window: Tuple[Tuple[int, int], Tuple[int, int]],
    latitude: float,
    longitude: float,
    month_label: str,
) -> date:
    """Locate a tithi of a named *nija* lunar month within a calendar year.

    Every lunation overlapping ``window`` is examined by index, rather than
    sampling a few candidate dates: sampling can step straight over a short
    month, which silently loses the target in some years.

    Args:
        year (int): Gregorian year to search.
        target_month_index (int): Index into :data:`~constants.LUNAR_MONTHS`.
        tithi (int): Tithi number sought within that month.
        window (Tuple[Tuple[int, int], Tuple[int, int]]):
            ``((start_month, start_day), (end_month, end_day))`` bounds.
        latitude (float): Observer latitude.
        longitude (float): Observer longitude.
        month_label (str): Month name, used only in the error message.

    Raises:
        OdiaCalendarError: if the month does not fall inside the window.

    Returns:
        date: The civil date carrying that tithi.
    """
    (start_month, start_day), (end_month, end_day) = window
    first_lunation = lunation_containing(date_to_jd(date(year, start_month, start_day)))
    last_lunation = lunation_containing(date_to_jd(date(year, end_month, end_day))) + 1

    for lunation in range(first_lunation, last_lunation + 1):
        month_index, is_adhika = amanta_month_of_lunation(lunation)
        # An adhika month is a repetition inserted before the true (nija)
        # month; observances always fall in the nija one.
        if month_index != target_month_index or is_adhika:
            continue
        return civil_day_bearing_tithi(
            new_moon_jd(lunation), tithi, latitude, longitude
        )

    raise OdiaCalendarError(f"could not locate {month_label} for {year}")
