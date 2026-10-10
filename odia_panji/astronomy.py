"""Positional astronomy: Sun, Moon, ayanamsa and sunrise.

Sun and Moon follow Meeus (*Astronomical Algorithms*, ch. 25 and 47);
sunrise follows the NOAA algorithm (accuracy ~1 minute); sankranti
instants are found by bisection on the sidereal solar longitude.  Series
coefficients are kept inline in the formulas they belong to.
"""

from __future__ import annotations

import math
from datetime import date

from .constants import (
    ARCSECONDS_PER_DEGREE,
    DEGREES_PER_RASHI,
    DAYS_PER_JULIAN_YEAR,
    FULL_CIRCLE_DEGREES,
    J2000_JD,
    MINUTES_PER_DAY,
    MINUTES_PER_DEGREE,
    MOON_LONGITUDE_TERMS,
    MOON_TERM_SCALE,
    PURI_LAT,
    PURI_LON,
    _EARTH_ECCENTRICITY,
    _SANKRANTI_LOOKBACK_DAYS,
    _SUNRISE_ITERATIONS,
    _SUNRISE_ZENITH_DEGREES,
)
from .julian_day import date_to_jd, julian_centuries_since_j2000
from .math_helpers import find_angle_crossing, normalize_degrees
from .validation import validate_observer

__all__ = [
    "sun_longitude",
    "moon_longitude",
    "ayanamsa",
    "sidereal_sun_longitude",
    "sunrise_jd",
    "solar_ingress_jd",
]


# --------------------------------------------------------------------------
# Solar longitude (Meeus, ch. 25) - apparent, tropical
# --------------------------------------------------------------------------


def sun_longitude(jd: float) -> float:
    """Return the apparent geocentric *tropical* longitude of the Sun, in degrees.

    Args:
        jd (float): Julian Day (UT).

    Returns:
        float: Longitude in [0, 360).
    """
    centuries = julian_centuries_since_j2000(jd)

    geometric_mean_longitude = (
        280.46646 + 36000.76983 * centuries + 0.0003032 * centuries**2
    )
    mean_anomaly = 357.52911 + 35999.05029 * centuries - 0.0001537 * centuries**2
    mean_anomaly_rad = math.radians(mean_anomaly)

    # Equation of the centre: the correction from the mean (uniform) motion
    # to the true motion on the eccentric orbit.
    equation_of_centre = (
        (1.914602 - 0.004817 * centuries - 0.000014 * centuries**2)
        * math.sin(mean_anomaly_rad)
        + (0.019993 - 0.000101 * centuries) * math.sin(2 * mean_anomaly_rad)
        + 0.000289 * math.sin(3 * mean_anomaly_rad)
    )
    true_longitude = geometric_mean_longitude + equation_of_centre

    # Convert true -> apparent: subtract the constant aberration term and the
    # nutation contribution driven by the Moon's ascending node.
    moon_ascending_node = 125.04 - 1934.136 * centuries
    apparent_longitude = (
        true_longitude - 0.00569 - 0.00478 * math.sin(math.radians(moon_ascending_node))
    )
    return normalize_degrees(apparent_longitude)


# --------------------------------------------------------------------------
# Lunar longitude (Meeus, ch. 47, table 47.A - all 60 terms)
# --------------------------------------------------------------------------


def moon_longitude(jd: float) -> float:
    """Return the apparent geocentric *tropical* longitude of the Moon, in degrees.

    Args:
        jd (float): Julian Day (UT).

    Returns:
        float: Longitude in [0, 360).
    """
    centuries = julian_centuries_since_j2000(jd)

    mean_longitude = normalize_degrees(
        218.3164477
        + 481267.88123421 * centuries
        - 0.0015786 * centuries**2
        + centuries**3 / 538841.0
        - centuries**4 / 65194000.0
    )
    mean_elongation = normalize_degrees(
        297.8501921
        + 445267.1114034 * centuries
        - 0.0018819 * centuries**2
        + centuries**3 / 545868.0
        - centuries**4 / 113065000.0
    )

    sun_mean_anomaly = normalize_degrees(
        357.5291092
        + 35999.0502909 * centuries
        - 0.0001536 * centuries**2
        + centuries**3 / 24490000.0
    )
    moon_mean_anomaly = normalize_degrees(
        134.9633964
        + 477198.8675055 * centuries
        + 0.0087414 * centuries**2
        + centuries**3 / 69699.0
        - centuries**4 / 14712000.0
    )

    argument_of_latitude = normalize_degrees(
        93.2720950
        + 483202.0175233 * centuries
        - 0.0036539 * centuries**2
        - centuries**3 / 3526000.0
        + centuries**4 / 863310000.0
    )

    venus_term_argument = normalize_degrees(119.75 + 131.849 * centuries)
    jupiter_term_argument = normalize_degrees(53.09 + 479264.290 * centuries)

    # Terms involving the Sun's anomaly are scaled by the slowly varying
    # eccentricity of Earth's orbit (Meeus' E factor).
    eccentricity_factor = 1 - 0.002516 * centuries - 0.0000074 * centuries**2

    periodic_sum = 0.0
    for (
        elongation_multiple,
        sun_anomaly_multiple,
        moon_anomaly_multiple,
        latitude_multiple,
        coefficient,
    ) in MOON_LONGITUDE_TERMS:
        argument = math.radians(
            elongation_multiple * mean_elongation
            + sun_anomaly_multiple * sun_mean_anomaly
            + moon_anomaly_multiple * moon_mean_anomaly
            + latitude_multiple * argument_of_latitude
        )
        term = coefficient * math.sin(argument)
        if abs(sun_anomaly_multiple) == 1:
            term *= eccentricity_factor
        elif abs(sun_anomaly_multiple) == 2:
            term *= eccentricity_factor**2
        periodic_sum += term

    # Additive corrections for Venus, Jupiter and the flattening of the Earth.
    periodic_sum += 3958 * math.sin(math.radians(venus_term_argument))
    periodic_sum += 1962 * math.sin(math.radians(mean_longitude - argument_of_latitude))
    periodic_sum += 318 * math.sin(math.radians(jupiter_term_argument))

    # Nutation in longitude (dominant terms only) converts true to apparent.
    moon_ascending_node = normalize_degrees(125.04452 - 1934.136261 * centuries)
    nutation_degrees = (
        -17.20 * math.sin(math.radians(moon_ascending_node))
        - 1.32 * math.sin(math.radians(2 * mean_longitude))
    ) / ARCSECONDS_PER_DEGREE

    return normalize_degrees(
        mean_longitude + periodic_sum / MOON_TERM_SCALE + nutation_degrees
    )


