"""The public API: package exports and version."""

from __future__ import annotations

import re

import odia_panji


def test_version_is_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", odia_panji.__version__)


def test_every_name_in_all_is_importable() -> None:
    for name in odia_panji.__all__:
        assert hasattr(odia_panji, name), name


def test_english_to_odia_is_convert() -> None:
    assert odia_panji.english_to_odia("07-10-2026") == odia_panji.convert("07-10-2026")


def test_error_is_a_value_error() -> None:
    assert issubclass(odia_panji.OdiaCalendarError, ValueError)
