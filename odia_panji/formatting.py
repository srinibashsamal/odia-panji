"""Human-readable output built on :func:`~odia_panji.odia_calendar.convert`.

Nothing here does calendar arithmetic; every function formats the
result of :func:`convert` for display or citation.
"""

from __future__ import annotations

from datetime import date
from typing import get_args

from .calendar_types import DateLike, HistoricalStyle, OdiaCalendarError
from .odia_calendar import convert
from .validation import validate_supported_date

__all__ = ["format_odia_date", "format_historical"]


def format_odia_date(date_like: DateLike, inclusive_end: bool = False) -> str:
    """Return a one-line human-readable summary of :func:`convert`."""
    converted = convert(date_like, inclusive_end)

    adhika_prefix = "Adhika " if converted["adhika"] else ""
    return (
        f"{converted['english_date']}  ->  {converted['utkalabda']} Utkalabda | "
        f"{converted['anka']} Anka ({converted['gajapati']}) | "
        f"Acce: {converted['years_since_accession']} | "
        f"{adhika_prefix}{converted['lunar_month']} {converted['paksha']} "
        f"{converted['tithi']} | "
        f"{converted['solar_day']} {converted['solar_month']} | "
        f"Sunia: {converted['sunia_of_year']} | Shakabda: {converted['shakabda']}"
    )


def _english_long_date(calendar_date: date) -> str:
    """Return e.g. ``"7 October 2026"`` (``%-d`` is not supported on Windows)."""
    return f"{calendar_date.day} {calendar_date.strftime('%B %Y')}"


def format_historical(
    date_like: DateLike,
    *,
    inclusive_end: bool = False,
    style: HistoricalStyle = "full",
    include_english: bool = True,
) -> str:
    """Return a scholar-friendly citation string for a Gregorian date.

    Designed for historical and archival use, such as land grants,
    palm-leaf records and Madala Panji style citations.

    Args:
        date_like (DateLike): ``"dd-mm-yyyy"``, ``date`` or ``datetime``.
        inclusive_end (bool, optional): See
            :func:`~odia_panji.odia_calendar.gajapati_reign`.
        style (HistoricalStyle, optional): ``"full"`` (two lines, default),
            ``"compact"`` (one line), ``"lunar"`` or ``"solar"`` (Odia date
            first, English date below).
        include_english (bool, optional): Include the Gregorian date.
            Defaults to ``True``.

    Returns:
        str: The formatted citation, suitable for footnotes, captions or
        bibliographic entries.

    Raises:
        OdiaCalendarError: if the date is unsupported, precedes the earliest
            known reign, or ``style`` is unknown.

    Examples:
        >>> print(format_historical("07-10-2026"))
        7 October 2026 = 1434 Utkalabda, Anka 71 of Divyasingha Deva IV
        Aswina Krushna Dwadasi | 21 Kanya | Shakabda 1948

        >>> print(format_historical("15-08-1947", style="solar"))
        31 Karkata, 1354 Utkalabda (Anka 25 of Ramachandra Deba IV)
        = 15 August 1947
    """
    valid_styles = get_args(HistoricalStyle)
    if style not in valid_styles:
        raise OdiaCalendarError(
            f"unknown style {style!r}; expected one of {', '.join(valid_styles)}"
        )

    parsed = validate_supported_date(date_like)
    converted = convert(parsed, inclusive_end)

    english = _english_long_date(parsed) if include_english else ""

    adhika_prefix = "Adhika " if converted["adhika"] else ""
    lunar = (
        f"{adhika_prefix}{converted['lunar_month']} "
        f"{converted['paksha']} {converted['tithi']}"
    )
    solar = f"{converted['solar_day']} {converted['solar_month']}"
    anka = f"Anka {converted['anka']} of {converted['gajapati']}"
    utkalabda = f"{converted['utkalabda']} Utkalabda"
    shakabda = f"Shakabda {converted['shakabda']}"

    if style == "full":
        first_line = f"{utkalabda}, {anka}"
        if english:
            first_line = f"{english} = {first_line}"
        return f"{first_line}\n{lunar} | {solar} | {shakabda}"

    if style == "compact":
        parts = [english, utkalabda, anka, lunar, solar]
        return " / ".join(part for part in parts if part)

    odia_date = lunar if style == "lunar" else solar
    head = f"{odia_date}, {utkalabda} ({anka})"
    return f"{head}\n= {english}" if english else head
