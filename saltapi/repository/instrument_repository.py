from typing import List, Dict, Any

from sqlalchemy.engine import Connection

from saltapi.repository.bvit_repository import BvitRepository
from saltapi.repository.hrs_repository import HrsRepository
from saltapi.repository.rss_repository import RssRepository
from saltapi.repository.salticam_repository import SalticamRepository
from saltapi.service.instrument import BVIT, HRS, RSS, Salticam


class InstrumentRepository:
    def __init__(self, connection: Connection) -> None:
        self.salticam_repository = SalticamRepository(connection)
        self.rss_repository = RssRepository(connection)
        self.hrs_repository = HrsRepository(connection)
        self.bvit_repository = BvitRepository(connection)

    def get_salticam(self, salticam_id: int) -> Salticam:
        """Return a Salticam setup."""
        return self.salticam_repository.get(salticam_id)

    def get_rss(self, rss_id: int) -> RSS:
        """Return an RSS setup."""
        return self.rss_repository.get(rss_id)

    def get_hrs(self, hrs_id: int) -> HRS:
        """Return an HRS setup."""
        return self.hrs_repository.get(hrs_id)

    def get_bvit(self, bvit_id: int) -> BVIT:
        """Return a BVIT setup."""
        return self.bvit_repository.get(bvit_id)

    def get_mos_mask_in_magazine(self) -> List[str]:
        """The list of MOS masks in the magazine."""
        return self.rss_repository.get_mos_mask_in_magazine()

    def get_mos_blocks(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """The list of MOS blocks."""
        return self.rss_repository.get_mos_blocks(semesters)

    def update_slit_mask(self, slit_mask: dict[str, Any]) -> dict[str, Any]:
        """Add or update slit mask cut information"""
        return self.rss_repository.update_slit_mask(slit_mask)
