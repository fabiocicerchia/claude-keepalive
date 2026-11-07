@domain:installation @area:local-install @from:claude-keepalive/makefile
Feature: Installing from a local checkout
  Lets an operator install the exact checkout they are looking at, rather than whatever is on main, so they can run a local or patched version as an ordinary command.

  Background:
    Given the operator has a local checkout of claude-keepalive

  @id:installation.local-install.001 @rule:installation.local-install.installs-checkout-as-package @inferred @source:Makefile#install @questionable
  Scenario: Installing from a checkout provides the claude-keepalive command and its man page
    Given the operator has set DEST to "/opt/tools/bin"
    When the operator runs "make install"
    Then the checkout is installed as a Python package with pip
    And a "claude-keepalive" command is available from pip's scripts directory
    And the claude-keepalive(1) man page is installed under share/man/man1
    And nothing is copied into "/opt/tools/bin"
