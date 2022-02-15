from typing import Any, Dict, Optional, List

from saltapi.repository.mos_repository import MosRepository


class MosService:
    def __init__(self, mos_repository: MosRepository):
        self.mos_repository = mos_repository

    def get_mos_data(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """
        Return MOS data
        """

        return self.mos_repository.get(semesters)
