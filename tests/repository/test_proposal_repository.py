import json
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.engine import Connection

from saltapi.repository.proposal_repository import ProposalRepository
from tests.markers import nodatabase

TEST_DATA = "repository/proposal_repository.yaml"


def _setup_proposal_file(
    proposal_code: str, submission: int, base_dir: Path, content: Any
) -> None:
    submission_dir = base_dir / proposal_code / str(submission)
    submission_dir.mkdir(parents=True)
    proposal_file = submission_dir / "Proposal.json"
    with open(proposal_file, "w") as f:
        json.dump(content, f)


@nodatabase
def test_get_returns_proposal_file_content(
    tmp_path: Path, dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    # set up fake proposal file
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["proposal_code"]
    submission = data["submission"]
    proposal_file_content = {"proposal_code": proposal_code}
    _setup_proposal_file(proposal_code, submission, tmp_path, proposal_file_content)

    # check that the file content is returned
    proposal_repository = ProposalRepository(dbconnection, tmp_path)
    proposal = proposal_repository.get(proposal_code)
    for key in proposal_file_content:
        assert key in proposal
        assert proposal[key] == proposal_file_content[key]


@nodatabase
def test_get_returns_blocks(
    tmp_path: Path, dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    # set up fake proposal file
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["proposal_code"]
    submission = data["submission"]
    proposal_file_content = {"proposal_code": proposal_code}
    _setup_proposal_file(proposal_code, submission, tmp_path, proposal_file_content)

    expected_blocks = data["blocks"]
    proposal_repository = ProposalRepository(dbconnection, tmp_path)
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
def test_get_returns_observations(
    dbconnection: Connection, tmp_path: Path, testdata: Callable[[str], Any]
) -> None:
    # set up fake proposal file
    data = testdata(TEST_DATA)["get"]
    proposal_code = data["proposal_code"]
    submission = data["submission"]
    proposal_file_content = {"proposal_code": proposal_code}
    _setup_proposal_file(proposal_code, submission, tmp_path, proposal_file_content)

    expected_observations = data["observations"]
    proposal_repository = ProposalRepository(dbconnection, tmp_path)
    proposal = proposal_repository.get(proposal_code)
    observations = proposal["observations"]
    assert set(tuple(o.items()) for o in observations) == set(
        tuple(o.items()) for o in expected_observations
    )
