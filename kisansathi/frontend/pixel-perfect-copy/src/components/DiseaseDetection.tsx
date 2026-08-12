import { useState } from 'react';
import { getAPIBaseURL } from '../utils/api';

function parseDiseaseName(raw: string) {
  const parts = raw.split('___');
  const crop = parts[0].replace(/_/g, ' ');
  const disease = parts[1] ? parts[1].replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Unknown';
  return { crop, disease };
}

function getDiseaseColor(disease: string) {
  if (disease.includes('healthy')) return 'bg-green-50 border-green-300';
  if (disease.includes('blight') || disease.includes('Blight')) return 'bg-red-50 border-red-300';
  if (disease.includes('rust')) return 'bg-orange-50 border-orange-300';
  if (disease.includes('spot') || disease.includes('Spot')) return 'bg-yellow-50 border-yellow-300';
  if (disease.includes('smut') || disease.includes('Smut')) return 'bg-orange-50 border-orange-300';
  return 'bg-gray-50 border-gray-300';
}

function getDiseaseIcon(disease: string) {
  if (disease.includes('healthy')) return '✅';
  if (disease.includes('blight') || disease.includes('Blight')) return '🔴';
  if (disease.includes('rust')) return '🟠';
  if (disease.includes('spot') || disease.includes('Spot')) return '🟡';
  return '⚠️';
}

