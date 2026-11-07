@domain:documentation-site @area:brand-theme @from:docs/stylesheets
Feature: Presenting the documentation in one consistent brand
  Readers of the claude-keepalive splash page and docs see one recognisable, legible look in light and dark mode without the pages fetching anything from third parties.

  Background:
    Given the documentation site is published with its splash page at / and the rendered docs at /docs/

  @id:documentation-site.brand-theme.001 @rule:docs.brand.single-accent-pair-shared @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The splash page and the docs share one accent colour pair
    Given the accent pair is cyan #22d3ee and indigo #6366f1
    When a reader opens the splash page and then the docs
    Then the splash page title and GitHub button use the cyan-to-indigo gradient
    And the docs home title and primary buttons use the same cyan-to-indigo gradient
    And changing the accent pair in the docs theme changes both the splash page and the docs

  @id:documentation-site.brand-theme.002 @rule:docs.brand.scheme-legible-link-colour @inferred @source:docs/stylesheets/extra.css#[data-md-color-scheme="slate"]
  Scenario Outline: Links take the accent colour that stays readable in the active colour scheme
    Given the reader's docs colour scheme is <scheme>
    When the reader views a docs page
    Then links are shown in <link colour>
    And the page background is <background>

    Examples:
      | scheme | link colour    | background                                               |
      | light  | indigo #6366f1 | the default light background                             |
      | dark   | cyan #22d3ee   | near-black #0b0f1a, with the header and tabs matching it |

  @id:documentation-site.brand-theme.003 @rule:docs.brand.no-placeholder-logo @inferred @source:docs/stylesheets/extra.css#.md-header__button.md-logo
  Scenario: The docs show no stand-in logo while the project has none
    Given no project logo is configured for the docs
    When a reader views any docs page
    Then the header shows no logo icon
    And the navigation title shows no logo icon

  @id:documentation-site.brand-theme.004 @rule:docs.brand.no-external-font-requests @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The docs render with system fonts and fetch no web fonts
    Given the reader's device has no network access to font or CDN hosts
    When the reader opens a docs page
    Then body text renders in the system sans-serif font
    And code renders in the system monospace font
    And the page requests no web font, CDN asset or analytics

  @id:documentation-site.brand-theme.005 @rule:docs.content.wide-tables-not-clipped @inferred @source:docs/stylesheets/extra.css#.md-typeset table:not([class]) @questionable
  Scenario: Wide tables in the docs stay fully readable on narrow screens
    Given a docs page has a plain table wider than the reader's screen
    When the reader views the page on a narrow screen
    Then the table is drawn as a rounded, bordered card with uppercase column headings
    And the columns past the edge of the screen are reachable by scrolling the table sideways rather than cut off
