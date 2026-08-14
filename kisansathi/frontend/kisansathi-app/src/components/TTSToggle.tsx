import React from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { useTextToSpeechContext } from '@/context/TextToSpeechContext';

/**
 * Global TTS Toggle Button
 * Add this to your navbar/header
 */
export const TTSToggle: React.FC = () => {
  const { isEnabled, toggleTTS, language, setLanguage } = useTextToSpeechContext();

  return (
    <div className="flex items-center gap-2">
      {/* Language selector */}
      {isEnabled && (
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as 'auto' | 'en' | 'hi')}
          className="px-2 py-1 text-sm border rounded bg-white dark:bg-gray-800"
          title="Select language for text-to-speech"
        >
          <option value="auto">Auto</option>
          <option value="en">English</option>
          <option value="hi">हिंदी</option>
        </select>
      )}

      {/* Toggle button */}
      <button
        onClick={toggleTTS}
        className={`p-2 rounded-full transition-all ${
          isEnabled
            ? 'bg-green-500 hover:bg-green-600 text-white'
            : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
        }`}
        title={isEnabled ? 'Disable text-to-speech' : 'Enable text-to-speech'}
        aria-label={isEnabled ? 'Disable text-to-speech' : 'Enable text-to-speech'}
      >
        {isEnabled ? (
          <Volume2 size={20} />
        ) : (
          <VolumeX size={20} />
        )}
      </button>
    </div>
  );
};
