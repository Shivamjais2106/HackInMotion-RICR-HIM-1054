import { useState, useRef } from 'react';
import { getAPIBaseURL } from '../utils/api';

interface VoiceState {
  isListening: boolean;
  transcript: string;
  isSpeaking: boolean;
  extractedData: any;
  recommendation: any;
  explanation: string;
}

function VoiceFertilizerPipeline() {
  const [state, setState] = useState<VoiceState>({
    isListening: false,
    transcript: '',
    isSpeaking: false,
    extractedData: null,
    recommendation: null,
    explanation: ''
  });

  const recognitionRef = useRef<any>(null);
  const [step, setStep] = useState<'input' | 'processing' | 'result'>('input');
  const [loading, setLoading] = useState(false);

  // Initialize Speech Recognition
  const initializeSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition not supported in your browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-IN';

    recognition.onstart = () => {
      setState(prev => ({ ...prev, isListening: true, transcript: '' }));
    };

    recognition.onresult = (event: any) => {
      let interim_transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setState(prev => ({ ...prev, transcript: prev.transcript + transcript }));
        } else {
          interim_transcript += transcript;
        }
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      alert('Error in speech recognition: ' + event.error);
    };

    recognition.onend = () => {
      setState(prev => ({ ...prev, isListening: false }));
    };

    recognitionRef.current = recognition;
  };

  // Start Voice Input
  const startVoiceInput = () => {
    if (!recognitionRef.current) {
      initializeSpeechRecognition();
    }
    recognitionRef.current?.start();
  };

  // Stop Voice Input
  const stopVoiceInput = () => {
    recognitionRef.current?.stop();
  };

  // Extract Information from Transcript
  const extractInformation = async (transcript: string) => {
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/extract-fertilizer-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript })
      });
      const data = await response.json();
      setState(prev => ({ ...prev, extractedData: data }));
      return data;
    } catch (error) {
      console.error('Error extracting information:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Get Fertilizer Recommendation
  const getFertilizerRecommendation = async (extractedData: any) => {
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/fertilizer/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crop_type: extractedData.crop || 'rice',
          nitrogen: extractedData.nitrogen || 80,
          phosphorus: extractedData.phosphorus || 45,
          potassium: extractedData.potassium || 60,
          temperature: extractedData.temperature || 25,
          humidity: extractedData.humidity || 70,
          moisture: extractedData.moisture || 50,
          soil_type: extractedData.soil_type || 'loamy'
        })
      });
      const data = await response.json();
      setState(prev => ({ ...prev, recommendation: data }));
      return data;
    } catch (error) {
      console.error('Error getting recommendation:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Generate Explanation using OpenAI
  const generateExplanation = async (recommendation: any, extractedData: any) => {
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/generate-explanation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fertilizer: recommendation.recommendation.recommended_fertilizer,
          crop: extractedData.crop,
          nitrogen: extractedData.nitrogen,
          phosphorus: extractedData.phosphorus,
          potassium: extractedData.potassium,
          soil_type: extractedData.soil_type
        })
      });
      const data = await response.json();
      setState(prev => ({ ...prev, explanation: data.explanation }));
      return data.explanation;
    } catch (error) {
      console.error('Error generating explanation:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Text-to-Speech Output
  const speakOutput = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.lang = 'en-IN';

    setState(prev => ({ ...prev, isSpeaking: true }));
    utterance.onend = () => setState(prev => ({ ...prev, isSpeaking: false }));

    window.speechSynthesis.speak(utterance);
  };

  // Stop Speaking
  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setState(prev => ({ ...prev, isSpeaking: false }));
  };

  // Process Voice Input
  const processVoiceInput = async () => {
    if (!state.transcript) {
      alert('Please provide voice input first');
      return;
    }

    setStep('processing');
    
    // Extract information
    const extracted = await extractInformation(state.transcript);
    if (!extracted) {
      alert('Failed to extract information');
      setStep('input');
      return;
    }

    // Get recommendation
    const recommendation = await getFertilizerRecommendation(extracted);
    if (!recommendation) {
      alert('Failed to get recommendation');
      setStep('input');
      return;
    }

    // Generate explanation
    const explanation = await generateExplanation(recommendation, extracted);

    setStep('result');

    // Speak the result
    if (explanation) {
      speakOutput(explanation);
    }
  };

  // Reset
  const reset = () => {
    setStep('input');
    setState({
      isListening: false,
      transcript: '',
      isSpeaking: false,
      extractedData: null,
      recommendation: null,
      explanation: ''
    });
  };

  return (
    <div className="min-h-screen bg-eco-cream py-20">
      <div className="max-w-4xl mx-auto px-6">
        <h1 className="text-4xl font-bold text-eco-green-dark mb-2">🎤 Voice Fertilizer Assistant</h1>
        <p className="text-gray-600 mb-8">Speak your crop details and get fertilizer recommendations with AI-powered explanations</p>

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Step 1: Voice Input */}
          {step === 'input' && (
            <div className="space-y-6">
              <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-300">
                <h2 className="text-xl font-bold text-blue-700 mb-3">🎤 Step 1: Provide Voice Input</h2>
                <p className="text-blue-600 mb-4">
                  Speak about your crop and soil conditions. Example: "I have rice crop with nitrogen 80, phosphorus 45, potassium 60, temperature 25 degrees, humidity 70 percent, loamy soil"
                </p>
              </div>

              {/* Transcript Display */}
              <div className="bg-gray-50 p-6 rounded-lg border-2 border-gray-300">
                <p className="text-sm text-gray-600 mb-2">Your Input:</p>
                <div className="bg-white p-4 rounded border border-gray-300 min-h-24">
                  <p className="text-gray-800">
                    {state.transcript || <span className="text-gray-400 italic">Your speech will appear here...</span>}
                  </p>
                </div>
              </div>

              {/* Voice Control Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={startVoiceInput}
                  disabled={state.isListening}
                  className="flex-1 bg-red-500 text-white font-semibold py-3 rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
                >
                  {state.isListening ? '🎤 Listening...' : '🎤 Start Recording'}
                </button>
                {state.isListening && (
                  <button
                    onClick={stopVoiceInput}
                    className="flex-1 bg-orange-500 text-white font-semibold py-3 rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    ⏹️ Stop Recording
                  </button>
                )}
              </div>

              {/* Process Button */}
              <button
                onClick={processVoiceInput}
                disabled={!state.transcript || loading}
                className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark disabled:opacity-50 transition-colors"
              >
                {loading ? '⏳ Processing...' : '➡️ Process & Get Recommendation'}
              </button>
            </div>
          )}

          {/* Step 2: Processing */}
          {step === 'processing' && (
            <div className="space-y-6 text-center">
              <div className="animate-spin text-6xl">⏳</div>
              <h2 className="text-2xl font-bold text-eco-green">Processing Your Request...</h2>
              <div className="space-y-2 text-gray-600">
                <p>📝 Extracting information from your input...</p>
                <p>🧪 Getting fertilizer recommendation...</p>
                <p>🤖 Generating AI-powered explanation...</p>
              </div>
            </div>
          )}

          {/* Step 3: Results */}
          {step === 'result' && state.recommendation && (
            <div className="space-y-6">
              {/* Extracted Data */}
              {state.extractedData && (
                <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-300">
                  <h3 className="text-lg font-bold text-blue-700 mb-4">📊 Extracted Information</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {state.extractedData.crop && (
                      <div>
                        <p className="text-sm text-gray-600">Crop</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.crop}</p>
                      </div>
                    )}
                    {state.extractedData.nitrogen && (
                      <div>
                        <p className="text-sm text-gray-600">Nitrogen</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.nitrogen} mg/kg</p>
                      </div>
                    )}
                    {state.extractedData.phosphorus && (
                      <div>
                        <p className="text-sm text-gray-600">Phosphorus</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.phosphorus} mg/kg</p>
                      </div>
                    )}
                    {state.extractedData.potassium && (
                      <div>
                        <p className="text-sm text-gray-600">Potassium</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.potassium} mg/kg</p>
                      </div>
                    )}
                    {state.extractedData.temperature && (
                      <div>
                        <p className="text-sm text-gray-600">Temperature</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.temperature}°C</p>
                      </div>
                    )}
                    {state.extractedData.soil_type && (
                      <div>
                        <p className="text-sm text-gray-600">Soil Type</p>
                        <p className="text-lg font-semibold text-gray-800">{state.extractedData.soil_type}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recommendation */}
              <div className="bg-eco-cream p-6 rounded-lg border-2 border-eco-green">
                <h3 className="text-lg font-bold text-eco-green-dark mb-4">🎯 Fertilizer Recommendation</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Recommended Fertilizer</p>
                    <p className="text-3xl font-bold text-eco-green">{state.recommendation.recommendation.recommended_fertilizer}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="text-lg font-semibold text-gray-800">{state.recommendation.recommendation.confidence}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Application Rate (per hectare)</p>
                    <p className="text-gray-700">
                      N: {state.recommendation.recommendation.application_rate.nitrogen} kg<br/>
                      P: {state.recommendation.recommendation.application_rate.phosphorus} kg<br/>
                      K: {state.recommendation.recommendation.application_rate.potassium} kg
                    </p>
                  </div>
                </div>
              </div>

              {/* AI Explanation */}
              {state.explanation && (
                <div className="bg-green-50 p-6 rounded-lg border-2 border-green-300">
                  <h3 className="text-lg font-bold text-green-700 mb-4">🤖 AI-Powered Explanation</h3>
                  <p className="text-gray-800 leading-relaxed">{state.explanation}</p>
                </div>
              )}

              {/* Voice Output Controls */}
              <div className="flex gap-3">
                <button
                  onClick={() => speakOutput(state.explanation || 'No explanation available')}
                  disabled={state.isSpeaking}
                  className="flex-1 bg-blue-500 text-white font-semibold py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
                >
                  {state.isSpeaking ? '🔊 Speaking...' : '🔊 Hear Explanation'}
                </button>
                {state.isSpeaking && (
                  <button
                    onClick={stopSpeaking}
                    className="flex-1 bg-red-500 text-white font-semibold py-3 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    ⏹️ Stop
                  </button>
                )}
              </div>

              {/* Reset Button */}
              <button
                onClick={reset}
                className="w-full bg-gray-500 text-white font-semibold py-3 rounded-lg hover:bg-gray-600 transition-colors"
              >
                🔄 Start Over
              </button>
            </div>
          )}
        </div>

        {/* Pipeline Diagram */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-eco-green-dark mb-6">📋 Voice Pipeline Process</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="bg-red-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">1</div>
              <div>
                <p className="font-semibold text-gray-800">Voice Input</p>
                <p className="text-gray-600">Speak your crop and soil details</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-orange-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">2</div>
              <div>
                <p className="font-semibold text-gray-800">Speech-to-Text</p>
                <p className="text-gray-600">Convert speech to text using Web Speech API</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-yellow-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">3</div>
              <div>
                <p className="font-semibold text-gray-800">Extract Information</p>
                <p className="text-gray-600">Parse crop, soil data, and parameters</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-green-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">4</div>
              <div>
                <p className="font-semibold text-gray-800">ML Prediction</p>
                <p className="text-gray-600">Get fertilizer recommendation from trained model</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-blue-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">5</div>
              <div>
                <p className="font-semibold text-gray-800">AI Explanation</p>
                <p className="text-gray-600">Generate detailed explanation using OpenAI API</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-purple-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold">6</div>
              <div>
                <p className="font-semibold text-gray-800">Text-to-Speech</p>
                <p className="text-gray-600">Convert explanation to voice output</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VoiceFertilizerPipeline;
