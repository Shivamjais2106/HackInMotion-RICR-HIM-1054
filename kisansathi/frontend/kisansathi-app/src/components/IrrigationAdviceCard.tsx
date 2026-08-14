/**
 * IrrigationAdviceCard — KisanSathi
 * Shows farm-profile-specific irrigation schedule pulled from
 * GET /api/farm-profile/irrigation-advice
 *
 * Author: Sumit Dangi
 */

import { useEffect, useState } from "react";
import { getAPIBaseURL, getAuthHeaders } from "@/utils/api";

interface IrrigationData {
  farm_location: string;
  soil_type: string;
  active_crops: string[];
  irrigation_type: string;
  weather: { temperature: number; humidity: number; rainfall_mm: number };
  weather_live: boolean;
  weather_warning?: string;
  irrigation_need_mm_per_day: number;
  schedule: string[];
  water_retention: string;
}

const riskColor = (need: number) => {
  if (need > 4) return "text-red-700 bg-red-50 border-red-200";
  if (need > 2) return "text-yellow-700 bg-yellow-50 border-yellow-200";
  return "text-green-700 bg-green-50 border-green-200";
};

const riskLabel = (need: number) => {
  if (need > 4) return "🔴 High Irrigation Need";
  if (need > 2) return "🟡 Moderate";
  return "🟢 Low — Adequate Moisture";
};

export default function IrrigationAdviceCard() {
  const [data, setData] = useState<IrrigationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const ctrl = new AbortController();
    fetch(`${getAPIBaseURL()}/farm-profile/irrigation-advice`, {
      headers: getAuthHeaders(),
      signal: ctrl.signal,
    })
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.json();
      })
      .then((d) => {
        if (d.success) setData(d);
        else setError(d.error || "Could not load irrigation advice.");
      })
      .catch((e) => {
        if (e.name !== "AbortError")
          setError("Set up your Farm Profile first to get irrigation advice.");
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, []);

  if (loading) return <div className="animate-pulse h-32 bg-blue-50 rounded-xl" />;

  if (error) return (
    <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 text-orange-700 text-sm">
      💧 {error}
    </div>
  );

  if (!data) return null;

  const need = data.irrigation_need_mm_per_day;

  return (
    <div className={`rounded-xl border p-5 ${riskColor(need)}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-base">💧 Irrigation Advice</h3>
        <span className="text-xs font-medium">{riskLabel(need)}</span>
      </div>

      {data.weather_warning && (
        <p className="text-xs mb-2 opacity-80">⚠️ {data.weather_warning}</p>
      )}

      {/* Weather row */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center text-xs">
        <div className="bg-white bg-opacity-60 rounded-lg p-2">
          <p className="opacity-60">Temp</p>
          <p className="font-bold">{data.weather.temperature}°C</p>
        </div>
        <div className="bg-white bg-opacity-60 rounded-lg p-2">
          <p className="opacity-60">Humidity</p>
          <p className="font-bold">{data.weather.humidity}%</p>
        </div>
        <div className="bg-white bg-opacity-60 rounded-lg p-2">
          <p className="opacity-60">ET₀ Need</p>
          <p className="font-bold">{need} mm/day</p>
        </div>
      </div>

      {/* Schedule */}
      <ul className="space-y-1">
        {data.schedule.map((s, i) => (
          <li key={i} className="text-sm">• {s}</li>
        ))}
      </ul>

      <p className="text-xs mt-3 opacity-60">
        Soil: {data.soil_type} · Retention: {data.water_retention} ·
        {data.weather_live ? " Live weather" : " Estimated weather"}
      </p>
    </div>
  );
}
