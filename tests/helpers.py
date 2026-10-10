"""Shared test helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterator


def daterange(start: date, end: date, step: int = 1) -> Iterator[date]:
    """Yield dates from ``start`` to ``end`` inclusive, ``step`` days apart."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=step)
