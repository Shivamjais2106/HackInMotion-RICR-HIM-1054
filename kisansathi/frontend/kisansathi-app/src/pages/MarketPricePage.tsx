/**
 * MarketPricePage — KisanSathi
 * Full-page mandi price view with commodity filter and trade advisories.
 * Route: /market
 *
 * Author: Sumit Dangi
 */

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import MarketPrices from "@/components/MarketPrices";
import { getAPIBaseURL } from "@/utils/api";

interface Price {
  commodity: string;
  commodity_key: string;
  unit: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  msp?: number;
  live: boolean;
  source: string;
}

export default function MarketPricePage() {
  const [prices, setPrices] = useState<Price[]>([]);
  const [filtered, setFiltered] = useState<Price[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  useEffect(() => {
    const ctrl = new AbortController();
    fetch(`${getAPIBaseURL()}/market/prices`, { signal: ctrl.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.json();
      })
      .then((d) => {
        if (d.success) {
          setPrices(d.prices);
          setFiltered(d.prices);
          setLastUpdated(new Date(d.timestamp).toLocaleString("en-IN"));
        } else setError("Could not load prices.");
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError("Network error.");
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(q ? prices.filter((p) => p.commodity.toLowerCase().includes(q)) : prices);
  }, [search, prices]);

  const advice = (p: Price) => {
    if (p.msp && p.modal_price < p.msp)
      return { text: "Below MSP", cls: "bg-red-100 text-red-700" };
    if (p.modal_price >= p.max_price * 0.9)
      return { text: "Sell Now ✅", cls: "bg-green-100 text-green-700" };
    if (p.modal_price >= p.max_price * 0.75)
      return { text: "Good Price", cls: "bg-blue-100 text-blue-700" };
    return { text: "Hold 🕐", cls: "bg-yellow-100 text-yellow-700" };
  };

  return (
    <div className="min-h-screen bg-eco-cream">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-20">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-eco-green-dark mb-2">
            📊 Live Mandi Market Prices
          </h1>
          <p className="text-gray-600">
            Real-time commodity prices from AGMARKNET (data.gov.in) · MSP Reference: GoI 2025-26
          </p>
          {lastUpdated && <p className="text-xs text-gray-400 mt-1">Last updated: {lastUpdated}</p>}
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search commodity — wheat, rice, onion..."
            className="w-full border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-eco-green"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 mb-6">
            ❌ {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-14 bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-eco-green text-white">
                <tr>
                  <th className="py-3 px-4 text-left">Commodity</th>
                  <th className="py-3 px-4 text-right">Min ₹</th>
                  <th className="py-3 px-4 text-right">Modal ₹</th>
                  <th className="py-3 px-4 text-right">Max ₹</th>
                  <th className="py-3 px-4 text-right">MSP ₹</th>
                  <th className="py-3 px-4 text-center">Advisory</th>
                  <th className="py-3 px-4 text-center">Data</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((p) => {
                  const adv = advice(p);
                  return (
                    <tr key={p.commodity_key} className="hover:bg-gray-50">
                      <td className="py-3 px-4 font-semibold text-gray-800">{p.commodity}</td>
                      <td className="py-3 px-4 text-right text-gray-500">
                        {p.min_price.toLocaleString("en-IN")}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-gray-900">
                        {p.modal_price.toLocaleString("en-IN")}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-500">
                        {p.max_price.toLocaleString("en-IN")}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-400 text-xs">
                        {p.msp ? p.msp.toLocaleString("en-IN") : "—"}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${adv.cls}`}>
                          {adv.text}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center text-xs">
                        {p.live ? (
                          <span className="text-green-600 font-medium">🟢 Live</span>
                        ) : (
                          <span className="text-yellow-600">🟡 MSP</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <p className="text-center py-8 text-gray-400">No commodities found for "{search}"</p>
            )}
          </div>
        )}

        <div className="mt-6 bg-blue-50 rounded-xl p-4 text-sm text-blue-700">
          <strong>Data Sources:</strong> Live prices from{" "}
          <a
            href="https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            AGMARKNET (data.gov.in)
          </a>{" "}
          · MSP reference from Government of India Kharif/Rabi 2025-26 notification.
        </div>
      </div>
      <Footer />
    </div>
  );
}
