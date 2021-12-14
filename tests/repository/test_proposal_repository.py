from typing import Any, Callable

import freezegun
import pytest
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.repository.proposal_repository import ProposalRepository
from tests.markers import nodatabase

TEST_DATA = "repository/proposal_repository.yaml"

USER_TEST_DATA = "users.yaml"


@nodatabase
def test_list_returns_correct_content(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    salt_astronomer = testdata(USER_TEST_DATA)["salt_astronomer"]
    data = testdata(TEST_DATA)["proposal_list_content"]
    for d in data:
        semester = d["semester"]
        expected_proposal = d["proposal"]
        proposal_repository = ProposalRepository(dbconnection)
        proposals = proposal_repository.list(salt_astronomer, semester, semester)
        proposal = [
            p
            for p in proposals
            if p["proposal_code"] == expected_proposal["proposal_code"]
        ][0]

        assert proposal == expected_proposal


@nodatabase
def test_list_returns_correct_proposal_codes(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["proposal_list"]
    proposal_repository = ProposalRepository(dbconnection)
    for d in data:
        from_semester = d["from_semester"]
        to_semester = d["to_semester"]
        username = d["username"]
        expected_proposal_codes = sorted(d["proposal_codes"])
        expected_proposal_count = d["proposal_count"]

        proposals = proposal_repository.list(
            username=username, from_semester=from_semester, to_semester=to_semester
        )
        proposal_codes = sorted(p["proposal_code"] for p in proposals)

        assert len(proposal_codes) == expected_proposal_count
        if expected_proposal_codes != ["many"]:
            assert proposal_codes == expected_proposal_codes


@nodatabase
def test_list_handles_omitted_semester_limits(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    proposal_repository = ProposalRepository(dbconnection)

    salt_astronomer = testdata(USER_TEST_DATA)["salt_astronomer"]
    assert len(
        proposal_repository.list(username=salt_astronomer, to_semester="2015-1")
    ) == len(
        proposal_repository.list(
            username=salt_astronomer, from_semester="2000-1", to_semester="2015-1"
        )
    )
    assert len(
        proposal_repository.list(username=salt_astronomer, from_semester="2020-1")
    ) == len(proposal_repository.list(username=salt_astronomer, from_semester="2020-1"))
    assert len(proposal_repository.list(username=salt_astronomer)) == len(
        proposal_repository.list(
            username=salt_astronomer, from_semester="2000-1", to_semester="2100-1"
        )
    )


@nodatabase
def test_list_results_can_be_limited(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    salt_astronomer = testdata(USER_TEST_DATA)["salt_astronomer"]
    data = testdata(TEST_DATA)["proposal_list_limit"]
    for d in data:
        semester = d["semester"]
        expected_proposal_codes = d["proposal_codes"]
        limit = len(expected_proposal_codes)
        proposal_repository = ProposalRepository(dbconnection)
        proposals = proposal_repository.list(
            username=salt_astronomer,
            from_semester=semester,
            to_semester=semester,
            limit=limit,
        )

        assert [p["proposal_code"] for p in proposals] == expected_proposal_codes


@nodatabase
def test_list_handles_omitted_limit(dbconnection: Connection) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    assert proposal_repository.list(
        username="someone", from_semester="2018-2", to_semester="2019-2"
    ) == proposal_repository.list(
        username="someone", from_semester="2018-2", to_semester="2019-2", limit=100000
    )


def test_list_raises_error_for_negative_limit(dbconnection: Connection) -> None:
    with pytest.raises(ValueError) as excinfo:
        proposal_repository = ProposalRepository(dbconnection)
        proposal_repository.list(username="someone", limit=-1)

    assert "negative" in str(excinfo)


@pytest.mark.parametrize(
    "incorrect_semester",
    ["200-1", "20212-1", "2020-", "2020-11", "2020", "20202", "abcd-1", "2021-a"],
)
@nodatabase
def test_list_raises_error_for_wrong_semester_format(
    incorrect_semester: str, dbconnection: Connection
) -> None:
    proposal_repository = ProposalRepository(dbconnection)

    with pytest.raises(ValueError) as excinfo:
        proposal_repository.list(username="someone", from_semester=incorrect_semester)
    assert "format" in str(excinfo)

    with pytest.raises(ValueError) as excinfo:
        proposal_repository.list(username="someone", to_semester=incorrect_semester)
    assert "format" in str(excinfo)


@nodatabase
def test_list_raises_error_for_wrong_semester_order(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(ValueError) as excinfo:
        username = testdata(USER_TEST_DATA)["salt_astronomer"]
        proposal_repository.list(
            username=username, from_semester="2021-2", to_semester="2021-1"
        )
    assert "semester" in str(excinfo.value)


@nodatabase
def test_get_raises_error_for_wrong_proposal_code(dbconnection: Connection) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(NotFoundError):
        proposal_repository.get(proposal_code="idontexist")


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


def test_get_returns_correct_value_for_is_self_activatable(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["is_self_activatable"]
    proposal_repository = ProposalRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]
        expected_may_activate = d["self_activatable"]
        proposal = proposal_repository.get(proposal_code)

        assert proposal["general_info"]["is_self_activatable"] == expected_may_activate


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
def test_get_returns_block_visits(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["proposal_code"]
    expected_observations = data["block_visits"]
    proposal_repository = ProposalRepository(dbconnection)
    proposal = proposal_repository.get(proposal_code)
    observations = proposal["block_visits"]

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


def test_get_proposal_type_returns_the_correct_proposal_type(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get_proposal_type"]
    proposal_repository = ProposalRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]
        expected_proposal_type = d["proposal_type"]
        proposal_type = proposal_repository.get_proposal_type(proposal_code)
        assert proposal_type == expected_proposal_type


def test_get_proposal_type_raises_not_found_error(dbconnection: Connection) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(NotFoundError):
        proposal_repository.get_proposal_type("idontexist")


def test_get_proposal_status(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["get_proposal_status"]
    for d in data:
        proposal_code = d["proposal_code"]
        expected_status = d["status"]
        proposal_repository = ProposalRepository(dbconnection)
        status = proposal_repository.get_proposal_status(proposal_code)

        assert expected_status == status


def test_get_proposal_status_raises_error_for_wrong_proposal_code(
    dbconnection: Connection,
) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(NotFoundError):
        proposal_repository.get_proposal_status("idontexist")


def test_update_proposal_status(dbconnection: Connection) -> None:
    # Set the status to "Active"
    proposal_repository = ProposalRepository(dbconnection)
    proposal_code = "2020-2-SCI-043"
    proposal_repository.update_proposal_status(proposal_code, "Active")
    status = proposal_repository.get_proposal_status(proposal_code)
    assert status["value"] == "Active"
    assert status["reason"] is None

    # Now set it to "Under technical review"
    proposal_repository.update_proposal_status(proposal_code, "Under technical review")
    assert (
        proposal_repository.get_proposal_status(proposal_code)["value"]
        == "Under technical review"
    )


def test_update_proposal_status_for_not_none_status_reason(
    dbconnection: Connection,
) -> None:
    # Set the status to "Expired"
    proposal_repository = ProposalRepository(dbconnection)
    proposal_code = "2019-1-SCI-010"
    proposal_repository.update_proposal_status(proposal_code, "Expired")
    status = proposal_repository.get_proposal_status(proposal_code)
    assert status["value"] == "Expired"
    assert status["reason"] == "Other"

    # Now set it to "Deleted"
    proposal_repository.update_proposal_status(proposal_code, "Deleted")
    assert proposal_repository.get_proposal_status(proposal_code)["value"] == "Deleted"


def test_update_proposal_status_raises_error_for_wrong_proposal_code(
    dbconnection: Connection,
) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(NotFoundError):
        proposal_repository.get_proposal_status("idontexist")


def test_update_proposal_status_raises_error_for_wrong_status(
    dbconnection: Connection,
) -> None:
    proposal_repository = ProposalRepository(dbconnection)
    with pytest.raises(ValueError) as excinfo:
        proposal_repository.update_proposal_status(
            "2020-2-SCIO-043", "Wrong proposal status"
        )

    assert "proposal status" in str(excinfo)


def test_is_self_activatable(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["is_self_activatable"]
    proposal_repository = ProposalRepository(dbconnection)
    for d in data:
        proposal_code = d["proposal_code"]
        expected_self_activatable = d["self_activatable"]

        assert (
            proposal_repository.is_self_activatable(proposal_code)
            == expected_self_activatable
        )
