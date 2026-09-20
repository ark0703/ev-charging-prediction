"use client";

import { useEffect, useState } from "react";
import { AlertCircle, BatteryCharging, Gauge, Loader2 } from "lucide-react";

import { PredictorForm } from "@/components/predictor-form";
import { MetricsPanel } from "@/components/metrics-panel";
import { RecentPredictions } from "@/components/recent-predictions";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  checkHealth,
  getMetrics,
  getRecentPredictions,
  getSchema,
  predictSession,
  type ModelMetrics,
  type PredictRequest,
  type PredictResponse,
  type RecentPrediction,
  type SchemaResponse,
} from "@/lib/api";

export function PredictorApp() {
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [recent, setRecent] = useState<RecentPrediction[]>([]);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState(false);

  const refreshRecent = async () => {
    try {
      const items = await getRecentPredictions();
      setRecent(items);
    } catch {
      // Non-fatal if recent list fails after a successful prediction.
    }
  };

  useEffect(() => {
    let active = true;

    async function bootstrap() {
      setLoading(true);
      setError(null);

      try {
        const health = await checkHealth();
        if (!active) return;
        setApiOnline(health.model_loaded);

        const [schemaData, metricsData, recentData] = await Promise.all([
          getSchema(),
          getMetrics(),
          getRecentPredictions(),
        ]);

        if (!active) return;
        setSchema(schemaData);
        setMetrics(metricsData);
        setRecent(recentData);
      } catch (err) {
        if (!active) return;
        setError(
          err instanceof Error
            ? err.message
            : "Unable to reach the prediction API. Start the dev server with npm run dev."
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    bootstrap();
    return () => {
      active = false;
    };
  }, []);

  const handlePredict = async (payload: PredictRequest) => {
    setPredicting(true);
    setError(null);

    try {
      const result = await predictSession(payload);
      setPrediction(result);
      await refreshRecent();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed.");
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8 md:px-6">
        <Skeleton className="h-10 w-72" />
        <Skeleton className="h-5 w-full max-w-2xl" />
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <Skeleton className="h-[520px] w-full" />
          <Skeleton className="h-[520px] w-full" />
        </div>
      </div>
    );
  }

  if (error && !schema) {
    return (
      <div className="mx-auto flex w-full max-w-3xl px-4 py-16 md:px-6">
        <Alert variant="destructive" className="w-full">
          <AlertCircle />
          <AlertTitle>Prediction service unavailable</AlertTitle>
          <AlertDescription>
            {error} Run <code className="rounded bg-muted px-1.5 py-0.5">npm run dev</code> to
            start the FastAPI backend and Next.js UI together.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8 md:px-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary" className="gap-1">
              <BatteryCharging className="size-3.5" />
              Supervised ML
            </Badge>
            <Badge variant={apiOnline ? "default" : "destructive"}>
              {apiOnline ? "Model loaded" : "Model missing"}
            </Badge>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            EV Charging Session Predictor
          </h1>
          <p className="max-w-2xl text-muted-foreground">
            Estimate how much energy a charging session will deliver based on station context,
            vehicle state, weather, and time-of-day patterns learned from synthetic session data.
          </p>
        </div>
        {prediction && (
          <div className="rounded-xl border bg-card p-4 shadow-sm">
            <p className="text-sm text-muted-foreground">Latest prediction</p>
            <p className="flex items-center gap-2 text-3xl font-semibold text-emerald-700">
              <Gauge className="size-7" />
              {prediction.predicted_session_energy_kwh.toFixed(1)} kWh
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              ± {prediction.confidence_band_kwh.toFixed(1)} kWh typical error band
            </p>
          </div>
        )}
      </header>

      {error && (
        <Alert variant="destructive">
          <AlertCircle />
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="predict" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="predict">Predict session</TabsTrigger>
          <TabsTrigger value="performance">Model performance</TabsTrigger>
        </TabsList>

        <TabsContent value="predict" className="mt-6">
          <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
            {schema ? (
              <PredictorForm
                schema={schema}
                onSubmit={handlePredict}
                loading={predicting}
                lastPrediction={prediction}
              />
            ) : (
              <Alert>
                <AlertTitle>No schema available</AlertTitle>
                <AlertDescription>
                  The API did not return feature metadata. Retrain the model and restart the dev
                  server.
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-6">
              {metrics && <MetricsPanel metrics={metrics} compact />}
              <RecentPredictions items={recent} dayNames={schema?.day_names ?? []} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="mt-6">
          {metrics ? (
            <MetricsPanel metrics={metrics} />
          ) : (
            <Alert>
              <AlertTitle>No metrics yet</AlertTitle>
              <AlertDescription>
                Train the model with <code className="rounded bg-muted px-1.5 py-0.5">npm run train</code>{" "}
                to generate evaluation metrics.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>

      {predicting && (
        <div className="fixed inset-x-0 bottom-4 mx-auto flex w-fit items-center gap-2 rounded-full border bg-background px-4 py-2 shadow-lg">
          <Loader2 className="size-4 animate-spin text-emerald-700" />
          <span className="text-sm">Running inference…</span>
        </div>
      )}
    </div>
  );
}
