from typing import List, Dict, Any

from saltapi.repository.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def get_mos_mask_in_magazine(self) -> List[str]:
        """The list of MOS masks in the magazine."""
        return self.instrument_repository.get_mos_mask_in_magazine()

    def get_mos_blocks(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """The list of MOS blocks."""

        return self.instrument_repository.get_mos_blocks(semesters)

    def update_slit_mask(self, slit_mask: Dict[str, Any]) -> Dict[str, Any]:
        """Add or update slit mask cut information"""
        return self.instrument_repository.update_slit_mask(slit_mask)