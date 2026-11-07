@domain:limit-recovery @area:auto-resume @from:claude-keepalive/claude-keepalive
Feature: Resuming the conversation after the reset
  Lets a developer come back to the same conversation, not a fresh one, once the limit has reset.

  Background:
    Given claude has hit its usage limit inside claude-keepalive
    And the wait for the reset has finished

  @id:limit-recovery.auto-resume.001 @rule:keepalive.resume.same-conversation @verified @source:claude_keepalive.py#main @test:tests/test_claude_keepalive.py#test_extracts_uuid @test:tests/test_claude_keepalive.py#test_rejects_partial_id
  Scenario Outline: claude is relaunched on the conversation the limit message names
    Given the limit message <names a session>
    When claude-keepalive relaunches claude
    Then "Resuming Claude..." is shown
    And claude is started as "<claude command>"
    And the relaunched session is watched for the limit again

    Examples:
      | names a session                                                 | claude command                                       |
      | includes "claude --resume abcdef12-3456-7890-abcd-ef1234567890" | claude --resume abcdef12-3456-7890-abcd-ef1234567890 |
      | includes only "claude --resume abc123"                          | claude --continue                                    |
      | names no session                                                | claude --continue                                    |

  @id:limit-recovery.auto-resume.002 @rule:keepalive.resume.started-id-not-reused @inferred @source:claude_keepalive.py#main @questionable
  Scenario: A session started with --resume continues the latest conversation when the limit message names none
    Given the developer started claude-keepalive with --resume 0f8e2a4c-1b3d-4e5f-9a7b-6c5d4e3f2a1b
    And the limit message names no session
    When claude-keepalive relaunches claude
    Then claude is started as "claude --continue", not on 0f8e2a4c-1b3d-4e5f-9a7b-6c5d4e3f2a1b
