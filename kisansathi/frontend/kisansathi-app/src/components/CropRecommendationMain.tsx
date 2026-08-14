import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2 } from "lucide-react";
import { getAPIBaseURL } from "@/utils/api";

interface CropRecommendation {
  crop: string;
  suitability: number;
  reason: string;
}

const CropRecommendationMain = () => {
  const { language } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<CropRecommendation[]>([]);
  const [formData, setFormData] = useState({
    nitrogen: "",
    phosphorus: "",
    potassium: "",
    ph: "",
    rainfall: "",
    temperature: "",
    humidity: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/recommendations/crop`, {
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
          humidity: parseFloat(formData.humidity) || 70,
          ph: parseFloat(formData.ph),
          rainfall: parseFloat(formData.rainfall),
          top_n: 2
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Transform backend response to match frontend expectations
        const transformed = data.recommendations.map((rec: any) => ({
          crop: rec.crop,
          suitability: parseFloat(rec.confidence_value || rec.confidence),
          reason: rec.reason
        }));
        setRecommendations(transformed);
      } else {
        console.error("API error:", response.status);
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            {language === "en" ? "Crop Recommendation" : "फसल की सिफारिश"}
          </h1>
          <p className="text-gray-600 mt-2">
            {language === "en"
              ? "Get personalized crop recommendations based on your soil and weather conditions"
              : "अपनी मिट्टी और मौसम की स्थिति के आधार पर व्यक्तिगत फसल सिफारिशें प्राप्त करें"}
          </p>
        </div>

        <Card className="bg-white shadow-lg mb-8">
          <CardHeader>
            <CardTitle>
              {language === "en" ? "Soil & Weather Information" : "मिट्टी और मौसम की जानकारी"}
            </CardTitle>
            <CardDescription>
              {language === "en"
                ? "Enter your soil parameters and weather conditions"
                : "अपनी मिट्टी के पैरामीटर और मौसम की स्थिति दर्ज करें"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
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
                <div>
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
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700"
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
            <h2 className="text-2xl font-bold text-gray-900">
              {language === "en" ? "Recommended Crops" : "अनुशंसित फसलें"}
            </h2>
            {recommendations.map((rec, index) => (
              <Card key={index} className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-lg">{rec.crop}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-gray-600">
                        {language === "en" ? "Suitability" : "उपयुक्तता"}
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${Math.min(rec.suitability, 100)}%` }}
                        ></div>
                      </div>
                      <p className="text-sm font-semibold mt-1">{rec.suitability.toFixed(2)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">
                        {language === "en" ? "Reason" : "कारण"}
                      </p>
                      <p className="text-gray-800 mt-1">{rec.reason}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CropRecommendationMain;