def ayanamsa(jd: float) -> float:
    """Return the Lahiri (Chitrapaksha) ayanamsa in degrees.

    This is a linear approximation, exact enough near J2000 but drifting
    outside roughly 1800-2100.  It is the dominant accuracy limit of this
    module; see the module docstring.
    """
    return 23.85300 + 0.0139700 * (jd - J2000_JD) / DAYS_PER_JULIAN_YEAR


def sidereal_sun_longitude(jd: float) -> float:
    """Return the sidereal (Lahiri) longitude of the Sun; 0 deg = start of Mesha."""
    return normalize_degrees(sun_longitude(jd) - ayanamsa(jd))


# --------------------------------------------------------------------------
# Sunrise (NOAA algorithm, accuracy ~1 minute)
# --------------------------------------------------------------------------


def sunrise_jd(
    calendar_date: date, latitude: float = PURI_LAT, longitude: float = PURI_LON
) -> float:
    """Return the Julian Day (UT) of sunrise on ``calendar_date`` at the given location.

    Args:
        calendar_date (date): Gregorian date.
        latitude (float, optional): Observer latitude in degrees, north
            positive. Defaults to PURI_LAT.
        longitude (float, optional): Observer longitude in degrees, east
            positive. Defaults to PURI_LON.

    Returns:
        float: Julian Day (UT) of sunrise.

    Raises:
        OdiaCalendarError: if the coordinates are outside valid ranges.

    Note:
        At polar latitudes the Sun may not rise or set at all on the given
        date.  The hour-angle cosine is clamped in that case, which yields a
        nominal time rather than an error; results there are meaningless but
        the default Puri location is never affected.
    """
    validate_observer(latitude, longitude)

    # Start from approximate local noon and iterate: the Sun's position is
    # needed to find sunrise, but depends on the time of sunrise itself.
    jd = date_to_jd(calendar_date) + 0.5 - longitude / FULL_CIRCLE_DEGREES
    for _ in range(_SUNRISE_ITERATIONS):
        centuries = julian_centuries_since_j2000(jd)
        apparent_longitude_rad = math.radians(sun_longitude(jd))
        obliquity_rad = math.radians(23.439291 - 0.0130042 * centuries)
        declination = math.asin(
            math.sin(obliquity_rad) * math.sin(apparent_longitude_rad)
        )

        mean_longitude_rad = math.radians(
            normalize_degrees(280.46646 + 36000.76983 * centuries)
        )
        mean_anomaly_rad = math.radians(
            normalize_degrees(357.52911 + 35999.05029 * centuries)
        )
        obliquity_factor = math.tan(obliquity_rad / 2) ** 2

        equation_of_time_minutes = MINUTES_PER_DEGREE * math.degrees(
            obliquity_factor * math.sin(2 * mean_longitude_rad)
            - 2 * _EARTH_ECCENTRICITY * math.sin(mean_anomaly_rad)
            + 4
            * _EARTH_ECCENTRICITY
            * obliquity_factor
            * math.sin(mean_anomaly_rad)
            * math.cos(2 * mean_longitude_rad)
            - 0.5 * obliquity_factor**2 * math.sin(4 * mean_longitude_rad)
            - 1.25 * _EARTH_ECCENTRICITY**2 * math.sin(2 * mean_anomaly_rad)
        )

        latitude_rad = math.radians(latitude)
        hour_angle_cosine = (
            math.cos(math.radians(_SUNRISE_ZENITH_DEGREES))
            - math.sin(latitude_rad) * math.sin(declination)
        ) / (math.cos(latitude_rad) * math.cos(declination))
        # Clamped for polar day/night, where no solution exists (see Note).
        hour_angle = math.degrees(math.acos(max(-1.0, min(1.0, hour_angle_cosine))))

        solar_noon_minutes = MINUTES_PER_DAY / 2
        minutes_ut = (
            solar_noon_minutes
            - MINUTES_PER_DEGREE * (longitude + hour_angle)
            - equation_of_time_minutes
        )
        jd = date_to_jd(calendar_date) + minutes_ut / MINUTES_PER_DAY
    return jd


# --------------------------------------------------------------------------
# Sankranti (solar ingress)
# --------------------------------------------------------------------------


def solar_ingress_jd(rashi_index: int, jd_end: float) -> float:
    """Return the instant the Sun entered sidereal sign ``rashi_index``.

    Args:
        rashi_index (int): Target sign, 0 = Mesha.
        jd_end (float): Search backwards from this instant.

    Returns:
        float: The Julian Day of the sankranti.
    """
    return find_angle_crossing(
        sidereal_sun_longitude,
        rashi_index * DEGREES_PER_RASHI,
        jd_end - _SANKRANTI_LOOKBACK_DAYS,
        jd_end,
    )
