from datetime import date
from typing import List, Optional, Dict

from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import Proposal, ProposalListItem
from saltapi.web.schema.common import Message
from saltapi.web.schema.proposal import DataReleaseDate


class ProposalService:
    def __init__(self, repository: ProposalRepository):
        self.repository = repository

    def list_proposal_summaries(self) -> List[ProposalListItem]:
        return self.repository.list()

    def get_proposal(self, proposal_code: str) -> Proposal:
        return self.repository.get(proposal_code)

    def get_data_release_date(
            self,
            proposal_code: str
    ) -> DataReleaseDate:
        return self.repository.get_data_release_date(proposal_code)

    def update_data_release_date(self, proposal_code: str, release_date: date) -> Message:
        print("Passing...")
        return self.repository.update_data_release_date(proposal_code, release_date)
