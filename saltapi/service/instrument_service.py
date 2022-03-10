from typing import List, Dict, Any, Optional

from saltapi.repository.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def get_mask_in_magazine(self, mask_type: Optional[str]) -> List[str]:
        """The list of MOS masks in the magazine."""
        return self.instrument_repository.get_masks_in_magazine(mask_type)

    def get_mos_mask_matadata(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """The list of MOS blocks."""

        return self.instrument_repository.get_mos_mask_matadata(semesters)

    def update_mos_mask_matadata(self, mos_mask_matadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update slit mask information"""
        return self.instrument_repository.update_most_mask_matadata(mos_mask_matadata)