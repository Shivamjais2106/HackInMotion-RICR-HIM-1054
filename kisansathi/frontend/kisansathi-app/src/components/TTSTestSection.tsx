import React from 'react';
import { useTextToSpeechContext } from '@/context/TextToSpeechContext';
import { SpeakableText, SpeakableParagraph } from './SpeakableText';

/**
 * Test section to demonstrate TTS functionality
 */
export const TTSTestSection: React.FC = () => {
  const { isEnabled } = useTextToSpeechContext();

  if (!isEnabled) {
    return null;
  }

  return (
    <section className="py-12 px-4 bg-gradient-to-r from-eco-green/10 to-eco-yellow/10 rounded-lg my-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-6 text-eco-green-dark">
          <SpeakableText text="Text-to-Speech Demo">
            Text-to-Speech Demo
          </SpeakableText>
        </h2>

        <div className="space-y-4">
          <SpeakableParagraph language="en">
            Welcome to KisanSathi! This is a demonstration of our text-to-speech feature. Hover over any text to hear it read aloud.
          </SpeakableParagraph>

          <SpeakableParagraph language="hi">
            किसान साथी में आपका स्वागत है! यह हमारी टेक्स्ट-टू-स्पीच सुविधा का प्रदर्शन है। किसी भी पाठ पर होवर करें इसे जोर से पढ़ा जाना सुनने के लिए।
          </SpeakableParagraph>

          <div className="bg-white p-4 rounded-lg border-2 border-eco-green">
            <h3 className="font-semibold mb-2">
              <SpeakableText text="Features">
                Features
              </SpeakableText>
            </h3>
            <ul className="space-y-2">
              <li>
                <SpeakableText text="✓ Hover to hear text (Desktop)">
                  ✓ Hover to hear text (Desktop)
                </SpeakableText>
              </li>
              <li>
                <SpeakableText text="✓ Tap to hear text (Mobile)">
                  ✓ Tap to hear text (Mobile)
                </SpeakableText>
              </li>
              <li>
                <SpeakableText text="✓ Auto language detection">
                  ✓ Auto language detection
                </SpeakableText>
              </li>
              <li>
                <SpeakableText text="✓ Works in English and Hindi">
                  ✓ Works in English and Hindi
                </SpeakableText>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TTSTestSection;
