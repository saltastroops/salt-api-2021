from typing import Any

from saltapi.repository.finding_chart_repository import FindingChartRepository


class FindingChartService:
    def __init__(self, finding_chart_repository: FindingChartRepository):
        self.finding_chart_repository = finding_chart_repository

    def get_finding_chart(self, finding_chart_id: int) -> Any:

        """
        Return a finding chart for a given id
        """
        return self.finding_chart_repository.get(finding_chart_id)
