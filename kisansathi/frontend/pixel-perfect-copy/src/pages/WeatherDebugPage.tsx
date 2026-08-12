import React, { useState, useEffect } from 'react';
import { getAPIBaseURL } from '../utils/api';

const WeatherDebugPage: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [data, setData] = useState<any>(null);

  const addLog = (message: string) => {
    console.log(message);
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  useEffect(() => {
    addLog('Page loaded');
    
    const baseURL = getAPIBaseURL();
    
    // Test 1: Backend location
    addLog('Testing backend location detection...');
    fetch(`${baseURL}/location/detect`)
      .then(res => {
        addLog(`Location response status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        addLog(`Location data: ${JSON.stringify(data)}`);
        setData(prev => ({ ...prev, location: data }));
        
        // Test 2: Weather for detected city
        const city = data.city || 'Delhi';
        addLog(`Fetching weather for: ${city}`);
        return fetch(`${baseURL}/weather/${city}`);
      })
      .then(res => {
        addLog(`Weather response status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        addLog(`Weather data: ${JSON.stringify(data)}`);
        setData(prev => ({ ...prev, weather: data }));
      })
      .catch(err => {
        addLog(`Error: ${err.message}`);
      });
  }, []);

  return (
    <div className="p-8 bg-gray-900 text-white min-h-screen font-mono">
      <h1 className="text-3xl font-bold mb-6">Weather Debug Console</h1>
      
      <div className="grid grid-cols-2 gap-8">
        {/* Logs */}
        <div>
          <h2 className="text-xl font-bold mb-4">Logs</h2>
          <div className="bg-black p-4 rounded h-96 overflow-y-auto border border-green-500">
            {logs.map((log, i) => (
              <div key={i} className="text-green-400 text-sm mb-1">
                {log}
              </div>
            ))}
          </div>
        </div>

        {/* Data */}
        <div>
          <h2 className="text-xl font-bold mb-4">Data</h2>
          <div className="bg-black p-4 rounded h-96 overflow-y-auto border border-blue-500">
            <pre className="text-blue-400 text-sm">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </div>
      </div>

      {/* Manual Test Buttons */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Manual Tests</h2>
        <div className="flex gap-4 flex-wrap">
          <button
            onClick={() => {
              const baseURL = getAPIBaseURL();
              addLog('Testing location detection...');
              fetch(`${baseURL}/location/detect`)
                .then(r => r.json())
                .then(d => addLog(`Location: ${JSON.stringify(d)}`))
                .catch(e => addLog(`Error: ${e.message}`));
            }}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded"
          >
            Test Location
          </button>
          
          <button
            onClick={() => {
              const baseURL = getAPIBaseURL();
              addLog('Testing weather for Delhi...');
              fetch(`${baseURL}/weather/Delhi`)
                .then(r => r.json())
                .then(d => addLog(`Weather: ${JSON.stringify(d.weather)}`))
                .catch(e => addLog(`Error: ${e.message}`));
            }}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
          >
            Test Weather
          </button>

          <button
            onClick={() => {
              setLogs([]);
              addLog('Logs cleared');
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded"
          >
            Clear Logs
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="mt-8 p-4 bg-gray-800 rounded">
        <h2 className="text-xl font-bold mb-4">Status</h2>
        <div className="space-y-2">
          <p>Backend: <span className="text-green-400">http://localhost:5000</span></p>
          <p>Frontend: <span className="text-green-400">http://localhost:8080</span></p>
          <p>Total Logs: <span className="text-yellow-400">{logs.length}</span></p>
        </div>
      </div>
    </div>
  );
};

export default WeatherDebugPage;
