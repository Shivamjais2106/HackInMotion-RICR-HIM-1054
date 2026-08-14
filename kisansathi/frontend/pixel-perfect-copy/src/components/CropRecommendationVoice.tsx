import { useState } from 'react';
import useSpeechRecognition from 'react-speech-recognition';
import { getAPIBaseURL } from '@/utils/api';

function CropRecommendationVoice() {
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
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);

  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  if (!browserSupportsSpeechRecognition) {
    return <div className="text-red-600">Browser doesn't support speech recognition.</div>;
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleVoiceInput = () => {
    if (!voiceMode) {
      setVoiceMode(true);
      resetTranscript();
    }
  };

  const parseVoiceInput = () => {
    // Simple parsing of voice input
    // Example: "nitrogen 90 phosphorus 42 potassium 43 temperature 20 humidity 82 ph 6.5 rainfall 202"
    const words = transcript.toLowerCase().split(/\s+/);
    const newData = { ...formData };

    for (let i = 0; i < words.length - 1; i++) {
      const key = words[i];
      const value = words[i + 1];

      if (key === 'nitrogen' && !isNaN(value)) newData.nitrogen = value;
      else if (key === 'phosphorus' && !isNaN(value)) newData.phosphorus = value;
      else if (key === 'potassium' && !isNaN(value)) newData.potassium = value;
      else if (key === 'temperature' && !isNaN(value)) newData.temperature = value;
      else if (key === 'humidity' && !isNaN(value)) newData.humidity = value;
      else if (key === 'ph' && !isNaN(value)) newData.ph = value;
      else if (key === 'rainfall' && !isNaN(value)) newData.rainfall = value;
    }

    setFormData(newData);
    setVoiceMode(false);
    resetTranscript();
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
      
      // Speak the result
      if (data.crop) {
        speakResult(data);
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Failed to get prediction' });
    }
    setLoading(false);
  };

  const speakResult = (data) => {
    const text = `The recommended crop is ${data.crop}. ${data.explanation || ''}`;
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

  return (
    <div className="min-h-screen bg-eco-cream py-20">
      <div className="max-w-2xl mx-auto px-6">
        <h1 className="text-4xl font-bold text-eco-green-dark mb-8">🎤 Crop Recommendation (Voice Enabled)</h1>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8">
          {/* Voice Input Section */}
          <div className="mb-8 p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-4">🎙️ Voice Input</h3>
            
            {voiceMode ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg ${listening ? 'bg-red-100 border-2 border-red-500' : 'bg-gray-100'}`}>
                  <p className="text-sm font-semibold mb-2">
                    {listening ? '🔴 Listening...' : '⏹️ Ready to listen'}
                  </p>
                  <p className="text-gray-700 min-h-12 p-2 bg-white rounded">
                    {transcript || 'Say: nitrogen 90 phosphorus 42 potassium 43 temperature 20 humidity 82 ph 6.5 rainfall 202'}
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      if (!listening) {
                        resetTranscript();
                      }
                    }}
                    className="flex-1 bg-red-500 text-white font-semibold py-2 rounded-lg hover:bg-red-600"
                  >
                    {listening ? '🔴 Recording...' : '🎙️ Start Recording'}
                  </button>
                  <button
                    type="button"
                    onClick={parseVoiceInput}
                    className="flex-1 bg-green-500 text-white font-semibold py-2 rounded-lg hover:bg-green-600"
                  >
                    ✓ Use This Input
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleVoiceInput}
                className="w-full bg-blue-500 text-white font-semibold py-3 rounded-lg hover:bg-blue-600 transition-colors"
              >
                🎤 Enable Voice Input
              </button>
            )}
          </div>

          {/* Manual Input Section */}
          <div className="mb-8">
            <h3 className="text-lg font-bold text-gray-800 mb-4">📝 Or Enter Manually</h3>
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
            {loading ? '⏳ Predicting...' : '🌾 Get Recommendation'}
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
                
                {result.explanation && (
                  <div className="bg-eco-cream rounded-lg p-6 mb-6 border-l-4 border-eco-green">
                    <h3 className="text-lg font-bold text-eco-green-dark mb-3">Why {result.primary_crop.toUpperCase()}?</h3>
                    <div className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                      {result.explanation}
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                  <div className="bg-blue-50 p-4 rounded">
                    <p className="text-gray-600">Temperature</p>
                    <p className="text-lg font-bold text-blue-600">{result.temperature}°C</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded">
                    <p className="text-gray-600">Humidity</p>
                    <p className="text-lg font-bold text-green-600">{result.humidity}%</p>
                  </div>
                </div>

                {/* Voice Output Controls */}
                <div className="flex gap-3">
                  <button
                    onClick={() => speakResult(result)}
                    disabled={isSpeaking}
                    className="flex-1 bg-blue-500 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
                  >
                    {isSpeaking ? '🔊 Speaking...' : '🔊 Speak Result'}
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
      </div>
    </div>
  );
}

export default CropRecommendationVoice;
