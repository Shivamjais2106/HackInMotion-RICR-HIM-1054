import React, { useState, useEffect } from 'react';
import { Bell, X, AlertCircle, CheckCircle, Info, AlertTriangle, Clock } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';

interface Notification {
  id: string;
  type: 'alert' | 'reminder' | 'info' | 'warning';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  priority: 'high' | 'medium' | 'low';
  actionUrl?: string;
}

const NotificationCenter: React.FC = () => {
  const { language } = useLanguage();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Mock notifications - in real app, these would come from backend
  useEffect(() => {
    const mockNotifications: Notification[] = [
      {
        id: '1',
        type: 'alert',
        title: language === 'en' ? 'Watering Time' : 'सिंचाई का समय',
        message: language === 'en' 
          ? 'Your rice field needs watering today' 
          : 'आपके चावल के खेत को आज सिंचाई की जरूरत है',
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
        read: false,
        priority: 'high'
      },
      {
        id: '2',
        type: 'reminder',
        title: language === 'en' ? 'Fertilizer Application' : 'खाद का प्रयोग',
        message: language === 'en'
          ? 'Apply nitrogen fertilizer to wheat field'
          : 'गेहूं के खेत में नाइट्रोजन खाद लगाएं',
        timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
        read: false,
        priority: 'high'
      },
      {
        id: '3',
        type: 'warning',
        title: language === 'en' ? 'Pest Alert' : 'कीट सतर्कता',
        message: language === 'en'
          ? 'Armyworm detected in nearby fields'
          : 'पास के खेतों में आर्मीवर्म पाया गया',
        timestamp: new Date(Date.now() - 4 * 60 * 60000).toISOString(),
        read: false,
        priority: 'high'
      },
      {
        id: '4',
        type: 'info',
        title: language === 'en' ? 'Weather Update' : 'मौसम अपडेट',
        message: language === 'en'
          ? 'Rain expected tomorrow, 60% probability'
          : 'कल बारिश की संभावना 60% है',
        timestamp: new Date(Date.now() - 6 * 60 * 60000).toISOString(),
        read: true,
        priority: 'medium'
      },
      {
        id: '5',
        type: 'reminder',
        title: language === 'en' ? 'Harvest Reminder' : 'कटाई की याद',
        message: language === 'en'
          ? 'Maize is ready for harvest'
          : 'मक्का कटाई के लिए तैयार है',
        timestamp: new Date(Date.now() - 24 * 60 * 60000).toISOString(),
        read: true,
        priority: 'medium'
      }
    ];

    setNotifications(mockNotifications);
    setUnreadCount(mockNotifications.filter(n => !n.read).length);
  }, [language]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'alert':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'reminder':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-green-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'alert':
        return 'bg-red-50 border-l-4 border-red-500';
      case 'warning':
        return 'bg-yellow-50 border-l-4 border-yellow-500';
      case 'reminder':
        return 'bg-blue-50 border-l-4 border-blue-500';
      case 'info':
        return 'bg-green-50 border-l-4 border-green-500';
      default:
        return 'bg-gray-50 border-l-4 border-gray-500';
    }
  };

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, read: true } : n
    ));
    setUnreadCount(Math.max(0, unreadCount - 1));
  };

  const deleteNotification = (id: string) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return language === 'en' ? 'Just now' : 'अभी';
    if (diffMins < 60) return `${diffMins}m ${language === 'en' ? 'ago' : 'पहले'}`;
    if (diffHours < 24) return `${diffHours}h ${language === 'en' ? 'ago' : 'पहले'}`;
    if (diffDays < 7) return `${diffDays}d ${language === 'en' ? 'ago' : 'पहले'}`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative">
      {/* Notification Bell Icon */}
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {showPanel && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-2xl z-50 max-h-96 overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-gradient-to-r from-green-600 to-green-700 text-white p-4 flex justify-between items-center">
            <h3 className="text-lg font-bold">
              {language === 'en' ? 'Notifications' : 'सूचनाएं'}
            </h3>
            <button
              onClick={() => setShowPanel(false)}
              className="hover:bg-green-800 p-1 rounded transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Notifications List */}
          {notifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>{language === 'en' ? 'No notifications' : 'कोई सूचना नहीं'}</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 ${getBackgroundColor(notification.type)} ${
                    !notification.read ? 'bg-opacity-100' : 'bg-opacity-50'
                  } hover:bg-opacity-100 transition-all cursor-pointer`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getIcon(notification.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-semibold text-gray-900">
                          {notification.title}
                        </h4>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">
                        {notification.message}
                      </p>
                      <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500">
                          {formatTime(notification.timestamp)}
                        </span>
                        {notification.priority === 'high' && (
                          <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded">
                            {language === 'en' ? 'High Priority' : 'उच्च प्राथमिकता'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="sticky bottom-0 bg-gray-50 p-3 border-t text-center">
              <button className="text-sm text-green-600 hover:text-green-700 font-semibold">
                {language === 'en' ? 'View All' : 'सभी देखें'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
