from typing import Any, Dict, List, Optional

from saltapi.repository.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def get_masks_in_magazine(self, mask_type: Optional[str]) -> List[str]:
        """The list of masks in the magazine."""
        return self.instrument_repository.get_masks_in_magazine(mask_type)

    def get_mos_mask_metadata(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """The list of MOS masks metadata."""
        return self.instrument_repository.get_mos_mask_metadata(semesters)

    def update_mos_mask_metadata(
        self, mos_mask_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update slit mask information"""
        return self.instrument_repository.update_mos_mask_metadata(mos_mask_metadata)
