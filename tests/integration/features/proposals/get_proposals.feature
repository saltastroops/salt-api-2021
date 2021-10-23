Feature: Get a list of proposals

  Scenario: Unauthenticated users cannot request a list of proposals

    Given I am not authenticated
    When I request a list of proposals
    Then I get an authentication error

  Scenario Outline: The start semester must be less than or equal to the end semester

    Given I am an administrator
    When I request a list of proposals from <from_semester> to <to_semester>
    Then I get a bad request error containing semester

    Examples:
      | from_semester | to_semester |
      | 2022-2        | 2021-2      |
      | 2020-1        | 2019-2      |
      | 2020-2        | 2020-1      |


  Scenario Outline: Invalid semesters are rejected

    Given I am a SALT Astronomer
    When I request a list of proposals from <from_semester> to <to_semester>
    Then I get an unprocessable entity error containing semester

    Examples:
      | from_semester | to_semester |
      | abc           | 2020-1      |
      | 2020          | 2020-1      |
      | 2             | 2020-1      |
      | 2021-3        | 2020-1      |
      | 2021-1        | abc         |
      | 2021-1        | 2020        |
      | 2021-1        | 2           |
      | 2021-1        | 2021-3      |

  Scenario: A negative value is rejected for the maximum number of results

    Given I am a SALT Astronomer
    When I request a list of proposals with a negative maximum number of results
    Then I get an unprocessable entity error containing limit

  Scenario Outline: Users request a list of proposals

    Given I am <user_type>
    When I request a list of proposals from <from_semester> to <to_semester>
    Then I get the <proposal_count> proposals <proposal_codes>

    Examples:
      | user_type                                          | from_semester | to_semester | proposal_count | proposal_codes                                                                                                                 |
      | TAC chair for partner RSA                          | 2020-1        | 2020-1      | 32             | many                                                                                                                           |
      | TAC chair for partner RU                           | 2021-1        | 2021-1      | 7              | 2018-1-SCI-012, 2018-1-SCI-041, 2021-1-MLT-007, 2021-1-SCI-012, 2021-1-SCI-015, 2021-1-SCI-028, 2021-1-SCI-031                 |
      | TAC member for partner UW                          | 2021-1        | 2021-1      | 8              | 2018-2-LSP-001, 2018-2-MLT-005, 2020-1-MLT-005, 2020-1-MLT-009, 2020-2-MLT-009, 2021-1-SCI-016, 2021-1-SCI-023, 2021-1-SCI-025 |
      | Principal Investigator for proposal 2014-2-SCI-078 | 2020-2        | 2020-2      | 0              |                                                                                                                                |
      | Principal Investigator for proposal 2018-2-LSP-001 | 2017-2        | 2021-1      | 35             | many                                                                                                                           |
      | SALT Astronomer                                    | 2020-2        | 2020-2      | 81             | many                                                                                                                           |
      | Administrator                                      | 2018-2        | 2018-2      | 79             | many                                                                                                                           |
      | Principal Investigator for proposal 2014-2-SCI-078 | 2018-2        | 2019-1      | 7              | many                                                                                                                           |
      | Principal Contact for proposal 2021-1-SCI-014      | 2018-2        | 2019-1      | 0              |                                                                                                                                |

  Scenario Outline: A maximum number of proposals is requested

    Given I am a SALT Astronomer
    When I request a list of up to <limit> proposals
    Then I get <limit> proposals

    Examples:
      | limit |
      | 0     |
      | 67    |
      | 823   |

  Scenario: The default maximum number of proposals is 1000

    Given I am a SALT Astronomer
    When I request a list of proposals
    Then I get 1000 proposals
