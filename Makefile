# Where `make install` puts the script — the same default install.sh uses.
DEST ?= $(HOME)/.local/bin
# Arguments for `make run`, e.g. make run ARGS="--resume <session-id>"
ARGS ?=

# Every verb this repository exposes lives here; `make` on its own prints them.
# FC-GEN-057: the same eight verbs in every repo, each either wired or a
# declared no-op that says why. None of them exit 0 quietly.

.DEFAULT_GOAL := help

.PHONY: help setup install build run test lint format analyze

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

setup: ## Install the pre-commit hook
	pre-commit install

# install.sh curls the script off main, which is right for a one-liner from
# the README and wrong here: this installs the checkout you are looking at.
install: ## Install this checkout into DEST (default ~/.local/bin)
	mkdir -p $(DEST)
	install -m 0755 claude-keepalive.py $(DEST)/claude-keepalive
	@echo "installed $(DEST)/claude-keepalive"

run: ## Run it from the checkout (make run ARGS="--resume <id>")
	./claude-keepalive.py $(ARGS)

test: ## Run tests
	python3 -m unittest discover -s tests

lint: ## Run the whole gate — every hook, every file
	pre-commit run --all-files

format: ## Format the tree with ruff, the formatter the gate checks
	ruff format .

analyze: ## Scan the tree the way CI does — vulnerabilities, misconfig, secrets
	@command -v trivy >/dev/null 2>&1 || { \
		echo "analyze needs trivy: https://trivy.dev/latest/getting-started/installation/" >&2; \
		exit 69; }
	trivy fs --scanners vuln,misconfig,secret --severity CRITICAL,HIGH .

# --- Declared no-op (FC-GEN-058) ---

build: ## Not applicable — nothing is compiled or packaged
	@echo "Nothing to build: one standard-library Python script, run in place or"
	@echo "copied onto PATH by 'make install'. See README > Not applicable."
