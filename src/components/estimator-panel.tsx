import { Activity, Calculator, Target } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { EstimatorInfo } from "@/lib/api";

type EstimatorPanelProps = {
  estimator: EstimatorInfo;
  compact?: boolean;
};

function InfoStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

export function EstimatorPanel({ estimator, compact = false }: EstimatorPanelProps) {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="size-5 text-emerald-700" />
          {compact ? "Formula snapshot" : "How the estimate works"}
        </CardTitle>
        <CardDescription>
          Uses average charger power and energy needed — no machine learning model required.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <InfoStat label="Level 2 power" value={`${estimator.average_power_kw.level2} kW`} />
          <InfoStat label="DC fast power" value={`${estimator.average_power_kw.dc_fast} kW`} />
        </div>

        {!compact && (
          <>
            <Separator />
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Target className="size-4 text-emerald-700" />
                  Target
                </div>
                <p className="text-sm text-muted-foreground">
                  <code className="rounded bg-muted px-1.5 py-0.5">{estimator.target}</code>
                </p>
                <p className="text-sm text-muted-foreground">{estimator.formula}</p>
                <p className="text-sm text-muted-foreground">{estimator.energy_formula}</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Activity className="size-4 text-emerald-700" />
                  Adjustments
                </div>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {estimator.adjustments.map((item) => (
                    <li key={item} className="rounded bg-muted/40 px-2 py-1">
                      {item}
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
