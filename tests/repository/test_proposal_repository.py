from typing import Any, Callable

import freezegun
from sqlalchemy.engine import Connection

from saltapi.repository.proposal_repository import ProposalRepository
from tests.markers import nodatabase

TEST_DATA = "repository/proposal_repository.yaml"


@nodatabase
def test_get_returns_general_info(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["proposal_code"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    expected_general_info = data["general_info"]
    general_info = proposal["general_info"]
    assert (general_info.keys()) == (expected_general_info.keys())
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
    proposal_code = data["proposal_code"]
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
        i for i in investigators if i["has_approved_proposal"] is True
    ]
    rejected_investigators = [
        i for i in investigators if i["has_approved_proposal"] is False
    ]
    undecided_investigators = [
        i for i in investigators if i["has_approved_proposal"] is None
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
    proposal_code = data["proposal_code"]
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
    proposal_code = data["proposal_code"]
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
    expected_allocations.sort(key=lambda v: v["partner_code"])
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code, semester)
    allocations = proposal["time_allocations"]
    allocations.sort(key=lambda v: v["partner_code"])

    assert len(expected_allocations) == len(allocations)
    for i in range(len(allocations)):
        allocation = allocations[i]
        ea = expected_allocations[i]
        expected_allocation = {
            "partner_name": ea["partner_name"],
            "partner_code": ea["partner_code"],
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


def test_get_returns_data_release_date(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["data_release_date"]
    proposal_repository = ProposalRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]
        expected_release_date = d["release_date"]
        proposal = proposal_repository.get(proposal_code)
        release_date = proposal["general_info"]["data_release_date"]
        assert release_date == expected_release_date


def test_get_returns_block_observability(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    for data in testdata(TEST_DATA)["observabilities"]:
        proposal_code = data["proposal_code"]
        semester = data["semester"]
        now = data["now"]
        expected_observabilities = data["observabilities"]

        with freezegun.freeze_time(now):
            proposal_repository = ProposalRepository(dbconnection)
            proposal = proposal_repository.get(proposal_code, semester)
            blocks = proposal["blocks"]
            for o in expected_observabilities:
                block_id = o["block_id"]
                block = next(b for b in blocks if b["id"] == block_id)
                assert block["is_observable_tonight"] == o["is_observable_tonight"]
                assert block["remaining_nights"] == o["remaining_nights"]


def test_get_returns_observation_comments(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["observation_comments"]
    proposal_code = data["proposal_code"]
    expected_comments = data["comments"]

    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    comments = proposal["observation_comments"]

    assert len(comments) == len(expected_comments)
    for i in range(len(comments)):
        assert comments[i]["comment_date"] == expected_comments[i]["comment_date"]
        assert comments[i]["author"] == expected_comments[i]["author"]
        assert expected_comments[i]["comment"] in comments[i]["comment"]
