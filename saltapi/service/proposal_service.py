from typing import List

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import ProposalSummary


class ProposalService:
    def __init__(self, repository: ProposalRepository):
        self.repository = repository

    def list_proposal_summaries(self) -> List[ProposalSummary]:
        return self.repository.list()
