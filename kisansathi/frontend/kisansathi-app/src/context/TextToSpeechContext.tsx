import React, { createContext, useContext, useState, ReactNode } from 'react';

interface TextToSpeechContextType {
  isEnabled: boolean;
  toggleTTS: () => void;
  language: 'auto' | 'en' | 'hi';
  setLanguage: (lang: 'auto' | 'en' | 'hi') => void;
}

const TextToSpeechContext = createContext<TextToSpeechContextType | undefined>(undefined);

export const TextToSpeechProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isEnabled, setIsEnabled] = useState(() => {
    // Load from localStorage
    const saved = localStorage.getItem('tts-enabled');
    return saved ? JSON.parse(saved) : false;
  });

  const [language, setLanguage] = useState<'auto' | 'en' | 'hi'>(() => {
    const saved = localStorage.getItem('tts-language');
    return (saved as 'auto' | 'en' | 'hi') || 'auto';
  });

  const toggleTTS = () => {
    setIsEnabled((prev) => {
      const newValue = !prev;
      localStorage.setItem('tts-enabled', JSON.stringify(newValue));
      return newValue;
    });
  };

  const handleSetLanguage = (lang: 'auto' | 'en' | 'hi') => {
    setLanguage(lang);
    localStorage.setItem('tts-language', lang);
  };

  return (
    <TextToSpeechContext.Provider
      value={{
        isEnabled,
        toggleTTS,
        language,
        setLanguage: handleSetLanguage,
      }}
    >
      {children}
    </TextToSpeechContext.Provider>
  );
};

export const useTextToSpeechContext = () => {
  const context = useContext(TextToSpeechContext);
  if (!context) {
    throw new Error('useTextToSpeechContext must be used within TextToSpeechProvider');
  }
  return context;
};
