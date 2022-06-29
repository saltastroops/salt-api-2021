from typing import Any, Callable
from sqlalchemy.engine import Connection

from saltapi.web.schema.common import Semester, ProposalCode
from tests.markers import nodatabase
from saltapi.repository.proposal_repository import ProposalRepository


TEST_DATA = "repository/proposal_repository.yaml"

@nodatabase
def test_get_observed_time_return_correct_time(dbconnection: Connection,
                                               testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["get_observed_time"]
    proposal_repository = ProposalRepository(dbconnection)
    observed_time = proposal_repository.get_observed_time(ProposalCode("2020-1-MLT-005"))
    assert data == observed_time


@nodatabase
def test_get_allocated_requested_time_return_correct_allocated_time(dbconnection: Connection,
                                               testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["allocated_requested_time"]
    proposal_repository = ProposalRepository(dbconnection)
    allocated_requested_times = proposal_repository.get_allocated_and_requested_time(
        ProposalCode("2020-1-MLT-005")
    )
    for d in data:
        e_semester = d["semester"]
        allocated_requested_time = [
            a
            for a in allocated_requested_times
            if a["semester"] == e_semester
        ][0]
        assert d == allocated_requested_time


@nodatabase
def test_get_progress_report_return_correct_report(dbconnection: Connection,
                                               testdata: Callable[[str], Any]) -> None:
    e_progress_report = testdata(TEST_DATA)["get_progress_report"]
    proposal_repository = ProposalRepository(dbconnection)
    progress_report = proposal_repository.get_progress_report(
        ProposalCode("2020-1-MLT-005"), Semester("2020-1"))

    assert progress_report["requested_time"] == e_progress_report["requested_time"]
    assert progress_report["transparency"] == e_progress_report["transparency"]
    assert progress_report["description_of_observing_constraints"] == \
           e_progress_report["description_of_observing_constraints"]
    assert progress_report["change_reason"] == \
           e_progress_report["change_reason"]
    assert progress_report["summary_of_proposal_status"] == \
           e_progress_report["summary_of_proposal_status"]
    assert progress_report["strategy_changes"] == e_progress_report["strategy_changes"]
    for p in progress_report["partner_requested_percentages"]:
        partner_code = p["code"]
        requester_amount = [
            r for r in e_progress_report["partner_requested_percentages"]
            if r["code"] == partner_code
        ][0]
        assert  p == requester_amount

@nodatabase
def test_get_progress_report_return_none_if_no_progress_report(dbconnection: Connection,
                                               testdata: Callable[[str], Any]) -> None:
    e_progress_report = testdata(TEST_DATA)["get_progress_report"]
    proposal_repository = ProposalRepository(dbconnection)
    progress_report = proposal_repository.get_progress_report(
        ProposalCode("2020-1-MLT-005"), Semester("2019-2"))

    assert progress_report is None
