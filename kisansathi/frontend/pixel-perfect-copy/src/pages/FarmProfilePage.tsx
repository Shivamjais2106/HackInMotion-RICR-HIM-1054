import { useState, useEffect } from 'react';
import { getAPIBaseURL, getAuthHeaders } from '@/utils/api';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const SOIL_TYPES = ['Sandy', 'Loamy', 'Clay', 'Clayey', 'Black', 'Red'];
const WATER_SOURCES = ['Canal', 'Borewell', 'River', 'Rainwater', 'Pond', 'Other'];
const IRRIGATION_TYPES = ['Drip', 'Sprinkler', 'Flood', 'Furrow', 'Manual'];
const STATES = [
  'Andhra Pradesh', 'Bihar', 'Gujarat', 'Haryana', 'Himachal Pradesh',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha',
  'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal', 'Other'
];
const COMMON_CROPS = [
  'Wheat', 'Rice', 'Maize', 'Cotton', 'Sugarcane', 'Soybean',
  'Chickpea', 'Mustard', 'Onion', 'Potato', 'Tomato', 'Groundnut',
  'Barley', 'Lentil', 'Turmeric', 'Chilli', 'Other'
];

interface FarmProfile {
  farm_name: string;
  location: string;
  state: string;
  district: string;
  land_size_acres: string;
  soil_type: string;
  water_source: string;
  irrigation_type: string;
  active_crops: string[];
  past_crops: string[];
}

const defaultProfile: FarmProfile = {
  farm_name: '', location: '', state: '', district: '',
  land_size_acres: '', soil_type: '', water_source: '',
  irrigation_type: '', active_crops: [], past_crops: []
};

