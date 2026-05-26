import { useQuery } from "@tanstack/react-query";

import {
  getOilPricesRequest,
  listOilSeriesRequest,
  listOilUnitsRequest,
  type OilPriceFilters,
} from "@/api/oil";

const OIL_SERIES_QUERY_KEY = ["oil", "series"] as const;
const OIL_UNITS_QUERY_KEY = ["oil", "units"] as const;
const OIL_PRICES_QUERY_KEY_PREFIX = ["oil", "prices"] as const;

export function useOilSeries() {
  return useQuery({
    queryKey: OIL_SERIES_QUERY_KEY,
    queryFn: listOilSeriesRequest,
  });
}

export function useOilUnits() {
  return useQuery({
    queryKey: OIL_UNITS_QUERY_KEY,
    queryFn: listOilUnitsRequest,
  });
}

export function useOilPrices(filters: OilPriceFilters) {
  return useQuery({
    queryKey: [...OIL_PRICES_QUERY_KEY_PREFIX, filters],
    queryFn: () => getOilPricesRequest(filters),
  });
}
