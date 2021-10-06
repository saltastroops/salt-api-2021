Feature: Authentication

  Users can authenticate to the API with valid credentials

  Scenario: Authenticating with a wrong username
    When I try to login with an incorrect username
    Then I get an authentication error
    And I get a message containing credentials

  Scenario: Authenticating with a wrong password
    When I try to login with an invalid password
    Then I get an authentication error
    And I get a message containing credentials

  Scenario: Authenticating with valid credential
    When I login with valid credentials
    Then I get an authorization token
