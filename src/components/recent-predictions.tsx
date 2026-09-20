import { History } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { RecentPrediction } from "@/lib/api";

type RecentPredictionsProps = {
  items: RecentPrediction[];
  dayNames: string[];
};

export function RecentPredictions({ items, dayNames }: RecentPredictionsProps) {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="size-5 text-emerald-700" />
          Recent predictions
        </CardTitle>
        <CardDescription>
          Last few inference calls in this running session (in-memory, no database).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="rounded-lg border border-dashed px-4 py-8 text-center text-sm text-muted-foreground">
            No predictions yet. Submit the form to see recent session estimates here.
          </div>
        ) : (
          <ul className="space-y-3">
            {items.map((item, index) => (
              <li
                key={`${item.station_id}-${item.hour_of_day}-${index}`}
                className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
              >
                <div>
                  <p className="font-medium capitalize">
                    {item.station_id} · {item.charger_type.replace("_", " ")}
                  </p>
                  <p className="text-muted-foreground">
                    {dayNames[item.day_of_week] ?? "Day"} {item.hour_of_day}:00 · SOC{" "}
                    {item.starting_soc_pct}%
                  </p>
                </div>
                <p className="text-base font-semibold text-emerald-700">
                  {item.predicted_session_energy_kwh.toFixed(1)} kWh
                </p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
