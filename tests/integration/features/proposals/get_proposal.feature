Feature: Get a proposal

  Scenario Outline: Unauthenticated users cannot request a proposal

    Given I am not authenticated
    When I request the proposal <proposal_code>
    Then I get an authentication error

    Examples:
      | proposal_code  |
      | 2018-2-LSP-001 |
      | 2016-1-COM-001 |
      | ENG_SKYFLAT    |
      | 2016-1-SVP-001 |
      | 2019-1-GWE-005 |
      | 2021-1-DDT-002 |

  Scenario Outline: Requesting a science proposal is not permitted for some users

    Given I am <user_type>
    When I request the proposal 2019-2-SCI-006
    Then I get a permission error

    Examples:
      | user_type                                          |
      | investigator for proposal 2018-2-LSP-001           |
      | Principal Contact for proposal 2018-2-LSP-001      |
      | Principal Investigator for proposal 2018-2-LSP-001 |
      | TAC chair for partner UW                           |
      | TAC member for partner UW                          |
      | Board member                                       |

  Scenario Outline: Getting a science proposal

    Given I am <user_type>
    When I request the proposal 2019-2-SCI-006
    Then I get the proposal 2019-2-SCI-006

    Examples:
      | user_type                                          |
      | investigator for proposal 2019-2-SCI-006           |
      | Principal Contact for proposal 2019-2-SCI-006      |
      | Principal Investigator for proposal 2019-2-SCI-006 |
      | TAC chair for partner RSA                          |
      | TAC member for partner RSA                         |
      | SALT Astronomer                                    |
      | Administrator                                      |

  Scenario Outline: Requesting a commissioning proposal is not permitted for some users

    Given I am <user_type>
    When I request the proposal 2016-1-COM-001
    Then I get a permission error

    Examples:
      | user_type                                          |
      | investigator for proposal 2018-2-LSP-001           |
      | Principal Contact for proposal 2018-2-LSP-001      |
      | Principal Investigator for proposal 2018-2-LSP-001 |
      | TAC chair for partner RSA                          |
      | TAC member for partner RSA                         |
      | TAC chair for partner POL                          |
      | TAC member for partner POL                         |
      | Board member                                       |

  Scenario Outline: Getting a commissioning proposal

    Given I am <user_type>
    When I request the proposal 2016-1-COM-001
    Then I get the proposal 2016-1-COM-001

    Examples:
      | user_type                                          |
      | investigator for proposal 2016-1-COM-001           |
      | Principal Contact for proposal 2016-1-COM-001      |
      | Principal Investigator for proposal 2016-1-COM-001 |
      | SALT Astronomer                                    |
      | Administrator                                      |