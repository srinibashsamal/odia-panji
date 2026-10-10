# Changelog

All notable changes to this project are documented here.
The project follows [Semantic Versioning](https://semver.org/):
`MAJOR.MINOR.PATCH`. Until 1.0.0, minor releases may change the public API.

## [Unreleased]

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
