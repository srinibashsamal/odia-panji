"""Anka numbering: which numbers are valid Anka years and their order.

Valid Anka numbers skip 1, every number ending in 6, and every number
ending in 0 except 10::

    2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, ...

These helpers are pure arithmetic; mapping a *date* to an Anka year
(which needs Sunia and the reign table) lives in :mod:`odia_calendar`.
"""

from __future__ import annotations

from calendar_types import OdiaCalendarError
from constants import ANKA_ALLOWED_EXCEPTIONS, ANKA_SKIPPED_LAST_DIGITS, MIN_ANKA

__all__ = ["is_valid_anka", "anka_from_index", "index_from_anka"]


def is_valid_anka(number: int) -> bool:
    """Return whether ``number`` can occur as an Anka year.

    Skipped by the Anka rules: 1 and anything below it, every number ending
    in 6, and every number ending in 0 except 10.

    Examples:
        >>> [n for n in range(1, 22) if is_valid_anka(n)]
        [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21]
    """
    if number < MIN_ANKA:
        return False
    if number in ANKA_ALLOWED_EXCEPTIONS:
        return True
    return number % 10 not in ANKA_SKIPPED_LAST_DIGITS


def anka_from_index(index: int) -> int:
    """Map a 1-based counting index to its Anka number.

    Args:
        index (int): Position in the sequence of valid Anka numbers.

    Raises:
        OdiaCalendarError: if ``index`` is below 1.

    Returns:
        int: The Anka number at that position.

    Examples:
        >>> [anka_from_index(i) for i in range(1, 9)]
        [2, 3, 4, 5, 7, 8, 9, 10]
    """
    if index < 1:
        raise OdiaCalendarError(f"index must be >= 1, got {index}")
    valid_seen = 0
    candidate = MIN_ANKA - 1
    while True:
        candidate += 1
        if is_valid_anka(candidate):
            valid_seen += 1
            if valid_seen == index:
                return candidate


def index_from_anka(anka: int) -> int:
    """Return the 1-based counting index of an Anka number.

    Inverse of :func:`anka_from_index`.

    Raises:
        OdiaCalendarError: if ``anka`` is not a valid Anka number.

    Examples:
        >>> index_from_anka(71)
        57
    """
    if not is_valid_anka(anka):
        raise OdiaCalendarError(f"{anka} is not a valid Anka year")
    return sum(1 for number in range(MIN_ANKA, anka + 1) if is_valid_anka(number))
