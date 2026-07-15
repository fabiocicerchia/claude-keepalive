# Basic Example

What it shows: starting a Claude session that survives a session-limit reset.

## Run

```sh
../../claude-keepalive.py
```

Use Claude as normal. If you hit the session limit, the wrapper reports the
reset time, waits, and resumes the same session — no action needed.
