import React, { useState, useEffect } from 'react';
import { AlertTriangle, X, Bell, Zap } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';

interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  action?: {
    label: string;
    url: string;
  };
}

const AlertBanner: React.FC = () => {
  const { language } = useLanguage();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Mock critical alerts
    const mockAlerts: Alert[] = [
      {
        id: 'alert-1',
        type: 'critical',
        title: language === 'en' ? '⚠️ Severe Weather Alert' : '⚠️ गंभीर मौसम सतर्कता',
        message: language === 'en'
          ? 'Heavy rainfall expected in your region. Secure your crops immediately!'
          : 'आपके क्षेत्र में भारी बारिश की संभावना है। अपनी फसलों को तुरंत सुरक्षित करें!',
        action: {
          label: language === 'en' ? 'View Details' : 'विवरण देखें',
          url: '/weather'
        }
      },
      {
        id: 'alert-2',
        type: 'warning',
        title: language === 'en' ? '🐛 Pest Outbreak' : '🐛 कीट प्रकोप',
        message: language === 'en'
          ? 'Armyworm detected in 3 nearby farms. Take preventive measures now.'
          : '3 पास के खेतों में आर्मीवर्म पाया गया। अभी निवारक उपाय लें।',
        action: {
          label: language === 'en' ? 'Learn More' : 'और जानें',
          url: '/pest-management'
        }
      }
    ];

    setAlerts(mockAlerts);
  }, [language]);

  const dismissAlert = (id: string) => {
    setDismissedAlerts(new Set([...dismissedAlerts, id]));
  };

  const visibleAlerts = alerts.filter(alert => !dismissedAlerts.has(alert.id));

  if (visibleAlerts.length === 0) return null;

  return (
    <div className="space-y-3 mb-6">
      {visibleAlerts.map((alert) => (
        <div
          key={alert.id}
          className={`rounded-lg p-4 flex items-start gap-4 ${
            alert.type === 'critical'
              ? 'bg-red-50 border-l-4 border-red-500'
              : alert.type === 'warning'
              ? 'bg-yellow-50 border-l-4 border-yellow-500'
              : 'bg-blue-50 border-l-4 border-blue-500'
          }`}
        >
          {/* Icon */}
          <div className="flex-shrink-0 mt-1">
            {alert.type === 'critical' && (
              <Zap className="w-6 h-6 text-red-600 animate-pulse" />
            )}
            {alert.type === 'warning' && (
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            )}
            {alert.type === 'info' && (
              <Bell className="w-6 h-6 text-blue-600" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${
              alert.type === 'critical'
                ? 'text-red-900'
                : alert.type === 'warning'
                ? 'text-yellow-900'
                : 'text-blue-900'
            }`}>
              {alert.title}
            </h3>
            <p className={`text-sm mt-1 ${
              alert.type === 'critical'
                ? 'text-red-800'
                : alert.type === 'warning'
                ? 'text-yellow-800'
                : 'text-blue-800'
            }`}>
              {alert.message}
            </p>
            {alert.action && (
              <a
                href={alert.action.url}
                className={`inline-block mt-3 font-semibold text-sm px-4 py-2 rounded transition-all ${
                  alert.type === 'critical'
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : alert.type === 'warning'
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {alert.action.label}
              </a>
            )}
          </div>

          {/* Close Button */}
          <button
            onClick={() => dismissAlert(alert.id)}
            className={`flex-shrink-0 ${
              alert.type === 'critical'
                ? 'text-red-600 hover:text-red-800'
                : alert.type === 'warning'
                ? 'text-yellow-600 hover:text-yellow-800'
                : 'text-blue-600 hover:text-blue-800'
            }`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default AlertBanner;
