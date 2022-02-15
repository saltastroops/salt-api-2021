from typing import List

from saltapi.repository.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, instrument_repository: InstrumentRepository):
        self.instrument_repository = instrument_repository

    def get_mos_mask_in_magazine(self) -> List[str]:
        """The list of MOS masks in the magazine."""
        return self.instrument_repository.get_mos_mask_in_magazine()