export default function FarmProfilePage() {
  const [profile, setProfile] = useState<FarmProfile>(defaultProfile);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [irrigationAdvice, setIrrigationAdvice] = useState<any>(null);
  const [loadingAdvice, setLoadingAdvice] = useState(false);
  const [language, setLanguage] = useState<'en' | 'hi'>('en');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getAPIBaseURL()}/farm-profile`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      if (data.profile) {
        setProfile({ ...defaultProfile, ...data.profile, land_size_acres: String(data.profile.land_size_acres || '') });
      }
    } catch (e) {
      console.error('Error fetching profile:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch(`${getAPIBaseURL()}/farm-profile`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ ...profile, land_size_acres: parseFloat(profile.land_size_acres) || 0 })
      });
      const data = await res.json();
      if (data.success) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (e) {
      console.error('Error saving:', e);
    } finally {
      setSaving(false);
    }
  };

  const fetchIrrigationAdvice = async () => {
    setLoadingAdvice(true);
    try {
      const res = await fetch(`${getAPIBaseURL()}/farm-profile/irrigation-advice`, {
        headers: getAuthHeaders()
      });
      const data = await res.json();
      setIrrigationAdvice(data);
    } catch (e) {
      console.error('Error fetching advice:', e);
    } finally {
      setLoadingAdvice(false);
    }
  };

  const toggleCrop = (crop: string, field: 'active_crops' | 'past_crops') => {
    setProfile(prev => ({
      ...prev,
      [field]: prev[field].includes(crop)
        ? prev[field].filter(c => c !== crop)
        : [...prev[field], crop]
    }));
  };

  if (loading) return (
    <div className="min-h-screen bg-eco-cream flex items-center justify-center">
      <div className="text-eco-green-dark text-xl">⏳ {language === 'en' ? 'Loading profile...' : 'प्रोफाइल लोड हो रही है...'}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-eco-cream">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-20">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-eco-green-dark mb-2">
            🌾 {language === 'en' ? 'Farm Profile' : 'खेत की प्रोफाइल'}
          </h1>
          <p className="text-gray-600">
            {language === 'en'
              ? 'Set up your farm details to get personalized crop, irrigation, and market recommendations'
              : 'व्यक्तिगत फसल, सिंचाई और बाजार सिफारिशें पाने के लिए अपने खेत का विवरण भरें'}
          </p>
          <button onClick={() => setLanguage(l => l === 'en' ? 'hi' : 'en')}
            className="mt-2 text-sm text-eco-green border border-eco-green rounded px-3 py-1">
            {language === 'en' ? 'हिंदी' : 'English'}
          </button>
        </div>

        {saved && (
          <div className="bg-green-100 border border-green-400 text-green-800 rounded-lg p-3 mb-6 text-center font-medium">
            ✅ {language === 'en' ? 'Farm profile saved successfully!' : 'खेत की प्रोफाइल सफलतापूर्वक सहेजी गई!'}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">

          {/* Basic Info */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-eco-green-dark mb-4">
              📋 {language === 'en' ? 'Basic Information' : 'मूल जानकारी'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'Farm Name' : 'खेत का नाम'}
                </label>
                <input type="text" value={profile.farm_name}
                  onChange={e => setProfile(p => ({ ...p, farm_name: e.target.value }))}
                  placeholder={language === 'en' ? 'e.g. Green Valley Farm' : 'जैसे: हरी घाटी खेत'}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'Land Size (Acres)' : 'भूमि का क्षेत्र (एकड़)'}
                </label>
                <input type="number" min="0" step="0.1" value={profile.land_size_acres}
                  onChange={e => setProfile(p => ({ ...p, land_size_acres: e.target.value }))}
                  placeholder="e.g. 5.5"
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'State' : 'राज्य'}
                </label>
                <select value={profile.state}
                  onChange={e => setProfile(p => ({ ...p, state: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none">
                  <option value="">{language === 'en' ? 'Select state...' : 'राज्य चुनें...'}</option>
                  {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'District / Location' : 'जिला / स्थान'}
                </label>
                <input type="text" value={profile.location}
                  onChange={e => setProfile(p => ({ ...p, location: e.target.value, district: e.target.value }))}
                  placeholder={language === 'en' ? 'e.g. Jaipur' : 'जैसे: जयपुर'}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none" />
              </div>
            </div>
          </div>

          {/* Soil & Water */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-eco-green-dark mb-4">
              🌱 {language === 'en' ? 'Soil & Water Details' : 'मिट्टी और पानी की जानकारी'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'Soil Type' : 'मिट्टी का प्रकार'}
                </label>
                <select value={profile.soil_type}
                  onChange={e => setProfile(p => ({ ...p, soil_type: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none">
                  <option value="">{language === 'en' ? 'Select...' : 'चुनें...'}</option>
                  {SOIL_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'Water Source' : 'पानी का स्रोत'}
                </label>
                <select value={profile.water_source}
                  onChange={e => setProfile(p => ({ ...p, water_source: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none">
                  <option value="">{language === 'en' ? 'Select...' : 'चुनें...'}</option>
                  {WATER_SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'en' ? 'Irrigation Type' : 'सिंचाई का प्रकार'}
                </label>
                <select value={profile.irrigation_type}
                  onChange={e => setProfile(p => ({ ...p, irrigation_type: e.target.value }))}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-eco-green focus:outline-none">
                  <option value="">{language === 'en' ? 'Select...' : 'चुनें...'}</option>
                  {IRRIGATION_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Active Crops */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-eco-green-dark mb-4">
              🌾 {language === 'en' ? 'Active Crops (Currently Growing)' : 'सक्रिय फसलें (अभी उगा रहे हैं)'}
            </h2>
            <div className="flex flex-wrap gap-2">
              {COMMON_CROPS.map(crop => (
                <button key={crop} type="button"
                  onClick={() => toggleCrop(crop, 'active_crops')}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                    profile.active_crops.includes(crop)
                      ? 'bg-eco-green text-white border-eco-green'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-eco-green'
                  }`}>
                  {crop}
                </button>
              ))}
            </div>
            {profile.active_crops.length > 0 && (
              <p className="mt-2 text-sm text-eco-green">
                ✅ {language === 'en' ? 'Selected:' : 'चुनी हुई:'} {profile.active_crops.join(', ')}
              </p>
            )}
          </div>

          {/* Past Crops */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-eco-green-dark mb-4">
              📅 {language === 'en' ? 'Past Crops (Previous Season)' : 'पिछली फसलें (पिछले मौसम में)'}
            </h2>
            <div className="flex flex-wrap gap-2">
              {COMMON_CROPS.map(crop => (
                <button key={crop} type="button"
                  onClick={() => toggleCrop(crop, 'past_crops')}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                    profile.past_crops.includes(crop)
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                  }`}>
                  {crop}
                </button>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <button type="submit" disabled={saving}
            className="w-full bg-eco-green hover:bg-eco-green-dark text-white font-bold py-3 rounded-xl text-lg transition-colors disabled:opacity-60">
            {saving ? '⏳ Saving...' : `💾 ${language === 'en' ? 'Save Farm Profile' : 'खेत प्रोफाइल सहेजें'}`}
          </button>
        </form>

        {/* Irrigation Advice */}
        <div className="mt-8 bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-eco-green-dark">
              💧 {language === 'en' ? 'Farm-Specific Irrigation Advice' : 'खेत-विशिष्ट सिंचाई सलाह'}
            </h2>
            <button onClick={fetchIrrigationAdvice} disabled={loadingAdvice}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-60">
              {loadingAdvice ? '⏳...' : `🔄 ${language === 'en' ? 'Get Advice' : 'सलाह पाएं'}`}
            </button>
          </div>

          {irrigationAdvice && irrigationAdvice.success && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Temperature</p>
                  <p className="font-bold text-blue-700">{irrigationAdvice.weather?.temperature}°C</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Humidity</p>
                  <p className="font-bold text-green-700">{irrigationAdvice.weather?.humidity}%</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Irrigation Need</p>
                  <p className="font-bold text-purple-700">{irrigationAdvice.irrigation_need_mm_per_day} mm/day</p>
                </div>
                <div className="bg-yellow-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Soil Type</p>
                  <p className="font-bold text-yellow-700">{irrigationAdvice.soil_type}</p>
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="font-medium text-green-800 mb-2">📋 Recommendations:</p>
                <ul className="space-y-1">
                  {irrigationAdvice.schedule?.map((s: string, i: number) => (
                    <li key={i} className="text-sm text-green-700">• {s}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          {irrigationAdvice && !irrigationAdvice.success && (
            <p className="text-orange-600 text-sm">⚠️ {irrigationAdvice.error || 'Save your farm profile first to get irrigation advice.'}</p>
          )}
        </div>

      </div>
      <Footer />
    </div>
  );
}
