@domain:interactive-session @area:launch @from:claude-keepalive/claude-keepalive
Feature: Starting a wrapped claude session
  Lets a developer run claude through claude-keepalive as if running claude directly, optionally on an existing conversation, and tells them plainly when it cannot start.

  Background:
    Given claude-keepalive is installed on the developer's machine

  @id:interactive-session.launch.001 @rule:keepalive.launch.requires-terminal @verified @source:claude_keepalive.py#main @test:tests/test_claude_keepalive.py#test_exits_ex_usage_without_a_tty
  Scenario: The wrapper refuses to run without an interactive terminal
    Given the developer's input is not a terminal (for example it is piped or redirected)
    When the developer runs claude-keepalive
    Then "claude-keepalive: stdin must be a TTY" is shown on standard error
    And claude is not started
    And claude-keepalive exits with code 64

  @id:interactive-session.launch.002 @rule:keepalive.launch.missing-claude-reported @inferred @source:claude_keepalive.py#spawn_claude
  Scenario: A missing claude command is reported and exits with 127
    Given the developer is in an interactive terminal
    And no claude command is on the PATH
    When the developer runs claude-keepalive
    Then "claude-keepalive: cannot launch claude" is shown on the screen
    And claude-keepalive exits with code 127

  @id:interactive-session.launch.003 @rule:keepalive.launch.resume-given-session @inferred @source:claude_keepalive.py#main
  Scenario Outline: A given session id starts claude on that conversation
    Given the developer is in an interactive terminal
    When the developer runs claude-keepalive with <arguments>
    Then claude is started as "<claude command>"

    Examples:
      | arguments                                     | claude command                                       |
      | --resume 0f8e2a4c-1b3d-4e5f-9a7b-6c5d4e3f2a1b | claude --resume 0f8e2a4c-1b3d-4e5f-9a7b-6c5d4e3f2a1b |
      | no arguments                                  | claude                                               |

  @id:interactive-session.launch.004 @rule:keepalive.terminal.output-and-keys-pass-through @verified @source:claude_keepalive.py#pump @test:tests/test_claude_keepalive.py#test_limit_banner_detected_and_child_stopped
  Scenario: The developer sees claude's output and types into claude as if running it directly
    Given claude is running inside claude-keepalive
    When claude prints output, including coloured text, and the developer types keystrokes
    Then claude's output appears on the developer's screen byte for byte
    And every keystroke reaches claude unchanged, including Ctrl-C
    And the developer's terminal returns to its previous mode when claude ends

  @id:interactive-session.launch.005 @rule:keepalive.terminal.window-size-follows-user @inferred @source:claude_keepalive.py#sync_winsize
  Scenario: claude always sees the developer's current window size
    Given claude is running inside claude-keepalive
    When the developer resizes their terminal window
    Then claude is told the new number of rows and columns
    And claude's layout matches the resized window
