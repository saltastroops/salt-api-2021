from typing import Any, Dict, List

from saltapi.repository.institution_repository import InstitutionRepository


class InstitutionService:
    def __init__(self, repository: InstitutionRepository):
        self.repository = repository

    def get_institutions(self) -> List[Dict[str, Any]]:
        institutions = self.repository.get_institutions()
        return institutions
