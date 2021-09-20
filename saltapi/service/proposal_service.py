from typing import List

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import Proposal, ProposalListItem
from saltapi.service.user import User
from saltapi.web.schema.proposal import ObservationComment


class ProposalService:
    def __init__(self, repository: ProposalRepository):
        self.repository = repository

    def list_proposal_summaries(self) -> List[ProposalListItem]:
        return self.repository.list()

    def get_proposal(self, proposal_code: str) -> Proposal:
        return self.repository.get(proposal_code)

    def get_observation_comments(self, proposal_code: str) -> List[ObservationComment]:
        return self.repository.get_observation_comments(proposal_code)

    def add_observation_comment(self, proposal_code: str, comment: str, user: User) -> None:
        # TODO only SA's, SO's and investigators can add a comment
        self.repository.add_observation_comment(proposal_code, comment, user)
