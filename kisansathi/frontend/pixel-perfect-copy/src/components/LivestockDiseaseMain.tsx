import { useState, useRef } from 'react';
import { Upload, AlertCircle, CheckCircle, Loader, ArrowLeft } from 'lucide-react';
import { getAPIBaseURL } from '@/utils/api';

interface DiseaseResult {
  success: boolean;
  animal_type: string;
  primary_disease: string;
  confidence: number;
  treatment: string;
  duration: string;
  cost_estimate: string;
  prevention: string;
  severity: string;
  vet_urgency: string;
  symptoms_match: string[];
  alternative_diseases: Array<{ disease: string; confidence: number }>;
  gemini_verification?: string;
}

function LivestockDiseaseMain() {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState<string>('cattle');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const animals = [
    { id: 'cattle', name: '🐄 Cattle', icon: '🐄' },
    { id: 'buffalo', name: '🐃 Buffalo', icon: '🐃' },
    { id: 'goat', name: '🐐 Goat', icon: '🐐' },
    { id: 'sheep', name: '🐑 Sheep', icon: '🐑' },
    { id: 'pig', name: '🐷 Pig', icon: '🐷' },
    { id: 'poultry', name: '🐔 Poultry', icon: '🐔' },
  ];

  const commonSymptoms = {
    cattle: ['Fever', 'Swelling', 'Lameness', 'Discharge', 'Reduced milk', 'Skin lesions'],
    buffalo: ['Fever', 'Swelling', 'Lameness', 'Discharge', 'Reduced milk', 'Cough'],
    goat: ['Lameness', 'Itching', 'Hair loss', 'Cough', 'Fever', 'Swollen udder'],
    sheep: ['Lameness', 'Itching', 'Hair loss', 'Cough', 'Fever', 'Swollen udder'],
    pig: ['Fever', 'Lethargy', 'Diarrhea', 'Cough', 'Reduced appetite', 'Swelling'],
    poultry: ['Twisted neck', 'Paralysis', 'Diarrhea', 'Cough', 'Lethargy', 'Reduced eggs'],
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setError('');
    }
  };

  const toggleSymptom = (symptom: string) => {
    setSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((s) => s !== symptom) : [...prev, symptom]
    );
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedImage) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('animal_type', selectedAnimal);
      symptoms.forEach((symptom) => formData.append('symptoms', symptom));

      const response = await fetch(`${getAPIBaseURL()}/livestock-disease-predict`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to predict disease');
      }
    } catch (err) {
      setError('Error connecting to server. Make sure backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'high':
        return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low':
        return 'bg-green-100 border-green-300 text-green-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'emergency':
        return 'text-red-600 bg-red-50';
      case 'immediate':
        return 'text-orange-600 bg-orange-50';
      case 'within 24 hours':
        return 'text-yellow-600 bg-yellow-50';
      case 'within 48 hours':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (!selectedOption) {
    return (
      <div className="min-h-screen bg-eco-cream py-20">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-4xl font-bold text-eco-green-dark mb-4 text-center">🏥 Livestock Disease Detection</h1>
          <p className="text-gray-600 text-center mb-12">Choose how you want to diagnose your animal</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Option 1: Image-based */}
            <div
              onClick={() => setSelectedOption('image')}
              className="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-shadow"
            >
              <div className="text-6xl mb-4">📸</div>
              <h2 className="text-2xl font-bold text-eco-green-dark mb-3">Image-Based Diagnosis</h2>
              <p className="text-gray-600 mb-4">
                Upload a photo of your sick animal and let our AI analyze it to detect diseases with high accuracy.
              </p>
              <div className="bg-eco-cream p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-700">
                  <strong>What you need:</strong> A clear photo of the affected animal
                </p>
              </div>
              <button className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors">
                Choose This Option →
              </button>
            </div>

            {/* Option 2: Symptom-based */}
            <div
              onClick={() => setSelectedOption('symptoms')}
              className="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-shadow"
            >
              <div className="text-6xl mb-4">🔍</div>
              <h2 className="text-2xl font-bold text-eco-green-dark mb-3">Symptom-Based Diagnosis</h2>
              <p className="text-gray-600 mb-4">
                Describe the symptoms you observe in your animal and get disease predictions based on symptom matching.
              </p>
              <div className="bg-eco-cream p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-700">
                  <strong>What you need:</strong> Description of observed symptoms
                </p>
              </div>
              <button className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors">
                Choose This Option →
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (selectedOption === 'image') {
    return (
      <div className="min-h-screen bg-eco-cream py-20">
        <div className="max-w-6xl mx-auto px-6">
          <button
            onClick={() => {
              setSelectedOption(null);
              setSelectedImage(null);
              setImagePreview('');
              setSymptoms([]);
              setResult(null);
              setError('');
            }}
            className="flex items-center gap-2 text-eco-green-dark font-semibold mb-8 hover:text-eco-green-dark/70"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Options
          </button>

          <h1 className="text-4xl font-bold text-eco-green-dark mb-4 text-center">📸 Image-Based Diagnosis</h1>
          <p className="text-gray-600 text-center mb-12">Upload a photo of your sick animal for AI diagnosis</p>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Panel */}
            <div className="lg:col-span-2 space-y-8">
              {/* Animal Selection */}
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-eco-green-dark mb-6">Select Animal Type</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {animals.map((animal) => (
                    <button
                      key={animal.id}
                      onClick={() => setSelectedAnimal(animal.id)}
                      className={`p-6 rounded-lg border-2 transition-all ${
                        selectedAnimal === animal.id
                          ? 'border-eco-green bg-eco-cream'
                          : 'border-gray-200 bg-white hover:border-eco-green'
                      }`}
                    >
                      <div className="text-4xl mb-2">{animal.icon}</div>
                      <div className="text-sm font-medium text-eco-green-dark">{animal.name.split(' ')[1]}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Image Upload */}
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-eco-green-dark mb-6">Upload Animal Photo</h2>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-eco-green/30 rounded-lg p-12 text-center cursor-pointer hover:bg-eco-cream transition-colors"
                >
                  <Upload className="w-16 h-16 text-eco-green mx-auto mb-4" />
                  <p className="text-eco-green-dark font-semibold text-lg mb-2">Click to upload or drag and drop</p>
                  <p className="text-gray-600">PNG, JPG, GIF up to 10MB</p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                />

                {imagePreview && (
                  <div className="mt-6">
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="w-full h-64 object-cover rounded-lg border-2 border-eco-green/30"
                    />
                    <button
                      onClick={() => {
                        setSelectedImage(null);
                        setImagePreview('');
                      }}
                      className="mt-4 text-red-600 hover:text-red-700 text-sm font-semibold"
                    >
                      ✕ Remove Image
                    </button>
                  </div>
                )}
              </div>

              {/* Symptoms Selection */}
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-eco-green-dark mb-6">Observed Symptoms (Optional)</h2>
                <div className="grid grid-cols-2 gap-3">
                  {commonSymptoms[selectedAnimal as keyof typeof commonSymptoms]?.map((symptom) => (
                    <button
                      key={symptom}
                      onClick={() => toggleSymptom(symptom)}
                      className={`p-3 rounded-lg border-2 transition-all text-sm font-medium ${
                        symptoms.includes(symptom)
                          ? 'border-eco-green bg-eco-cream text-eco-green-dark'
                          : 'border-gray-200 bg-white text-gray-700 hover:border-eco-green'
                      }`}
                    >
                      {symptom}
                    </button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
                    <p className="text-red-700">{error}</p>
                  </div>
                </div>
              )}

              {/* Predict Button */}
              <form onSubmit={handlePredict}>
                <button
                  type="submit"
                  disabled={!selectedImage || loading}
                  className="w-full bg-gradient-to-r from-eco-green to-eco-green-dark text-white font-bold py-4 rounded-lg hover:from-eco-green-dark hover:to-eco-green disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center text-lg"
                >
                  {loading ? (
                    <>
                      <Loader className="w-6 h-6 mr-3 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    '🔍 Predict Disease'
                  )}
                </button>
              </form>
            </div>

            {/* Right Panel - Results */}
            <div className="lg:col-span-1">
              {result && (
                <div className="bg-white rounded-lg shadow-md p-8 sticky top-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-eco-green-dark">Diagnosis</h3>
                    <CheckCircle className="w-6 h-6 text-eco-green" />
                  </div>

                  {/* Primary Disease */}
                  <div className={`p-4 rounded-lg border-2 ${getSeverityColor(result.severity)}`}>
                    <p className="text-sm text-gray-600 mb-1">Primary Disease</p>
                    <p className="text-xl font-bold">{result.primary_disease}</p>
                    <p className="text-sm mt-2">Confidence: {result.confidence}%</p>
                  </div>

                  {/* Severity Badge */}
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 font-medium">Severity:</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getSeverityColor(result.severity)}`}>
                      {result.severity}
                    </span>
                  </div>

                  {/* Vet Urgency */}
                  <div className={`p-3 rounded-lg ${getUrgencyColor(result.vet_urgency)}`}>
                    <p className="text-sm font-semibold">Call Vet: {result.vet_urgency}</p>
                  </div>

                  {/* Treatment */}
                  <div className="border-t pt-4">
                    <p className="text-sm font-semibold text-eco-green-dark mb-2">Treatment</p>
                    <p className="text-sm text-gray-600">{result.treatment}</p>
                    <p className="text-xs text-gray-500 mt-2">Duration: {result.duration}</p>
                    <p className="text-xs text-gray-500">Cost: {result.cost_estimate}</p>
                  </div>

                  {/* Prevention */}
                  <div className="border-t pt-4">
                    <p className="text-sm font-semibold text-eco-green-dark mb-2">Prevention</p>
                    <p className="text-sm text-gray-600">{result.prevention}</p>
                  </div>

                  {/* Symptom Match */}
                  {result.symptoms_match && result.symptoms_match.length > 0 && (
                    <div className="border-t pt-4">
                      <p className="text-sm font-semibold text-eco-green-dark mb-2">Matching Symptoms</p>
                      <div className="flex flex-wrap gap-2">
                        {result.symptoms_match.map((symptom) => (
                          <span
                            key={symptom}
                            className="bg-eco-cream text-eco-green-dark text-xs px-2 py-1 rounded"
                          >
                            ✓ {symptom}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Alternative Diseases */}
                  {result.alternative_diseases && result.alternative_diseases.length > 0 && (
                    <div className="border-t pt-4">
                      <p className="text-sm font-semibold text-eco-green-dark mb-2">Other Possibilities</p>
                      <div className="space-y-2">
                        {result.alternative_diseases.map((alt) => (
                          <div key={alt.disease} className="flex justify-between text-sm">
                            <span className="text-gray-600">{alt.disease}</span>
                            <span className="text-gray-500">{alt.confidence}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {!result && !loading && (
                <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500 sticky top-6">
                  <p className="text-sm">Upload an image and click "Predict Disease" to see results</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (selectedOption === 'symptoms') {
    return (
      <div className="min-h-screen bg-eco-cream py-20">
        <div className="max-w-4xl mx-auto px-6">
          <button
            onClick={() => {
              setSelectedOption(null);
              setSymptoms([]);
              setResult(null);
              setError('');
            }}
            className="flex items-center gap-2 text-eco-green-dark font-semibold mb-8 hover:text-eco-green-dark/70"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Options
          </button>

          <h1 className="text-4xl font-bold text-eco-green-dark mb-4 text-center">🔍 Symptom-Based Diagnosis</h1>
          <p className="text-gray-600 text-center mb-12">Coming Soon - Symptom-based diagnosis feature</p>

          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-600 text-lg">This feature is coming soon. Please use the Image-Based Diagnosis for now.</p>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default LivestockDiseaseMain;
