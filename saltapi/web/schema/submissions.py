from pydantic import UUID4, BaseModel, Field


class SubmissionIdentifier(BaseModel):
    submission_identifier: UUID4 = Field(
        ...,
        title="Submission identifier",
        description="Unique identifier for the submission",
    )
