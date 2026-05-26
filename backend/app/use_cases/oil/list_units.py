from app.services.oil.oil_series_service import OilSeriesService


class ListUnitsUseCase:
    def __init__(self, oil_series_service: OilSeriesService) -> None:
        self.oil_series_service = oil_series_service

    async def execute(self) -> list[str]:
        return await self.oil_series_service.get_distinct_units()
