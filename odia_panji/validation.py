"""Input parsing and validation helpers shared by the calendar modules."""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict

from .calendar_types import DateLike, OdiaCalendarError
from .constants import (
    DATE_SEPARATORS,
    LATITUDE_RANGE,
    LONGITUDE_RANGE,
    MAX_SUPPORTED_YEAR,
    MIN_SUPPORTED_YEAR,
    _INPUT_DATE_FORMAT,
)

__all__ = [
    "parse_date",
    "validate_int",
    "validate_year",
    "validate_supported_date",
    "validate_observer",
    "lookup_name",
]


def parse_date(date_like: DateLike) -> date:
    """Convert the input to a :class:`datetime.date`.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"`` (``/`` and ``.`` separators are
            accepted too), or an existing ``date`` / ``datetime``.

    Raises:
        OdiaCalendarError: if a string does not match ``dd-mm-yyyy``, or the
            date_like is of an unsupported type.

    Returns:
        date: The corresponding ``date``.

    Examples:
        >>> parse_date("23-09-2026")
        datetime.date(2026, 9, 23)
        >>> parse_date("23/09/2026")
        datetime.date(2026, 9, 23)
    """
    # datetime must be tested first: datetime is a subclass of date, so the
    # isinstance(date_like, date) branch would otherwise swallow it and return
    # the datetime itself rather than its date part.
    if isinstance(date_like, datetime):
        return date_like.date()
    if isinstance(date_like, date):
        return date_like
    if not isinstance(date_like, str):
        raise OdiaCalendarError(
            f"expected a str, date or datetime, got {type(date_like).__name__}"
        )
    normalised = date_like.strip()
    for separator in DATE_SEPARATORS:
        normalised = normalised.replace(separator, "-")
    try:
        return datetime.strptime(normalised, _INPUT_DATE_FORMAT).date()
    except ValueError as exc:
        raise OdiaCalendarError(
            f"could not parse {date_like!r} as a date; expected dd-mm-yyyy"
        ) from exc


def validate_int(value: int, label: str) -> int:
    """Return ``value`` if it is a genuine ``int`` (``bool`` is rejected).

    Raises:
        OdiaCalendarError: naming ``label`` if ``value`` is not an int.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise OdiaCalendarError(f"{label} must be an int, got {type(value).__name__}")
    return value


def validate_year(year: int, maximum: int = MAX_SUPPORTED_YEAR) -> int:
    """Return ``year`` if it is inside the supported range.

    Validating up front turns an obscure failure deep in the lunation search
    into an immediate, explicit error naming the supported range.

    Args:
        year (int): Gregorian year to check.
        maximum (int, optional): Highest acceptable year. Defaults to
            :data:`~constants.MAX_SUPPORTED_YEAR`.

    Raises:
        OdiaCalendarError: if ``year`` is outside the supported range.
    """
    validate_int(year, "year")
    if not MIN_SUPPORTED_YEAR <= year <= maximum:
        raise OdiaCalendarError(
            f"year {year} is outside the supported range "
            f"{MIN_SUPPORTED_YEAR}-{maximum}"
        )
    return year


def validate_supported_date(date_like: DateLike) -> date:
    """Parse ``date_like`` and confirm its year is supported."""
    parsed = parse_date(date_like)
    validate_year(parsed.year)
    return parsed


def validate_observer(latitude: float, longitude: float) -> None:
    """Reject observer coordinates outside the valid geographic ranges."""
    min_latitude, max_latitude = LATITUDE_RANGE
    min_longitude, max_longitude = LONGITUDE_RANGE
    if not min_latitude <= latitude <= max_latitude:
        raise OdiaCalendarError(
            f"latitude {latitude} is outside {min_latitude:g}..{max_latitude:g}"
        )
    if not min_longitude <= longitude <= max_longitude:
        raise OdiaCalendarError(
            f"longitude {longitude} is outside {min_longitude:g}..{max_longitude:g}"
        )


def lookup_name(raw: str, table: Dict[str, str], label: str) -> str:
    """Case-insensitive lookup of ``raw`` in ``table``, or a clear error.

    Args:
        raw (str): Name supplied by the caller.
        table (Dict[str, str]): Lower-cased name -> canonical name.
        label (str): What is being looked up, used in the error message.

    Raises:
        OdiaCalendarError: if ``raw`` is not a key of ``table``.
    """
    try:
        return table[raw.strip().lower()]
    except KeyError:
        valid = ", ".join(sorted(table.values()))
        raise OdiaCalendarError(
            f"unknown {label} {raw!r}; expected one of {valid}"
        ) from None
