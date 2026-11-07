@domain:limit-recovery @area:status-messages @from:claude-keepalive/claude-keepalive
Feature: Telling the developer what happens after a limit
  Keeps a developer who glances at the terminal informed of why claude stopped and when it will come back.

  Background:
    Given claude has hit its usage limit inside claude-keepalive

  @id:limit-recovery.status-messages.001 @rule:keepalive.status.limit-and-wait-announced @inferred @source:claude_keepalive.py#main
  Scenario Outline: The developer is told the reset time and how long the wait is
    Given the limit message <reset detail>
    And the computed wait is <wait> seconds, ending around <until>
    When claude-keepalive starts waiting
    Then "<first line>" is shown
    And "Waiting <wait>s (until ~<until>). Press Ctrl-C to stop." is shown

    Examples:
      | reset detail         | wait | until | first line                                            |
      | says "resets 4:30pm" | 9060 | 16:31 | Session limit reached. Resets at 4:30pm.              |
      | shows no reset time  | 1800 | 14:30 | Session limit reached; couldn't parse the reset time. |
