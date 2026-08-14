import { useState, useEffect } from 'react';
import { getAPIBaseURL } from '@/utils/api';

function CropRecommendationMonth() {
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: '',
    month: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [months, setMonths] = useState([]);

  useEffect(() => {
    // Fetch available months
    fetch(`${getAPIBaseURL()}/months`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setMonths(data.months);
        }
      })
      .catch(err => console.error('Error fetching months:', err));
  }, []);

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
        body: JSON.stringify({
          nitrogen: formData.nitrogen,
          phosphorus: formData.phosphorus,
          potassium: formData.potassium,
          temperature: formData.temperature,
          humidity: formData.humidity,
          ph: formData.ph,
          rainfall: formData.rainfall,
          month: formData.month
        })
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
        <h1 className="text-4xl font-bold text-eco-green-dark mb-8">📅 Seasonal Crop Recommendation</h1>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8">
          {/* Month Selection */}
          <div className="mb-8 p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-4">📅 Select Month</h3>
            <select
              name="month"
              value={formData.month}
              onChange={handleChange}
              className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
              required
            >
              <option value="">Choose a month...</option>
              {months.map(month => (
                <option key={month} value={month}>{month}</option>
              ))}
            </select>
            <p className="text-sm text-blue-700 mt-3">
              💡 Selecting a month helps us recommend crops suitable for that season
            </p>
          </div>

          {/* Soil Parameters */}
          <div className="mb-8">
            <h3 className="text-lg font-bold text-gray-800 mb-4">🌱 Soil Parameters</h3>
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
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50"
          >
            {loading ? '⏳ Predicting...' : '🌾 Get Seasonal Recommendation'}
          </button>
        </form>

        {result && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-8">
            {result.error ? (
              <p className="text-red-600">{result.error}</p>
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
                
                {/* Month Info */}
                {result.month_info && (
                  <div className={`rounded-lg p-6 mb-6 ${result.month_info.suitable ? 'bg-green-50 border-2 border-green-300' : 'bg-yellow-50 border-2 border-yellow-300'}`}>
                    <h3 className="text-lg font-bold mb-3">
                      {result.month_info.suitable ? '✅ Seasonal Match' : '⚠️ Seasonal Adjustment'}
                    </h3>
                    <p className="text-gray-700 mb-3">{result.month_info.reason}</p>
                    
                    {result.month_info.season && (
                      <div className="bg-white rounded p-3 mb-3">
                        <p className="text-sm text-gray-600">Season: <span className="font-bold text-eco-green">{result.month_info.season}</span></p>
                      </div>
                    )}
                    
                    {result.month_info.alternatives && result.month_info.alternatives.length > 0 && (
                      <div className="bg-white rounded p-3">
                        <p className="text-sm font-semibold text-gray-700 mb-2">
                          {result.month_info.suitable ? 'Other suitable crops:' : 'Recommended alternatives:'}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {result.month_info.alternatives.map((crop, idx) => (
                            <span key={idx} className="bg-eco-green text-white px-3 py-1 rounded-full text-sm">
                              {crop}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Primary Crop Explanation */}
                {result.explanation && (
                  <div className="bg-eco-cream rounded-lg p-6 mb-6 border-l-4 border-eco-green">
                    <h3 className="text-lg font-bold text-eco-green-dark mb-3">Why {result.primary_crop.toUpperCase()}?</h3>
                    <div className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                      {result.explanation}
                    </div>
                  </div>
                )}
                
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

export default CropRecommendationMonth;
