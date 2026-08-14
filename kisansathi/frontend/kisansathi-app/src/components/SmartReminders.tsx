import React, { useState, useEffect } from 'react';
import { Calendar, CheckCircle, AlertCircle, Upload, Plus, Trash2, Camera, Clock, Bell } from 'lucide-react';
import { getAPIBaseURL } from '@/utils/api';
import AlertBanner from './AlertBanner';
import NotificationCenter from './NotificationCenter';

interface Crop {
  id: string;
  crop_name: string;
  planting_date: string;
  field_name: string;
  area_acres: number;
  status: string;
  statistics: {
    days_elapsed: number;
    reminders: {
      total: number;
      completed: number;
      percentage: number;
    };
    photos_count: number;
  };
}

interface Reminder {
  id: string;
  task: string;
  task_type: string;
  priority: string;
  scheduled_date: string;
  day: number;
  completed: boolean;
  notes: string;
}

interface Photo {
  id: string;
  filename: string;
  uploaded_at: string;
  notes: string;
  analysis?: {
    disease: string;
    healthy: boolean;
    info: string;
  };
}

const SmartReminders: React.FC = () => {
  const [farmerId] = useState('default_farmer');
  const [farmerName, setFarmerName] = useState('Farmer');
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<Crop | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'crops' | 'reminders' | 'photos'>('crops');
  const [showAddCrop, setShowAddCrop] = useState(false);
  const [availableCrops, setAvailableCrops] = useState<any[]>([]);
  const [showNameInput, setShowNameInput] = useState(false);

  // Form states
  const [newCrop, setNewCrop] = useState({
    crop_name: 'moong',
    planting_date: new Date().toISOString().split('T')[0],
    field_name: 'Field 1',
    area_acres: 1,
  });

  useEffect(() => {
    fetchCrops();
    fetchAvailableCrops();
  }, []);

  const fetchCrops = async () => {
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/crops/${farmerId}`);
      const data = await response.json();
      if (data.success) {
        setCrops(data.crops);
        if (data.crops.length > 0) {
          setSelectedCrop(data.crops[0]);
          fetchReminders(data.crops[0].id);
          fetchPhotos(data.crops[0].id);
        }
      }
    } catch (err) {
      setError('Error fetching crops');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableCrops = async () => {
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/available-crops`);
      const data = await response.json();
      if (data.success) {
        setAvailableCrops(data.crops);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchReminders = async (cropId: string) => {
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/all/${cropId}`);
      const data = await response.json();
      if (data.success) {
        setReminders(data.reminders);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPhotos = async (cropId: string) => {
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/photos/${cropId}`);
      const data = await response.json();
      if (data.success) {
        setPhotos(data.photos);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddCrop = async () => {
    setLoading(true);
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/add-crop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: farmerId,
          ...newCrop,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setShowAddCrop(false);
        setNewCrop({
          crop_name: 'moong',
          planting_date: new Date().toISOString().split('T')[0],
          field_name: 'Field 1',
          area_acres: 1,
        });
        fetchCrops();
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Error adding crop');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteReminder = async (reminderId: string, notes: string) => {
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/reminders/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reminder_id: reminderId, notes }),
      });

      const data = await response.json();
      if (data.success) {
        if (selectedCrop) {
          fetchReminders(selectedCrop.id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUploadPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedCrop || !e.target.files) return;

    const file = e.target.files[0];
    const notes = prompt('Add notes about this photo (optional):') || '';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('notes', notes);

    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(
        `${baseURL}/reminders/upload-photo/${selectedCrop.id}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json();
      if (data.success) {
        fetchPhotos(selectedCrop.id);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Error uploading photo');
      console.error(err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low':
        return 'bg-blue-100 border-blue-300 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getTaskTypeIcon = (taskType: string) => {
    const icons: { [key: string]: string } = {
      preparation: '🌱',
      irrigation: '💧',
      maintenance: '🔧',
      fertilizer: '🧪',
      monitoring: '👁️',
      pest_control: '🐛',
      harvest: '🌾',
    };
    return icons[taskType] || '📋';
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-IN';
      window.speechSynthesis.speak(utterance);
    }
  };

  const getPersonalizedMessage = (reminder: Reminder) => {
    const daysElapsed = selectedCrop ? Math.floor((new Date().getTime() - new Date(selectedCrop.planting_date).getTime()) / (1000 * 60 * 60 * 24)) : 0;
    
    const cropHindi: { [key: string]: string } = {
      'moong': 'moong',
      'rice': 'chawal',
      'wheat': 'gehun',
      'maize': 'makka',
      'cotton': 'kapas',
      'potato': 'aloo',
      'tomato': 'tamatar'
    };
    
    const cropName = selectedCrop ? cropHindi[selectedCrop.crop_name.toLowerCase()] || selectedCrop.crop_name : 'crop';
    
    const getDayDesc = (days: number) => {
      if (days === 0) return 'aaj';
      if (days === 1) return 'kal';
      if (days === 2) return 'parson';
      if (days === 3) return '3 din pehle';
      if (days <= 7) return `${days} din pehle`;
      return `${Math.floor(days / 7)} hafte pehle`;
    };
    
    const dayDesc = getDayDesc(daysElapsed);
    
    if (reminder.task_type === 'irrigation') {
      return `${farmerName} ji, aapne ${dayDesc} ${cropName} lagayi thi. Aaj halka paani dena zaroori hai.`;
    } else if (reminder.task_type === 'weeding') {
      return `${farmerName} ji, ${cropName} ab thik se badh gayi hogi. Aaj nindai (weeding) kar dena zaroori hai.`;
    } else if (reminder.task_type === 'fertilizer') {
      return `${farmerName} ji, ${cropName} ko ab khad ki zaroorat hai. Aaj nitrogen khad daal dena.`;
    } else if (reminder.task_type === 'monitoring') {
      return `${farmerName} ji, ${cropName} ko dhyan se dekh lena. Koi bimari toh nahi hai?`;
    } else if (reminder.task_type === 'pest_control') {
      return `${farmerName} ji, ${cropName} mein keede aa sakte hain. Aaj spray kar dena zaroori hai.`;
    } else if (reminder.task_type === 'harvest') {
      return `${farmerName} ji, ${cropName} kaatne ka samay aa gaya! Badhai ho!`;
    }
    
    return `${farmerName} ji, ${reminder.task} karna zaroori hai.`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Alert Banner */}
        <AlertBanner />

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">📅 Smart Reminders</h1>
          <p className="text-gray-600">Track your crops and never miss important tasks</p>
          
          {/* Farmer Name Input */}
          <div className="mt-4 flex justify-center gap-2">
            {!showNameInput ? (
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-green-700">👨‍🌾 {farmerName}</span>
                <button
                  onClick={() => setShowNameInput(true)}
                  className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                >
                  Edit
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={farmerName}
                  onChange={(e) => setFarmerName(e.target.value)}
                  placeholder="Enter your name"
                  className="px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
                <button
                  onClick={() => setShowNameInput(false)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Save
                </button>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Crops Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">🌾 My Crops</h2>
            <button
              onClick={() => setShowAddCrop(!showAddCrop)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
            >
              <Plus className="w-5 h-5" /> Add Crop
            </button>
          </div>

          {/* Add Crop Form */}
          {showAddCrop && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Crop
                  </label>
                  <select
                    value={newCrop.crop_name}
                    onChange={(e) =>
                      setNewCrop({ ...newCrop, crop_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    {availableCrops.map((crop) => (
                      <option key={crop.name} value={crop.name}>
                        {crop.name.charAt(0).toUpperCase() + crop.name.slice(1)} ({crop.duration_days} days)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Planting Date
                  </label>
                  <input
                    type="date"
                    value={newCrop.planting_date}
                    onChange={(e) =>
                      setNewCrop({ ...newCrop, planting_date: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Field Name
                  </label>
                  <input
                    type="text"
                    value={newCrop.field_name}
                    onChange={(e) =>
                      setNewCrop({ ...newCrop, field_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Area (Acres)
                  </label>
                  <input
                    type="number"
                    value={newCrop.area_acres}
                    onChange={(e) =>
                      setNewCrop({ ...newCrop, area_acres: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              <button
                onClick={handleAddCrop}
                disabled={loading}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition"
              >
                {loading ? 'Adding...' : 'Add Crop & Create Schedule'}
              </button>
            </div>
          )}

          {/* Crops List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {crops.map((crop) => (
              <div
                key={crop.id}
                onClick={() => {
                  setSelectedCrop(crop);
                  fetchReminders(crop.id);
                  fetchPhotos(crop.id);
                  setActiveTab('reminders');
                }}
                className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                  selectedCrop?.id === crop.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white hover:border-green-300'
                }`}
              >
                <h3 className="font-bold text-lg text-gray-800 mb-2">
                  {crop.crop_name.toUpperCase()}
                </h3>
                <p className="text-sm text-gray-600 mb-2">📍 {crop.field_name}</p>
                <p className="text-sm text-gray-600 mb-2">📏 {crop.area_acres} acres</p>
                <p className="text-sm text-gray-600 mb-3">
                  ⏱️ {crop.statistics.days_elapsed} days elapsed
                </p>

                {/* Progress Bar */}
                <div className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Tasks Progress</span>
                    <span>
                      {crop.statistics.reminders.completed}/{crop.statistics.reminders.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${crop.statistics.reminders.percentage}%`,
                      }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {crop.statistics.reminders.percentage}% complete
                  </p>
                </div>

                <p className="text-xs text-gray-600">
                  📸 {crop.statistics.photos_count} photos
                </p>
              </div>
            ))}
          </div>

          {crops.length === 0 && !showAddCrop && (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">No crops added yet</p>
              <button
                onClick={() => setShowAddCrop(true)}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Add Your First Crop
              </button>
            </div>
          )}
        </div>

        {/* Tabs */}
        {selectedCrop && (
          <>
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setActiveTab('reminders')}
                className={`px-6 py-2 rounded-lg font-semibold transition ${
                  activeTab === 'reminders'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                📋 Reminders
              </button>
              <button
                onClick={() => setActiveTab('photos')}
                className={`px-6 py-2 rounded-lg font-semibold transition ${
                  activeTab === 'photos'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                📸 Photos
              </button>
            </div>

            {/* Reminders Tab */}
            {activeTab === 'reminders' && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">📅 Task Schedule</h2>

                {reminders.length === 0 ? (
                  <p className="text-gray-600">No reminders found</p>
                ) : (
                  <div className="space-y-3">
                    {reminders.map((reminder) => (
                      <div
                        key={reminder.id}
                        className={`p-4 rounded-lg border-l-4 ${getPriorityColor(
                          reminder.priority
                        )} ${reminder.completed ? 'opacity-60' : ''}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-2xl">
                                {getTaskTypeIcon(reminder.task_type)}
                              </span>
                              <h3 className="font-bold text-lg">
                                Day {reminder.day}: {reminder.task}
                              </h3>
                              {reminder.completed && (
                                <CheckCircle className="w-5 h-5 text-green-600" />
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mb-2">
                              📅 {new Date(reminder.scheduled_date).toLocaleDateString()}
                            </p>
                            
                            {/* Personalized Hindi Message */}
                            <div className="bg-green-50 border border-green-200 rounded p-3 mb-2">
                              <p className="text-sm font-semibold text-green-800">
                                💬 {getPersonalizedMessage(reminder)}
                              </p>
                            </div>
                            
                            {reminder.notes && (
                              <p className="text-sm text-gray-700 italic">
                                Notes: {reminder.notes}
                              </p>
                            )}
                          </div>

                          {!reminder.completed && (
                            <div className="flex gap-2 ml-4">
                              <button
                                onClick={() => {
                                  const notes = prompt('Add notes (optional):') || '';
                                  handleCompleteReminder(reminder.id, notes);
                                }}
                                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition"
                              >
                                ✓ Done
                              </button>
                              <button
                                onClick={() => speakText(getPersonalizedMessage(reminder))}
                                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition"
                              >
                                🔊
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Photos Tab */}
            {activeTab === 'photos' && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-800">📸 Crop Photos</h2>
                  <label className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition flex items-center gap-2">
                    <Upload className="w-5 h-5" /> Upload Photo
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleUploadPhoto}
                      className="hidden"
                    />
                  </label>
                </div>

                {photos.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">No photos uploaded yet</p>
                    <p className="text-sm text-gray-500">
                      Upload photos to track your crop's health and get disease analysis
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {photos.map((photo) => (
                      <div key={photo.id} className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="bg-gray-200 h-48 flex items-center justify-center">
                          <Camera className="w-12 h-12 text-gray-400" />
                        </div>
                        <div className="p-4">
                          <p className="text-sm text-gray-600 mb-2">
                            📅 {new Date(photo.uploaded_at).toLocaleDateString()}
                          </p>
                          {photo.notes && (
                            <p className="text-sm text-gray-700 mb-2">
                              📝 {photo.notes}
                            </p>
                          )}
                          {photo.analysis && (
                            <div
                              className={`p-2 rounded text-sm ${
                                photo.analysis.healthy
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {photo.analysis.healthy ? '✅ Healthy' : '⚠️ ' + photo.analysis.disease}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SmartReminders;
