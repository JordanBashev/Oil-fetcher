import { apiClient } from "./client";

export type OilSeries = {
  id: string;
  series: string;
  series_description: string;
  duoarea: string;
  area_name: string;
  product: string;
  product_name: string;
  process: string;
  process_name: string;
  units: string;
};

export type OilPricePoint = {
  period: string;
  value: number;
};

export type OilPriceSeries = {
  series_code: string;
  series_description: string;
  points: OilPricePoint[];
};

export type OilPricesResponse = {
  is_aggregated: boolean;
  matched_series_count: number;
  date_from: string | null;
  date_to: string | null;
  unit_label: string | null;
  series: OilPriceSeries[];
};

export type OilPriceFilters = {
  oil_series_id?: string;
  duoarea?: string;
  product?: string;
  process?: string;
  units?: string;
  date_from?: string;
  date_to?: string;
};

export async function listOilSeriesRequest(): Promise<OilSeries[]> {
  const { data } = await apiClient.get<OilSeries[]>("/oil/series");
  return data;
}

export async function listOilUnitsRequest(): Promise<string[]> {
  const { data } = await apiClient.get<string[]>("/oil/units");
  return data;
}

export async function getOilPricesRequest(filters: OilPriceFilters): Promise<OilPricesResponse> {
  const { data } = await apiClient.get<OilPricesResponse>("/oil/prices", { params: filters });
  return data;
}
