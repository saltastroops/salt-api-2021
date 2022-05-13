import pathlib
from typing import Dict, List

from saltapi.exceptions import NotFoundError
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.proposal import Proposal, ProposalListItem
from saltapi.service.user import User
from saltapi.settings import get_settings
from saltapi.util import semester_start


class ProposalService:
    def __init__(self, repository: ProposalRepository):
        self.repository = repository

    def list_proposal_summaries(
        self,
        username: str,
        from_semester: str = "2000-1",
        to_semester: str = "2099-2",
        limit: int = 1000,
    ) -> List[ProposalListItem]:
        """
        Return the list of proposals for a semester range.

        The maximum number of proposals to be returned can be set with the limit
        parameter; the default is 1000.
        """
        if semester_start(from_semester) > semester_start(to_semester):
            raise ValueError(
                "The from semester must not be later than the to semester."
            )

        if limit < 0:
            raise ValueError("The limit must not be negative.")

        return self.repository.list(username, from_semester, to_semester, limit)

    def get_proposal_zip(self, proposal_code: str) -> pathlib.Path:
        """
        Return the file path of proposal zip file.

        Parameters
        ----------
        proposal_code: str
            Proposal code.

        Returns
        -------
        `~pathlib.Path`
            The file path of the proposal zip file.
        """
        proposals_dir = pathlib.Path(get_settings().proposals_dir)
        version = self.repository.get_current_version(proposal_code)
        path = proposals_dir / proposal_code / str(version) / f"{proposal_code}.zip"
        if not path.exists():
            raise NotFoundError("Proposal file not found")
        return path

    def get_proposal(self, proposal_code: str) -> Proposal:
        """
        Return the JSON representation of a proposal.

        Parameters
        ----------
        proposal_code: str
            Proposal code.

        Returns
        -------
        Proposal
            The JSON representation of the proposal.
        """
        return self.repository.get(proposal_code)

    def get_observation_comments(self, proposal_code: str) -> List[Dict[str, str]]:
        return self.repository.get_observation_comments(proposal_code)

    def add_observation_comment(
        self, proposal_code: str, comment: str, user: User
    ) -> Dict[str, str]:
        return self.repository.add_observation_comment(proposal_code, comment, user)
