import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";
import { LogOut } from "lucide-react";
import { getAPIBaseURL, getAuthHeaders } from "@/utils/api";

const DashboardEnhanced = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();

  const [user, setUser]                 = useState<any>(null);
  const [farmProfile, setFarmProfile]   = useState<any>(null);
  const [weather, setWeather]           = useState<any>(null);
  const [irrigation, setIrrigation]     = useState<any>(null);
  const [marketPrices, setMarketPrices] = useState<any[]>([]);
  const [marketTrends, setMarketTrends] = useState<Record<string, any>>({});
  const [healthLogs, setHealthLogs]     = useState<any[]>([]);
  const [cropRec, setCropRec]           = useState<any>(null);
  const [weatherAlerts, setWeatherAlerts] = useState<string[]>([]);
  const [loading, setLoading]           = useState(true);

  const t = (en: string, hi: string) => language === "en" ? en : hi;

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) { try { setUser(JSON.parse(stored)); } catch {} }
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    await Promise.allSettled([
      loadFarmProfile(),
      loadMarketPrices(),
    ]);
    setLoading(false);
  };

  const loadFarmProfile = async () => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/farm-profile`, { headers: getAuthHeaders() });
      const d = await r.json();
      if (d.profile) {
        setFarmProfile(d.profile);
        // Load weather + irrigation + crop rec based on profile
        const loc = d.profile.location || "Delhi";
        loadWeather(loc);
        loadIrrigation();
        loadCropRec(d.profile);
        loadHealthLogs();
      }
    } catch {}
  };

  const loadWeather = async (location: string) => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/weather/${encodeURIComponent(location)}`);
      const d = await r.json();
      setWeather(d);
      computeWeatherAlerts(d, farmProfile);
    } catch {}
  };

  const loadIrrigation = async () => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/farm-profile/irrigation-advice`, { headers: getAuthHeaders() });
      const d = await r.json();
      if (d.success) setIrrigation(d);
    } catch {}
  };

  const loadMarketPrices = async () => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/market/prices`);
      const d = await r.json();
      if (d.success) {
        setMarketPrices(d.prices.slice(0, 10));
        // Fetch trends for top 6 commodities
        const top6 = d.prices.slice(0, 6).map((p: any) => p.commodity_key);
        const tr = await fetch(`${getAPIBaseURL()}/market/trends/bulk`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ commodities: top6 }),
        });
        const td = await tr.json();
        if (td.success) {
          const tmap: Record<string, any> = {};
          td.trends.forEach((t: any) => { tmap[t.commodity.toLowerCase()] = t; });
          setMarketTrends(tmap);
        }
      }
    } catch {}
  };

  const computeWeatherAlerts = (w: any, profile: any) => {
    if (!w?.forecast?.[0]) return;
    const f = w.forecast[0];
    const crops = profile?.active_crops || [];
    const alerts: string[] = [];
    if (f.temp_max > 40) alerts.push(`🌡️ Extreme heat (${f.temp_max}°C) — cover seedlings, irrigate early morning`);
    if (f.humidity > 80) alerts.push(`💧 High humidity (${f.humidity}%) — risk of fungal disease${crops.includes('Cotton') ? ' for Cotton' : ''}`);
    if ((f.rainfall_mm || 0) > 50) alerts.push(`🌧️ Heavy rain expected (${f.rainfall_mm}mm) — skip irrigation today`);
    if (f.temp_max < 10) alerts.push(`❄️ Cold alert (${f.temp_max}°C) — protect sensitive crops`);
    if (f.wind_speed > 40) alerts.push(`💨 High winds (${f.wind_speed} km/h) — secure crop supports`);
    if (alerts.length === 0) alerts.push(`✅ No weather risks today — conditions are favourable`);
    setWeatherAlerts(alerts);
  };

  const loadHealthLogs = async () => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/farm-profile/health-logs`, { headers: getAuthHeaders() });
      const d = await r.json();
      if (d.success) setHealthLogs(d.logs.slice(0, 3));
    } catch {}
  };

  const loadCropRec = async (profile: any) => {
    try {
      const r = await fetch(`${getAPIBaseURL()}/recommendations/advanced-crop`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          month: new Date().toLocaleString("en-US", { month: "long" }),
          location: profile.location || "Central India",
        }),
      });
      const d = await r.json();
      if (d.success) setCropRec(d);
    } catch {}
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/auth");
  };

  // Quick action cards
  const quickActions = [
    { icon: "🌾", label: t("Crop Recommendation","फसल सिफारिश"), path: "/crop", color: "bg-green-50 border-green-200" },
    { icon: "🌱", label: t("Soil Analysis","मिट्टी विश्लेषण"), path: "/soil-analysis", color: "bg-yellow-50 border-yellow-200" },
    { icon: "🧪", label: t("Fertilizer","उर्वरक"), path: "/fertilizer", color: "bg-blue-50 border-blue-200" },
    { icon: "🔬", label: t("Disease Detect","रोग पहचान"), path: "/disease", color: "bg-red-50 border-red-200" },
    { icon: "⛅", label: t("Weather","मौसम"), path: "/weather", color: "bg-sky-50 border-sky-200" },
    { icon: "📅", label: t("Reminders","रिमाइंडर"), path: "/reminders", color: "bg-purple-50 border-purple-200" },
    { icon: "🐄", label: t("Livestock","पशुधन"), path: "/livestock", color: "bg-orange-50 border-orange-200" },
    { icon: "👥", label: t("Community","समुदाय"), path: "/community", color: "bg-teal-50 border-teal-200" },
    { icon: "🏪", label: t("Market Prices","मंडी भाव"), path: "/shop", color: "bg-amber-50 border-amber-200" },
    { icon: "🏡", label: t("Farm Profile","खेत प्रोफाइल"), path: "/farm-profile", color: "bg-lime-50 border-lime-200" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">

      {/* Top Bar */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🌾</span>
            <div>
              <h1 className="font-bold text-eco-green-dark text-lg">
                {t("KisanSathi Dashboard","किसानसाथी डैशबोर्ड")}
              </h1>
              {user && <p className="text-xs text-gray-500">{t("Welcome,","स्वागत,")} {user.name || user.email}</p>}
            </div>
          </div>
          <button onClick={handleLogout}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-red-600 border border-gray-200 rounded-lg px-3 py-1.5">
            <LogOut className="w-4 h-4" />
            {t("Logout","लॉगआउट")}
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* Farm Profile Banner */}
        {!farmProfile ? (
          <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-yellow-800">⚠️ {t("Farm profile not set up","खेत प्रोफाइल सेट नहीं है")}</p>
              <p className="text-sm text-yellow-700">{t("Set up your farm profile to get personalized recommendations","व्यक्तिगत सिफारिशें पाने के लिए खेत प्रोफाइल सेट करें")}</p>
            </div>
            <button onClick={() => navigate("/farm-profile")}
              className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg text-sm font-medium">
              {t("Setup Now →","अभी सेट करें →")}
            </button>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            <div><p className="text-xs text-gray-500">{t("Farm","खेत")}</p><p className="font-bold text-eco-green-dark">{farmProfile.farm_name || t("My Farm","मेरा खेत")}</p></div>
            <div><p className="text-xs text-gray-500">{t("Location","स्थान")}</p><p className="font-bold">{farmProfile.location || "—"}</p></div>
            <div><p className="text-xs text-gray-500">{t("Land Size","भूमि")}</p><p className="font-bold">{farmProfile.land_size_acres ? `${farmProfile.land_size_acres} acres` : "—"}</p></div>
            <div><p className="text-xs text-gray-500">{t("Soil Type","मिट्टी")}</p><p className="font-bold">{farmProfile.soil_type || "—"}</p></div>
          </div>
        )}

        {/* Top 3 widgets row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* Weather Widget */}
          <div className="bg-white rounded-xl shadow p-4 border border-blue-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">⛅ {t("Weather","मौसम")}</h3>
              <button onClick={() => navigate("/weather")} className="text-xs text-blue-500 hover:underline">{t("Details →","विवरण →")}</button>
            </div>
            {weather?.forecast?.[0] ? (
              <div className="space-y-2">
                <div className="flex items-end gap-2">
                  <span className="text-4xl font-bold text-blue-700">{weather.forecast[0].temp_max}°C</span>
                  <span className="text-gray-500 text-sm mb-1">{weather.forecast[0].description}</span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-blue-50 rounded p-2"><p className="text-gray-500">{t("Humidity","नमी")}</p><p className="font-bold text-blue-700">{weather.forecast[0].humidity}%</p></div>
                  <div className="bg-blue-50 rounded p-2"><p className="text-gray-500">{t("Rain","वर्षा")}</p><p className="font-bold text-blue-700">{weather.forecast[0].rainfall_mm ?? 0}mm</p></div>
                  <div className="bg-blue-50 rounded p-2"><p className="text-gray-500">{t("Wind","हवा")}</p><p className="font-bold text-blue-700">{weather.forecast[0].wind_speed ?? "—"}</p></div>
                </div>
                {/* Crop-specific risk alerts */}
                {weatherAlerts.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {weatherAlerts.map((alert, i) => (
                      <p key={i} className={`text-xs rounded px-2 py-1 ${alert.startsWith('✅') ? 'bg-green-50 text-green-700' : 'bg-orange-50 text-orange-700 font-medium'}`}>{alert}</p>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400 text-sm">
                {farmProfile ? "⏳ Loading..." : t("Set farm profile to see weather","खेत प्रोफाइल सेट करें")}
              </div>
            )}
          </div>

          {/* Irrigation Widget */}
          <div className="bg-white rounded-xl shadow p-4 border border-green-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">💧 {t("Irrigation","सिंचाई")}</h3>
              <button onClick={() => navigate("/farm-profile")} className="text-xs text-green-500 hover:underline">{t("Details →","विवरण →")}</button>
            </div>
            {irrigation ? (
              <div className="space-y-2">
                <div className="bg-blue-50 rounded-lg p-2 text-center">
                  <p className="text-xs text-gray-500">{t("Water Need","पानी की जरूरत")}</p>
                  <p className="text-2xl font-bold text-blue-700">{irrigation.irrigation_need_mm_per_day} <span className="text-sm">mm/day</span></p>
                </div>
                <ul className="text-xs space-y-1">
                  {irrigation.schedule?.slice(0, 2).map((s: string, i: number) => (
                    <li key={i} className="text-gray-600">• {s}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400 text-sm">
                {farmProfile ? "⏳ Loading..." : t("Set farm profile first","पहले खेत प्रोफाइल सेट करें")}
              </div>
            )}
          </div>

          {/* Crop Recommendation Widget */}
          <div className="bg-white rounded-xl shadow p-4 border border-yellow-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">🌾 {t("Recommended Crops","अनुशंसित फसलें")}</h3>
              <button onClick={() => navigate("/crop")} className="text-xs text-yellow-600 hover:underline">{t("More →","और →")}</button>
            </div>
            {cropRec?.recommendations?.length > 0 ? (
              <div className="space-y-2">
                <p className="text-xs text-gray-500">{t("This month:","इस महीने:")} {cropRec.month} • {cropRec.recommendations[0]?.season}</p>
                {cropRec.recommendations.slice(0, 4).map((rec: any, i: number) => (
                  <div key={i} className="flex items-center justify-between bg-yellow-50 rounded px-2 py-1">
                    <span className="text-sm font-medium capitalize">{rec.crop}</span>
                    <span className="text-xs text-yellow-700">{rec.confidence}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400 text-sm">
                {farmProfile ? "⏳ Loading..." : t("Set farm profile first","पहले खेत प्रोफाइल सेट करें")}
              </div>
            )}
          </div>
        </div>

        {/* Market Prices + Health Logs row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          {/* Market Prices */}
          <div className="bg-white rounded-xl shadow p-4 border border-orange-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">📊 {t("Mandi Prices","मंडी भाव")}</h3>
              <button onClick={() => navigate("/shop")} className="text-xs text-orange-500 hover:underline">{t("All prices →","सभी भाव →")}</button>
            </div>
            {marketPrices.length > 0 ? (
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {marketPrices.map((item: any) => {
                  const tr = marketTrends[item.commodity_key];
                  const arrow = tr?.trend_direction === 'rising' ? '📈' : tr?.trend_direction === 'falling' ? '📉' : '→';
                  const pct = tr?.change_pct;
                  const pctColor = tr?.trend_direction === 'rising' ? 'text-green-600' : tr?.trend_direction === 'falling' ? 'text-red-500' : 'text-gray-400';
                  return (
                    <div key={item.commodity_key} className="flex justify-between items-center text-sm border-b border-gray-50 py-1">
                      <span className="capitalize text-gray-700">{item.commodity}</span>
                      <div className="text-right flex items-center gap-1">
                        <span className="font-bold text-eco-green">₹{item.modal_price?.toLocaleString("en-IN")}</span>
                        <span>{arrow}</span>
                        {pct !== undefined && <span className={`text-xs font-medium ${pctColor}`}>{pct > 0 ? '+' : ''}{pct}%</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400 text-sm">⏳ {t("Loading prices...","भाव लोड हो रहे हैं...")}</div>
            )}
            <p className="text-xs text-gray-400 mt-2">* {t("Source: AGMARKNET / MSP Reference 2025-26","स्रोत: AGMARKNET / MSP 2025-26")}</p>
          </div>

          {/* Crop Health Flags */}
          <div className="bg-white rounded-xl shadow p-4 border border-red-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">🔬 {t("Crop Health Logs","फसल स्वास्थ्य लॉग")}</h3>
              <button onClick={() => navigate("/disease")} className="text-xs text-red-500 hover:underline">{t("Add Log →","लॉग जोड़ें →")}</button>
            </div>
            {healthLogs.length > 0 ? (
              <div className="space-y-2">
                {healthLogs.map((log: any, i: number) => (
                  <div key={i} className="bg-red-50 rounded-lg p-2 text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium capitalize">{log.crop}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        log.severity === "high" ? "bg-red-200 text-red-800" :
                        log.severity === "medium" ? "bg-yellow-200 text-yellow-800" :
                        "bg-green-200 text-green-800"}`}>{log.severity}</span>
                    </div>
                    <p className="text-gray-600 text-xs mt-1">{log.observation}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400 text-sm">
                <p className="text-3xl mb-2">✅</p>
                <p>{t("No health issues logged","कोई स्वास्थ्य समस्या दर्ज नहीं")}</p>
                <button onClick={() => navigate("/disease")}
                  className="mt-2 text-xs text-blue-500 hover:underline">
                  {t("Detect disease from photo →","फोटो से रोग पहचानें →")}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Active Crops */}
        {farmProfile?.active_crops?.length > 0 && (
          <div className="bg-white rounded-xl shadow p-4 border border-green-100">
            <h3 className="font-bold text-gray-800 mb-3">🌱 {t("Your Active Crops","आपकी सक्रिय फसलें")}</h3>
            <div className="flex flex-wrap gap-2">
              {farmProfile.active_crops.map((crop: string) => (
                <span key={crop} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  {crop}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div>
          <h3 className="font-bold text-gray-800 mb-3">⚡ {t("Quick Actions","त्वरित कार्य")}</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {quickActions.map((action) => (
              <button key={action.path} onClick={() => navigate(action.path)}
                className={`${action.color} border rounded-xl p-3 text-center hover:shadow-md transition-all`}>
                <div className="text-2xl mb-1">{action.icon}</div>
                <div className="text-xs font-medium text-gray-700">{action.label}</div>
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardEnhanced;
