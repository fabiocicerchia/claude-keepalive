# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 (2026-07-29)


### Features

* add install.sh one-liner installer ([cf74e06](https://github.com/fabiocicerchia/claude-keepalive/commit/cf74e061b29c3f758f6141dbe8ae87aecded5eb2))


### Bug Fixes

* sort imports and document deliberately-naive datetime usage ([#14](https://github.com/fabiocicerchia/claude-keepalive/issues/14)) ([5355e5c](https://github.com/fabiocicerchia/claude-keepalive/commit/5355e5c089c1768d4bd4cf7e77d824163b77ac1d))

## [Unreleased]

## [0.1.0]

### Added

- Transparent PTY wrapper around the `claude` CLI.
- Detects the session-limit message, parses the reset time, and waits it out.
- Resumes the same session (`--resume`, falling back to `--continue`) after the wait.

[Unreleased]: https://github.com/fabiocicerchia/claude-keepalive/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/claude-keepalive/releases/tag/v0.1.0