function DiseaseDetection() {
  const [activeTab, setActiveTab] = useState<'general' | 'rice'>('general');

  // General disease state
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Rice disease state
  const [riceFile, setRiceFile] = useState<File | null>(null);
  const [riceResult, setRiceResult] = useState<any>(null);
  const [riceLoading, setRiceLoading] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const newFiles = Array.from(files).filter((f: File) => f.type.includes('image'));
      if (newFiles.length > 0) setUploadedFiles(prev => [...prev, ...newFiles]);
      else alert('Please select image files');
    }
  };

  const removeFile = (index: number) => setUploadedFiles(prev => prev.filter((_, i) => i !== index));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (uploadedFiles.length === 0) { alert('Please select at least one image'); return; }
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const formData = new FormData();
      uploadedFiles.forEach(file => formData.append('files', file));
      const response = await fetch(`${baseURL}/disease-predict`, { method: 'POST', body: formData });
      const data = await response.json();
      setResult(data);
      if (data.success) speakResult(data);
    } catch {
      setResult({ success: false, error: 'Failed to analyze images' });
    }
    setLoading(false);
  };

  const handleRiceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!riceFile) { alert('Please select a rice leaf image'); return; }
    setRiceLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const fd = new FormData();
      fd.append('file', riceFile);
      const res = await fetch(`${baseURL}/rice-disease-predict`, { method: 'POST', body: fd });
      const data = await res.json();
      setRiceResult(data);
    } catch {
      setRiceResult({ success: false, error: 'Failed to analyze image' });
    }
    setRiceLoading(false);
  };

  const speakResult = (data: any) => {
    const { crop, disease } = parseDiseaseName(data.most_common_disease);
    const cleanInfo = data.disease_info.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    const text = `Analyzed ${data.total_images} images. Crop: ${crop}. Disease: ${disease}. ${cleanInfo.substring(0, 200)}`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => { window.speechSynthesis.cancel(); setIsSpeaking(false); };

  return (
    <div className="min-h-screen bg-eco-cream py-20">
      <div className="max-w-4xl mx-auto px-6">
        <h1 className="text-4xl font-bold text-eco-green-dark mb-2">🔍 Disease Detection</h1>
        <p className="text-gray-600 mb-6">Upload plant leaf images for accurate disease detection and analysis</p>

        {/* Tab switcher */}
        <div className="flex gap-2 mb-6 border-b-2 border-gray-200">
          <button onClick={() => setActiveTab('general')}
            className={`px-6 py-3 font-semibold transition-colors ${activeTab === 'general' ? 'text-eco-green border-b-4 border-eco-green' : 'text-gray-500 hover:text-eco-green'}`}>
            🌿 General Plant Disease
          </button>
          <button onClick={() => setActiveTab('rice')}
            className={`px-6 py-3 font-semibold transition-colors ${activeTab === 'rice' ? 'text-eco-green border-b-4 border-eco-green' : 'text-gray-500 hover:text-eco-green'}`}>
            🌾 Rice Leaf Disease
          </button>
        </div>

        {/* ── RICE TAB ── */}
        {activeTab === 'rice' && (
          <div>
            <div className="bg-white rounded-lg shadow-lg p-8">
              <form onSubmit={handleRiceSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Upload Rice Leaf Image</label>
                  <div className="border-2 border-dashed border-eco-green rounded-lg p-8 text-center">
                    <input type="file" accept="image/*" id="rice-input" className="hidden"
                      onChange={e => setRiceFile(e.target.files?.[0] || null)} />
                    <label htmlFor="rice-input" className="cursor-pointer">
                      <div className="text-4xl mb-2">🌾</div>
                      <p className="text-gray-700 font-semibold">Click to upload rice leaf image</p>
                      <p className="text-gray-500 text-sm mt-1">Detects: Bacterial leaf blight · Brown spot · Leaf smut</p>
                    </label>
                    {riceFile && <p className="mt-3 text-eco-green font-semibold">✅ {riceFile.name}</p>}
                  </div>
                </div>
                <button type="submit" disabled={riceLoading || !riceFile}
                  className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50">
                  {riceLoading ? '⏳ Analyzing...' : '🔍 Detect Rice Disease'}
                </button>
              </form>
            </div>

            {riceResult && (
              <div className="mt-8">
                {!riceResult.success ? (
                  <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6">
                    <p className="text-red-700 font-semibold">❌ {riceResult.error}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className={`p-6 rounded-lg border-2 ${getDiseaseColor(riceResult.disease)}`}>
                      <h3 className="text-lg font-bold text-gray-800 mb-2">🌾 Rice Disease Detected</h3>
                      <p className="text-2xl font-bold text-eco-green mb-1">{riceResult.disease}</p>
                      <p className="text-sm text-gray-600 mb-3">Confidence: <strong>{riceResult.confidence}%</strong></p>
                      <p className="text-gray-700 text-sm">{riceResult.info}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      <p className="font-semibold text-gray-700 mb-3">📊 All Probabilities</p>
                      {Object.entries(riceResult.all_probabilities).map(([cls, prob]: [string, any]) => (
                        <div key={cls} className="mb-2">
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-700">{cls}</span>
                            <span className="font-semibold">{prob}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div className="bg-eco-green h-2 rounded-full" style={{ width: `${prob}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── GENERAL TAB ── */}
        {activeTab === 'general' && (
          <div>
            <div className="bg-white rounded-lg shadow-lg p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Upload Plant Leaf Images</label>
                  <div className="border-2 border-dashed border-eco-green rounded-lg p-8 text-center cursor-pointer hover:bg-eco-cream transition-colors">
                    <input type="file" accept="image/*" multiple onChange={handleFileUpload} className="hidden" id="image-input" />
                    <label htmlFor="image-input" className="cursor-pointer">
                      <div className="text-4xl mb-2">🖼️</div>
                      <p className="text-gray-700 font-semibold">Click to upload plant leaf images</p>
                      <p className="text-gray-500 text-sm mt-1">JPG, PNG, GIF, BMP supported - Multiple files allowed</p>
                    </label>
                  </div>
                </div>

                {uploadedFiles.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-800 mb-3">📁 Uploaded Files ({uploadedFiles.length})</h3>
                    <div className="space-y-2">
                      {uploadedFiles.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-300">
                          <div className="flex items-center gap-2">
                            <span>🖼️</span>
                            <span className="text-gray-700 font-semibold">{file.name}</span>
                            <span className="text-gray-500 text-sm">({(file.size / 1024).toFixed(2)} KB)</span>
                          </div>
                          <button type="button" onClick={() => removeFile(idx)} className="text-red-500 hover:text-red-700 font-bold">✕</button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                  <p className="text-blue-700 text-sm">
                    <span className="font-semibold">💡 Tip:</span> Upload multiple images for better accuracy. The system analyzes each image and identifies the most common disease.
                  </p>
                </div>

                <button type="submit" disabled={loading || uploadedFiles.length === 0}
                  className="w-full bg-eco-green text-white font-semibold py-3 rounded-lg hover:bg-eco-green-dark transition-colors disabled:opacity-50">
                  {loading ? '⏳ Analyzing Images...' : `🔍 Detect Disease (${uploadedFiles.length})`}
                </button>
              </form>
            </div>

            {result && (
              <div className="mt-8 bg-white rounded-lg shadow-lg p-8">
                {!result.success ? (
                  <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6">
                    <p className="text-red-700 font-semibold">❌ Error</p>
                    <p className="text-red-600 mt-2">{result.error}</p>
                  </div>
                ) : (
                  <div>
                    <h2 className="text-2xl font-bold text-eco-green-dark mb-6">🔍 Disease Detection Results</h2>

                    <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-300 mb-6">
                      <p className="text-blue-700 text-lg">
                        <span className="font-semibold">📊 Summary:</span> Analyzed {result.total_images} image(s). Most common: <strong>{(() => { const { crop, disease } = parseDiseaseName(result.most_common_disease); return `${crop} — ${disease}`; })()}</strong>
                      </p>
                    </div>

                    <div className={`p-6 rounded-lg border-2 mb-6 ${getDiseaseColor(result.most_common_disease)}`}>
                      <h3 className="text-lg font-bold text-gray-800 mb-3">{getDiseaseIcon(result.most_common_disease)} Most Common Disease</h3>
                      {(() => {
                        const { crop, disease } = parseDiseaseName(result.most_common_disease);
                        return (
                          <>
                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-0.5">Crop</p>
                            <p className="text-2xl font-bold text-eco-green mb-2">{crop}</p>
                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-0.5">Disease</p>
                            <p className="text-xl font-semibold text-gray-800 mb-4">{disease}</p>
                          </>
                        );
                      })()}
                      <div className="text-gray-700 text-sm leading-relaxed prose max-w-none"
                        dangerouslySetInnerHTML={{ __html: result.disease_info }} />
                    </div>

                    <div className="mb-6">
                      <h3 className="text-lg font-bold text-gray-800 mb-4">📋 Individual Image Analysis</h3>
                      <div className="space-y-3">
                        {result.predictions.map((pred: any, idx: number) => (
                          <div key={idx} className={`p-4 rounded-lg border-2 ${getDiseaseColor(pred.disease || '')}`}>
                            <p className="font-semibold text-gray-800">{getDiseaseIcon(pred.disease || '')} {pred.filename}</p>
                            {pred.success ? (
                              <div className="mt-2 flex flex-wrap gap-2">
                                {(() => { const { crop, disease } = parseDiseaseName(pred.disease); return (<>
                                  <span className="bg-white border border-gray-300 rounded px-2 py-0.5 text-xs text-gray-600">🌿 {crop}</span>
                                  <span className="bg-white border border-gray-300 rounded px-2 py-0.5 text-xs text-gray-600">🦠 {disease}</span>
                                  {pred.confidence !== undefined && <span className="bg-white border border-gray-300 rounded px-2 py-0.5 text-xs text-gray-600">🎯 {pred.confidence}% confidence</span>}
                                </>); })()}
                              </div>
                            ) : (
                              <p className="text-red-600 mt-1 text-sm">Error: {pred.error}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-6">
                      <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300 text-center">
                        <p className="text-gray-600 text-sm">Total Images</p>
                        <p className="text-3xl font-bold text-green-600 mt-1">{result.total_images}</p>
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300 text-center">
                        <p className="text-gray-600 text-sm">Successful</p>
                        <p className="text-3xl font-bold text-blue-600 mt-1">{result.predictions.filter((p: any) => p.success).length}</p>
                      </div>
                      <div className="bg-orange-50 p-4 rounded-lg border-2 border-orange-300 text-center">
                        <p className="text-gray-600 text-sm">Failed</p>
                        <p className="text-3xl font-bold text-orange-600 mt-1">{result.predictions.filter((p: any) => !p.success).length}</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <button onClick={() => speakResult(result)} disabled={isSpeaking}
                        className="flex-1 bg-blue-500 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50">
                        {isSpeaking ? '🔊 Speaking...' : '🔊 Speak Results'}
                      </button>
                      {isSpeaking && (
                        <button onClick={stopSpeaking} className="flex-1 bg-red-500 text-white font-semibold py-2 rounded-lg hover:bg-red-600">
                          ⏹️ Stop
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default DiseaseDetection;
