from app.schemas.oil.responses import OilSeriesResponse
from app.services.oil.oil_series_service import OilSeriesService


class ListOilSeriesUseCase:
    def __init__(self, oil_series_service: OilSeriesService) -> None:
        self.oil_series_service = oil_series_service

    async def execute(self) -> list[OilSeriesResponse]:
        all_series = await self.oil_series_service.get_all()
        return [OilSeriesResponse.model_validate(oil_series) for oil_series in all_series]
