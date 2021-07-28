from sqlalchemy.engine import Connection

from saltapi.service.instrument import BVIT, HRS, RSS, Salticam


class InstrumentRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_salticam(self, salticam_id: int) -> Salticam:
        """Return a Salticam setup."""
        return f"Salticam with id {salticam_id}"

    def get_rss(self, rss_id: int) -> RSS:
        """Return an RSS setup."""
        return f"RSS with id {rss_id}"

    def get_hrs(self, hrs_id: int) -> HRS:
        """Return an HRS setup."""
        return f"HRS with id {hrs_id}"

    def get_bvit(self, bvit_id: int) -> BVIT:
        """Return a BVIT setup."""
        return f"BVIT with id {bvit_id}"
