import React, { useState, useRef } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { getAPIBaseURL } from '../utils/api';

interface TextToSpeechProps {
  text: string;
  language?: 'en' | 'hi' | 'auto';
  className?: string;
}

export const TextToSpeech: React.FC<TextToSpeechProps> = ({
  text,
  language = 'auto',
  className = '',
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const playAudio = async () => {
    try {
      setIsLoading(true);

      // Call backend TTS endpoint
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language: language === 'auto' ? 'auto' : language === 'hi' ? 'hi-IN' : 'en-US',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate speech');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error playing audio:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
      />
      
      <button
        onClick={isPlaying ? stopAudio : playAudio}
        disabled={isLoading}
        className={`p-1 rounded-full transition-all ${
          isPlaying
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-green-500 hover:bg-green-600 text-white'
        } disabled:opacity-50`}
        title={isPlaying ? 'Stop audio' : 'Play audio'}
      >
        {isPlaying ? (
          <VolumeX size={18} />
        ) : (
          <Volume2 size={18} />
        )}
      </button>
    </div>
  );
};

// Hook for using TTS in any component
export const useTextToSpeech = () => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const speak = async (text: string, language: string = 'auto') => {
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language: language === 'auto' ? 'auto' : language === 'hi' ? 'hi-IN' : 'en-US',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate speech');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      if (!audioRef.current) {
        const audio = new Audio();
        audioRef.current = audio;
      }

      audioRef.current.src = audioUrl;
      audioRef.current.play();
      setIsPlaying(true);
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return { speak, stop, isPlaying };
};
