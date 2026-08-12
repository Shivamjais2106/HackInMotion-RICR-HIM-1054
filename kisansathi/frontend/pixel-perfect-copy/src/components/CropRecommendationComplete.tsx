import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2 } from "lucide-react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { getAPIBaseURL } from '@/utils/api';

interface CropRecommendation {
  crop: string;
  suitability: number;
  reason: string;
  confidence?: number;
  confidence_str?: string;
  rank?: number;
}

interface Result {
  crop?: string;
  top_crops?: CropRecommendation[];
  explanation?: string;
  primary_crop?: string;
  temperature?: number;
  humidity?: number;
  month_info?: any;
  error?: string;
}

const CropRecommendationComplete = () => {
  const { language } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [extractingImage, setExtractingImage] = useState(false);
  const [activeTab, setActiveTab] = useState<'manual' | 'advanced' | 'perMonth'>('manual');
  const [voiceMode, setVoiceMode] = useState(false);
  const [cameraMode, setCameraMode] = useState(false);
  const [months, setMonths] = useState<string[]>([]);
  const [soilPhotoFile, setSoilPhotoFile] = useState<File | null>(null);
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [locationDetected, setLocationDetected] = useState(false);
  
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    rainfall: '',
    temperature: '',
    humidity: '',
    month: '',
    location: ''
  });

  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  // Function to map coordinates to Indian region
  const mapCoordinatesToRegion = (latitude: number, longitude: number): string => {
    // India's approximate regions based on coordinates
    // North India: latitude > 28, longitude 75-85
    // South India: latitude < 15, longitude 75-80
    // East India: latitude 20-28, longitude > 85
    // West India: latitude 18-28, longitude < 75
    // Central India: latitude 20-25, longitude 75-82
    // Northeast India: latitude > 24, longitude > 88

    if (latitude > 28 && longitude >= 75 && longitude <= 85) {
      return 'North India';
    } else if (latitude < 15 && longitude >= 75 && longitude <= 80) {
      return 'South India';
    } else if (latitude >= 20 && latitude <= 28 && longitude > 85) {
      return 'East India';
    } else if (latitude >= 18 && latitude <= 28 && longitude < 75) {
      return 'West India';
    } else if (latitude >= 20 && latitude <= 25 && longitude >= 75 && longitude <= 82) {
      return 'Central India';
    } else if (latitude > 24 && longitude > 88) {
      return 'Northeast India';
    }
    
    // Default to North India if coordinates don't match
    return 'North India';
  };

  // Detect current location on component mount
  useEffect(() => {
    // Fetch months
    fetch(`${getAPIBaseURL()}/months`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setMonths(data.months);
        }
      })
      .catch(err => console.error('Error fetching months:', err));

    // Detect geolocation
    if (navigator.geolocation) {
      setDetectingLocation(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const detectedRegion = mapCoordinatesToRegion(latitude, longitude);
          setFormData((prev) => ({
            ...prev,
            location: detectedRegion
          }));
          setLocationDetected(true);
          setDetectingLocation(false);
        },
        (error) => {
          console.log('Geolocation error:', error);
          setDetectingLocation(false);
          // Silently fail - user can manually select location
        }
      );
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleVoiceInput = () => {
    if (!voiceMode) {
      setVoiceMode(true);
      resetTranscript();
    }
  };

  const parseVoiceInput = () => {
    const words = transcript.toLowerCase().split(/\s+/);
    const newData = { ...formData };

    for (let i = 0; i < words.length - 1; i++) {
      const key = words[i];
      const value = words[i + 1];

      if (key === 'nitrogen' && !isNaN(Number(value))) newData.nitrogen = value;
      else if (key === 'phosphorus' && !isNaN(Number(value))) newData.phosphorus = value;
      else if (key === 'potassium' && !isNaN(Number(value))) newData.potassium = value;
      else if (key === 'temperature' && !isNaN(Number(value))) newData.temperature = value;
      else if (key === 'humidity' && !isNaN(Number(value))) newData.humidity = value;
      else if (key === 'ph' && !isNaN(Number(value))) newData.ph = value;
      else if (key === 'rainfall' && !isNaN(Number(value))) newData.rainfall = value;
    }

    setFormData(newData);
    setVoiceMode(false);
    resetTranscript();
  };

  const handleCameraCapture = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setExtractingImage(true);
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('image', file);

      const response = await fetch(`${getAPIBaseURL()}/recommendations/extract-from-image`, {
        method: 'POST',
        body: formDataToSend,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.values) {
          // Fill form with extracted values
          const values = data.values;
          setFormData((prev) => ({
            ...prev,
            nitrogen: values.nitrogen ? String(values.nitrogen) : prev.nitrogen,
            phosphorus: values.phosphorus ? String(values.phosphorus) : prev.phosphorus,
            potassium: values.potassium ? String(values.potassium) : prev.potassium,
            ph: values.ph ? String(values.ph) : prev.ph,
            rainfall: values.rainfall ? String(values.rainfall) : prev.rainfall,
            temperature: values.temperature ? String(values.temperature) : prev.temperature,
            humidity: values.humidity ? String(values.humidity) : prev.humidity,
          }));
          setCameraMode(false);
        }
      }
    } catch (error) {
      console.error('Error processing image:', error);
    } finally {
      setExtractingImage(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      let endpoint = '';
      let payload: any = {};
      
      if (activeTab === 'manual') {
        // Manual input endpoint
        endpoint = `${getAPIBaseURL()}/recommendations/crop`;
        payload = {
          N: parseFloat(formData.nitrogen),
          P: parseFloat(formData.phosphorus),
          K: parseFloat(formData.potassium),
          temperature: parseFloat(formData.temperature),
          humidity: parseFloat(formData.humidity) || 70,
          ph: parseFloat(formData.ph),
          rainfall: parseFloat(formData.rainfall),
          top_n: 2
        };
      } else if (activeTab === 'perMonth') {
        // Per Month endpoint - uses advanced-crop with just month
        endpoint = `${getAPIBaseURL()}/recommendations/advanced-crop`;
        payload = {
          month: formData.month,
          location: 'Central India' // Default location for per-month recommendations
        };
      } else {
        // Advanced endpoint - Location & Season
        endpoint = `${getAPIBaseURL()}/recommendations/advanced-crop`;
        payload = {
          month: formData.month,
          location: formData.location
        };
        
        // Add soil photo if provided
        if (soilPhotoFile) {
          const formDataToSend = new FormData();
          formDataToSend.append('month', formData.month);
          formDataToSend.append('location', formData.location);
          formDataToSend.append('soil_photo', soilPhotoFile);
          
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: formDataToSend,
          });

          if (response.ok) {
            const data = await response.json();
            const transformed = {
              top_crops: data.recommendations.map((rec: any, idx: number) => ({
                crop: rec.crop,
                suitability: parseFloat(rec.confidence_value || rec.confidence || 0),
                reason: rec.reason,
                confidence: parseFloat(rec.confidence_value || rec.confidence || 0),
                confidence_str: `${(parseFloat(rec.confidence_value || rec.confidence || 0) * 100).toFixed(1)}%`,
                rank: idx + 1,
                detailed_explanation: rec.detailed_explanation || ''
              })),
              primary_crop: data.recommendations[0]?.crop || 'Unknown',
              explanation: data.recommendations[0]?.reason || '',
            };
            setResult(transformed);
            
            // Auto-speak result
            if (transformed.primary_crop) {
              speakResult(transformed);
            }
          } else {
            setResult({ error: 'Failed to get recommendations' });
          }
          setLoading(false);
          return;
        }
        
        // If no soil photo, send as JSON
        payload = {
          month: formData.month,
          location: formData.location,
          N: formData.nitrogen ? parseFloat(formData.nitrogen) : undefined,
          P: formData.phosphorus ? parseFloat(formData.phosphorus) : undefined,
          K: formData.potassium ? parseFloat(formData.potassium) : undefined,
          ph: formData.ph ? parseFloat(formData.ph) : undefined,
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        const transformed = {
          top_crops: data.recommendations.map((rec: any, idx: number) => ({
            crop: rec.crop,
            suitability: parseFloat(rec.confidence_value || rec.confidence || 0),
            reason: rec.reason,
            confidence: parseFloat(rec.confidence_value || rec.confidence || 0),
            confidence_str: `${(parseFloat(rec.confidence_value || rec.confidence || 0) * 100).toFixed(1)}%`,
            rank: idx + 1,
            detailed_explanation: rec.detailed_explanation || ''
          })),
          primary_crop: data.recommendations[0]?.crop || 'Unknown',
          explanation: data.recommendations[0]?.reason || '',
          temperature: parseFloat(formData.temperature) || 25,
          humidity: parseFloat(formData.humidity) || 65,
        };
        setResult(transformed);
        
        // Auto-speak result
        if (transformed.primary_crop) {
          speakResult(transformed);
        }
      } else {
        setResult({ error: 'Failed to get recommendations' });
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Error fetching recommendations' });
    } finally {
      setLoading(false);
    }
  };

  const speakExplanation = (explanation: string) => {
    if (!explanation) return;
    
    // Truncate very long explanations for audio
    let text = explanation;
    if (text.length > 500) {
      text = text.substring(0, 500) + '...';
    }
    
    // Try to use Hindi voice if available, otherwise use English
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Get available voices
    const voices = window.speechSynthesis.getVoices();
    const hindiVoice = voices.find(voice => voice.lang.includes('hi'));
    
    if (hindiVoice) {
      utterance.voice = hindiVoice;
      utterance.lang = 'hi-IN';
    } else {
      // Fallback to English if Hindi not available
      utterance.lang = 'en-US';
    }
    
    utterance.rate = 0.85;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
    };
    
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const speakResult = (data: Result) => {
    // Create a shorter version for audio - just the key information
    let text = '';
    
    if (data.top_crops && data.top_crops.length > 0) {
      const crop1 = data.top_crops[0];
      const crop2 = data.top_crops[1];
      
      // Try Hindi first, but have English fallback
      text = `Recommended crops are: First crop ${crop1.crop} with confidence ${crop1.confidence_str}. Second crop ${crop2?.crop || 'none'} with confidence ${crop2?.confidence_str || '0%'}.`;
    } else {
      text = `Recommended crop is ${data.primary_crop}. ${data.explanation || ''}`;
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US'; // Use English for better browser support
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
    };
    
    window.speechSynthesis.cancel(); // Cancel any previous speech
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const renderAdvancedTab = () => (
    <div className="space-y-6">
      {/* Month Selection */}
      <div className="p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-900 mb-4">📅 {language === 'en' ? 'Select Month' : 'महीना चुनें'}</h3>
        <select
          name="month"
          value={formData.month}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
          required
        >
          <option value="">{language === 'en' ? 'Choose a month...' : 'एक महीना चुनें...'}</option>
          {months.map(month => (
            <option key={month} value={month}>{month}</option>
          ))}
        </select>
        <p className="text-sm text-blue-700 mt-3">
          💡 {language === 'en' ? 'Select the month to get crops suitable for that season' : 'उस मौसम के लिए उपयुक्त फसलें प्राप्त करने के लिए महीना चुनें'}
        </p>
      </div>

      {/* Location Selection */}
      <div className="p-6 bg-purple-50 rounded-lg border-2 border-purple-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-purple-900">🌍 {language === 'en' ? 'Select Location' : 'स्थान चुनें'}</h3>
          {detectingLocation && (
            <span className="text-sm text-purple-600 font-semibold">
              📍 {language === 'en' ? 'Detecting...' : 'पता लगा रहे हैं...'}
            </span>
          )}
          {locationDetected && !detectingLocation && (
            <span className="text-sm text-green-600 font-semibold">
              ✓ {language === 'en' ? 'Auto-detected' : 'स्वचालित रूप से पता लगाया गया'}
            </span>
          )}
        </div>
        <select
          name="location"
          value={formData.location}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
          required
        >
          <option value="">{language === 'en' ? 'Choose a location...' : 'एक स्थान चुनें...'}</option>
          <option value="North India">{language === 'en' ? 'North India' : 'उत्तर भारत'}</option>
          <option value="South India">{language === 'en' ? 'South India' : 'दक्षिण भारत'}</option>
          <option value="East India">{language === 'en' ? 'East India' : 'पूर्व भारत'}</option>
          <option value="West India">{language === 'en' ? 'West India' : 'पश्चिम भारत'}</option>
          <option value="Central India">{language === 'en' ? 'Central India' : 'मध्य भारत'}</option>
          <option value="Northeast India">{language === 'en' ? 'Northeast India' : 'पूर्वोत्तर भारत'}</option>
        </select>
        <p className="text-sm text-purple-700 mt-3">
          💡 {language === 'en' ? 'Your location is auto-detected. You can change it manually if needed.' : 'आपका स्थान स्वचालित रूप से पता लगाया गया है। यदि आवश्यक हो तो आप इसे मैन्युअल रूप से बदल सकते हैं।'}
        </p>
      </div>

      {/* Soil Photo Upload (Optional) */}
      <div className="p-6 bg-orange-50 rounded-lg border-2 border-orange-200">
        <h3 className="text-lg font-bold text-orange-900 mb-4">📷 {language === 'en' ? 'Upload Soil Photo (Optional)' : 'मिट्टी की फोटो अपलोड करें (वैकल्पिक)'}</h3>
        <div className="space-y-3">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setSoilPhotoFile(file);
              }
            }}
            className="w-full px-4 py-3 border-2 border-orange-300 rounded-lg"
          />
          {soilPhotoFile && (
            <p className="text-sm text-orange-700 font-semibold">
              ✓ {language === 'en' ? 'File selected:' : 'फाइल चुनी गई:'} {soilPhotoFile.name}
            </p>
          )}
          <p className="text-sm text-orange-700">
            💡 {language === 'en' ? 'Upload a soil photo for more accurate recommendations (optional)' : 'अधिक सटीक सिफारिशों के लिए मिट्टी की फोटो अपलोड करें (वैकल्पिक)'}
          </p>
        </div>
      </div>
    </div>
  );

  const renderManualTab = () => (
    <div className="space-y-6">
      {/* Camera Input Section */}
      <div className="p-6 bg-orange-50 rounded-lg border-2 border-orange-200">
        <h3 className="text-lg font-bold text-orange-900 mb-4">📷 {language === 'en' ? 'Capture Soil Report (Optional)' : 'मिट्टी रिपोर्ट की फोटो लें (वैकल्पिक)'}</h3>
        
        {cameraMode ? (
          <div className="space-y-4">
            <div className="p-4 bg-gray-100 rounded-lg border-2 border-gray-300">
              <p className="text-sm font-semibold mb-3 text-gray-700">
                {extractingImage ? '⏳ Processing image...' : '📸 Select or capture soil report image'}
              </p>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleCameraCapture}
                disabled={extractingImage}
                className="w-full"
              />
            </div>
            <button
              type="button"
              onClick={() => setCameraMode(false)}
              className="w-full bg-gray-500 text-white font-semibold py-2 rounded-lg hover:bg-gray-600"
            >
              ✕ Cancel
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setCameraMode(true)}
            className="w-full bg-orange-500 text-white font-semibold py-3 rounded-lg hover:bg-orange-600 transition-colors"
          >
            📷 {language === 'en' ? 'Capture Soil Report' : 'मिट्टी रिपोर्ट की फोटो लें'}
          </button>
        )}
      </div>

      {/* Manual Input Section */}
      <div className="p-6 bg-green-50 rounded-lg border-2 border-green-200">
        <h3 className="text-lg font-bold text-green-900 mb-4">📝 {language === 'en' ? 'Soil Parameters' : 'मिट्टी के पैरामीटर'}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'en' ? 'Nitrogen (N)' : 'नाइट्रोजन (N)'}
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
              {language === 'en' ? 'Phosphorus (P)' : 'फॉस्फोरस (P)'}
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
              {language === 'en' ? 'Potassium (K)' : 'पोटेशियम (K)'}
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
              {language === 'en' ? 'pH Level' : 'पीएच स्तर'}
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
              {language === 'en' ? 'Rainfall (mm)' : 'वर्षा (मिमी)'}
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
              {language === 'en' ? 'Temperature (°C)' : 'तापमान (°C)'}
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
              {language === 'en' ? 'Humidity (%)' : 'आर्द्रता (%)'}
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
      </div>
    </div>
  );

  const renderVoiceTab = () => (
    <div className="space-y-6">
      {!browserSupportsSpeechRecognition && (
        <div className="text-red-600 p-4 bg-red-50 rounded-lg">
          {language === 'en' ? "Browser doesn't support speech recognition." : "आपका ब्राउज़र स्पीच रिकग्निशन को सपोर्ट नहीं करता।"}
        </div>
      )}

      <div className="p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-900 mb-4">🎙️ {language === 'en' ? 'Voice Input' : 'वॉयस इनपुट'}</h3>
        
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
            🎤 {language === 'en' ? 'Enable Voice Input' : 'वॉयस इनपुट सक्षम करें'}
          </button>
        )}
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">📝 {language === 'en' ? 'Or Enter Manually' : 'या मैन्युअल रूप से दर्ज करें'}</h3>
        {renderManualTab()}
      </div>
    </div>
  );

  const renderSeasonalTab = () => (
    <div className="space-y-6">
      <div className="p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-900 mb-4">📅 {language === 'en' ? 'Select Month' : 'महीना चुनें'}</h3>
        <select
          name="month"
          value={formData.month}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
          required
        >
          <option value="">{language === 'en' ? 'Choose a month...' : 'एक महीना चुनें...'}</option>
          {months.map(month => (
            <option key={month} value={month}>{month}</option>
          ))}
        </select>
        <p className="text-sm text-blue-700 mt-3">
          💡 {language === 'en' ? 'Selecting a month helps us recommend crops suitable for that season' : 'महीना चुनने से हमें उस मौसम के लिए उपयुक्त फसलों की सिफारिश करने में मदद मिलती है'}
        </p>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">🌱 {language === 'en' ? 'Soil Parameters' : 'मिट्टी के पैरामीटर'}</h3>
        {renderManualTab()}
      </div>
    </div>
  );

  const renderPerMonthTab = () => (
    <div className="space-y-6">
      <div className="p-6 bg-purple-50 rounded-lg border-2 border-purple-200">
        <h3 className="text-lg font-bold text-purple-900 mb-4">📅 {language === 'en' ? 'Select Month for Recommendations' : 'सिफारिशों के लिए महीना चुनें'}</h3>
        <select
          name="month"
          value={formData.month}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-eco-green text-lg"
          required
        >
          <option value="">{language === 'en' ? 'Choose a month...' : 'एक महीना चुनें...'}</option>
          {months.map(month => (
            <option key={month} value={month}>{month}</option>
          ))}
        </select>
        <p className="text-sm text-purple-700 mt-3">
          💡 {language === 'en' ? 'Get crops recommended specifically for the selected month' : 'चुने गए महीने के लिए विशेष रूप से अनुशंसित फसलें प्राप्त करें'}
        </p>
      </div>

      <div className="p-6 bg-indigo-50 rounded-lg border-2 border-indigo-200">
        <h3 className="text-lg font-bold text-indigo-900 mb-4">ℹ️ {language === 'en' ? 'About This Option' : 'इस विकल्प के बारे में'}</h3>
        <p className="text-sm text-indigo-700 leading-relaxed">
          {language === 'en' 
            ? 'This option provides crops that are best suited for the selected month based on seasonal patterns. The recommendations are consistent and based on traditional agricultural practices in India.'
            : 'यह विकल्प चुने गए महीने के लिए सबसे उपयुक्त फसलें प्रदान करता है। सिफारिशें भारत में पारंपरिक कृषि प्रथाओं पर आधारित हैं।'}
        </p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            {language === 'en' ? '🌾 Crop Recommendation' : '🌾 फसल की सिफारिश'}
          </h1>
          <p className="text-gray-600 mt-2">
            {language === 'en'
              ? 'Get personalized crop recommendations using manual input, voice, or seasonal selection'
              : 'मैन्युअल इनपुट, वॉयस, या मौसमी चयन का उपयोग करके व्यक्तिगत फसल सिफारिशें प्राप्त करें'}
          </p>
        </div>

        <Card className="bg-white shadow-lg mb-8">
          <CardContent className="pt-6">
            {/* Tab Selection */}
            <div className="flex gap-4 mb-6 border-b-2 overflow-x-auto">
              <button
                onClick={() => setActiveTab('manual')}
                className={`px-6 py-3 font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'manual'
                    ? 'text-green-600 border-b-4 border-green-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📝 {language === 'en' ? 'Manual Input' : 'मैन्युअल इनपुट'}
              </button>
              <button
                onClick={() => setActiveTab('advanced')}
                className={`px-6 py-3 font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'advanced'
                    ? 'text-blue-600 border-b-4 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🌍 {language === 'en' ? 'By Location & Season' : 'स्थान और मौसम से'}
              </button>
              <button
                onClick={() => setActiveTab('perMonth')}
                className={`px-6 py-3 font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'perMonth'
                    ? 'text-purple-600 border-b-4 border-purple-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📅 {language === 'en' ? 'Per Month' : 'प्रति महीना'}
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Manual Tab */}
              {activeTab === 'manual' && (
                <>
                  {/* PDF Upload Section */}
                  <div className="p-6 bg-red-50 rounded-lg border-2 border-red-200">
                    <h3 className="text-lg font-bold text-red-900 mb-4">📄 {language === 'en' ? 'Upload Soil Report PDF' : 'मिट्टी रिपोर्ट PDF अपलोड करें'}</h3>
                    <div className="space-y-3">
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={async (e) => {
                          const file = e.target.files?.[0];
                          if (!file) return;
                          
                          setExtractingImage(true);
                          try {
                            const formDataToSend = new FormData();
                            formDataToSend.append('pdf', file);
                            
                            const response = await fetch(`${getAPIBaseURL()}/recommendations/extract-from-pdf`, {
                              method: 'POST',
                              body: formDataToSend,
                            });
                            
                            if (response.ok) {
                              const data = await response.json();
                              if (data.success && data.values) {
                                const values = data.values;
                                setFormData((prev) => ({
                                  ...prev,
                                  nitrogen: values.nitrogen ? String(values.nitrogen) : prev.nitrogen,
                                  phosphorus: values.phosphorus ? String(values.phosphorus) : prev.phosphorus,
                                  potassium: values.potassium ? String(values.potassium) : prev.potassium,
                                  ph: values.ph ? String(values.ph) : prev.ph,
                                  rainfall: values.rainfall ? String(values.rainfall) : prev.rainfall,
                                  temperature: values.temperature ? String(values.temperature) : prev.temperature,
                                  humidity: values.humidity ? String(values.humidity) : prev.humidity,
                                }));
                                alert(language === 'en' ? 'PDF processed successfully!' : 'PDF सफलतापूर्वक प्रोसेस हुआ!');
                              } else {
                                alert(data.error || (language === 'en' ? 'Could not extract values from PDF' : 'PDF से values निकालने में विफल'));
                              }
                            }
                          } catch (error) {
                            console.error('Error processing PDF:', error);
                            alert(language === 'en' ? 'Error processing PDF' : 'PDF प्रोसेस करने में त्रुटि');
                          } finally {
                            setExtractingImage(false);
                          }
                        }}
                        disabled={extractingImage}
                        className="w-full"
                      />
                      <p className="text-sm text-red-700">
                        💡 {language === 'en' ? 'Upload a soil report PDF to auto-fill parameters' : 'मिट्टी रिपोर्ट PDF अपलोड करें ताकि parameters स्वचालित रूप से भर जाएं'}
                      </p>
                    </div>
                  </div>

                  {renderManualTab()}

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {language === 'en' ? 'Getting Recommendations...' : 'सिफारिशें प्राप्त हो रही हैं...'}
                      </>
                    ) : (
                      language === 'en' ? '🌾 Get Recommendations' : '🌾 सिफारिशें प्राप्त करें'
                    )}
                  </Button>
                </>
              )}

              {/* Advanced Tab */}
              {activeTab === 'advanced' && (
                <>
                  {renderAdvancedTab()}

                  <Button
                    type="submit"
                    disabled={loading || !formData.month || !formData.location}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {language === 'en' ? 'Getting Recommendations...' : 'सिफारिशें प्राप्त हो रही हैं...'}
                      </>
                    ) : (
                      language === 'en' ? '🌾 Get Recommendations' : '🌾 सिफारिशें प्राप्त करें'
                    )}
                  </Button>
                </>
              )}

              {/* Per Month Tab */}
              {activeTab === 'perMonth' && (
                <>
                  {renderPerMonthTab()}

                  <Button
                    type="submit"
                    disabled={loading || !formData.month}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {language === 'en' ? 'Getting Recommendations...' : 'सिफारिशें प्राप्त हो रही हैं...'}
                      </>
                    ) : (
                      language === 'en' ? '🌾 Get Recommendations' : '🌾 सिफारिशें प्राप्त करें'
                    )}
                  </Button>
                </>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
          <div className="space-y-4">
            {result.error ? (
              <Card className="bg-red-50 border-red-200">
                <CardContent className="pt-6">
                  <p className="text-red-600">{result.error}</p>
                </CardContent>
              </Card>
            ) : (
              <>
                <h2 className="text-2xl font-bold text-gray-900">
                  {language === 'en' ? 'Recommended Crops' : 'अनुशंसित फसलें'}
                </h2>

                {/* Top Crops */}
                {result.top_crops && result.top_crops.map((crop, index) => (
                  <Card key={index} className={`${index === 0 ? 'border-2 border-green-600' : ''}`}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">
                            #{crop.rank} {crop.crop.toUpperCase()}
                          </CardTitle>
                          <CardDescription>{crop.reason}</CardDescription>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-600">{crop.confidence_str}</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${Math.min(crop.suitability, 100)}%` }}
                        ></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {/* Explanation */}
                {result.top_crops?.[0]?.detailed_explanation && (
                  <Card className="bg-green-50 border-green-200">
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>
                          {language === 'en' ? `Why ${result.primary_crop}?` : `${result.primary_crop} क्यों?`}
                        </CardTitle>
                        <div className="flex gap-2 items-center">
                          <Button
                            onClick={() => speakExplanation(result.top_crops![0].detailed_explanation!)}
                            disabled={isSpeaking}
                            size="sm"
                            className="bg-blue-600 hover:bg-blue-700"
                            title="Hindi voice may not be available on all browsers"
                          >
                            {isSpeaking ? '🔊' : '🔊'}
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{result.top_crops[0].detailed_explanation}</p>
                    </CardContent>
                  </Card>
                )}

                {/* Fallback Explanation */}
                {!result.top_crops?.[0]?.detailed_explanation && result.explanation && (
                  <Card className="bg-green-50 border-green-200">
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>
                          {language === 'en' ? `Why ${result.primary_crop}?` : `${result.primary_crop} क्यों?`}
                        </CardTitle>
                        <Button
                          onClick={() => speakExplanation(result.explanation!)}
                          disabled={isSpeaking}
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          {isSpeaking ? '🔊' : '🔊'}
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 whitespace-pre-wrap">{result.explanation}</p>
                    </CardContent>
                  </Card>
                )}

                {/* Voice Output */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => speakResult(result)}
                    disabled={isSpeaking}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    {isSpeaking ? '🔊 Speaking...' : '🔊 Speak Result'}
                  </Button>
                  {isSpeaking && (
                    <Button
                      onClick={stopSpeaking}
                      className="flex-1 bg-red-600 hover:bg-red-700"
                    >
                      ⏹️ Stop
                    </Button>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CropRecommendationComplete;
