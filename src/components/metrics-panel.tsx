import { Activity, BarChart3, Target } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { ModelMetrics } from "@/lib/api";

type MetricsPanelProps = {
  metrics: ModelMetrics;
  compact?: boolean;
};

function MetricStat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

export function MetricsPanel({ metrics, compact = false }: MetricsPanelProps) {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="size-5 text-emerald-700" />
          {compact ? "Model snapshot" : "Model performance"}
        </CardTitle>
        <CardDescription>
          {metrics.model} trained on {metrics.train_rows.toLocaleString()} sessions, evaluated on{" "}
          {metrics.test_rows.toLocaleString()} held-out sessions.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-3">
          <MetricStat
            label="RMSE"
            value={`${metrics.rmse_kwh.toFixed(2)} kWh`}
            hint="Root mean squared error on test set"
          />
          <MetricStat
            label="MAE"
            value={`${metrics.mae_kwh.toFixed(2)} kWh`}
            hint="Typical absolute prediction error"
          />
          <MetricStat
            label="R²"
            value={metrics.r2.toFixed(3)}
            hint="Variance explained on test set"
          />
        </div>

        {!compact && (
          <>
            <Separator />
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Target className="size-4 text-emerald-700" />
                  Prediction target
                </div>
                <p className="text-sm text-muted-foreground">
                  <code className="rounded bg-muted px-1.5 py-0.5">{metrics.target}</code> — energy
                  delivered during a single charging session.
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Activity className="size-4 text-emerald-700" />
                  Input features
                </div>
                <ul className="grid grid-cols-2 gap-1 text-sm text-muted-foreground">
                  {metrics.features.map((feature) => (
                    <li key={feature} className="rounded bg-muted/40 px-2 py-1">
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
