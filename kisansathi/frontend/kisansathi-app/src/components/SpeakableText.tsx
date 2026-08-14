import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { useTextToSpeechContext } from '@/context/TextToSpeechContext';
import { getAPIBaseURL } from '@/utils/api';

interface SpeakableTextProps {
  children: React.ReactNode;
  text?: string;
  language?: 'auto' | 'en' | 'hi';
  className?: string;
  showIcon?: boolean;
  onSpeak?: () => void;
}

/**
 * Wrapper component that makes any text speakable
 * Shows audio icon on hover/tap
 * Works like Android TalkBack
 */
export const SpeakableText: React.FC<SpeakableTextProps> = ({
  children,
  text,
  language: propLanguage = 'auto',
  className = '',
  showIcon = true,
  onSpeak,
}) => {
  const { isEnabled, language: contextLanguage } = useTextToSpeechContext();
  const [isPlaying, setIsPlaying] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  const textContent = text || (typeof children === 'string' ? children : '');
  
  // Use context language if prop language is 'auto'
  const finalLanguage = propLanguage === 'auto' ? contextLanguage : propLanguage;

  const playAudio = async () => {
    try {
      if (!textContent) {
        console.warn('No text content to speak');
        return;
      }

      setIsPlaying(true);
      onSpeak?.();

      const baseURL = getAPIBaseURL();
      console.log('Fetching TTS for:', textContent, 'Language:', finalLanguage);

      const response = await fetch(`${baseURL}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textContent,
          language: finalLanguage === 'auto' ? 'auto' : finalLanguage === 'hi' ? 'hi-IN' : 'en-US',
        }),
      });

      console.log('TTS Response Status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('TTS Error:', errorText);
        throw new Error(`Failed to generate speech: ${response.status}`);
      }

      const audioBlob = await response.blob();
      console.log('Audio Blob Size:', audioBlob.size);

      const audioUrl = URL.createObjectURL(audioBlob);
      console.log('Audio URL created:', audioUrl);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        console.log('Playing audio...');
        audioRef.current.play().catch(err => {
          console.error('Play error:', err);
          setIsPlaying(false);
        });
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
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
    <span
      className={`relative inline-block group ${className}`}
      onMouseEnter={() => isEnabled && setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
      onTouchStart={() => isEnabled && setShowControls(true)}
      onTouchEnd={() => setShowControls(false)}
    >
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Main text */}
      <span className="inline-block">{children}</span>

      {/* Audio controls - visible on hover/tap only if TTS is enabled */}
      {isEnabled && showIcon && showControls && (
        <button
          onClick={isPlaying ? stopAudio : playAudio}
          className={`ml-1 inline-flex items-center justify-center p-1 rounded-full transition-all ${
            isPlaying
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
          title={isPlaying ? 'Stop audio' : 'Play audio'}
          aria-label={isPlaying ? 'Stop audio' : 'Play audio'}
        >
          {isPlaying ? (
            <VolumeX size={14} />
          ) : (
            <Volume2 size={14} />
          )}
        </button>
      )}

      {/* Always show icon on mobile if TTS is enabled */}
      {isEnabled && showIcon && !showControls && (
        <button
          onClick={isPlaying ? stopAudio : playAudio}
          className="md:hidden ml-1 inline-flex items-center justify-center p-1 rounded-full bg-gray-300 hover:bg-gray-400 text-gray-600 transition-all"
          title={isPlaying ? 'Stop audio' : 'Play audio'}
          aria-label={isPlaying ? 'Stop audio' : 'Play audio'}
        >
          <Volume2 size={14} />
        </button>
      )}
    </span>
  );
};

/**
 * Paragraph component with TTS support
 */
export const SpeakableParagraph: React.FC<{
  children: string;
  language?: 'auto' | 'en' | 'hi';
  className?: string;
}> = ({ children, language = 'auto', className = '' }) => {
  return (
    <p className={className}>
      <SpeakableText text={children} language={language} showIcon={true}>
        {children}
      </SpeakableText>
    </p>
  );
};

/**
 * Heading component with TTS support
 */
export const SpeakableHeading: React.FC<{
  level?: 1 | 2 | 3 | 4 | 5 | 6;
  children: string;
  language?: 'auto' | 'en' | 'hi';
  className?: string;
}> = ({ level = 2, children, language = 'auto', className = '' }) => {
  const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements;

  return React.createElement(
    HeadingTag,
    { className },
    <SpeakableText text={children} language={language} showIcon={true}>
      {children}
    </SpeakableText>
  );
};
