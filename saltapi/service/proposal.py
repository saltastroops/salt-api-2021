from typing import Any, NewType

Proposal = Any

# TODO: This to be removed, casting str to this type is more pain than gain
ProposalCode = NewType("ProposalCode", str)

ProposalListItem = Any
