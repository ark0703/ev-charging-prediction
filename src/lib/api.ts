export type PredictRequest = {
  hour_of_day: number;
  day_of_week: number;
  station_id: string;
  charger_type: string;
  vehicle_battery_kwh: number;
  starting_soc_pct: number;
  target_soc_pct: number;
  ambient_temp_c: number;
  station_occupancy_pct: number;
};

export type PredictResponse = {
  predicted_session_duration_minutes: number;
  human_readable: string;
  energy_kwh: number;
  average_power_kw: number;
  summary: string;
};

export type EstimatorInfo = {
  method: string;
  target: string;
  formula: string;
  energy_formula: string;
  average_power_kw: Record<string, number>;
  features: string[];
  adjustments: string[];
};

export type SchemaResponse = {
  stations: string[];
  charger_types: string[];
  day_names: string[];
  target: string;
  features: string[];
};

export type RecentPrediction = {
  predicted_session_duration_minutes: number;
  human_readable: string;
  hour_of_day: number;
  day_of_week: number;
  station_id: string;
  charger_type: string;
  starting_soc_pct: number;
  target_soc_pct: number;
};

const API_BASE = "/api/ml";
const REQUEST_TIMEOUT_MS = 10000;

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
      cache: "no-store",
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Request failed (${response.status})`);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("Request timed out. Check that the prediction API is running.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export function getEstimatorInfo() {
  return fetchJson<EstimatorInfo>("/metrics");
}

export function getSchema() {
  return fetchJson<SchemaResponse>("/schema");
}

export function getRecentPredictions() {
  return fetchJson<RecentPrediction[]>("/recent");
}

export function predictSession(payload: PredictRequest) {
  return fetchJson<PredictResponse>("/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function checkHealth() {
  return fetchJson<{ status: string; estimator_ready: boolean }>("/health");
}
