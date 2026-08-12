import React, { useState, useEffect } from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, MapPin, Search, AlertCircle, Calendar, Thermometer } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { getAPIBaseURL } from '@/utils/api';

interface CurrentWeather {
  temperature: number;
  feels_like: number;
  temp_min: number;
  temp_max: number;
  humidity: number;
  description: string;
  wind_speed: number;
  timestamp: string;
}

interface ForecastDay {
  date: string;
  day: string;
  temp_min: number;
  temp_max: number;
  temp_avg: number;
  humidity_avg: number;
  description: string;
  wind_speed_avg: number;
}

interface WeatherForecastData {
  success: boolean;
  city: string;
  country: string;
  current: CurrentWeather;
  upcoming_days: ForecastDay[];
}

const WeatherForecast: React.FC = () => {
  const { t } = useLanguage();
  const [city, setCity] = useState('Delhi');
  const [searchInput, setSearchInput] = useState('');
  const [forecastData, setForecastData] = useState<WeatherForecastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getWeatherIcon = (description: string) => {
    const lower = description.toLowerCase();
    if (lower.includes('rain')) return <CloudRain className="w-12 h-12 text-blue-400" />;
    if (lower.includes('cloud')) return <Cloud className="w-12 h-12 text-gray-400" />;
    if (lower.includes('clear') || lower.includes('sunny')) return <Sun className="w-12 h-12 text-yellow-400" />;
    if (lower.includes('partly')) return <Cloud className="w-12 h-12 text-gray-300" />;
    return <Cloud className="w-12 h-12 text-gray-400" />;
  };

  const getWeatherColor = (description: string) => {
    const lower = description.toLowerCase();
    if (lower.includes('rain')) return 'from-blue-400 to-blue-600';
    if (lower.includes('cloud')) return 'from-gray-400 to-gray-600';
    if (lower.includes('clear') || lower.includes('sunny')) return 'from-yellow-300 to-yellow-500';
    if (lower.includes('partly')) return 'from-blue-300 to-gray-400';
    return 'from-gray-400 to-gray-600';
  };

  const fetchForecast = async (cityName: string) => {
    if (!cityName.trim()) return;

    setLoading(true);
    setError('');
    try {
      const baseURL = getAPIBaseURL();
      const response = await fetch(`${baseURL}/weather/${encodeURIComponent(cityName)}`);
      const data = await response.json();

      if (data.weather) {
        // Transform backend response to match frontend expectations
        const weather = data.weather;
        const forecast = data.forecast || [];
        
        // Transform forecast data to match ForecastDay interface
        const transformedForecast: ForecastDay[] = forecast.map((day: any) => ({
          date: day.date || '',
          day: day.day || new Date(day.date).getDate().toString(),
          temp_min: day.temp_min || 20,
          temp_max: day.temp_max || 30,
          temp_avg: day.temp_avg || 25,
          humidity_avg: day.humidity_avg || 60,
          description: day.description || 'Clear',
          wind_speed_avg: day.wind_speed_avg || 10
        }));
        
        const transformedData: WeatherForecastData = {
          success: true,
          city: weather.location || cityName,
          country: 'India',
          current: {
            temperature: weather.temperature || 25,
            feels_like: weather.temperature || 25,
            temp_min: (weather.temperature || 25) - 5,
            temp_max: (weather.temperature || 25) + 5,
            humidity: weather.humidity || 60,
            description: weather.condition || 'Clear',
            wind_speed: weather.wind_speed || 10,
            timestamp: data.timestamp || new Date().toISOString()
          },
          upcoming_days: transformedForecast
        };
        setForecastData(transformedData);
        setCity(cityName);
      } else {
        setError(data.error || 'Failed to fetch forecast');
      }
    } catch (err) {
      setError('Unable to connect to weather service');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      fetchForecast(searchInput);
      setSearchInput('');
    }
  };

  const handleLocationClick = () => {
    setLoading(true);
    setError('');
    
    const baseURL = getAPIBaseURL();
    console.log('Current location button clicked');
    
    // Try browser geolocation first (more accurate)
    if (navigator.geolocation) {
      console.log('Browser geolocation available, requesting permission...');
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          console.log('Got geolocation:', latitude, longitude);
          try {
            // Send GPS coordinates to backend for reverse geocoding
            console.log('Sending GPS coordinates to backend...');
            const response = await fetch(`${baseURL}/location/from-gps`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                latitude: latitude,
                longitude: longitude
              })
            });
            
            const data = await response.json();
            console.log('Backend reverse geocoding response:', data);
            
            if (data.success && data.city) {
              console.log('Detected city from GPS:', data.city);
              setCity(data.city);
              fetchForecast(data.city);
            } else {
              throw new Error('Reverse geocoding failed');
            }
          } catch (err) {
            console.log('Backend reverse geocoding failed:', err);
            // Fallback to backend IP detection
            try {
              const backendResponse = await fetch(`${baseURL}/location/detect`, { timeout: 5000 });
              const backendData = await backendResponse.json();
              if (backendData.success && backendData.city) {
                console.log('Using backend detected city:', backendData.city);
                setCity(backendData.city);
                fetchForecast(backendData.city);
              } else {
                throw new Error('Backend detection failed');
              }
            } catch (backendErr) {
              console.log('Backend detection also failed:', backendErr);
              setCity('Delhi');
              fetchForecast('Delhi');
            }
          }
        },
        (err) => {
          console.log('Geolocation permission denied or error:', err);
          // Fallback to backend detection
          fetch(`${baseURL}/location/detect`, { timeout: 5000 })
            .then(res => res.json())
            .then(data => {
              if (data.success && data.city) {
                console.log('Using backend detected city:', data.city);
                setCity(data.city);
                fetchForecast(data.city);
              } else {
                throw new Error('Backend detection failed');
              }
            })
            .catch(backendErr => {
              console.log('Backend detection failed:', backendErr);
              setCity('Delhi');
              fetchForecast('Delhi');
            });
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      console.log('Geolocation not supported, using backend detection');
      // Fallback to backend detection
      fetch(`${baseURL}/location/detect`, { timeout: 5000 })
        .then(res => res.json())
        .then(data => {
          if (data.success && data.city) {
            console.log('Using backend detected city:', data.city);
            setCity(data.city);
            fetchForecast(data.city);
          } else {
            throw new Error('Backend detection failed');
          }
        })
        .catch(err => {
          console.log('Backend detection failed:', err);
          setCity('Delhi');
          fetchForecast('Delhi');
        });
    }
  };

  // Auto-detect location on component mount
  useEffect(() => {
    const autoDetectLocation = async () => {
      const baseURL = getAPIBaseURL();
      console.log('Starting auto-detection...');
      
      // Try backend location detection first (no permission needed)
      try {
        console.log('Trying backend location detection...');
        const backendResponse = await fetch(`${baseURL}/location/detect`);
        const backendData = await backendResponse.json();
        console.log('Backend response:', backendData);
        
        if (backendData.success && backendData.city) {
          console.log('Backend detected city:', backendData.city);
          setCity(backendData.city);
          fetchForecast(backendData.city);
          return; // Success, exit
        }
      } catch (err) {
        console.log('Backend detection failed:', err);
      }
      
      // If backend fails, use Delhi
      console.log('Using Delhi as fallback');
      setCity('Delhi');
      fetchForecast('Delhi');
    };

    // Call auto-detect immediately
    autoDetectLocation();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-green-50 to-yellow-50 p-2 sm:p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-1 sm:mb-2">Weather Forecast</h1>
          <p className="text-gray-600 text-sm sm:text-base md:text-lg">5-day forecast for your farming activities</p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6 sm:mb-8">
          <div className="flex gap-1 sm:gap-2 flex-col sm:flex-row">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search city..."
                className="w-full px-3 sm:px-6 py-2 sm:py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm sm:text-base"
              />
              <Search className="absolute right-3 sm:right-4 top-2.5 sm:top-3.5 w-4 sm:w-5 h-4 sm:h-5 text-gray-400" />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-3 sm:px-6 py-2 sm:py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg shadow-md transition disabled:bg-gray-400 font-semibold text-sm sm:text-base"
            >
              {loading ? 'Loading...' : 'Search'}
            </button>
            <button
              type="button"
              onClick={handleLocationClick}
              disabled={loading}
              className="px-3 sm:px-6 py-2 sm:py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-md transition disabled:bg-gray-400 font-semibold flex items-center justify-center gap-1 sm:gap-2 text-sm sm:text-base"
            >
              <MapPin className="w-4 sm:w-5 h-4 sm:h-5" />
              <span className="hidden sm:inline">Current</span>
              <span className="sm:hidden">GPS</span>
            </button>
          </div>
        </form>

        {/* Quick Location Selector */}
        <div className="mb-6 sm:mb-8 bg-white rounded-lg shadow-md p-3 sm:p-4">
          <p className="text-xs sm:text-sm font-semibold text-gray-700 mb-2 sm:mb-3">📍 Popular Locations:</p>
          <div className="flex flex-wrap gap-1 sm:gap-2">
            {['Jaipur', 'Jodhpur', 'Udaipur', 'Bikaner', 'Ajmer', 'Kota', 'Delhi', 'Mumbai'].map((loc) => (
              <button
                key={loc}
                onClick={() => {
                  setCity(loc);
                  fetchForecast(loc);
                }}
                disabled={loading}
                className={`px-2 sm:px-4 py-1 sm:py-2 rounded-lg font-medium transition text-xs sm:text-sm ${
                  city === loc
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                } disabled:opacity-50`}
              >
                {loc}
              </button>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 sm:px-6 py-3 sm:py-4 rounded-lg mb-4 sm:mb-6 flex items-start sm:items-center gap-2 sm:gap-3 text-sm sm:text-base">
            <AlertCircle className="w-4 sm:w-5 h-4 sm:h-5 flex-shrink-0 mt-0.5 sm:mt-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Current Weather Card */}
        {forecastData && (
          <>
            <div className="bg-white rounded-2xl shadow-lg p-4 sm:p-6 md:p-8 mb-6 sm:mb-8">
              {/* Location Header */}
              <div className="flex items-center gap-2 text-gray-600 mb-4 sm:mb-6 text-sm sm:text-base md:text-lg">
                <MapPin className="w-4 sm:w-5 h-4 sm:h-5 flex-shrink-0" />
                <span className="font-semibold">{forecastData.city}, {forecastData.country}</span>
              </div>

              {/* Current Weather Display */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
                {/* Left: Temperature and Condition */}
                <div className="flex flex-col justify-center">
                  <div className="flex items-start gap-3 sm:gap-4 mb-4 sm:mb-6">
                    <div>
                      <div className="flex items-baseline gap-1 sm:gap-2">
                        <span className="text-5xl sm:text-6xl md:text-7xl font-bold text-gray-800">
                          {Math.round(forecastData.current.temperature)}
                        </span>
                        <span className="text-2xl sm:text-3xl md:text-4xl text-gray-600">°C</span>
                      </div>
                      <p className="text-gray-600 text-xs sm:text-sm md:text-base mt-1 sm:mt-2">
                        Feels like {Math.round(forecastData.current.feels_like)}°C
                      </p>
                    </div>
                    <div className="flex justify-center">
                      {getWeatherIcon(forecastData.current.description)}
                    </div>
                  </div>
                  <p className="text-gray-700 text-base sm:text-lg md:text-xl font-medium capitalize mb-2 sm:mb-4">
                    {forecastData.current.description}
                  </p>
                  <p className="text-gray-500 text-xs sm:text-sm">
                    {new Date(forecastData.current.timestamp).toLocaleString()}
                  </p>
                </div>

                {/* Right: Weather Details */}
                <div className="grid grid-cols-2 gap-2 sm:gap-3 md:gap-4">
                  {/* Min/Max Temperature */}
                  <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-3 sm:p-4 border border-orange-200">
                    <div className="flex items-center gap-2 mb-1 sm:mb-2">
                      <Thermometer className="w-4 sm:w-5 h-4 sm:h-5 text-red-500 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700">Temp Range</span>
                    </div>
                    <p className="text-lg sm:text-xl md:text-2xl font-bold text-gray-800">
                      {Math.round(forecastData.current.temp_min)}° - {Math.round(forecastData.current.temp_max)}°C
                    </p>
                  </div>

                  {/* Humidity */}
                  <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-3 sm:p-4 border border-blue-200">
                    <div className="flex items-center gap-2 mb-1 sm:mb-2">
                      <Droplets className="w-4 sm:w-5 h-4 sm:h-5 text-blue-500 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700">Humidity</span>
                    </div>
                    <p className="text-lg sm:text-xl md:text-2xl font-bold text-gray-800">{forecastData.current.humidity}%</p>
                  </div>

                  {/* Wind Speed */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-3 sm:p-4 border border-green-200">
                    <div className="flex items-center gap-2 mb-1 sm:mb-2">
                      <Wind className="w-4 sm:w-5 h-4 sm:h-5 text-green-500 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700">Wind</span>
                    </div>
                    <p className="text-lg sm:text-xl md:text-2xl font-bold text-gray-800">{Math.round(forecastData.current.wind_speed)} km/h</p>
                  </div>

                  {/* Avg Humidity */}
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-3 sm:p-4 border border-purple-200">
                    <div className="flex items-center gap-2 mb-1 sm:mb-2">
                      <Cloud className="w-4 sm:w-5 h-4 sm:h-5 text-purple-500 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700">Condition</span>
                    </div>
                    <p className="text-sm sm:text-base md:text-lg font-bold text-gray-800 capitalize">
                      {forecastData.current.description}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 5-Day Forecast */}
            {forecastData.upcoming_days.length > 0 && (
            <div className="mb-6 sm:mb-8">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-3 sm:mb-4 flex items-center gap-2">
                <Calendar className="w-5 sm:w-6 h-5 sm:h-6" />
                5-Day Forecast
              </h2>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 sm:gap-3 md:gap-4">
                {forecastData.upcoming_days.map((day, index) => (
                  <div
                    key={index}
                    className="bg-white rounded-xl shadow-md hover:shadow-lg transition overflow-hidden"
                  >
                    {/* Header with gradient */}
                    <div className={`bg-gradient-to-r ${getWeatherColor(day.description)} p-2 sm:p-3 md:p-4 text-white`}>
                      <p className="font-bold text-sm sm:text-base md:text-lg">{day.day}</p>
                      <p className="text-xs sm:text-sm opacity-90">{day.date}</p>
                    </div>

                    {/* Content */}
                    <div className="p-2 sm:p-3 md:p-4">
                      {/* Weather Icon */}
                      <div className="flex justify-center mb-2 sm:mb-3 md:mb-4">
                        <div className="w-8 sm:w-10 md:w-12 h-8 sm:h-10 md:h-12">
                          {getWeatherIcon(day.description)}
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-center text-gray-700 font-medium text-xs sm:text-sm mb-2 sm:mb-3 md:mb-4 capitalize">
                        {day.description}
                      </p>

                      {/* Temperature */}
                      <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-2 sm:p-2.5 md:p-3 mb-2 sm:mb-2.5 md:mb-3">
                        <p className="text-xs text-gray-600 mb-0.5 sm:mb-1">Temp</p>
                        <p className="text-sm sm:text-base md:text-lg font-bold text-gray-800">
                          {Math.round(day.temp_min)}° - {Math.round(day.temp_max)}°C
                        </p>
                        <p className="text-xs text-gray-600 mt-0.5 sm:mt-1">
                          Avg: {Math.round(day.temp_avg)}°C
                        </p>
                      </div>

                      {/* Humidity */}
                      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-2 sm:p-2.5 md:p-3 mb-2 sm:mb-2.5 md:mb-3">
                        <div className="flex items-center gap-1 mb-0.5 sm:mb-1">
                          <Droplets className="w-3 sm:w-4 h-3 sm:h-4 text-blue-500" />
                          <p className="text-xs text-gray-600">Humidity</p>
                        </div>
                        <p className="text-sm sm:text-base md:text-lg font-bold text-gray-800">{Math.round(day.humidity_avg)}%</p>
                      </div>

                      {/* Wind Speed */}
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-2 sm:p-2.5 md:p-3">
                        <div className="flex items-center gap-1 mb-0.5 sm:mb-1">
                          <Wind className="w-3 sm:w-4 h-3 sm:h-4 text-green-500" />
                          <p className="text-xs text-gray-600">Wind</p>
                        </div>
                        <p className="text-sm sm:text-base md:text-lg font-bold text-gray-800">{Math.round(day.wind_speed_avg)} km/h</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            )}

            {/* Farming Tips */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4 sm:p-6">
              <h3 className="text-lg sm:text-xl font-bold text-green-800 mb-3 sm:mb-4">🌾 Farming Tips</h3>
              <div className="space-y-2 sm:space-y-3">
                {forecastData.current.temperature > 35 && (
                  <div className="flex gap-2 sm:gap-3 items-start">
                    <span className="text-xl sm:text-2xl flex-shrink-0">🌡️</span>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm sm:text-base">High Temperature Alert</p>
                      <p className="text-gray-700 text-xs sm:text-sm">Increase irrigation frequency and use shade nets for sensitive crops</p>
                    </div>
                  </div>
                )}
                {forecastData.current.humidity > 80 && (
                  <div className="flex gap-2 sm:gap-3 items-start">
                    <span className="text-xl sm:text-2xl flex-shrink-0">🍃</span>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm sm:text-base">Disease Risk</p>
                      <p className="text-gray-700 text-xs sm:text-sm">High humidity increases fungal disease risk. Ensure proper ventilation</p>
                    </div>
                  </div>
                )}
                {forecastData.current.wind_speed > 40 && (
                  <div className="flex gap-2 sm:gap-3 items-start">
                    <span className="text-xl sm:text-2xl flex-shrink-0">💨</span>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm sm:text-base">Strong Winds</p>
                      <p className="text-gray-700 text-xs sm:text-sm">Protect crops from wind damage. Check support structures</p>
                    </div>
                  </div>
                )}
                {forecastData.current.temperature <= 35 && forecastData.current.humidity <= 80 && forecastData.current.wind_speed <= 40 && (
                  <div className="flex gap-2 sm:gap-3 items-start">
                    <span className="text-xl sm:text-2xl flex-shrink-0">✅</span>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm sm:text-base">Favorable Conditions</p>
                      <p className="text-gray-700 text-xs sm:text-sm">Weather conditions are favorable for farming activities</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherForecast;
