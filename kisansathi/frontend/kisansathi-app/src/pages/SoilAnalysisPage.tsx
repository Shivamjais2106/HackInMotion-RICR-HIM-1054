import React, { useState, useEffect } from 'react';
import { Leaf, Droplets, Thermometer, Wind, Zap, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { getAPIBaseURL } from '../utils/api';

interface SoilAnalysisResult {
  success: boolean;
  soil_analysis: {
    temperature: number;
    humidity: number;
    moisture: number;
    soil_type: string;
    nitrogen: number;
    potassium: number;
    phosphorous: number;
  };
  crop_recommendation: {
    primary: string;
    confidence: number;
    top_3: Array<{ name: string; confidence: number }>;
  };
  fertilizer_recommendation: {
    primary: string;
    confidence: number;
    top_3: Array<{ name: string; confidence: number }>;
  };
  recommendations: string[];
}

const SoilAnalysisPage: React.FC = () => {
  const { t } = useLanguage();
  const [soilTypes, setSoilTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SoilAnalysisResult | null>(null);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    temperature: 28,
    humidity: 54,
    moisture: 46,
    soil_type: 'Clayey',
    nitrogen: 35,
    potassium: 0,
    phosphorous: 0,
  });

  // Load soil types on mount
  useEffect(() => {
    const loadSoilTypes = async () => {
      try {
        const baseURL = getAPIBaseURL();
        const response = await fetch(`${baseURL}/soil/types`);
        const data = await response.json();
        if (data.success) {
          setSoilTypes(data.soil_types);
        }
      } catch (err) {
        console.error('Error loading soil types:', err);
        setSoilTypes(['Sandy', 'Loamy', 'Black', 'Red', 'Clayey']);
      }
    };
    loadSoilTypes();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(Number(value)) ? value : Number(value)
    }));
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/soil/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Analysis failed');
      }
    } catch (err) {
      setError('Unable to connect to server');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-yellow-50 p-2 sm:p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-1 sm:mb-2">🌾 Soil Analysis</h1>
          <p className="text-gray-600 text-sm sm:text-base md:text-lg">Analyze your soil and get crop & fertilizer recommendations</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
          {/* Input Form */}
          <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6 md:p-8">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-4 sm:mb-6">📊 Soil Parameters</h2>
            
            <form onSubmit={handleAnalyze} className="space-y-3 sm:space-y-4">
              {/* Temperature */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Thermometer className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Temperature (°C)
                </label>
                <input
                  type="number"
                  name="temperature"
                  value={formData.temperature}
                  onChange={handleInputChange}
                  min="0"
                  max="50"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Humidity */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Wind className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Humidity (%)
                </label>
                <input
                  type="number"
                  name="humidity"
                  value={formData.humidity}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Moisture */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Droplets className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Moisture (%)
                </label>
                <input
                  type="number"
                  name="moisture"
                  value={formData.moisture}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Soil Type */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Leaf className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Soil Type
                </label>
                <select
                  name="soil_type"
                  value={formData.soil_type}
                  onChange={handleInputChange}
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                >
                  {soilTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* Nitrogen */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Zap className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Nitrogen (N)
                </label>
                <input
                  type="number"
                  name="nitrogen"
                  value={formData.nitrogen}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Potassium */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <TrendingUp className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Potassium (K)
                </label>
                <input
                  type="number"
                  name="potassium"
                  value={formData.potassium}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Phosphorous */}
              <div>
                <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-2">
                  <Leaf className="inline w-3 sm:w-4 h-3 sm:h-4 mr-1 sm:mr-2" />
                  Phosphorous (P)
                </label>
                <input
                  type="number"
                  name="phosphorous"
                  value={formData.phosphorous}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                  className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-4 sm:mt-6 px-4 sm:px-6 py-2 sm:py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-md transition disabled:bg-gray-400 font-semibold text-sm sm:text-base"
              >
                {loading ? 'Analyzing...' : 'Analyze Soil'}
              </button>
            </form>
          </div>

          {/* Results */}
          <div>
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-3 sm:px-6 py-3 sm:py-4 rounded-lg mb-4 sm:mb-6 flex items-start sm:items-center gap-2 sm:gap-3 text-xs sm:text-sm">
                <AlertCircle className="w-4 sm:w-5 h-4 sm:h-5 flex-shrink-0 mt-0.5 sm:mt-0" />
                {error}
              </div>
            )}

            {result && (
              <div className="space-y-4 sm:space-y-6">
                {/* Crop Recommendation */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-lg p-4 sm:p-6 border-2 border-green-200">
                  <h3 className="text-lg sm:text-xl font-bold text-green-800 mb-3 sm:mb-4 flex items-center gap-2">
                    <Leaf className="w-5 sm:w-6 h-5 sm:h-6" />
                    Recommended Crop
                  </h3>
                  <div className="bg-white rounded-lg p-3 sm:p-4 mb-3 sm:mb-4">
                    <p className="text-2xl sm:text-3xl font-bold text-green-600">{result.crop_recommendation.primary}</p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2">
                      Confidence: {(result.crop_recommendation.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="space-y-1 sm:space-y-2">
                    <p className="text-xs sm:text-sm font-semibold text-gray-700">Top Alternatives:</p>
                    {result.crop_recommendation.top_3.map((crop, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-white rounded p-2 text-xs sm:text-sm">
                        <span className="text-gray-700">{crop.name}</span>
                        <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs">
                          {(crop.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Fertilizer Recommendation */}
                <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl shadow-lg p-4 sm:p-6 border-2 border-blue-200">
                  <h3 className="text-lg sm:text-xl font-bold text-blue-800 mb-3 sm:mb-4 flex items-center gap-2">
                    <Zap className="w-5 sm:w-6 h-5 sm:h-6" />
                    Recommended Fertilizer
                  </h3>
                  <div className="bg-white rounded-lg p-3 sm:p-4 mb-3 sm:mb-4">
                    <p className="text-2xl sm:text-3xl font-bold text-blue-600">{result.fertilizer_recommendation.primary}</p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1 sm:mt-2">
                      Confidence: {(result.fertilizer_recommendation.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="space-y-1 sm:space-y-2">
                    <p className="text-xs sm:text-sm font-semibold text-gray-700">Top Alternatives:</p>
                    {result.fertilizer_recommendation.top_3.map((fert, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-white rounded p-2 text-xs sm:text-sm">
                        <span className="text-gray-700">{fert.name}</span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">
                          {(fert.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl shadow-lg p-4 sm:p-6 border-2 border-yellow-200">
                  <h3 className="text-lg sm:text-xl font-bold text-yellow-800 mb-3 sm:mb-4 flex items-center gap-2">
                    <CheckCircle className="w-5 sm:w-6 h-5 sm:h-6" />
                    Farming Tips
                  </h3>
                  <div className="space-y-2 sm:space-y-3">
                    {result.recommendations.map((rec, idx) => (
                      <div key={idx} className="flex gap-2 sm:gap-3 items-start bg-white rounded p-2 sm:p-3">
                        <span className="text-base sm:text-lg flex-shrink-0">💡</span>
                        <p className="text-xs sm:text-sm text-gray-700">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SoilAnalysisPage;
