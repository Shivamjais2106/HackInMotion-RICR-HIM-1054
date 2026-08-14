import React, { useState, useEffect } from 'react';
import { getAPIBaseURL } from '../utils/api';
import './Monitoring.css';

interface Stats {
  uptime_seconds: number;
  total_requests: number;
  total_errors: number;
  error_rate: number;
  avg_response_time_ms: number;
  requests_per_minute: number;
}

interface SystemStats {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
}

interface Alert {
  type: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
}

const Monitoring: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const baseURL = getAPIBaseURL();
        const response = await fetch(`${baseURL}/dashboard/summary`);
        const data = await response.json();
        
        // Parse the data
        const statsResponse = await fetch(`${baseURL}/dashboard/stats`);
        const statsData = await statsResponse.json();
        setStats(statsData.performance);
        setSystemStats(statsData.system);
        
        const alertsResponse = await fetch(`${baseURL}/dashboard/alerts`);
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching monitoring data:', error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="monitoring-loading">Loading monitoring data...</div>;
  }

  return (
    <div className="monitoring-container">
      <h1>System Monitoring Dashboard</h1>
      
      <div className="monitoring-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          Performance
        </button>
        <button 
          className={`tab ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          System
        </button>
        <button 
          className={`tab ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Alerts ({alerts.length})
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="monitoring-section">
          <h2>System Overview</h2>
          <div className="overview-grid">
            <div className="overview-card">
              <h3>Uptime</h3>
              <p className="value">{stats ? (stats.uptime_seconds / 3600).toFixed(2) : 0} hours</p>
            </div>
            <div className="overview-card">
              <h3>Total Requests</h3>
              <p className="value">{stats?.total_requests || 0}</p>
            </div>
            <div className="overview-card">
              <h3>Error Rate</h3>
              <p className={`value ${(stats?.error_rate || 0) > 5 ? 'error' : 'success'}`}>
                {stats?.error_rate.toFixed(2) || 0}%
              </p>
            </div>
            <div className="overview-card">
              <h3>Avg Response Time</h3>
              <p className="value">{stats?.avg_response_time_ms.toFixed(2) || 0}ms</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="monitoring-section">
          <h2>Performance Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Requests/Minute</h3>
              <p className="metric-value">{stats?.requests_per_minute.toFixed(2) || 0}</p>
            </div>
            <div className="metric-card">
              <h3>Total Errors</h3>
              <p className={`metric-value ${(stats?.total_errors || 0) > 0 ? 'error' : 'success'}`}>
                {stats?.total_errors || 0}
              </p>
            </div>
            <div className="metric-card">
              <h3>Error Rate</h3>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{width: `${Math.min(stats?.error_rate || 0, 100)}%`}}
                ></div>
              </div>
              <p>{stats?.error_rate.toFixed(2) || 0}%</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="monitoring-section">
          <h2>System Resources</h2>
          <div className="resources-grid">
            <div className="resource-card">
              <h3>CPU Usage</h3>
              <div className="progress-bar">
                <div 
                  className="progress-fill cpu" 
                  style={{width: `${systemStats?.cpu_percent || 0}%`}}
                ></div>
              </div>
              <p>{systemStats?.cpu_percent.toFixed(1) || 0}%</p>
            </div>
            <div className="resource-card">
              <h3>Memory Usage</h3>
              <div className="progress-bar">
                <div 
                  className="progress-fill memory" 
                  style={{width: `${systemStats?.memory_percent || 0}%`}}
                ></div>
              </div>
              <p>{systemStats?.memory_used_mb.toFixed(0) || 0}MB / {systemStats?.memory_total_mb.toFixed(0) || 0}MB</p>
            </div>
            <div className="resource-card">
              <h3>Disk Usage</h3>
              <div className="progress-bar">
                <div 
                  className="progress-fill disk" 
                  style={{width: `${systemStats?.disk_percent || 0}%`}}
                ></div>
              </div>
              <p>{systemStats?.disk_used_gb.toFixed(1) || 0}GB / {systemStats?.disk_total_gb.toFixed(1) || 0}GB</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="monitoring-section">
          <h2>System Alerts</h2>
          {alerts.length === 0 ? (
            <p className="no-alerts">No active alerts</p>
          ) : (
            <div className="alerts-list">
              {alerts.map((alert, index) => (
                <div key={index} className={`alert alert-${alert.severity}`}>
                  <span className="alert-type">{alert.type.toUpperCase()}</span>
                  <span className="alert-message">{alert.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Monitoring;
