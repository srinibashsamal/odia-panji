# Changelog

All notable changes to this project are documented here.
The project follows [Semantic Versioning](https://semver.org/):
`MAJOR.MINOR.PATCH`. Until 1.0.0, minor releases may change the public API.

## [Unreleased]

## [0.2.0] - 2026-10-11

### Added

- `to_english()`: single entry point for Odia -> English, the reverse of
  `convert()`. Accepts an Utkalabda or Anka year with a solar or lunar date.
- `format_historical()`: scholar-friendly formatter for historical and
  archival use, with four output styles (`full`, `compact`, `lunar`, `solar`).
- `HistoricalStyle` type for the `style` argument of `format_historical()`.

### Changed

- `format_odia_date` moved to `odia_panji.formatting`; import it from
  `odia_panji` directly.

## [0.1.0] - 2026-10-10

### Added

- Installable `odia_panji` package with `pyproject.toml`.
- Public API re-exported from the package root (`from odia_panji import convert`).
- `english_to_odia()` alias of `convert()`.
- `odia-panji` command and `python -m odia_panji` (replaces `call.py`).
- `py.typed` marker, so type checkers use the library's annotations.
- Test suite under `tests/` and docstring examples run by pytest.
- `examples/` folder and GitHub Actions CI.

### Changed

- Modules moved into the `odia_panji/` package and use relative imports.
- Demo `_main()` blocks removed from library modules; use the CLI instead.
- Minimum Python version is now 3.9.
