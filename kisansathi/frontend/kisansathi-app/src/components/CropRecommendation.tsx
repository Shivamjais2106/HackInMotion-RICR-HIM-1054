import { useState } from 'react';
import { getAPIBaseURL } from '@/utils/api';

function CropRecommendation() {
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${getAPIBaseURL()}/crop-predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Failed to get prediction' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-eco-cream py-20">
      <div className="max-w-2xl mx-auto px-6">
        <h1 className="text-4xl font-bold text-eco-green-dark mb-8">Crop Recommendation</h1>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nitrogen (N)</label>
              <input
                type="number"
                name="nitrogen"
                value={formData.nitrogen}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phosphorus (P)</label>
              <input
                type="number"
                name="phosphorus"
                value={formData.phosphorus}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Potassium (K)</label>
              <input
                type="number"
                name="potassium"
                value={formData.potassium}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Temperature (°C)</label>
              <input
                type="number"
                name="temperature"
                value={formData.temperature}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Humidity (%)</label>
              <input
                type="number"
                name="humidity"
                value={formData.humidity}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">pH</label>
              <input
                type="number"
                name="ph"
                value={formData.ph}
                onChange={handleChange}
                step="0.1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rainfall (mm)</label>
              <input
                type="number"
                name="rainfall"
                value={formData.rainfall}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-8 w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50"
          >
            {loading ? 'Predicting...' : 'Get Recommendation'}
          </button>
        </form>

        {result && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-8">
            {result.error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 font-semibold">Error</p>
                <p className="text-red-500 text-sm">{result.error}</p>
              </div>
            ) : (
              <div>
                <h2 className="text-2xl font-bold text-eco-green-dark mb-6">Top 5 Crop Recommendations</h2>
                
                {/* Top 5 Crops List */}
                <div className="space-y-4 mb-8">
                  {result.top_crops && result.top_crops.map((crop, index) => (
                    <div key={index} className={`border-l-4 p-4 rounded-lg ${
                      index === 0 ? 'border-eco-green bg-eco-cream' : 'border-gray-300 bg-gray-50'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className={`text-2xl font-bold ${index === 0 ? 'text-eco-green' : 'text-gray-400'}`}>
                            #{crop.rank}
                          </span>
                          <div>
                            <p className="text-xl font-bold text-eco-green-dark">{crop.crop.toUpperCase()}</p>
                            <p className="text-sm text-gray-600">{crop.reason}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`text-2xl font-bold ${index === 0 ? 'text-eco-green' : 'text-gray-500'}`}>
                            {crop.confidence_str}
                          </p>
                          <div className="w-24 h-2 bg-gray-200 rounded-full mt-2 overflow-hidden">
                            <div 
                              className={`h-full ${index === 0 ? 'bg-eco-green' : 'bg-gray-400'}`}
                              style={{width: `${Math.min(crop.confidence, 100)}%`}}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Primary Crop Explanation */}
                {result.explanation && (
                  <div className="bg-eco-cream rounded-lg p-6 mb-6 border-l-4 border-eco-green">
                    <h3 className="text-lg font-bold text-eco-green-dark mb-3">Why {result.primary_crop.toUpperCase()}?</h3>
                    <div className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                      {result.explanation}
                    </div>
                  </div>
                )}
                
                {/* Weather Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-blue-50 p-4 rounded">
                    <p className="text-gray-600">Temperature</p>
                    <p className="text-lg font-bold text-blue-600">{result.temperature}°C</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded">
                    <p className="text-gray-600">Humidity</p>
                    <p className="text-lg font-bold text-green-600">{result.humidity}%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CropRecommendation;
