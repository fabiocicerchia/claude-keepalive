# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repo.

## Project

`claude-keepalive` is a single-file Python 3 CLI (`claude-keepalive.py`) that
wraps the `claude` binary in a PTY. It forwards the interactive session
through, watches the output for the session-limit message, waits until the
reset time, then relaunches with `--resume <id>` (or `--continue`). Standard
library only — no dependencies.

## Commands

```sh
# run:  ./claude-keepalive.py [--resume <session-id>]
# lint: pre-commit run --all-files   (or: make lint)
# test: make test
make help    # Show this help
make setup   # Install the pre-commit hook
make lint    # Run all pre-commit checks on the whole tree
make test    # Run tests
```

## Tooling

Shared config — the GitHub workflows, `.pre-commit-config.yaml`,
`.editorconfig`, `.hadolint.yaml`, `SECURITY.md` — comes from
[repo-skeleton](https://github.com/fabiocicerchia/repo-skeleton). Edit it
there, not here; a local edit is drift and the next sync overwrites it.
`check-drift.sh` in that repo reports what has diverged.

- `make setup` installs the pre-commit hook, and that is the whole of it.
  Don't add a `.githooks/` directory: `core.hooksPath` replaces `.git/hooks/`
  wholesale, so setting it silently stops every pre-commit hook from running.
- Hooks are pinned by commit SHA with the tag in a trailing comment. A tag can
  be moved, a SHA cannot.
- CI runs this same `.pre-commit-config.yaml` through `pre-commit/action`, so
  what passes locally is what gates the pull request.

## Conventions

- Match existing style; don't reformat unrelated code.
- Conventional Commits for messages (see CONTRIBUTING.md).
- Update CHANGELOG.md (`## [Unreleased]`), docs/, and examples/ with behavior changes.
- Never commit secrets; CI runs gitleaks. Keep `.env` out of git.

## Guardrails

- Don't add dependencies without a clear reason; prefer stdlib.
- Don't touch generated files or lockfiles by hand.
- Ask before large refactors or destructive operations.
