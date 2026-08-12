import { useLanguage } from '@/context/LanguageContext';

const LanguageToggle = () => {
  const { language, toggleLanguage } = useLanguage();

  return (
    <button
      onClick={toggleLanguage}
      className="fixed top-24 right-6 z-40 bg-gradient-to-r from-eco-green to-teal-600 text-white font-bold px-4 py-2 rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105 flex items-center gap-2"
      title="Toggle Language"
    >
      <span className="text-lg">{language === 'en' ? '🇬🇧' : '🇮🇳'}</span>
      <span className="text-sm">{language === 'en' ? 'EN' : 'HI'}</span>
    </button>
  );
};

export default LanguageToggle;
