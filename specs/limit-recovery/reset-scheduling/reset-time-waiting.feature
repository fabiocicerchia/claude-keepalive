@domain:limit-recovery @area:reset-scheduling @from:claude-keepalive/claude-keepalive
Feature: Waiting for the usage limit to reset
  Lets a developer's session pick up again as soon as the limit has really reset, without them watching the clock.

  Background:
    Given claude has hit its usage limit inside claude-keepalive

  @id:limit-recovery.reset-scheduling.001 @rule:keepalive.reset.wait-until-advertised-time @verified @source:claude_keepalive.py#seconds_until @test:tests/test_claude_keepalive.py#test_hour_only @test:tests/test_claude_keepalive.py#test_hour_and_minutes @test:tests/test_claude_keepalive.py#test_will_reset_at_variant @test:tests/test_claude_keepalive.py#test_resets_at_variant @test:tests/test_claude_keepalive.py#test_future_same_day @test:tests/test_claude_keepalive.py#test_past_rolls_to_next_day @test:tests/test_claude_keepalive.py#test_midnight
  Scenario Outline: claude-keepalive waits until a minute after the advertised reset time
    Given the limit message says "<message>"
    And the local time is <now>
    When claude-keepalive schedules the relaunch
    Then it waits <wait> seconds before relaunching claude

    Examples:
      | message                          | now   | wait  |
      | resets 3pm                       | 14:00 | 3660  |
      | resets 4:30pm                    | 14:00 | 9060  |
      | resets 1pm                       | 14:00 | 82860 |
      | resets at 12am                   | 23:00 | 3660  |
      | Your limit will reset at 11:45pm | 23:00 | 2760  |

  @id:limit-recovery.reset-scheduling.002 @rule:keepalive.reset.fallback-wait @inferred @source:claude_keepalive.py#main @questionable
  Scenario Outline: Without a readable reset time claude-keepalive waits 30 minutes
    Given the limit message <reset detail>
    When claude-keepalive schedules the relaunch
    Then it waits 1800 seconds before relaunching claude

    Examples:
      | reset detail         |
      | shows no reset time  |
      | says "resets 99pm"   |
      | says "resets 3:75pm" |
