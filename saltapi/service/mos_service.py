from typing import Any, Dict, Optional

from saltapi.repository.mos_repository import MosRepository


class MosService:
    def __init__(self, mos_repository: MosRepository):
        self.mos_repository = mos_repository

    def get_mos_data(
            self,
            semester: str,
            include_next_semester: Optional[bool],
            include_previous_semester: Optional[bool]) -> Any:
        """
        Return MOS data
        """

        return self.mos_repository.get(
            semester, include_next_semester, include_previous_semester)
