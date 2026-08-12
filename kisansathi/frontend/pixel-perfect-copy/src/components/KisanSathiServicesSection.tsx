import { Link } from 'react-router-dom';
import { useLanguage } from '@/context/LanguageContext';

const KisanSathiServicesSection = () => {
  const { t } = useLanguage();
  
  const services = [
    {
      title: t('services.chatbot'),
      description: t('services.chatbot_desc'),
      icon: '🤖',
      link: '/about'
    },
    {
      title: t('services.crop'),
      description: t('services.crop_desc'),
      icon: '🌾',
      link: '/crop'
    },
    {
      title: t('services.fertilizer'),
      description: t('services.fertilizer_desc'),
      icon: '🧪',
      link: '/fertilizer'
    },
    {
      title: t('services.disease'),
      description: t('services.disease_desc'),
      icon: '🔍',
      link: '/disease'
    },
    {
      title: t('services.weather'),
      description: t('services.weather_desc'),
      icon: '🌤️',
      link: '/weather'
    },
    {
      title: t('services.reminders'),
      description: t('services.reminders_desc'),
      icon: '📅',
      link: '/reminders'
    }
  ];

  // Note: Crop recommendation now includes all features (manual, voice, seasonal) in one component at /crop

  return (
    <section className="py-20 bg-eco-cream">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-14">
          <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">KisanSathi Services</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3">
            {t('services.title')}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, i) => (
            <Link key={i} to={service.link}>
              <div className="group cursor-pointer bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all hover:scale-105 h-full">
                <div className="text-4xl mb-3">{service.icon}</div>
                <h3 className="text-lg font-bold text-eco-green-dark mb-2">{service.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{service.description}</p>
                <div className="flex items-center gap-2 text-eco-green font-semibold text-sm">
                  {t('services.getStarted')} <span>→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default KisanSathiServicesSection;
