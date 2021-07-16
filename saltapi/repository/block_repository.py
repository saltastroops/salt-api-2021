import json
from pathlib import Path
from typing import Dict, NamedTuple, Union

from sqlalchemy import text
from sqlalchemy.engine import Connection

from saltapi.exceptions import NotFoundError
from saltapi.service.block import Block


class BlockData(NamedTuple):
    path: Path
    status: str
    observation_time: int
    overhead_time: int
    probabilities: Dict[str, Union[float, str]]


class BlockRepository:
    def __init__(self, connection: Connection, proposals_dir: Path) -> None:
        self.connection = connection
        self.proposals_dir = proposals_dir

    def get(self, block_id: int) -> Block:
        """
        Return the block content for a block id.
        """

        block_data = self._block_data(block_id)
        block_path = block_data.path

        if not block_path.exists():
            raise FileNotFoundError()

        with open(block_path) as f:
            block = json.load(f)

        block["status"] = block_data.status
        block["observation_time"] = block_data.observation_time
        block["overhead_time"] = block_data.overhead_time
        block["probabilities"] = block_data.probabilities

        return block

    def _block_data(self, block_id: int) -> BlockData:
        stmt = text(
            """
SELECT PC.Proposal_Code AS proposal_code,
       BC.BlockCode AS block_code,
       CONCAT(S.Year, '-', S.Semester) AS semester,
       BS.BlockStatus AS status,
       B.ObsTime AS observation_time,
       B.OverheadTime AS overhead_time,
       BP.MoonProbability AS moon_probability,
       BP.CompetitionProbability AS competition_probability,
       BP.ObservabilityProbability AS observability_probability,
       BP.SeeingProbability AS seeing_probability,
       BP.AveRanking AS average_ranking,
       BP.TotalProbability AS total_probability
FROM ProposalCode PC
         JOIN Block B on PC.ProposalCode_Id = B.ProposalCode_Id
         JOIN BlockCode BC on B.BlockCode_Id = BC.BlockCode_Id
         JOIN BlockStatus BS ON B.BlockStatus_Id = BS.BlockStatus_Id
         JOIN Proposal P ON B.Proposal_Id = P.Proposal_Id
         JOIN Semester S ON P.Semester_Id = S.Semester_Id
         LEFT JOIN BlockProbabilities BP ON B.Block_Id = BP.Block_Id
WHERE B.Block_Id = :block_id;

        """
        )
        result = self.connection.execute(stmt, {"block_id": block_id})
        row = result.one_or_none()
        if not row:
            raise NotFoundError(f"Unknown block id: {block_id}")
        proposal_code = row["proposal_code"]
        block_code = row["block_code"]
        semester = row["semester"]
        status = row["status"]
        observation_time = row["observation_time"]
        overhead_time = row["overhead_time"]
        probabilities = {
            "moon_probability": row["moon_probability"],
            "competition_probability": row["competition_probability"],
            "observability_probability": row["observability_probability"],
            "seeing_probability": row["seeing_probability"],
            "average_ranking": row["average_ranking"],
            "total_probability": row["total_probability"],
        }
        path = (
            self.proposals_dir
            / proposal_code
            / "Included"
            / f"Block-{block_code}-{semester}.json"
        )

        return BlockData(
            path=path,
            status=status,
            observation_time=observation_time,
            overhead_time=overhead_time,
            probabilities=probabilities,
        )
