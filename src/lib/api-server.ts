import type {
  EstimatorInfo,
  RecentPrediction,
  SchemaResponse,
} from "@/lib/api";

const API_BASE = process.env.ML_API_URL ?? "http://127.0.0.1:8765";
const REQUEST_TIMEOUT_MS = 8000;

async function fetchJson<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      signal: controller.signal,
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Request failed (${response.status}) for ${path}`);
    }

    return response.json() as Promise<T>;
  } finally {
    clearTimeout(timeoutId);
  }
}

export type BootstrapData = {
  ok: true;
  apiOnline: boolean;
  schema: SchemaResponse;
  estimator: EstimatorInfo;
  recent: RecentPrediction[];
};

export type BootstrapError = {
  ok: false;
  message: string;
};

export async function loadBootstrapData(): Promise<BootstrapData | BootstrapError> {
  try {
    const health = await fetchJson<{ status: string; estimator_ready: boolean }>("/health");
    const [schema, estimator, recent] = await Promise.all([
      fetchJson<SchemaResponse>("/schema"),
      fetchJson<EstimatorInfo>("/metrics"),
      fetchJson<RecentPrediction[]>("/recent"),
    ]);

    return {
      ok: true,
      apiOnline: health.estimator_ready,
      schema,
      estimator,
      recent,
    };
  } catch (error) {
    const message =
      error instanceof Error && error.name === "AbortError"
        ? "Prediction API timed out. Ensure `npm run dev` is running."
        : error instanceof Error
          ? error.message
          : "Unable to reach the prediction API.";

    return { ok: false, message };
  }
}
