export type PredictRequest = {
  hour_of_day: number;
  day_of_week: number;
  station_id: string;
  charger_type: string;
  vehicle_battery_kwh: number;
  starting_soc_pct: number;
  ambient_temp_c: number;
  station_occupancy_pct: number;
};

export type PredictResponse = {
  predicted_session_energy_kwh: number;
  confidence_band_kwh: number;
  summary: string;
};

export type ModelMetrics = {
  target: string;
  features: string[];
  train_rows: number;
  test_rows: number;
  rmse_kwh: number;
  mae_kwh: number;
  r2: number;
  model: string;
};

export type SchemaResponse = {
  stations: string[];
  charger_types: string[];
  day_names: string[];
  target: string;
  features: string[];
};

export type RecentPrediction = {
  predicted_session_energy_kwh: number;
  hour_of_day: number;
  day_of_week: number;
  station_id: string;
  charger_type: string;
  starting_soc_pct: number;
};

const API_BASE = "/api/ml";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
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
}

export function getMetrics() {
  return fetchJson<ModelMetrics>("/metrics");
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
  return fetchJson<{ status: string; model_loaded: boolean }>("/health");
}
