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
    Then I get an unprocessable entity error

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
