import pathlib
import re
import subprocess  # nosec
import tempfile
import threading
import zipfile
from datetime import datetime
from typing import Any, Optional, cast

from defusedxml.ElementTree import fromstring
from fastapi import UploadFile

from saltapi.exceptions import ValidationError
from saltapi.repository.database import engine
from saltapi.repository.submission_repository import SubmissionRepository
from saltapi.service.submission import SubmissionMessageType, SubmissionStatus
from saltapi.service.user import User
from saltapi.settings import Settings

settings = Settings()


class SubmissionService:
    def __init__(self, submission_repository: SubmissionRepository):
        self.submission_repository = submission_repository

    async def submit_proposal(
        self, submitter: User, proposal: UploadFile, proposal_code: Optional[str]
    ) -> str:
        """
        Submit a proposal.

        Parameters
        ----------
        submitter: User
            The user submitting the proposal.
        proposal: UploadFile
            The uploaded proposal file.
        proposal_code: str, optional
            The proposal code of the submitted proposal.

        Returns
        -------
        str
            The unique identifier for the submission.
        """
        if not zipfile.is_zipfile(proposal.file):
            raise ValidationError("The submitted file must be a zipfile.")

        # Get and check the proposal code for consistency
        xml = await self._extract_xml(proposal)
        if proposal_code:
            xml_proposal_code = SubmissionService._extract_proposal_code(xml)
            if proposal_code != xml_proposal_code:
                raise ValidationError(
                    f"The proposal code passed as query parameter "
                    f"({proposal_code}) is not the same as that "
                    f"given in the proposal file "
                    f"({xml_proposal_code})."
                )

        # Record the submission in the database
        submission_identifier = self.submission_repository.create(
            submitter, proposal_code
        )

        # Save the submitted file content
        saved_file = await self._save_submitted_content(proposal, submission_identifier)

        # Submit the proposal
        self.submission_repository.create_log_entry(
            submission_identifier=submission_identifier,
            message_type=SubmissionMessageType.INFO,
            message="Calling the submission script.",
        )
        t = threading.Thread(
            target=SubmissionService._perform_submission,
            args=[saved_file, proposal_code, submission_identifier, submitter],
        )
        t.start()
        return submission_identifier

    @staticmethod
    async def _extract_xml(proposal: UploadFile) -> str:
        await proposal.seek(0)
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

    @staticmethod
    def _extract_proposal_code(xml: str) -> Optional[str]:
        root = fromstring(xml)
        if re.match(r"([{].*[}])?Proposal$", root.tag):
            return str(root.attrib.get("code"))
        else:
            return None

    @staticmethod
    def _perform_submission(
        saved_file: pathlib.Path,
        proposal_code: Optional[str],
        submission_identifier: str,
        submitter: User,
    ) -> int:
        """Execute the submission."""
        return_code = SubmissionService._call_submission_tool(
            saved_file=saved_file,
            proposal_code=proposal_code,
            submission_identifier=submission_identifier,
            submitter=submitter,
        )

        # As this command is running in a separate thread, it needs its own database
        # connection.
        connection = engine.connect()
        submission_repository = SubmissionRepository(connection)
        submission = submission_repository.get(submission_identifier)

        # Make sure the submission is marked as finished in the database
        if submission["finished_at"] is None:
            if return_code:
                submission_repository.create_log_entry(
                    submission_identifier=submission_identifier,
                    message_type=SubmissionMessageType.ERROR,
                    message="The submission request has failed.",
                )
                submission_repository.finish(
                    submission_identifier, SubmissionStatus.FAILED
                )
            else:
                submission_repository.create_log_entry(
                    submission_identifier=submission_identifier,
                    message_type=SubmissionMessageType.ERROR,
                    message="It is unclear whether the submission request bas been "
                    "successful.",
                )
                submission_repository.finish(
                    submission_identifier, SubmissionStatus.FAILED
                )

        return return_code

    @staticmethod
    def _call_submission_tool(
        saved_file: pathlib.Path,
        proposal_code: Optional[str],
        submission_identifier: str,
        submitter: User,
    ) -> int:
        command_string = SubmissionService._submission_command(
            saved_file=saved_file,
            submission_identifier=submission_identifier,
            submitter=submitter,
            proposal_code=proposal_code,
        )
        command = command_string.split(" ")
        if proposal_code:
            command.insert(-1, "-proposalCode")
            command.insert(-1, proposal_code)
        completed_process = subprocess.run(command)  # nosec
        return completed_process.returncode

    @staticmethod
    def _submission_command(
        saved_file: pathlib.Path,
        submitter: User,
        proposal_code: Optional[str],
        submission_identifier: str,
    ) -> str:
        """Generate the command for submitting the proposal."""
        # Ensure the proposal code and username are safe.
        if proposal_code and not re.match(r"^[\w-]+$", proposal_code):
            raise ValueError(
                "The proposal code must only contain word characters and " "dashes."
            )
        if not re.match(r"^[\w-]+$", submitter.username):
            raise ValueError(
                "The username must only contain word characters and " "dashes."
            )

        log_name = SubmissionService._mapping_log_name(proposal_code)
        sentry_dsn = f"-sentryDSN {settings.sentry_dsn}" if settings.sentry_dsn else ""
        command = f"""
        {settings.java_command} -Xms85m -Xmx1024m
             -jar {settings.mapping_tool_jar}
             -submissionIdentifier {submission_identifier}
             -access {settings.mapping_tool_database_access_config}
             -log {settings.mapping_tool_log_dir}/{log_name}
             -user {submitter.username}
             -convert {settings.image_conversion_command}
             -save {settings.mapping_tool_proposals_dir}
             -file {saved_file.absolute()}
             {('-proposalCode ' + proposal_code) if proposal_code else ""}
             -piptDir {settings.pipt_dir}
             -server {settings.web_manager_url}
             -ephemerisUrl {settings.ephemeris_url}
             -findingChartGenerationScript {settings.finder_chart_tool}
             -python {settings.python_interpreter}
             {sentry_dsn}
             {settings.mapping_tool_api_key}
        """
        command = re.sub(r"\s+", " ", command)
        command = command.replace("\n", "").strip()
        return command

    @staticmethod
    async def _save_submitted_content(
        content: UploadFile, submission_identifier: str
    ) -> pathlib.Path:
        """
        Save the submitted proposal.

        The path of the generated file is returned.
        """
        await content.seek(0)
        saved_filepath = (
            pathlib.Path(tempfile.gettempdir()) / f"{submission_identifier}.zip"
        )
        saved_filepath.write_bytes(cast(bytes, await content.read()))

        return saved_filepath

    @staticmethod
    def _mapping_log_name(proposal_code: Optional[str]) -> str:
        """Generate the name for the log file."""
        name = f"{proposal_code}-" if proposal_code else ""
        return name + datetime.now().isoformat() + ".log"
