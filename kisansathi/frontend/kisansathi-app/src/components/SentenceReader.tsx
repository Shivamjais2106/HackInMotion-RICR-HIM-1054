import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { useTextToSpeechContext } from '@/context/TextToSpeechContext';
import { getAPIBaseURL } from '@/utils/api';

interface SentenceReaderProps {
  children: string;
  language?: 'auto' | 'en' | 'hi';
  className?: string;
}

/**
 * Component to read complete sentences/paragraphs
 * Reads the ENTIRE text as one continuous audio
 */
export const SentenceReader: React.FC<SentenceReaderProps> = ({
  children,
  language = 'auto',
  className = '',
}) => {
  const { isEnabled, language: contextLanguage } = useTextToSpeechContext();
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  const finalLanguage = language === 'auto' ? contextLanguage : language;

  const playFullSentence = async () => {
    try {
      if (!children || children.trim().length === 0) {
        console.warn('No text to read');
        return;
      }

      setIsPlaying(true);
      console.log('Reading complete sentence:', children);
      console.log('Language:', finalLanguage);

      const response = await fetch(`${getAPIBaseURL()}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: children,
          language: finalLanguage === 'auto' ? 'auto' : finalLanguage === 'hi' ? 'hi-IN' : 'en-US',
        }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('TTS Error:', errorText);
        throw new Error(`Failed to generate speech: ${response.status}`);
      }

      const audioBlob = await response.blob();
      console.log('Audio blob size:', audioBlob.size);

      const audioUrl = URL.createObjectURL(audioBlob);
      console.log('Playing audio...');

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (error) {
      console.error('Error reading sentence:', error);
      setIsPlaying(false);
    }
  };

  const stopReading = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  if (!isEnabled) {
    return <p className={className}>{children}</p>;
  }

  return (
    <div className={`flex items-start gap-2 ${className}`}>
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onError={() => setIsPlaying(false)}
      />

      <p className="flex-1">{children}</p>

      <button
        onClick={isPlaying ? stopReading : playFullSentence}
        className={`flex-shrink-0 p-2 rounded-full transition-all ${
          isPlaying
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-green-500 hover:bg-green-600 text-white'
        }`}
        title={isPlaying ? 'Stop reading' : 'Read sentence'}
        aria-label={isPlaying ? 'Stop reading' : 'Read sentence'}
      >
        {isPlaying ? (
          <VolumeX size={20} />
        ) : (
          <Volume2 size={20} />
        )}
      </button>
    </div>
  );
};

export default SentenceReader;
