Feature: Get a block visit

  Scenario: Unauthenticated users cannot request a block visit

    Given I am not authenticated
    When I request a block visit 1
    Then I get an authentication error

  Scenario: Non-existing block visit cannot be requested

    Given I am a SALT Astronomer
    When I request a block visit 0
    Then I get a not found error

  Scenario Outline: Requesting a block visit is not permitted for some users

    Given I am <user_type>
    When I request a block visit 100
    Then I get a permission error

    Examples:
      | user_type                                     |
      | Principal Contact for proposal 2020-2-SCI-018 |
      | TAC chair for partner UW                      |
      | TAC member for partner UW                     |

  Scenario Outline: Getting a block visit

    Given I am <user_type>
    When I request a block visit 11713
    Then I get the block visit 11713

    Examples:
      | user_type                                    |
      | investigator for the proposal 2016-1-COM-001 |
      | SALT Astronomer                              |
      | Administrator                                |
      | TAC member for the partner RU                |