"""Odia Panji: convert between Gregorian dates and the Odia calendar.

Quick start::

    >>> from odia_panji import convert, english_date_from_solar
    >>> convert("23-09-2026")["utkalabda"]
    1434
    >>> english_date_from_solar(1434, "Kanya", 21)
    datetime.date(2026, 10, 7)

Everything listed in ``__all__`` is importable directly from
``odia_panji``; the submodules remain available for less common helpers.
"""

from __future__ import annotations

from .anka import anka_from_index, index_from_anka, is_valid_anka
from .anka_to_english import (
    anka_year_span,
    english_date_from_anka_lunar,
    english_date_from_anka_solar,
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
    CHAITRA_OVERRIDES,
    GAJAPATI_REIGNS,
    MAX_SUPPORTED_YEAR,
    MIN_SUPPORTED_YEAR,
    SUNIA_OVERRIDES,
)
from .odia_calendar import (
    anka_index,
    anka_year,
    convert,
    english_to_odia,
    format_odia_date,
    gajapati_accession,
    gajapati_reign,
    lunar_date,
    odia_solar_date,
    odia_year_start,
    shaka_new_year,
    shaka_year,
    sunia_date,
    to_odia_numerals,
    utkalabda_year,
    years_since_accession,
)
from .odia_to_english import english_date_from_lunar, english_date_from_solar
from .validation import parse_date

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # types and errors
    "DateLike",
    "LunarDate",
    "OdiaCalendarError",
    "OdiaConversion",
    "Reign",
    "SolarDate",
    # configuration tables
    "CHAITRA_OVERRIDES",
    "GAJAPATI_REIGNS",
    "MAX_SUPPORTED_YEAR",
    "MIN_SUPPORTED_YEAR",
    "SUNIA_OVERRIDES",
    # English -> Odia
    "convert",
    "english_to_odia",
    "format_odia_date",
    "utkalabda_year",
    "shaka_year",
    "anka_year",
    "anka_index",
    "years_since_accession",
    "lunar_date",
    "odia_solar_date",
    "odia_year_start",
    "sunia_date",
    "shaka_new_year",
    "gajapati_reign",
    "gajapati_accession",
    "to_odia_numerals",
    "parse_date",
    # Odia -> English
    "english_date_from_solar",
    "english_date_from_lunar",
    "english_date_from_anka_solar",
    "english_date_from_anka_lunar",
    "anka_year_span",
    # Anka numbering
    "is_valid_anka",
    "anka_from_index",
    "index_from_anka",
]
