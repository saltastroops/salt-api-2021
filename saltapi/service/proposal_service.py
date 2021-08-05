from typing import List

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import Proposal, ProposalListItem


class ProposalService:
    def __init__(self, repository: ProposalRepository):
        self.repository = repository

    def list_proposal_summaries(self) -> List[ProposalListItem]:
        return self.repository.list()

    def get_proposal(self, proposal_code: str) -> Proposal:
        return self.repository.get(proposal_code)
