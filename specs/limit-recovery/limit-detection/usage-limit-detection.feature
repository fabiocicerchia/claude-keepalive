@domain:limit-recovery @area:limit-detection @from:claude-keepalive/claude-keepalive
Feature: Detecting that claude hit its usage limit
  Lets a developer leave claude-keepalive unattended, knowing it recognises a real session or usage limit and only that.

  Background:
    Given claude is running inside claude-keepalive

  @id:limit-recovery.limit-detection.001 @rule:keepalive.limit.banner-recognised @verified @source:claude_keepalive.py#found_limit @test:tests/test_claude_keepalive.py#test_matches_known_phrases @test:tests/test_claude_keepalive.py#test_is_case_insensitive @test:tests/test_claude_keepalive.py#test_strips_csi_sequences @test:tests/test_claude_keepalive.py#test_normalizes_curly_apostrophe @test:tests/test_claude_keepalive.py#test_limit_banner_detected_and_child_stopped
  Scenario Outline: Every known wording of the limit message stops the session for recovery
    Given claude is a version that words its limit message as "<message>"
    When claude shows its limit message, in any letter case, colour or with a curly apostrophe
    Then claude-keepalive recognises the usage limit
    And claude is stopped, and forcibly killed if still running 5 seconds later
    And claude-keepalive moves on to waiting for the reset

    Examples:
      | message                         |
      | You've hit your session limit   |
      | You've hit your usage limit     |
      | You've reached your usage limit |
      | Claude usage limit reached      |
      | 5-hour limit reached            |
      | Session limit reached           |

  @id:limit-recovery.limit-detection.002 @rule:keepalive.limit.warnings-not-mistaken @verified @source:claude_keepalive.py#found_limit @test:tests/test_claude_keepalive.py#test_ignores_approaching_warning @test:tests/test_claude_keepalive.py#test_ignores_ordinary_output
  Scenario Outline: Ordinary output and early warnings do not interrupt the session
    Given claude has not hit its limit
    When claude shows "<output>"
    Then claude keeps running
    And claude-keepalive does not wait or relaunch

    Examples:
      | output                                |
      | Approaching usage limit · resets 4pm  |
      | let's talk about rate limits in nginx |

  @id:limit-recovery.limit-detection.003 @rule:keepalive.limit.replayed-history-ignored @inferred @source:claude_keepalive.py#pump @questionable
  Scenario: An old limit message replayed from a resumed conversation is ignored
    Given claude-keepalive starts claude on an existing conversation (given with --resume, or after a reset)
    And the conversation's replayed history contains an old limit message within the first 8 KiB of output
    When claude replays the history
    Then claude keeps running
    And no new wait starts
    And a limit message shown after the first 8 KiB of output is recognised
