import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2 } from "lucide-react";
import { getAPIBaseURL } from "@/utils/api";

interface CropRecommendation {
  rank: number;
  crop: string;
  confidence: string;
  confidence_value: number;
  season: string;
}

const SeasonalCropRecommendation = () => {
  const { language } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [seasons, setSeasons] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<CropRecommendation[]>([]);
  const [formData, setFormData] = useState({
    nitrogen: "",
    phosphorus: "",
    potassium: "",
    ph: "",
    rainfall: "",
    temperature: "",
    humidity: "",
    season: "Kharif",
  });

  // Load available seasons on mount
  useEffect(() => {
    const loadSeasons = async () => {
      try {
        const response = await fetch(`${getAPIBaseURL()}/seasons`, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        if (response.ok) {
          const data = await response.json();
          setSeasons(data.seasons || []);
        }
      } catch (error) {
        console.error("Error loading seasons:", error);
      }
    };
    loadSeasons();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${getAPIBaseURL()}/recommendations/seasonal-crop`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          N: parseFloat(formData.nitrogen),
          P: parseFloat(formData.phosphorus),
          K: parseFloat(formData.potassium),
          temperature: parseFloat(formData.temperature),
          humidity: parseFloat(formData.humidity),
          ph: parseFloat(formData.ph),
          rainfall: parseFloat(formData.rainfall),
          season: formData.season,
          top_n: 2
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        console.error("API error:", response.status);
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSeasonColor = (season: string) => {
    switch (season) {
      case "Kharif":
        return "from-blue-500 to-blue-600";
      case "Rabi":
        return "from-green-500 to-green-600";
      case "Summer":
        return "from-yellow-500 to-yellow-600";
      case "Perennial":
        return "from-purple-500 to-purple-600";
      default:
        return "from-gray-500 to-gray-600";
    }
  };

  const getSeasonEmoji = (season: string) => {
    switch (season) {
      case "Kharif":
        return "🌧️";
      case "Rabi":
        return "❄️";
      case "Summer":
        return "☀️";
      case "Perennial":
        return "🌿";
      default:
        return "🌾";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            {language === "en" ? "Seasonal Crop Recommendation" : "मौसमी फसल की सिफारिश"}
          </h1>
          <p className="text-gray-600 mt-2">
            {language === "en"
              ? "Get personalized crop recommendations based on season and soil conditions"
              : "मौसम और मिट्टी की स्थिति के आधार पर व्यक्तिगत फसल सिफारिशें प्राप्त करें"}
          </p>
        </div>

        <Card className="bg-white shadow-lg mb-8">
          <CardHeader>
            <CardTitle>
              {language === "en" ? "Soil & Weather Information" : "मिट्टी और मौसम की जानकारी"}
            </CardTitle>
            <CardDescription>
              {language === "en"
                ? "Enter your soil parameters, weather conditions, and select the season"
                : "अपनी मिट्टी के पैरामीटर, मौसम की स्थिति दर्ज करें और मौसम चुनें"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Season Selection */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border-2 border-green-200">
                <label className="block text-sm font-bold text-gray-800 mb-3">
                  {language === "en" ? "🌾 Select Season" : "🌾 मौसम चुनें"}
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {seasons.map((season) => (
                    <button
                      key={season}
                      type="button"
                      onClick={() => setFormData({ ...formData, season })}
                      className={`p-3 rounded-lg font-semibold transition ${
                        formData.season === season
                          ? `bg-gradient-to-r ${getSeasonColor(season)} text-white shadow-lg`
                          : "bg-white border-2 border-gray-300 text-gray-700 hover:border-green-500"
                      }`}
                    >
                      <span className="text-lg">{getSeasonEmoji(season)}</span>
                      <div className="text-xs mt-1">{season}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Soil Parameters */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  {language === "en" ? "Soil Parameters" : "मिट्टी के पैरामीटर"}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Nitrogen (N)" : "नाइट्रोजन (N)"}
                    </label>
                    <Input
                      type="number"
                      name="nitrogen"
                      value={formData.nitrogen}
                      onChange={handleInputChange}
                      placeholder="mg/kg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Phosphorus (P)" : "फॉस्फोरस (P)"}
                    </label>
                    <Input
                      type="number"
                      name="phosphorus"
                      value={formData.phosphorus}
                      onChange={handleInputChange}
                      placeholder="mg/kg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Potassium (K)" : "पोटेशियम (K)"}
                    </label>
                    <Input
                      type="number"
                      name="potassium"
                      value={formData.potassium}
                      onChange={handleInputChange}
                      placeholder="mg/kg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "pH Level" : "पीएच स्तर"}
                    </label>
                    <Input
                      type="number"
                      name="ph"
                      value={formData.ph}
                      onChange={handleInputChange}
                      placeholder="0-14"
                      step="0.1"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Weather Parameters */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  {language === "en" ? "Weather Conditions" : "मौसम की स्थिति"}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Temperature (°C)" : "तापमान (°C)"}
                    </label>
                    <Input
                      type="number"
                      name="temperature"
                      value={formData.temperature}
                      onChange={handleInputChange}
                      placeholder="°C"
                      step="0.1"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Humidity (%)" : "आर्द्रता (%)"}
                    </label>
                    <Input
                      type="number"
                      name="humidity"
                      value={formData.humidity}
                      onChange={handleInputChange}
                      placeholder="%"
                      min="0"
                      max="100"
                      required
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {language === "en" ? "Rainfall (mm)" : "वर्षा (मिमी)"}
                    </label>
                    <Input
                      type="number"
                      name="rainfall"
                      value={formData.rainfall}
                      onChange={handleInputChange}
                      placeholder="mm/year"
                      required
                    />
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {language === "en" ? "Getting Recommendations..." : "सिफारिशें प्राप्त हो रही हैं..."}
                  </>
                ) : (
                  language === "en" ? "Get Recommendations" : "सिफारिशें प्राप्त करें"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {recommendations.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-3xl">{getSeasonEmoji(recommendations[0].season)}</span>
              <h2 className="text-2xl font-bold text-gray-900">
                {language === "en" ? "Recommended Crops" : "अनुशंसित फसलें"}
              </h2>
              <span className="text-lg font-semibold text-gray-600">
                ({recommendations[0].season} {language === "en" ? "Season" : "मौसम"})
              </span>
            </div>

            {recommendations.map((rec, index) => (
              <Card key={index} className="bg-white shadow-lg hover:shadow-xl transition">
                <CardHeader className={`bg-gradient-to-r ${getSeasonColor(rec.season)}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-white text-2xl">
                        #{rec.rank} {rec.crop.toUpperCase()}
                      </CardTitle>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-white">{rec.confidence}</div>
                      <div className="text-white text-sm opacity-90">
                        {language === "en" ? "Confidence" : "आत्मविश्वास"}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`bg-gradient-to-r ${getSeasonColor(rec.season)} h-3 rounded-full transition-all`}
                      style={{ width: `${rec.confidence_value}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-3">
                    {language === "en" ? "Suitability Score" : "उपयुक्तता स्कोर"}: {rec.confidence_value.toFixed(2)}%
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SeasonalCropRecommendation;
