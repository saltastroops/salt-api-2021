from typing import List, Dict, Any

from saltapi.repository.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def get_mos_mask_in_magazine(self) -> List[str]:
        """The list of MOS masks in the magazine."""
        return self.instrument_repository.get_mos_mask_in_magazine()

    def get_mos_data(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """
        Return MOS data
        """

        return self.instrument_repository.get_mos_block(semesters)