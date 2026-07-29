# claude-keepalive

> Runs the Claude Code CLI and, when you hit the session limit, waits until the
> reset time and resumes the same session automatically.

[![CI](https://github.com/fabiocicerchia/claude-keepalive/actions/workflows/code-quality.yml/badge.svg)](https://github.com/fabiocicerchia/claude-keepalive/actions/workflows/code-quality.yml)
[![Security](https://github.com/fabiocicerchia/claude-keepalive/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/claude-keepalive/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/claude-keepalive/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/claude-keepalive)
[![Release](https://img.shields.io/github/v/release/fabiocicerchia/claude-keepalive)](https://github.com/fabiocicerchia/claude-keepalive/releases)

## Features

- Transparent wrapper: runs `claude` inside a PTY, so the interactive TUI behaves normally.
- Detects "You've hit your session limit", parses the reset time, and sleeps until then.
- Resumes the exact session (`claude --resume <id>`) after the wait, falling back to `--continue`.
- Pure Python 3 standard library — nothing to install.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/claude-keepalive/main/install.sh | bash
```

Or clone it directly:

```sh
git clone https://github.com/fabiocicerchia/claude-keepalive.git
cd claude-keepalive
```

Requires Python 3 and the [`claude`](https://docs.claude.com/en/docs/claude-code) CLI on your `PATH`.

## Usage

```sh
# Start a fresh session and keep it alive across the limit reset:
./claude-keepalive.py

# Resume a specific session id:
./claude-keepalive.py --resume <session-id>
```

Press `Ctrl-C` to stop.

## Documentation

Full docs live in [`docs/`](docs/). Runnable examples live in [`examples/`](examples/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a public issue.

## Support

Need help implementing this? [Get in touch](https://fabiocicerchia.it/contact).

## License

[MIT](LICENSE) © 2026 Fabio Cicerchia
