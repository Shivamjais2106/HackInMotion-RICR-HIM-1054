import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/context/LanguageContext";
import { Loader2 } from "lucide-react";
import useSpeechRecognition from 'react-speech-recognition';
import { getAPIBaseURL } from "@/utils/api";

interface LivestockRecommendation {
  disease: string;
  severity: number;
  treatment: string;
  confidence?: number;
  confidence_str?: string;
  rank?: number;
}

interface Result {
  disease?: string;
  top_diseases?: LivestockRecommendation[];
  treatment?: string;
  primary_disease?: string;
  temperature?: number;
  humidity?: number;
  error?: string;
}

type TabType = 'manual' | 'voice' | 'seasonal';

const LivestockHealthComplete = () => {
  const { language } = useLanguage();
  const [activeTab, setActiveTab] = useState<TabType>('manual');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [animalTypes, setAnimalTypes] = useState<string[]>([]);
  
  const [formData, setFormData] = useState({
    animal_type: '',
    age: '',
    weight: '',
    temperature: '',
    appetite: '',
    behavior: '',
    symptoms: '',
    season: ''
  });

  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  // Fetch animal types on component mount
  useEffect(() => {
    setAnimalTypes(['Cow', 'Buffalo', 'Goat', 'Sheep', 'Pig', 'Chicken', 'Horse']);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
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

      if (key === 'age' && !isNaN(Number(value))) newData.age = value;
      else if (key === 'weight' && !isNaN(Number(value))) newData.weight = value;
      else if (key === 'temperature' && !isNaN(Number(value))) newData.temperature = value;
    }

    setFormData(newData);
    setVoiceMode(false);
    resetTranscript();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        animal_type: formData.animal_type,
        age: parseFloat(formData.age) || 0,
        weight: parseFloat(formData.weight) || 0,
        temperature: parseFloat(formData.temperature) || 37,
        appetite: formData.appetite,
        behavior: formData.behavior,
        symptoms: formData.symptoms,
        season: activeTab === 'seasonal' ? formData.season : '',
        top_n: 5
      };

      const response = await fetch(`${getAPIBaseURL()}/livestock/disease-predict`, {
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
          top_diseases: data.diseases?.map((dis: any, idx: number) => ({
            disease: dis.disease || dis.name,
            severity: parseFloat(dis.confidence || dis.severity || 0),
            treatment: dis.treatment || dis.recommendation || '',
            confidence: parseFloat(dis.confidence || dis.severity || 0),
            confidence_str: `${(parseFloat(dis.confidence || dis.severity || 0)).toFixed(1)}%`,
            rank: idx + 1
          })) || [],
          primary_disease: data.diseases?.[0]?.disease || data.diseases?.[0]?.name || 'Unknown',
          treatment: data.diseases?.[0]?.treatment || data.diseases?.[0]?.recommendation || '',
          temperature: parseFloat(formData.temperature),
          humidity: 60
        };
        setResult(transformed);
        
        // Auto-speak result
        if (transformed.primary_disease) {
          speakResult(transformed);
        }
      } else {
        setResult({ error: 'Failed to get health assessment' });
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Error fetching health assessment' });
    } finally {
      setLoading(false);
    }
  };

  const speakResult = (data: Result) => {
    const text = `The detected condition is ${data.primary_disease}. ${data.treatment || ''}`;
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

  const renderManualTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {language === 'en' ? 'Animal Type' : 'पशु का प्रकार'}
          </label>
          <select
            name="animal_type"
            value={formData.animal_type}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600"
            required
          >
            <option value="">{language === 'en' ? 'Select animal...' : 'पशु चुनें...'}</option>
            {animalTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {language === 'en' ? 'Age (years)' : 'आयु (वर्ष)'}
          </label>
          <Input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleInputChange}
            placeholder="2"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {language === 'en' ? 'Weight (kg)' : 'वजन (किग्रा)'}
          </label>
          <Input
            type="number"
            name="weight"
            value={formData.weight}
            onChange={handleInputChange}
            placeholder="500"
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
            placeholder="37"
            step="0.1"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {language === 'en' ? 'Appetite' : 'भूख'}
          </label>
          <select
            name="appetite"
            value={formData.appetite}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600"
            required
          >
            <option value="">{language === 'en' ? 'Select...' : 'चुनें...'}</option>
            <option value="normal">{language === 'en' ? 'Normal' : 'सामान्य'}</option>
            <option value="reduced">{language === 'en' ? 'Reduced' : 'कम'}</option>
            <option value="absent">{language === 'en' ? 'Absent' : 'नहीं'}</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {language === 'en' ? 'Behavior' : 'व्यवहार'}
          </label>
          <select
            name="behavior"
            value={formData.behavior}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600"
            required
          >
            <option value="">{language === 'en' ? 'Select...' : 'चुनें...'}</option>
            <option value="normal">{language === 'en' ? 'Normal' : 'सामान्य'}</option>
            <option value="lethargic">{language === 'en' ? 'Lethargic' : 'सुस्त'}</option>
            <option value="aggressive">{language === 'en' ? 'Aggressive' : 'आक्रामक'}</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {language === 'en' ? 'Symptoms' : 'लक्षण'}
        </label>
        <textarea
          name="symptoms"
          value={formData.symptoms}
          onChange={handleInputChange}
          placeholder={language === 'en' ? 'Describe symptoms...' : 'लक्षणों का वर्णन करें...'}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600"
          rows={3}
          required
        />
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
                {transcript || 'Say: age 2 weight 500 temperature 37'}
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
        <h3 className="text-lg font-bold text-blue-900 mb-4">📅 {language === 'en' ? 'Select Season' : 'मौसम चुनें'}</h3>
        <select
          name="season"
          value={formData.season}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-green-600 text-lg"
          required
        >
          <option value="">{language === 'en' ? 'Choose a season...' : 'एक मौसम चुनें...'}</option>
          <option value="summer">{language === 'en' ? 'Summer' : 'गर्मी'}</option>
          <option value="monsoon">{language === 'en' ? 'Monsoon' : 'बारिश'}</option>
          <option value="winter">{language === 'en' ? 'Winter' : 'सर्दी'}</option>
        </select>
        <p className="text-sm text-blue-700 mt-3">
          💡 {language === 'en' ? 'Seasonal health risks vary for livestock' : 'पशुओं के लिए मौसमी स्वास्थ्य जोखिम अलग-अलग होते हैं'}
        </p>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">🐄 {language === 'en' ? 'Animal Information' : 'पशु की जानकारी'}</h3>
        {renderManualTab()}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            {language === 'en' ? '🐄 Livestock Health' : '🐄 पशु स्वास्थ्य'}
          </h1>
          <p className="text-gray-600 mt-2">
            {language === 'en'
              ? 'Monitor and manage your livestock health with AI-powered assessments'
              : 'AI-संचालित मूल्यांकन के साथ अपने पशुओं के स्वास्थ्य की निगरानी करें'}
          </p>
        </div>

        <Card className="bg-white shadow-lg mb-8">
          {/* Tab Navigation */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('manual')}
              className={`flex-1 py-4 px-6 font-semibold text-center transition-colors ${
                activeTab === 'manual'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📝 {language === 'en' ? 'Manual Input' : 'मैन्युअल इनपुट'}
            </button>
            <button
              onClick={() => setActiveTab('voice')}
              className={`flex-1 py-4 px-6 font-semibold text-center transition-colors ${
                activeTab === 'voice'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🎤 {language === 'en' ? 'Voice Input' : 'वॉयस इनपुट'}
            </button>
            <button
              onClick={() => setActiveTab('seasonal')}
              className={`flex-1 py-4 px-6 font-semibold text-center transition-colors ${
                activeTab === 'seasonal'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📅 {language === 'en' ? 'Seasonal' : 'मौसमी'}
            </button>
          </div>

          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Tab Content */}
              {activeTab === 'manual' && renderManualTab()}
              {activeTab === 'voice' && renderVoiceTab()}
              {activeTab === 'seasonal' && renderSeasonalTab()}

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {language === 'en' ? 'Analyzing...' : 'विश्लेषण हो रहा है...'}
                  </>
                ) : (
                  language === 'en' ? '🐄 Get Health Assessment' : '🐄 स्वास्थ्य मूल्यांकन प्राप्त करें'
                )}
              </Button>
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
                  {language === 'en' ? 'Health Assessment' : 'स्वास्थ्य मूल्यांकन'}
                </h2>

                {/* Top Diseases */}
                {result.top_diseases && result.top_diseases.map((disease, index) => (
                  <Card key={index} className={`${index === 0 ? 'border-2 border-green-600' : ''}`}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">
                            #{disease.rank} {disease.disease.toUpperCase()}
                          </CardTitle>
                          <CardDescription>{disease.treatment}</CardDescription>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-600">{disease.confidence_str}</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${Math.min(disease.severity, 100)}%` }}
                        ></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {/* Treatment */}
                {result.treatment && (
                  <Card className="bg-green-50 border-green-200">
                    <CardHeader>
                      <CardTitle>
                        {language === 'en' ? 'Recommended Treatment' : 'अनुशंसित उपचार'}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 whitespace-pre-wrap">{result.treatment}</p>
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

export default LivestockHealthComplete;
