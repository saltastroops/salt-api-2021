from pathlib import Path
from typing import Tuple

from saltapi.repository.finder_chart_repository import FinderChartRepository
from saltapi.settings import get_settings


class FinderChartService:
    def __init__(self, finder_chart_repository: FinderChartRepository):
        self.finder_chart_repository = finder_chart_repository

    def get_finder_chart(self, finder_chart_id: int) -> Tuple[str, Path]:

        """
        Return the proposal code and path of a finder chart with a given id.
        """
        proposals_directory = get_settings().proposals_dir
        proposal_code, finder_chart_path = self.finder_chart_repository.get(
            finder_chart_id
        )
        full_finder_chart_path = proposals_directory / proposal_code / finder_chart_path
        return proposal_code, Path(full_finder_chart_path).resolve()
