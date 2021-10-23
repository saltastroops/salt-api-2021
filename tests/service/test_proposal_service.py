from typing import List, cast

import pytest

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import ProposalListItem
from saltapi.service.proposal_service import ProposalService


class FakeProposalRepository:
    def list(
        self, username: str, from_semester: str, to_semester: str, limit: str
    ) -> List[ProposalListItem]:
        return [
            cast(ProposalListItem, from_semester),
            cast(ProposalListItem, to_semester),
            cast(ProposalListItem, limit),
        ]


def create_proposal_repository() -> ProposalService:
    proposal_repository = FakeProposalRepository()
    proposal_service = ProposalService(cast(ProposalRepository, proposal_repository))
    return proposal_service


def test_list_proposal_summaries_returns_correct_proposals() -> None:
    proposal_service = create_proposal_repository()
    assert proposal_service.list_proposal_summaries(
        username="someone", from_semester="2019-1", to_semester="2020-1"
    ) == ["2019-1", "2020-1", 1000]
    assert proposal_service.list_proposal_summaries(
        username="someone", from_semester="2019-1"
    ) == ["2019-1", "2099-2", 1000]
    assert proposal_service.list_proposal_summaries(
        username="someone", to_semester="2020-1"
    ) == ["2000-1", "2020-1", 1000]
    assert proposal_service.list_proposal_summaries(username="someone", limit=67) == [
        "2000-1",
        "2099-2",
        67,
    ]


def test_list_proposal_summaries_raises_error_for_negative_limit() -> None:
    proposal_service = create_proposal_repository()
    with pytest.raises(ValueError) as excinfo:
        proposal_service.list_proposal_summaries(
            username="someone", from_semester="2019-1", to_semester="2019-2", limit=-1
        )
    assert "negative" in str(excinfo.value)


def test_list_proposal_summaries_raises_error_from_wrong_semester_order() -> None:
    proposal_service = create_proposal_repository()
    with pytest.raises(ValueError) as excinfo:
        proposal_service.list_proposal_summaries(
            username="someone", from_semester="2019-1", to_semester="2018-2"
        )
    assert "semester" in str(excinfo.value)
