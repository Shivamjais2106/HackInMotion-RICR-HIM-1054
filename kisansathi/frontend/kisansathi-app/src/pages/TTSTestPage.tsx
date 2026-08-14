import React, { useState } from 'react';
import { useTextToSpeechContext } from '@/context/TextToSpeechContext';
import { SentenceReader } from '@/components/SentenceReader';
import { getAPIBaseURL } from '../utils/api';

/**
 * Dedicated TTS Testing Page
 */
const TTSTestPage = () => {
  const { isEnabled, toggleTTS, language, setLanguage } = useTextToSpeechContext();
  const [testText, setTestText] = useState('Welcome to KisanSathi. This is a complete sentence that will be read aloud.');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTestTTS = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const baseURL = getAPIBaseURL();
      console.log('Testing TTS with text:', testText);
      console.log('Language:', language);

      const response = await fetch(`${baseURL}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: testText,
          language: language === 'auto' ? 'auto' : language === 'hi' ? 'hi-IN' : 'en-US',
        }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const audioBlob = await response.blob();
      console.log('Audio blob size:', audioBlob.size);

      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onplay = () => {
        setSuccess('🔊 Audio is playing...');
      };

      audio.onerror = (e) => {
        console.error('Audio error:', e);
        setError('❌ Audio playback error');
      };

      audio.onended = () => {
        setSuccess('✅ Audio finished playing');
      };

      await audio.play();
    } catch (err) {
      console.error('Error:', err);
      setError(`❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-eco-green to-eco-green-dark p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">🎤 TTS Test Page</h1>

        {/* Status */}
        <div className="bg-white rounded-lg p-6 mb-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Status</h2>
          <div className="space-y-2">
            <p>
              <strong>TTS Enabled:</strong>{' '}
              <span className={isEnabled ? 'text-green-600' : 'text-red-600'}>
                {isEnabled ? '✅ Yes' : '❌ No'}
              </span>
            </p>
            <p>
              <strong>Language:</strong> <span className="text-blue-600">{language}</span>
            </p>
          </div>
        </div>

        {/* Toggle */}
        <div className="bg-white rounded-lg p-6 mb-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Enable TTS</h2>
          <button
            onClick={toggleTTS}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              isEnabled
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-green-500 hover:bg-green-600'
            }`}
          >
            {isEnabled ? 'Disable TTS' : 'Enable TTS'}
          </button>
        </div>

        {/* Language Selector */}
        {isEnabled && (
          <div className="bg-white rounded-lg p-6 mb-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Select Language</h2>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as 'auto' | 'en' | 'hi')}
              className="w-full px-4 py-2 border-2 border-eco-green rounded-lg"
            >
              <option value="auto">Auto Detect</option>
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
            </select>
          </div>
        )}

        {/* Test Input */}
        <div className="bg-white rounded-lg p-6 mb-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Test Text</h2>
          <textarea
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            className="w-full px-4 py-2 border-2 border-eco-green rounded-lg"
            rows={4}
            placeholder="Enter text to convert to speech..."
          />
        </div>

        {/* Test Button */}
        <div className="bg-white rounded-lg p-6 mb-6 shadow-lg">
          <button
            onClick={handleTestTTS}
            disabled={isLoading || !isEnabled}
            className={`w-full px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              isLoading || !isEnabled
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-eco-green hover:bg-eco-green-dark'
            }`}
          >
            {isLoading ? '⏳ Testing...' : '🎤 Test TTS'}
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-100 border-2 border-red-500 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border-2 border-green-500 rounded-lg p-4 mb-6 text-green-700">
            {success}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Instructions</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Click "Enable TTS" button above</li>
            <li>Select a language (Auto, English, or Hindi)</li>
            <li>Enter or modify the test text</li>
            <li>Click "Test TTS" button</li>
            <li>You should hear the COMPLETE SENTENCE read aloud</li>
            <li>Check browser console (F12) for detailed logs</li>
          </ol>
        </div>

        {/* Live Demo */}
        {isEnabled && (
          <div className="bg-white rounded-lg p-6 shadow-lg mt-6">
            <h2 className="text-xl font-semibold mb-4">📖 Live Demo - Click Speaker to Read</h2>
            <div className="space-y-4">
              <SentenceReader language="en">
                Welcome to KisanSathi, your AI-powered agricultural assistant for modern farming.
              </SentenceReader>

              <SentenceReader language="hi">
                किसान साथी आपका कृषि सहायक है जो आपको बेहतर फसल उगाने में मदद करता है।
              </SentenceReader>

              <SentenceReader language="en">
                Get personalized crop recommendations based on your soil, weather, and location.
              </SentenceReader>

              <SentenceReader language="hi">
                अपनी मिट्टी, मौसम और स्थान के आधार पर व्यक्तिगत फसल सिफारिशें प्राप्त करें।
              </SentenceReader>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TTSTestPage;
