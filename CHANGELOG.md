# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Added

- Transparent PTY wrapper around the `claude` CLI.
- Detects the session-limit message, parses the reset time, and waits it out.
- Resumes the same session (`--resume`, falling back to `--continue`) after the wait.

[Unreleased]: https://github.com/fabiocicerchia/claude-keepalive/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/claude-keepalive/releases/tag/v0.1.0
