import type { ForecastJob, ForecastTarget } from "@/api/forecasts";
import type { OilSeries } from "@/api/oil";

export function describeForecastTarget(
  job: Pick<ForecastJob, "oil_series_id" | "units">,
  seriesById?: Map<string, OilSeries>,
): string {
  if (job.oil_series_id) {
    const series = seriesById?.get(job.oil_series_id);
    return series ? series.series_description : "Single series";
  }
  if (job.units) {
    return `Aggregate (${job.units})`;
  }
  return "—";
}

export function jobToTarget(job: Pick<ForecastJob, "oil_series_id" | "units">): ForecastTarget {
  if (job.oil_series_id) {
    return { oil_series_id: job.oil_series_id };
  }
  if (job.units) {
    return { units: job.units };
  }
  return {};
}
