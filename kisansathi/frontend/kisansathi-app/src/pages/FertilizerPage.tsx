import { useState } from 'react';
import FertilizerRecommendation from '@/components/FertilizerRecommendation';
import VoiceFertilizerPipeline from '@/components/VoiceFertilizerPipeline';

export default function FertilizerPage() {
  const [mode, setMode] = useState<'manual' | 'voice'>('manual');

  return (
    <div>
      {/* Mode Selector */}
      <div className="bg-white border-b-2 border-eco-green sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex gap-4">
          <button
            onClick={() => setMode('manual')}
            className={`px-6 py-2 font-semibold rounded-lg transition-colors ${
              mode === 'manual'
                ? 'bg-eco-green text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📝 Manual Input
          </button>
          <button
            onClick={() => setMode('voice')}
            className={`px-6 py-2 font-semibold rounded-lg transition-colors ${
              mode === 'voice'
                ? 'bg-eco-green text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🎤 Voice Assistant
          </button>
        </div>
      </div>

      {/* Content */}
      {mode === 'manual' && <FertilizerRecommendation />}
      {mode === 'voice' && <VoiceFertilizerPipeline />}
    </div>
  );
}
