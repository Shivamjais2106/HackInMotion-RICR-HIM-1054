import { useState } from 'react';
import { getAPIBaseURL } from '@/utils/api';

function FertilizerRecommendation() {
  const [formData, setFormData] = useState({
    crop: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    moisture: '',
    soil_type: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [activeTab, setActiveTab] = useState('manual');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.crop || !formData.nitrogen || !formData.phosphorus || !formData.potassium) {
      alert('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${getAPIBaseURL()}/fertilizer/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crop_type: formData.crop,
          nitrogen: parseFloat(formData.nitrogen),
          phosphorus: parseFloat(formData.phosphorus),
          potassium: parseFloat(formData.potassium),
          temperature: parseFloat(formData.temperature) || 25,
          humidity: parseFloat(formData.humidity) || 70,
          moisture: parseFloat(formData.moisture) || 50,
          soil_type: formData.soil_type || 'loamy'
        })
      });
      const data = await response.json();
      setResult(data);
      
      if (data.recommendation) {
        speakResult(data);
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({ success: false, error: 'Failed to get recommendation' });
    }
    setLoading(false);
  };

  const speakResult = (data) => {
    const rec = data.recommendation;
    const text = `For ${formData.crop}, recommended fertilizer is ${rec.recommended_fertilizer}. Apply ${rec.application_rate.nitrogen} kg nitrogen, ${rec.application_rate.phosphorus} kg phosphorus, and ${rec.application_rate.potassium} kg potassium per hectare. ${rec.timing[0]}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const handleFileUpload = (e) => {
    const files = e.target.files;
    if (files) {
      const newFiles = Array.from(files).filter(file => file.type.includes('image'));
      if (newFiles.length > 0) {
        setUploadedFiles([...uploadedFiles, ...newFiles]);
      } else {
        alert('Please select image files');
      }
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index));
  };

  const handleImagesSubmit = async (e) => {
    e.preventDefault();
    if (uploadedFiles.length === 0) {
      alert('Please select at least one image');
      return;
    }

    setLoading(true);
    try {
      // Process each image
      const results = [];
      for (const file of uploadedFiles) {
        const formDataFile = new FormData();
        formDataFile.append('file', file);

        const response = await fetch(`${getAPIBaseURL()}/fertilizer-from-image`, {
          method: 'POST',
          body: formDataFile
        });
        const data = await response.json();
        results.push({
          filename: file.name,
          data: data
        });
      }

      // Show results for all images
      setResult({ success: true, results: results });
      
      if (results.length > 0 && results[0].data.success) {
        // Speak the summary
        const summary = results[0].data.summary;
        if (summary) {
          const utterance = new SpeechSynthesisUtterance(summary);
          utterance.rate = 0.9;
          utterance.pitch = 1;
          utterance.volume = 1;
          setIsSpeaking(true);
          utterance.onend = () => setIsSpeaking(false);
          window.speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({ success: false, error: 'Failed to process images' });
    }
    setLoading(false);
  };

  const crops = [
    'rice', 'wheat', 'maize', 'cotton', 'potato', 'coffee',
    'sugarcane', 'soybean', 'chickpea', 'lentil', 'groundnut',
    'sunflower', 'mustard', 'tomato', 'onion', 'cabbage',
    'carrot', 'brinjal', 'chilli', 'turmeric', 'ginger',
    'banana', 'mango', 'coconut', 'tea'
  ];

  return (
    <div className="min-h-screen bg-eco-cream py-20">
      <div className="max-w-4xl mx-auto px-6">
        <h1 className="text-4xl font-bold text-eco-green-dark mb-2">🧪 Fertilizer Recommendation</h1>
        <p className="text-gray-600 mb-8">Get personalized fertilizer suggestions based on your crop and soil nutrients</p>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Tab Navigation */}
          <div className="flex gap-2 mb-8 border-b-2 border-gray-200">
            <button
              onClick={() => setActiveTab('manual')}
              className={`px-6 py-3 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'manual'
                  ? 'text-eco-green border-b-4 border-eco-green'
                  : 'text-gray-600 hover:text-eco-green'
              }`}
            >
              📝 Manual Input
            </button>
            <button
              onClick={() => setActiveTab('image')}
              className={`px-6 py-3 font-semibold transition-colors whitespace-nowrap ${
                activeTab === 'image'
                  ? 'text-eco-green border-b-4 border-eco-green'
                  : 'text-gray-600 hover:text-eco-green'
              }`}
            >
              🖼️ Crop Image
            </button>
          </div>

          {/* Manual Input Tab */}
          {activeTab === 'manual' && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Crop Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Crop</label>
                <select
                  name="crop"
                  value={formData.crop}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-eco-green rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
                  required
                >
                  <option value="">Choose a crop...</option>
                  {crops.map(crop => (
                    <option key={crop} value={crop}>
                      {crop.charAt(0).toUpperCase() + crop.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

            {/* Soil Parameters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nitrogen (N) mg/kg</label>
                <input
                  type="number"
                  name="nitrogen"
                  value={formData.nitrogen}
                  onChange={handleChange}
                  placeholder="e.g., 90"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phosphorus (P) mg/kg</label>
                <input
                  type="number"
                  name="phosphorus"
                  value={formData.phosphorus}
                  onChange={handleChange}
                  placeholder="e.g., 42"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Potassium (K) mg/kg</label>
                <input
                  type="number"
                  name="potassium"
                  value={formData.potassium}
                  onChange={handleChange}
                  placeholder="e.g., 43"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                  required
                />
              </div>
            </div>

            {/* Additional Parameters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Temperature (°C)</label>
                <input
                  type="number"
                  name="temperature"
                  value={formData.temperature}
                  onChange={handleChange}
                  placeholder="e.g., 25"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Humidity (%)</label>
                <input
                  type="number"
                  name="humidity"
                  value={formData.humidity}
                  onChange={handleChange}
                  placeholder="e.g., 70"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Moisture (%)</label>
                <input
                  type="number"
                  name="moisture"
                  value={formData.moisture}
                  onChange={handleChange}
                  placeholder="e.g., 50"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Soil Type</label>
                <select
                  name="soil_type"
                  value={formData.soil_type}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-eco-green"
                >
                  <option value="">Select...</option>
                  <option value="loamy">Loamy</option>
                  <option value="sandy">Sandy</option>
                  <option value="clay">Clay</option>
                  <option value="silty">Silty</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50"
            >
              {loading ? '⏳ Analyzing...' : '🧪 Get Fertilizer Recommendation'}
            </button>
            </form>
          )}

          {/* Image Upload Tab */}
          {activeTab === 'image' && (
            <form onSubmit={handleImagesSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Upload Crop Images</label>
                <div className="border-2 border-dashed border-eco-green rounded-lg p-8 text-center cursor-pointer hover:bg-eco-cream transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                    id="image-input"
                  />
                  <label htmlFor="image-input" className="cursor-pointer">
                    <div className="text-4xl mb-2">🖼️</div>
                    <p className="text-gray-700 font-semibold">
                      Click to upload crop images
                    </p>
                    <p className="text-gray-500 text-sm mt-1">JPG, PNG, GIF, BMP supported - Multiple files allowed</p>
                  </label>
                </div>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-800 mb-3">📁 Uploaded Files ({uploadedFiles.length})</h3>
                  <div className="space-y-2">
                    {uploadedFiles.map((file, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-300">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🖼️</span>
                          <span className="text-gray-700 font-semibold">{file.name}</span>
                          <span className="text-gray-500 text-sm">({(file.size / 1024).toFixed(2)} KB)</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(idx)}
                          className="text-red-500 hover:text-red-700 font-bold"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                <p className="text-blue-700 text-sm">
                  <span className="font-semibold">💡 Tip:</span> Upload multiple crop images. The system will identify each crop and recommend fertilizer for each one.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || uploadedFiles.length === 0}
                className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50"
              >
                {loading ? '⏳ Analyzing Images...' : `📷 Identify Crops & Recommend Fertilizer (${uploadedFiles.length})`}
              </button>
            </form>
          )}
        </div>

        {/* Results - Manual */}
        {result && activeTab === 'manual' && result.recommendation && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-8">
            <div>
              <h2 className="text-2xl font-bold text-eco-green-dark mb-6">
                Fertilizer Recommendation for {formData.crop.toUpperCase()}
              </h2>

              {/* Primary Recommendation */}
              <div className="bg-eco-cream rounded-lg p-6 mb-6 border-2 border-eco-green">
                <h3 className="text-xl font-bold text-eco-green-dark mb-4">
                  🎯 Recommended Fertilizer
                </h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Fertilizer</p>
                    <p className="text-lg font-bold text-eco-green">
                      {result.recommendation.recommended_fertilizer}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="text-lg font-semibold text-gray-800">
                      {result.recommendation.confidence}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Application Rate (per hectare)</p>
                    <p className="text-gray-700">
                      N: {result.recommendation.application_rate.nitrogen} kg<br/>
                      P: {result.recommendation.application_rate.phosphorus} kg<br/>
                      K: {result.recommendation.application_rate.potassium} kg
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Timing</p>
                    <ul className="text-gray-700 mt-1">
                      {result.recommendation.timing.map((t, i) => (
                        <li key={i}>• {t}</li>
                      ))}
                    </ul>
                  </div>
                  {result.recommendation.precautions && result.recommendation.precautions.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-600">Precautions</p>
                      <ul className="text-gray-700 mt-1">
                        {result.recommendation.precautions.map((p, i) => (
                          <li key={i}>• {p}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Summary */}
              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300 mb-6">
                <p className="text-blue-700">
                  <span className="font-semibold">Source:</span> {result.recommendation.source}
                </p>
              </div>

              {/* Voice Output */}
              <div className="flex gap-3">
                <button
                  onClick={() => speakResult(result)}
                  disabled={isSpeaking}
                  className="flex-1 bg-blue-500 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
                >
                  {isSpeaking ? '🔊 Speaking...' : '🔊 Speak Recommendation'}
                </button>
                {isSpeaking && (
                  <button
                    onClick={stopSpeaking}
                    className="flex-1 bg-red-500 text-white font-semibold py-2 rounded-lg hover:bg-red-600"
                  >
                    ⏹️ Stop
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Results - Image */}
        {result && activeTab === 'image' && result.success && (
          <div className="mt-8 space-y-6">
            <h2 className="text-2xl font-bold text-eco-green-dark">
              🖼️ Crop Health Analysis Results ({result.results.length} images)
            </h2>

            {result.results.map((item, idx) => (
              <div key={idx} className="bg-white rounded-lg shadow-lg p-8">
                <h3 className="text-xl font-bold text-eco-green-dark mb-6">
                  📸 Image {idx + 1}: {item.filename}
                </h3>

                {item.data.success ? (
                  <>
                    {/* Health Status */}
                    <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-300 mb-6">
                      <h4 className="text-lg font-bold text-blue-700 mb-3">🏥 Crop Health Status</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-gray-600 text-sm">Health Status</p>
                          <p className="text-3xl font-bold text-blue-600 mt-2">
                            {item.data.health_analysis.status}
                          </p>
                          <p className="text-gray-700 text-sm mt-2">
                            Confidence: {item.data.health_analysis.confidence}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600 text-sm">Assessment</p>
                          <p className="text-gray-700 mt-2">
                            {item.data.health_analysis.details.assessment}
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-green-100 p-3 rounded">
                          <p className="text-green-700 text-sm font-semibold">Green Coverage</p>
                          <p className="text-2xl font-bold text-green-600">
                            {item.data.health_analysis.details.green_coverage}
                          </p>
                        </div>
                        <div className="bg-yellow-100 p-3 rounded">
                          <p className="text-yellow-700 text-sm font-semibold">Yellow Coverage</p>
                          <p className="text-2xl font-bold text-yellow-600">
                            {item.data.health_analysis.details.yellow_coverage}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Size/Growth Stage */}
                    <div className="bg-purple-50 p-6 rounded-lg border-2 border-purple-300 mb-6">
                      <h4 className="text-lg font-bold text-purple-700 mb-3">📏 Crop Size & Growth Stage</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <p className="text-gray-600 text-sm">Size Category</p>
                          <p className="text-2xl font-bold text-purple-600 mt-2">
                            {item.data.size_analysis.category}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600 text-sm">Growth Stage</p>
                          <p className="text-lg font-semibold text-purple-700 mt-2">
                            {item.data.size_analysis.growth_stage}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600 text-sm">Estimated Age</p>
                          <p className="text-lg font-semibold text-purple-700 mt-2">
                            {item.data.size_analysis.estimated_age}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Fertilizer Recommendation */}
                    <div className="bg-eco-cream rounded-lg p-6 mb-6 border-2 border-eco-green">
                      <h4 className="text-lg font-bold text-eco-green-dark mb-4">
                        🎯 Recommended Fertilizer (Based on Health & Size)
                      </h4>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600">Primary Recommendation</p>
                          <p className="text-lg font-bold text-eco-green">
                            {item.data.fertilizer_recommendation.primary_recommendation}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Quantity</p>
                          <p className="text-lg font-semibold text-gray-800">
                            {item.data.fertilizer_recommendation.quantity}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Timing</p>
                          <p className="text-lg font-semibold text-gray-800">
                            {item.data.fertilizer_recommendation.timing}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Reason</p>
                          <p className="text-gray-700 mt-1">
                            {item.data.fertilizer_recommendation.reason}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Nutrient Focus */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                      <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                        <p className="text-blue-700 font-semibold text-sm">Nitrogen Focus</p>
                        <p className="text-2xl font-bold text-blue-600 mt-2">
                          {item.data.fertilizer_recommendation.nutrient_focus.nitrogen}
                        </p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300">
                        <p className="text-green-700 font-semibold text-sm">Phosphorus Focus</p>
                        <p className="text-2xl font-bold text-green-600 mt-2">
                          {item.data.fertilizer_recommendation.nutrient_focus.phosphorus}
                        </p>
                      </div>
                      <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-300">
                        <p className="text-yellow-700 font-semibold text-sm">Potassium Focus</p>
                        <p className="text-2xl font-bold text-yellow-600 mt-2">
                          {item.data.fertilizer_recommendation.nutrient_focus.potassium}
                        </p>
                      </div>
                    </div>

                    {/* Additional Measures */}
                    <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300 mb-6">
                      <p className="text-green-700 font-semibold">📋 Additional Measures</p>
                      <p className="text-green-600 mt-2">
                        {item.data.fertilizer_recommendation.additional_measures}
                      </p>
                    </div>

                    {/* Warning if any */}
                    {item.data.fertilizer_recommendation.warning && (
                      <div className="bg-red-50 p-4 rounded-lg border-2 border-red-300 mb-6">
                        <p className="text-red-700 font-semibold">⚠️ Important Warning</p>
                        <p className="text-red-600 mt-2">
                          {item.data.fertilizer_recommendation.warning}
                        </p>
                      </div>
                    )}

                    {/* Summary */}
                    <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                      <p className="text-blue-700">
                        <span className="font-semibold">Summary:</span> {item.data.summary}
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6">
                    <p className="text-red-700 font-semibold">❌ Error</p>
                    <p className="text-red-600 mt-2">{item.data.error}</p>
                  </div>
                )}
              </div>
            ))}

            {/* Voice Output for First Image */}
            {result.results.length > 0 && result.results[0].data.success && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      const summary = result.results[0].data.summary;
                      const utterance = new SpeechSynthesisUtterance(summary);
                      utterance.rate = 0.9;
                      utterance.pitch = 1;
                      utterance.volume = 1;
                      setIsSpeaking(true);
                      utterance.onend = () => setIsSpeaking(false);
                      window.speechSynthesis.speak(utterance);
                    }}
                    disabled={isSpeaking}
                    className="flex-1 bg-blue-500 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
                  >
                    {isSpeaking ? '🔊 Speaking...' : '🔊 Speak Analysis'}
                  </button>
                  {isSpeaking && (
                    <button
                      onClick={stopSpeaking}
                      className="flex-1 bg-red-500 text-white font-semibold py-2 rounded-lg hover:bg-red-600"
                    >
                      ⏹️ Stop
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Results */}
        {result && !result.success && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-8">
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6">
              <p className="text-red-700 font-semibold">❌ Error</p>
              <p className="text-red-600 mt-2">{result.error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FertilizerRecommendation;

