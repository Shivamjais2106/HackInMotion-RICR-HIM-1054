/**
 * MarketPrices Component — KisanSathi
 * Displays live mandi commodity prices fetched from the backend.
 * Shows modal price, MSP badge, trade advisory, and trend indicator.
 *
 * Author: Sumit Dangi
 */

import { useEffect, useState } from "react";
import { getAPIBaseURL } from "@/utils/api";

interface CommodityPrice {
  commodity: string;
  commodity_key: string;
  unit: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  msp?: number;
  source: string;
  live: boolean;
}

interface TradeAdvice {
  label: string;
  color: string;
  bg: string;
}

function getTradeAdvice(price: CommodityPrice): TradeAdvice {
  if (price.msp && price.modal_price < price.msp) {
    return { label: "Below MSP", color: "text-red-700", bg: "bg-red-100" };
  }
  if (price.modal_price >= price.max_price * 0.9) {
    return { label: "Sell Now", color: "text-green-700", bg: "bg-green-100" };
  }
  if (price.modal_price >= price.max_price * 0.75) {
    return { label: "Good Price", color: "text-blue-700", bg: "bg-blue-100" };
  }
  return { label: "Hold", color: "text-yellow-700", bg: "bg-yellow-100" };
}

export default function MarketPrices({ limit = 10 }: { limit?: number }) {
  const [prices, setPrices] = useState<CommodityPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${getAPIBaseURL()}/market/prices`, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`Server error ${r.status}`);
        return r.json();
      })
      .then((d) => {
        if (d.success) {
          setPrices(d.prices.slice(0, limit));
          setLastUpdated(new Date(d.timestamp).toLocaleTimeString());
        } else {
          setError("Could not load market prices.");
        }
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError("Network error — could not fetch prices.");
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [limit]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-10 bg-gray-100 rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        ❌ {error}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800">🌾 Mandi Prices (₹/Quintal)</h3>
        <span className="text-xs text-gray-400">Updated {lastUpdated}</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 border-b">
              <th className="pb-2 font-medium">Commodity</th>
              <th className="pb-2 font-medium text-right">Modal ₹</th>
              <th className="pb-2 font-medium text-right">MSP ₹</th>
              <th className="pb-2 font-medium text-center">Advisory</th>
              <th className="pb-2 font-medium text-center">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {prices.map((p) => {
              const advice = getTradeAdvice(p);
              return (
                <tr key={p.commodity_key} className="hover:bg-gray-50 transition-colors">
                  <td className="py-2 font-medium text-gray-800">{p.commodity}</td>
                  <td className="py-2 text-right font-bold text-gray-900">
                    {p.modal_price.toLocaleString("en-IN")}
                  </td>
                  <td className="py-2 text-right text-gray-500 text-xs">
                    {p.msp ? p.msp.toLocaleString("en-IN") : "—"}
                  </td>
                  <td className="py-2 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${advice.bg} ${advice.color}`}>
                      {advice.label}
                    </span>
                  </td>
                  <td className="py-2 text-center">
                    {p.live ? (
                      <span className="inline-block w-2 h-2 rounded-full bg-green-500" title="Live data" />
                    ) : (
                      <span className="inline-block w-2 h-2 rounded-full bg-yellow-400" title="MSP reference" />
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-400 mt-2">
        🟢 Live (AGMARKNET) &nbsp;|&nbsp; 🟡 MSP Reference (GoI 2025-26)
      </p>
    </div>
  );
}
