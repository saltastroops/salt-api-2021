from typing import Any, Dict, List,Optional

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

    def get_masks_in_magazine(self, mask_type: Optional[str]) -> List[str]:
        """The list of masks in the magazine."""
        return self.rss_repository.get_mask_in_magazine(mask_type)

    def get_mos_mask_metadata(self, semesters: List[str]) -> List[Dict[str, Any]]:
        """The list of MOS metadata."""
        return self.rss_repository.get_mos_masks_metadata(semesters)

    def update_mos_mask_metadata(self, mos_mask_metadata: dict[str, Any]) -> Dict[str, Any]:
        """Update MOS mask metadata"""
        return self.rss_repository.update_mos_mask_metadata(mos_mask_metadata)
