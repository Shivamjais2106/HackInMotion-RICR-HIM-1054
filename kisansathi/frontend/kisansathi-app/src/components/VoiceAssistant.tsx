import React, { useState, useRef } from 'react';
import { Mic, Send, Volume2, Copy, Loader } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { getAPIBaseURL } from '@/utils/api';

interface Message {
  id: string;
  type: 'question' | 'answer';
  text_en: string;
  text_hi: string;
  timestamp: Date;
}

const VoiceAssistant: React.FC = () => {
  const { t, language: contextLanguage } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState<'en' | 'hi'>(contextLanguage === 'hi' ? 'hi' : 'en');
  const [cropName, setCropName] = useState('');
  const [location, setLocation] = useState('');
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize speech recognition
  React.useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = language === 'hi' ? 'hi-IN' : 'en-IN';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputText(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  }, [language]);

  // Auto-scroll to bottom
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const handleSendQuestion = async () => {
    if (!inputText.trim()) return;

    // Add question to messages
    const questionMessage: Message = {
      id: `q-${Date.now()}`,
      type: 'question',
      text_en: inputText,
      text_hi: inputText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, questionMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/voice-assistant/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: inputText,
          crop_name: cropName,
          location: location,
        }),
      });

      const data = await response.json();

      if (data.success) {
        const answerMessage: Message = {
          id: `a-${Date.now()}`,
          type: 'answer',
          text_en: data.answer_en,
          text_hi: data.answer_hi,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, answerMessage]);

        // Auto-speak answer
        speakText(language === 'hi' ? data.answer_hi : data.answer_en);
      } else {
        const errorMessage: Message = {
          id: `e-${Date.now()}`,
          type: 'answer',
          text_en: data.error || 'Error processing question',
          text_hi: 'Sawaal process karte samay error aaya',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (err) {
      console.error(err);
      const errorMessage: Message = {
        id: `e-${Date.now()}`,
        type: 'answer',
        text_en: 'Error connecting to server',
        text_hi: 'Server se connect karte samay error aaya',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const displayText = (message: Message) => {
    return language === 'hi' ? message.text_hi : message.text_en;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center">
              <Mic className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">{t('voice.title')}</h1>
          <p className="text-gray-600">{t('voice.subtitle')}</p>
        </div>

        {/* Settings */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('voice.language')}</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as 'en' | 'hi')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="en">{t('voice.english')}</option>
                <option value="hi">{t('voice.hindi')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('voice.crop')}</label>
              <input
                type="text"
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                placeholder={t('voice.cropPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">{t('voice.location')}</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder={t('voice.locationPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 h-96 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Mic className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">
                  {language === 'hi'
                    ? 'Apna sawaal poochein...'
                    : t('voice.askQuestion')}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'question' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                      message.type === 'question'
                        ? 'bg-blue-500 text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-800 rounded-bl-none'
                    }`}
                  >
                    <p className="text-sm">{displayText(message)}</p>
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => speakText(displayText(message))}
                        className="text-xs opacity-70 hover:opacity-100 flex items-center gap-1"
                      >
                        <Volume2 className="w-3 h-3" /> {t('voice.speak')}
                      </button>
                      <button
                        onClick={() => copyToClipboard(displayText(message))}
                        className="text-xs opacity-70 hover:opacity-100 flex items-center gap-1"
                      >
                        <Copy className="w-3 h-3" /> {t('voice.copy')}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg rounded-bl-none">
                    <Loader className="w-5 h-5 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendQuestion()}
              placeholder={
                language === 'hi'
                  ? 'Apna sawaal likhen ya bolein...'
                  : t('voice.typeOrSpeak')
              }
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            <button
              onClick={isListening ? stopListening : startListening}
              className={`px-4 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
                isListening
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              <Mic className="w-5 h-5" />
              {isListening ? t('voice.stop') : t('voice.speak')}
            </button>

            <button
              onClick={handleSendQuestion}
              disabled={!inputText.trim() || isLoading}
              className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              {t('voice.send')}
            </button>
          </div>

          {/* Quick Questions */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {[
              { text: language === 'hi' ? 'Paani kaise dein?' : t('voice.howToWater'), type: 'watering' },
              { text: language === 'hi' ? 'Khad kaise lagayen?' : t('voice.howToFertilize'), type: 'fertilizer' },
              { text: language === 'hi' ? 'Keede se kaise bachein?' : t('voice.pestControl'), type: 'pest_control' },
              { text: language === 'hi' ? 'Kaatne ka samay?' : t('voice.whenToHarvest'), type: 'harvest' },
            ].map((quick) => (
              <button
                key={quick.type}
                onClick={() => setInputText(quick.text)}
                className="text-xs px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
              >
                {quick.text}
              </button>
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            💡 <strong>{t('voice.tip')}</strong> {language === 'hi' 
              ? 'Apne crop ka naam aur location batayein taaki AI aapko better jawab de sake.'
              : t('voice.tipText')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistant;
