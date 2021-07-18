from typing import Any, NamedTuple


class ContactDetails(NamedTuple):
    given_name: str
    family_name: str
    email: str


class ProposalSummary(NamedTuple):
    id: int
    proposal_code: str
    semester: str
    title: str
    phase: int
    status: str
    proposal_type: str
    principal_investigator: ContactDetails
    principal_contact: ContactDetails
    liaison_astronomer: ContactDetails


Proposal = Any
