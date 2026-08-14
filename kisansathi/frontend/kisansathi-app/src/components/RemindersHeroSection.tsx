import { useLanguage } from '@/context/LanguageContext';
import { Clock, Bell, CheckCircle } from 'lucide-react';

const RemindersHeroSection = () => {
  const { language } = useLanguage();

  return (
    <div className="relative w-full bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 overflow-hidden py-20">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            {language === 'en' 
              ? 'Never Miss a Farm Task Again' 
              : 'कभी भी खेत का काम न भूलें'}
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto mb-8">
            {language === 'en'
              ? 'Smart reminders for crop care, irrigation, fertilization, and harvesting. Stay organized and maximize your yield.'
              : 'फसल की देखभाल, सिंचाई, खाद और कटाई के लिए स्मार्ट रिमाइंडर्स'}
          </p>
          <button className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg transition-all transform hover:scale-105 inline-flex items-center gap-2">
            <Bell className="w-5 h-5" />
            {language === 'en' ? 'Set Your First Reminder' : 'अपना पहला रिमाइंडर सेट करें'}
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          {[
            {
              icon: <Clock className="w-8 h-8" />,
              titleEn: 'Timely Alerts',
              titleHi: 'समय पर सूचनाएं',
              descEn: 'Get notifications at the right time',
              descHi: 'सही समय पर सूचनाएं प्राप्त करें'
            },
            {
              icon: <CheckCircle className="w-8 h-8" />,
              titleEn: 'Track Progress',
              titleHi: 'प्रगति ट्रैक करें',
              descEn: 'Monitor completed tasks',
              descHi: 'पूर्ण किए गए कार्यों की निगरानी करें'
            },
            {
              icon: <Bell className="w-8 h-8" />,
              titleEn: 'Custom Reminders',
              titleHi: 'कस्टम रिमाइंडर्स',
              descEn: 'Create personalized reminders',
              descHi: 'व्यक्तिगत रिमाइंडर्स बनाएं'
            }
          ].map((stat, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-md rounded-lg p-6 text-white border border-white/20">
              <div className="text-blue-300 mb-3">{stat.icon}</div>
              <h3 className="text-xl font-bold mb-2">
                {language === 'en' ? stat.titleEn : stat.titleHi}
              </h3>
              <p className="text-blue-100">
                {language === 'en' ? stat.descEn : stat.descHi}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RemindersHeroSection;
