@domain:interactive-session @area:exit-and-cleanup @from:claude-keepalive/claude-keepalive
Feature: Ending a wrapped claude session
  Lets scripts and developers rely on claude-keepalive ending exactly as claude ended, and stay able to stop it at any time.

  Background:
    Given the developer is in an interactive terminal

  @id:interactive-session.exit-and-cleanup.001 @rule:keepalive.exit.code-passed-through @verified @source:claude_keepalive.py#exit_code @test:tests/test_claude_keepalive.py#test_normal_exit_passes_through_exit_code
  Scenario Outline: claude-keepalive exits with the same code claude ended with
    Given claude is running inside claude-keepalive
    And claude has not hit a usage limit
    When claude <ends>
    Then claude-keepalive exits with code <exit code>
    And no waiting or resuming happens

    Examples:
      | ends                  | exit code |
      | exits with code 0     | 0         |
      | exits with code 5     | 5         |
      | is killed by signal 9 | 137       |

  @id:interactive-session.exit-and-cleanup.002 @rule:keepalive.interrupts.termination-forwarded-to-claude @inferred @source:claude_keepalive.py#forward_signal
  Scenario Outline: A stop request sent to claude-keepalive reaches claude
    Given claude is running inside claude-keepalive
    When the operator sends <signal> to the claude-keepalive process
    Then claude receives <signal>
    And claude-keepalive exits with claude's resulting exit code, <exit code> if claude dies from it

    Examples:
      | signal  | exit code |
      | SIGTERM | 143       |
      | SIGINT  | 130       |

  @id:interactive-session.exit-and-cleanup.003 @rule:keepalive.interrupts.stop-while-waiting @inferred @source:claude_keepalive.py#forward_signal
  Scenario Outline: The developer can stop claude-keepalive while it waits for the reset
    Given claude-keepalive is waiting for a usage limit to reset
    When the developer <stops it>
    Then claude-keepalive exits at once with code <exit code>
    And claude is not relaunched

    Examples:
      | stops it       | exit code |
      | presses Ctrl-C | 130       |
      | sends SIGTERM  | 143       |
