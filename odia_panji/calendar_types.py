"""Shared types for the Odia calendar package.

Holds the input type alias, the package exception and the existing
record types, so every helper module can import them without pulling in
the full :mod:`odia_calendar` API (which would create import cycles).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, NamedTuple, TypedDict, Union

__all__ = [
    "DateLike",
    "HistoricalStyle",
    "OdiaCalendarError",
    "Reign",
    "LunarDate",
    "SolarDate",
    "OdiaConversion",
]

DateLike = Union[str, date, datetime]
"""Anything accepted as an input date: ``"dd-mm-yyyy"``, ``date`` or ``datetime``."""

HistoricalStyle = Literal["full", "compact", "lunar", "solar"]
"""Layouts accepted by :func:`~odia_calendar.format_historical`."""


class OdiaCalendarError(ValueError):
    """Raised for unsupported dates or malformed calendar arguments.

    Subclasses :class:`ValueError` deliberately: callers that already guard
    these functions with ``except ValueError`` keep working unchanged, while
    callers that want to distinguish calendar problems from generic value
    errors now can.
    """


class Reign(NamedTuple):
    """One monarch's reign, for resolving the Anka regnal count.

    Attributes:
        name: Regnal name of the Gajapati.
        accession: Date the monarch acceded.  The Anka count restarts here.
        predecessor_died_same_day: ``True`` when the previous Gajapati died
            on this very date, so the throne passed the same day and the two
            reigns share a calendar day.  Which monarch that shared day is
            credited to is then a caller's choice -- see the
            ``inclusive_end`` argument of
            :func:`~odia_calendar.gajapati_reign`.  ``False`` means the
            accession followed a gap (abdication, interregnum, or simply an
            unrecorded handover), so the date is unambiguous.
    """

    name: str
    accession: date
    predecessor_died_same_day: bool = False


class LunarDate(NamedTuple):
    """A Purnimanta lunar date as it appears in an Odia panji.

    Attributes:
        month: Name of the lunar month (e.g. ``"Bhadraba"``).
        paksha: ``"Shukla"`` (bright / waxing) or ``"Krushna"`` (dark / waning).
        tithi: Name of the lunar day (e.g. ``"Dwadasi"``, ``"Purnima"``).
        adhika: ``True`` when the month is an intercalary (extra) month.
    """

    month: str
    paksha: str
    tithi: str
    adhika: bool


class SolarDate(NamedTuple):
    """An Odia solar date, as printed in a panji or palm-leaf horoscope.

    Attributes:
        rashi: Sidereal sign the Sun occupies (e.g. ``"Simha"``).
        month: Solar month name.  Identical to :attr:`rashi` by definition,
            since Odia solar months take the name of the sign; kept as a
            separate field so the tuple stays readable at call sites.
        day: Day number within the solar month, counting the Sankranti day
            as day 1.
        lunar_equivalent: Lunar month name almanacs pair with this solar
            month (e.g. ``"Bhadraba"`` for Simha), as in "1 Baisakha (Mesa)".
    """

    rashi: str
    month: str
    day: int
    lunar_equivalent: str


class OdiaConversion(TypedDict):
    """Return type of :func:`~odia_calendar.convert`."""

    english_date: str
    utkalabda: int
    utkalabda_odia: str
    gajapati: str
    gajapati_accession: str
    is_accession_day: bool
    anka: int
    anka_odia: str
    anka_index: int
    years_since_accession: int
    odia_year_start: str
    odia_year_end: str
    sunia_of_year: str
    lunar_month: str
    adhika: bool
    paksha: str
    tithi: str
    solar_rashi: str
    solar_month: str
    solar_day: int
    solar_month_lunar_equivalent: str
    shakabda: int
