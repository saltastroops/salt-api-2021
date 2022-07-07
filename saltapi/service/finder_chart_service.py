from typing import Any

from saltapi.repository.finder_chart_repository import FinderChartRepository


class FinderChartService:
    def __init__(self, finder_chart_repository: FinderChartRepository):
        self.finder_chart_repository = finder_chart_repository

    def get_finder_chart(self, finder_chart_id: int) -> Any:

        """
        Return a finder chart for a given id
        """
        return self.finder_chart_repository.get(finder_chart_id)
