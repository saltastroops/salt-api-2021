import re
import zipfile
from typing import Any, Optional, cast

from defusedxml.ElementTree import fromstring
from fastapi import UploadFile

from saltapi.exceptions import ValidationError
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.service.user import User


class SubmissionService:
    def __init__(self, submission_repository: SubmissionRepository):
        self.submission_repository = submission_repository

    def submit_proposal(
        self, user: User, proposal: UploadFile, proposal_code: Optional[str]
    ) -> None:
        if not zipfile.is_zipfile(proposal.file):
            raise ValidationError("The submitted file must be a zipfile.")

        # Get and check the proposal code for consistency
        xml = self._extract_xml(proposal)
        if proposal_code:
            xml_proposal_code = self._extract_proposal_code(xml)
            if proposal_code != xml_proposal_code:
                raise ValidationError(
                    f"The proposal code passed as query parameter "
                    f"({proposal_code}) is not the same as that "
                    f"given in the proposal file "
                    f"({xml_proposal_code})."
                )

        # Record the submission in the database
        self.submission_repository.create_submission(user, proposal_code)

    def _extract_xml(self, proposal: UploadFile) -> str:
        proposal.file.seek(0)
        with zipfile.ZipFile(cast(Any, proposal.file)._file) as z:
            contents = z.namelist()
            if "Proposal.xml" in contents:
                return z.read("Proposal.xml").decode("UTF-8")
            elif "Blocks.xml" in contents:
                return z.read("Blocks.xml").decode("UTF-8")
            else:
                raise ValidationError(
                    "The zipfile must contain a file Proposal.xml "
                    "or a file Blocks.xml."
                )

    def _extract_proposal_code(self, xml: str) -> Optional[str]:
        root = fromstring(xml)
        if re.match(r"([{].*[}])?Proposal$", root.tag):
            return str(root.attrib.get("code"))
        else:
            return None
