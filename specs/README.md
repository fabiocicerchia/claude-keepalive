# Specifications of claude-keepalive

What this code does, one atomic Gherkin scenario per behaviour, read from the code by code-atlas.
Tags: `@verified` a test asserts it · `@inferred` read from the code only · `@gap` an entry point no test covers · `@human` written or amended by a person, never rewritten.

## Documentation Site
The look and feel of the project's published documentation and landing page.

- **Brand theme & colours**: [Presenting the documentation in one consistent brand](documentation-site/brand-theme/docs-brand-theme.feature) (5)

## Installation
Getting claude-keepalive onto a user's machine and onto their PATH.

- **Install from checkout**: [Installing from a local checkout](installation/local-install/install-from-checkout.feature) (1)
- **One-line installer**: [Installing with the one-line installer](installation/one-line-installer/one-line-installer.feature) (3)
- **PATH guidance**: [Telling the user where the tool was installed](installation/path-guidance/install-path-guidance.feature) (1)

## Interactive Session
Running Claude Code through the wrapper so it feels exactly like using claude directly.

- **Exit & cleanup**: [Ending a wrapped claude session](interactive-session/exit-and-cleanup/wrapped-session-exit.feature) (3)
- **Launch & startup**: [Starting a wrapped claude session](interactive-session/launch/wrapped-session-launch.feature) (5)

## Usage-Limit Recovery
Noticing when Claude hits a usage or session limit and picking the conversation back up automatically once it resets.

- **Automatic resume**: [Resuming the conversation after the reset](limit-recovery/auto-resume/automatic-resume.feature) (2)
- **Limit detection**: [Detecting that claude hit its usage limit](limit-recovery/limit-detection/usage-limit-detection.feature) (3)
- **Reset-time waiting**: [Waiting for the usage limit to reset](limit-recovery/reset-scheduling/reset-time-waiting.feature) (2)
- **Status messages**: [Telling the developer what happens after a limit](limit-recovery/status-messages/limit-status-messages.feature) (1)
