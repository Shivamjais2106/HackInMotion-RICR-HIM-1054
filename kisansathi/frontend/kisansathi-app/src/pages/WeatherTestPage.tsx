import React, { useState } from 'react';
import { getAPIBaseURL } from '../utils/api';

const WeatherTestPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const testWeather = async (city: string) => {
    setLoading(true);
    setError('');
    try {
      const baseURL = getAPIBaseURL();
      console.log(`Fetching weather for ${city}...`);
      const response = await fetch(`${baseURL}/weather/${encodeURIComponent(city)}`);
      console.log('Response status:', response.status);
      
      const json = await response.json();
      console.log('Response data:', json);
      
      setData(json);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Weather API Test</h1>
      
      <div className="mb-6 flex gap-2 flex-wrap">
        <button
          onClick={() => testWeather('Delhi')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test Delhi
        </button>
        <button
          onClick={() => testWeather('Mumbai')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test Mumbai
        </button>
        <button
          onClick={() => testWeather('Bangalore')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test Bangalore
        </button>
      </div>

      {loading && <p className="text-lg">Loading...</p>}
      {error && <p className="text-red-600 text-lg">Error: {error}</p>}
      
      {data && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">{data.location}</h2>
          
          {data.weather && (
            <div className="space-y-2 mb-6">
              <p><strong>Temperature:</strong> {data.weather.temperature}°C</p>
              <p><strong>Condition:</strong> {data.weather.condition}</p>
              <p><strong>Humidity:</strong> {data.weather.humidity}%</p>
              <p><strong>Wind Speed:</strong> {data.weather.wind_speed} km/h</p>
              <p><strong>Rainfall:</strong> {data.weather.rainfall} mm</p>
            </div>
          )}
          
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default WeatherTestPage;
