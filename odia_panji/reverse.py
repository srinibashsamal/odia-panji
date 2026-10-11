"""One entry point for every Odia -> English conversion.

:func:`to_english` is the reverse counterpart of
:func:`~odia_panji.odia_calendar.convert`.  It takes an Odia date in any
supported form and dispatches to the specialised functions in
:mod:`odia_panji.odia_to_english` and :mod:`odia_panji.anka_to_english`:

==========================  =========================================
Year given as               Date given as
==========================  =========================================
``utkalabda=``              solar (``month``, ``day``)
``utkalabda=``              lunar (``month``, ``paksha=``, ``tithi=``)
``anka=`` (+ ``gajapati=``) solar (``month``, ``day``)
``anka=`` (+ ``gajapati=``) lunar (``month``, ``paksha=``, ``tithi=``)
==========================  =========================================
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from .anka_to_english import english_date_from_anka_lunar, english_date_from_anka_solar
from .calendar_types import OdiaCalendarError
from .odia_to_english import english_date_from_lunar, english_date_from_solar

__all__ = ["to_english"]


def _check_arguments(
    day: Optional[int],
    paksha: Optional[str],
    tithi: Optional[str],
    adhika: bool,
    utkalabda: Optional[int],
    anka: Optional[int],
    gajapati: Optional[str],
    inclusive_end: bool,
) -> None:
    """Reject missing, conflicting or meaningless argument combinations."""
    if (utkalabda is None) == (anka is None):
        raise OdiaCalendarError("give exactly one of utkalabda= or anka=")

    is_solar = day is not None
    is_lunar = paksha is not None or tithi is not None
    if is_solar == is_lunar:
        raise OdiaCalendarError(
            "give either a solar day, or a lunar paksha= and tithi=, not both"
        )
    if is_lunar and (paksha is None or tithi is None):
        raise OdiaCalendarError("a lunar date needs both paksha= and tithi=")
    if is_solar and adhika:
        raise OdiaCalendarError("adhika= applies only to lunar dates")
    if utkalabda is not None and (gajapati is not None or inclusive_end):
        raise OdiaCalendarError(
            "gajapati= and inclusive_end= apply only together with anka="
        )


def to_english(
    month: str,
    day: Optional[int] = None,
    *,
    paksha: Optional[str] = None,
    tithi: Optional[str] = None,
    adhika: bool = False,
    utkalabda: Optional[int] = None,
    anka: Optional[int] = None,
    gajapati: Optional[str] = None,
    inclusive_end: bool = False,
) -> date:
    """Convert an Odia date to its English (Gregorian) date.

    Give the year as **either** ``utkalabda`` **or** ``anka``, and the date
    as **either** a solar ``month`` + ``day`` **or** a lunar ``month`` +
    ``paksha`` + ``tithi``.

    Args:
        month (str): Solar month (rashi, e.g. ``"Kanya"``) for a solar date,
            or Purnimanta lunar month (e.g. ``"Aswina"``) for a lunar date.
            Case-insensitive.
        day (int, optional): Day of the solar month (Sankranti = day 1).
            Give this for a solar date only.
        paksha (str, optional): ``"Shukla"`` or ``"Krushna"``, lunar only.
        tithi (str, optional): Tithi name, or ``"Purnima"`` / ``"Amabasya"``,
            lunar only.
        adhika (bool, optional): ``True`` for an intercalary lunar month.
        utkalabda (int, optional): Utkalabda year.
        anka (int, optional): Anka (regnal) year.
        gajapati (str, optional): Reigning Gajapati for ``anka``; defaults to
            the current reign.
        inclusive_end (bool, optional): Handover-day rule for ``anka``; see
            :func:`~odia_panji.odia_calendar.gajapati_reign`.

    Returns:
        date: The matching English date.  Pass it to
        :func:`~odia_panji.odia_calendar.convert` for the full Odia details.

    Raises:
        OdiaCalendarError: for a missing or conflicting argument, an unknown
            name, no matching day, or an ambiguous match.

    Examples:
        >>> to_english("Kanya", 21, utkalabda=1434)
        datetime.date(2026, 10, 7)
        >>> to_english("Aswina", paksha="Krushna", tithi="Dwadasi", utkalabda=1434)
        datetime.date(2026, 10, 7)
        >>> to_english("Kanya", 21, anka=71)
        datetime.date(2026, 10, 7)
        >>> to_english("Karkata", 31, anka=25, gajapati="Ramachandra Deba IV")
        datetime.date(1947, 8, 15)
    """
    _check_arguments(
        day, paksha, tithi, adhika, utkalabda, anka, gajapati, inclusive_end
    )

    if utkalabda is not None:
        if day is not None:
            return english_date_from_solar(utkalabda, month, day)
        assert paksha is not None and tithi is not None
        return english_date_from_lunar(utkalabda, month, paksha, tithi, adhika)

    assert anka is not None
    if day is not None:
        return english_date_from_anka_solar(anka, month, day, gajapati, inclusive_end)
    assert paksha is not None and tithi is not None
    return english_date_from_anka_lunar(
        anka, month, paksha, tithi, adhika, gajapati, inclusive_end
    )
