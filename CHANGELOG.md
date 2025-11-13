# Changelog
All notable changes to this project will be documented in this
file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
the [PEP 440 version scheme](https://peps.python.org/pep-0440/#version-scheme).

## [2.0.0] - 2025-11-13
### Added
- `service_kit.logging.intercept_uvicorn_loggers()`


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
