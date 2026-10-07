"""Angle arithmetic and root finding shared by the astronomy modules."""

from __future__ import annotations

from typing import Callable

from constants import (
    FULL_CIRCLE_DEGREES,
    HALF_CIRCLE_DEGREES,
    _BISECTION_STEPS,
    _BISECTION_TOLERANCE_DAYS,
)

__all__ = ["normalize_degrees", "signed_angle_difference", "find_angle_crossing"]


def normalize_degrees(angle: float) -> float:
    """Normalise an angle to the half-open interval [0, 360)."""
    return angle % FULL_CIRCLE_DEGREES


def signed_angle_difference(angle: float, target: float) -> float:
    """Return ``angle - target`` wrapped into [-180, 180).

    Wrapping keeps the 0/360 deg discontinuity from masquerading as a sign
    change, which would otherwise derail a bisection.
    """
    return (
        (angle - target + HALF_CIRCLE_DEGREES) % FULL_CIRCLE_DEGREES
    ) - HALF_CIRCLE_DEGREES


def find_angle_crossing(
    angle_at: Callable[[float], float],
    target_degrees: float,
    jd_low: float,
    jd_high: float,
) -> float:
    """Find the instant in ``[jd_low, jd_high]`` where ``angle_at`` hits a target.

    Args:
        angle_at (Callable[[float], float]): Angle (degrees) as a function of
            Julian Day; must increase through the target inside the bracket.
        target_degrees (float): Angle to solve for.
        jd_low (float): Start of the bracket; must precede the crossing.
        jd_high (float): End of the bracket; must follow the crossing.

    Returns:
        float: The Julian Day of the crossing.
    """

    def residual(jd: float) -> float:
        return signed_angle_difference(angle_at(jd), target_degrees)

    low, high = jd_low, jd_high
    residual_at_low = residual(low)
    for _ in range(_BISECTION_STEPS):
        midpoint = (low + high) / 2.0
        residual_at_mid = residual(midpoint)
        if residual_at_low * residual_at_mid <= 0:
            high = midpoint
        else:
            low, residual_at_low = midpoint, residual_at_mid
        if high - low < _BISECTION_TOLERANCE_DAYS:
            break
    return (low + high) / 2.0
