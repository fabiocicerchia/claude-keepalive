@domain:installation @area:path-guidance @from:claude-keepalive/install
Feature: Telling the user where the tool was installed
  Tells the person installing claude-keepalive where it landed and whether they still need to add that directory to PATH to run it by name.

  Background:
    Given the download of claude-keepalive succeeds

  @id:installation.path-guidance.001 @rule:installation.path-guidance.hint-only-when-not-on-path @inferred @source:install.sh#DEST
  Scenario Outline: The installer reports the install location and asks to extend PATH only when the directory is not on it
    Given the install directory is /home/alex/.local/bin
    And /home/alex/.local/bin <on_path> on the user's PATH
    When the user runs the one-line installer
    Then the installer prints "claude-keepalive installed to /home/alex/.local/bin/claude-keepalive"
    And <path_hint>

    Examples:
      | on_path | path_hint                                                                                      |
      | is      | no PATH advice is printed                                                                      |
      | is not  | the installer prints "Add /home/alex/.local/bin to your PATH to run it as 'claude-keepalive'." |
