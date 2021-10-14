Feature: Get a block visit status

  Scenario: Unauthenticated users cannot request a block visit status

    Given I am not authenticated
    When I request a block visit 1 status
    Then I get an authentication error

  Scenario: Block visit status of non-existing block visit cannot be requested

    Given I am a SALT Astronomer
    When I request a block visit 0 status
    Then I get a not found error

  Scenario Outline: Requesting a block visit is not permitted for some users

    Given I am <user_type>
    When I request a block visit 1 status
    Then I get a permission error

    Examples:
      | user_type                                     |
      | investigator for proposal 2020-2-SCI-018      |
      | Principal Contact for proposal 2020-2-SCI-018 |
      | TAC chair for partner UW                      |
      | TAC member for partner UW                     |

  Scenario Outline: Getting a block visit status

    Given I am <user_type>
    When I request a block visit 11713 status
    Then I get a block visit 11713 status Accepted

    Examples:
      | user_type                                    |
      | investigator for the proposal 2016-1-COM-001 |
      | SALT Astronomer                              |
      | Administrator                                |
      | Board member                                 |
      | TAC member for partner RU                    |