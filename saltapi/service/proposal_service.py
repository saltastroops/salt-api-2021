import pathlib
from datetime import datetime

import pdfkit
from typing import Dict, List, Any

from dateutil.relativedelta import relativedelta

from saltapi.exceptions import NotFoundError
from saltapi.repository.proposal_repository import ProposalRepository
from saltapi.service.create_html import create_html
from saltapi.service.proposal import Proposal, ProposalListItem
from saltapi.service.user import User
from saltapi.settings import get_settings
from saltapi.util import semester_start, next_semester
from saltapi.web.schema.common import Semester, ProposalCode


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

    def insert_proposal_progress(
            self,
            proposal_code: ProposalCode,
            progress_report_data: Dict[str, Any]
    ):
        semester = next_semester()
        self.repository.insert_progress_report(
            progress_report_data, proposal_code, semester)

        requested_time = progress_report_data["requested_time"]
        for rp in progress_report_data["requested_percentages"]:
            partner_code = rp["partner_code"]
            partner_percentage = rp["partner_percentage"]
            time_requested_per_partner = requested_time * (partner_percentage / 100)
            self.repository.insert_progress_report_requested_time(
                proposal_code=proposal_code,
                semester=semester,
                partner_code=partner_code,
                requested_time_percent=partner_percentage,
                requested_time_amount=time_requested_per_partner
            )
        self.repository.insert_observing_conditions(
            proposal_code=proposal_code,
            semester=semester,
            seeing=progress_report_data["maximum_seeing"],
            transparency=progress_report_data["transparency"],
            observing_conditions_description=progress_report_data["observing_constraints"]
        )

    def create_progress_report_pdf(
            self,
            proposal_code: str,
            semester: str,
            new_request: Dict["str", Any]
    ):

        previous_allocated_requested = self.repository.get_allocated_requested_time(
            proposal_code)
        previous_observed_time = self.repository.get_observed_time(proposal_code)
        previous_requests = []
        for ar in previous_allocated_requested:
            for ot in previous_observed_time:
                if ot["semester"] == ar["semester"]:
                    previous_requests.append({
                        "semester": ar["semester"],
                        "requested_time": ar["requested_time"],
                        "allocated_time": ar["allocated_time"],
                        "observed_time": ot["observed_time"]
                    })
        create_html(
            proposal_code=proposal_code,
            semester=semester,
            previous_requests=previous_requests,
            previous_conditions=self.repository.get_observing_conditions(proposal_code, semester),
            new_request=new_request
        )
        output_file = "ProposalProgressReport.pdf"
        with open('./pdf_report.html') as f:
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': "UTF-8",
                'no-outline': None
            }
            pdfkit.from_file(f, output_file, options=options)

    def get_progress_report(self, proposal_code: ProposalCode, semester: Semester) -> \
            Dict[str, any]:
        return self.repository.get_progress_report(proposal_code, semester)

    def get_previous_time_requests(self, proposal_code: ProposalCode) -> \
            List[Dict[str, any]]:
        return self.repository.get_previous_time_requests(proposal_code)
