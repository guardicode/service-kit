# Changelog
All notable changes to this project will be documented in this
file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
the [PEP 440 version scheme](https://peps.python.org/pep-0440/#version-scheme).


## [Unreleased]
### Added
### Changed
### Deprecated
### Fixed
- A bug in pydantic(https://github.com/pydantic/pydantic/issues/9139) causes
  `SecretString` to still be logged plaintext in case of a validation error.
  This bug is circumvented by hiding all input in validation errors by default.

### Removed
### Security


## [2.4.0] - 2026-08-19
### Added
- `extra` parameter to `api.bootstrap_logging()`.

### Changed
- Logging of the `ServiceConfiguration` in `bootstrap_logging()` to have a
  better structure.


## [2.3.0] - 2026-08-18
### Added
- `sort_fields` parameter to `logging.configure_logger()`.
- `extra` parameter to `logging.configure_logger()`.

### Changed
- Leave structured log fields unsorted by default. This allows for a more
  natural ordering of fields. Fields can still be sorted by passing the
  `sort_fields=True` parameter to `logging.configure_logger()`.

### Deprecated
- "UNKNOWN" as parent commit value when parent commits are not provided to
  `log_git_status()`.


## [2.2.0] - 2026-07-01
### Added
- `log_python_version()`
- `log_startup_information()` -- a shortcut for logging both the Python version
  and git status.


## [2.1.0] - 2026-04-05
### Added
- `service_kit.configuration.FeatureFlag` pydantic type.


## [2.0.1] - 2026-02-05
### Changed
- Module exports to comply with the latest guidance from typing.python.org.

### Fixed
- All dependency specifications to be PEP 508 compliant.


## [2.0.0] - 2025-11-19
### Added
- `service_kit.logging.intercept_uvicorn_loggers()`
- `service_kit.utils.Timer`

### Changed
- FastAPI, Uvicorn, and related dependencies are only installed if the \[api\]
  extra is specified.
- RequestIDMiddleware to use UUIDv7 instead of ULID if UUIDv7 is available.
- `service_kit.testing` has been split into `service_kit.api.testing` and
  `service_kit.logging.testing`.


## [1.4.0.post1] - 2025-10-30
### Changed
- Allow use of ServiceKit with monkey-types 2.0.0.


## [1.4.0] - 2025-08-07
### Added
- Parent commit IDs to the log message produced by `log_git_status()`.


## [1.3.0] - 2025-08-05
### Added
- `log_git_status()` function to service\_kit.logging.


## [1.2.0.post1] - 2025-03-05
### Added
- Documentation generated with Sphinx.


## [1.2.0] - 2025-02-21
### Added
- 403 FORBIDDEN response type.


## [1.1.1] - 2025-01-21
### Changed
- Use poetry 2.x.

### Fixed
- Added missing dependency "pygments".


## [1.1.0] - 2025-01-16
### Added
- service\_kit.logging.log\_postgres\_error().
