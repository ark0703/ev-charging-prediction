"use client";

import { useMemo, useState } from "react";
import { Zap } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { PredictRequest, PredictResponse, SchemaResponse } from "@/lib/api";

type PredictorFormProps = {
  schema: SchemaResponse;
  onSubmit: (payload: PredictRequest) => Promise<void>;
  loading: boolean;
  lastPrediction: PredictResponse | null;
};

const defaultValues = {
  hour_of_day: 18,
  day_of_week: 2,
  station_id: "downtown",
  charger_type: "dc_fast",
  vehicle_battery_kwh: 75,
  starting_soc_pct: 35,
  ambient_temp_c: 18,
  station_occupancy_pct: 55,
};

export function PredictorForm({
  schema,
  onSubmit,
  loading,
  lastPrediction,
}: PredictorFormProps) {
  const [form, setForm] = useState(defaultValues);

  const chargerLabel = useMemo(
    () => (form.charger_type === "dc_fast" ? "DC fast (150 kW)" : "Level 2 (11 kW)"),
    [form.charger_type]
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onSubmit(form);
  };

  const updateNumber = (key: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [key]: Number(value) }));
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="size-5 text-emerald-700" />
          Session inputs
        </CardTitle>
        <CardDescription>
          Adjust station, vehicle, and environmental features to predict delivered session energy.
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="grid gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="hour">Hour of day</Label>
            <Input
              id="hour"
              type="number"
              min={0}
              max={23}
              value={form.hour_of_day}
              onChange={(e) => updateNumber("hour_of_day", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="day">Day of week</Label>
            <Select
              value={String(form.day_of_week)}
              onValueChange={(value) =>
                setForm((current) => ({ ...current, day_of_week: Number(value) }))
              }
            >
              <SelectTrigger id="day" className="w-full">
                <SelectValue placeholder="Select day" />
              </SelectTrigger>
              <SelectContent>
                {schema.day_names.map((day, index) => (
                  <SelectItem key={day} value={String(index)}>
                    {day}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="station">Station</Label>
            <Select
              value={form.station_id}
              onValueChange={(value) => {
                if (!value) return;
                setForm((current) => ({ ...current, station_id: value }));
              }}
            >
              <SelectTrigger id="station" className="w-full">
                <SelectValue placeholder="Select station" />
              </SelectTrigger>
              <SelectContent>
                {schema.stations.map((station) => (
                  <SelectItem key={station} value={station}>
                    {station.charAt(0).toUpperCase() + station.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="charger">Charger type</Label>
            <Select
              value={form.charger_type}
              onValueChange={(value) => {
                if (!value) return;
                setForm((current) => ({ ...current, charger_type: value }));
              }}
            >
              <SelectTrigger id="charger" className="w-full">
                <SelectValue placeholder="Select charger" />
              </SelectTrigger>
              <SelectContent>
                {schema.charger_types.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type === "dc_fast" ? "DC fast" : "Level 2"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="battery">Vehicle battery (kWh)</Label>
            <Input
              id="battery"
              type="number"
              min={20}
              max={150}
              step={0.1}
              value={form.vehicle_battery_kwh}
              onChange={(e) => updateNumber("vehicle_battery_kwh", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="soc">Starting state of charge (%)</Label>
            <Input
              id="soc"
              type="number"
              min={5}
              max={95}
              step={0.1}
              value={form.starting_soc_pct}
              onChange={(e) => updateNumber("starting_soc_pct", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="temp">Ambient temperature (°C)</Label>
            <Input
              id="temp"
              type="number"
              min={-15}
              max={45}
              step={0.1}
              value={form.ambient_temp_c}
              onChange={(e) => updateNumber("ambient_temp_c", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="occupancy">Station occupancy (%)</Label>
            <Input
              id="occupancy"
              type="number"
              min={0}
              max={100}
              step={0.1}
              value={form.station_occupancy_pct}
              onChange={(e) => updateNumber("station_occupancy_pct", e.target.value)}
            />
          </div>
        </CardContent>

        <CardFooter className="flex flex-col items-start gap-4 border-t pt-6">
          <div className="text-sm text-muted-foreground">
            Using {chargerLabel} at {form.station_id} with {form.starting_soc_pct}% starting SOC.
          </div>
          <Button type="submit" disabled={loading} className="w-full sm:w-auto">
            {loading ? "Predicting…" : "Predict session energy"}
          </Button>
          {lastPrediction && (
            <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
              {lastPrediction.summary}
            </p>
          )}
        </CardFooter>
      </form>
    </Card>
  );
}
