from typing import Any, Callable

from sqlalchemy.engine import Connection

from saltapi.repository.proposal_repository import ProposalRepository
from tests.markers import nodatabase

TEST_DATA = "repository/proposal_repository.yaml"


@nodatabase
def test_get_returns_general_info(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["general_info"]["code"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    expected_general_info = data["general_info"]
    general_info = proposal["general_info"]
    assert len(general_info.keys()) == len(expected_general_info.keys())
    for key in expected_general_info:
        assert key in general_info
        if key == "summary_for_salt_astronomer":
            assert expected_general_info[key] in general_info[key]
        else:
            assert general_info[key] == expected_general_info[key]


@nodatabase
def test_get_returns_investigators(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["general_info"]["code"]
    expected_investigators = data["investigators"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    investigators = proposal["investigators"]
    assert len(investigators) == len(expected_investigators)
    for i in range(len(investigators)):
        assert investigators[i] == expected_investigators[i]


def test_get_returns_correct_proposal_approval(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["proposal_approval"]
    proposal_code = data["proposal_code"]

    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    investigators = proposal["investigators"]

    approved_investigators = [
        i for i in investigators if i["approved_proposal"] is True
    ]
    rejected_investigators = [
        i for i in investigators if i["approved_proposal"] is False
    ]
    undecided_investigators = [
        i for i in investigators if i["approved_proposal"] is None
    ]

    assert len(approved_investigators) == data["approved_count"]
    assert len(rejected_investigators) == data["rejected_count"]
    assert len(undecided_investigators) == data["undecided_count"]

    assert data["approved_investigator"] in [
        i["family_name"] for i in approved_investigators
    ]
    assert data["rejected_investigator"] in [
        i["family_name"] for i in rejected_investigators
    ]


@nodatabase
def test_get_returns_blocks(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["general_info"]["code"]
    expected_blocks = data["blocks"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    blocks = proposal["blocks"]
    for expected_block in expected_blocks:
        block = next(b for b in blocks if b["id"] == expected_block["id"])
        for key in expected_block:
            assert key in block
            if key == "targets":
                assert set(block["targets"]) == set(expected_block["targets"])
            elif key == "instruments":
                expected_instruments = expected_block["instruments"]
                instruments = block["instruments"]
                assert len(instruments) == len(expected_instruments)
                for expected_instrument in expected_instruments:
                    instrument = next(
                        i
                        for i in instruments
                        if i["name"] == expected_instrument["name"]
                    )
                    assert set(instrument["modes"]) == set(expected_instrument["modes"])
            else:
                assert block[key] == expected_block[key]


@nodatabase
def test_get_returns_executed_observations(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["general_info"]["code"]
    expected_observations = data["executed_observations"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    observations = proposal["executed_observations"]

    assert len(observations) == len(expected_observations)
    for i in range(len(observations)):
        assert observations[i] == expected_observations[i]


@nodatabase
def test_get_returns_time_allocations(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get_allocations"]
    proposal_code = data["proposal_code"]
    semester = data["semester"]

    expected_allocations = data["time_allocations"]
    expected_allocations.sort(key=lambda v: v["partner"])
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code, semester)
    allocations = proposal["time_allocations"]
    allocations.sort(key=lambda v: v["partner"])

    assert len(expected_allocations) == len(allocations)
    for i in range(len(allocations)):
        allocation = allocations[i]
        ea = expected_allocations[i]
        expected_allocation = {
            "partner": ea["partner"],
            "priority_0": ea["allocations"][0],
            "priority_1": ea["allocations"][1],
            "priority_2": ea["allocations"][2],
            "priority_3": ea["allocations"][3],
            "priority_4": ea["allocations"][4],
            "tac_comment": ea["tac_comment"],
        }

        # The test data contains a substring of the comment only
        if expected_allocation["tac_comment"]:
            assert expected_allocation["tac_comment"] in allocation["tac_comment"]
            allocation["tac_comment"] = expected_allocation["tac_comment"]
        assert allocation == expected_allocation


@nodatabase
def test_get_returns_charged_time(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get_charged_time"]
    proposal_code = data["proposal_code"]
    semester = data["semester"]

    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code, semester)
    charged_time = proposal["charged_time"]

    assert data["priority_0"] == charged_time["priority_0"]
    assert data["priority_1"] == charged_time["priority_1"]
    assert data["priority_2"] == charged_time["priority_2"]
    assert data["priority_3"] == charged_time["priority_3"]
    assert data["priority_4"] == charged_time["priority_4"]
