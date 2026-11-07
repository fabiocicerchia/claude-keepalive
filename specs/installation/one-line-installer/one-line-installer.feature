@domain:installation @area:one-line-installer @from:claude-keepalive/install
Feature: Installing with the one-line installer
  Lets a user install claude-keepalive with a single curl-pipe command, into a directory of their choice, ready to run.

  Background:
    Given the user's machine has bash and curl and can reach raw.githubusercontent.com

  @id:installation.one-line-installer.001 @rule:installation.installer.installs-executable-into-chosen-directory @inferred @source:install.sh#DEST
  Scenario Outline: The installer puts an executable claude-keepalive into the chosen directory
    Given the install directory is <dest_setting>
    When the user runs the one-line installer
    Then the directory <installed_dir> exists
    And <installed_dir>/claude-keepalive contains the claude_keepalive.py script from the main branch
    And <installed_dir>/claude-keepalive is executable

    Examples:
      | dest_setting        | installed_dir  |
      | not set             | ~/.local/bin   |
      | DEST=/opt/tools/bin | /opt/tools/bin |

  @id:installation.one-line-installer.002 @rule:installation.installer.reinstall-replaces-with-latest-main @inferred @source:install.sh#DEST @questionable
  Scenario: Re-running the installer replaces the installed copy with the latest version from main
    Given claude-keepalive is already installed in ~/.local/bin
    When the user runs the one-line installer again
    Then ~/.local/bin/claude-keepalive is overwritten with the current claude_keepalive.py from the main branch
    And no confirmation is asked before replacing it

  @id:installation.one-line-installer.003 @rule:installation.installer.download-failure-aborts @inferred @source:install.sh#DEST
  Scenario: A failed download stops the installer without reporting success
    Given the script cannot be downloaded from GitHub (network error or HTTP error)
    When the user runs the one-line installer
    Then the installer exits with a non-zero status
    And the message "claude-keepalive installed to …" is not printed
    And no executable claude-keepalive is produced by this run
