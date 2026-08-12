import { useNavigate } from "react-router-dom";
import { Mic } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const About = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  return (
    <section id="about" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-20">
          {/* Microphone Button Section */}
          <div className="relative h-[500px] rounded-3xl overflow-hidden bg-gradient-to-br from-eco-green via-eco-green-dark to-eco-green-dark flex items-center justify-center group">
            {/* Animated background elements */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-10 right-10 w-40 h-40 bg-eco-yellow rounded-full blur-3xl"></div>
              <div className="absolute bottom-10 left-10 w-40 h-40 bg-eco-yellow rounded-full blur-3xl"></div>
            </div>
            
            {/* Content */}
            <div className="relative z-10 flex flex-col items-center gap-6">
              <div className="text-center">
                <h3 className="text-primary-foreground text-2xl font-bold mb-2">{t('about.talk')}</h3>
                <p className="text-primary-foreground/70 text-sm">{t('about.click')}</p>
              </div>
              
              <button
                onClick={() => navigate("/about")}
                className="bg-eco-yellow text-eco-green-dark p-8 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 hover:shadow-3xl hover:brightness-110 group/btn"
              >
                <Mic className="w-12 h-12 group-hover/btn:animate-pulse" />
              </button>
              
              <p className="text-primary-foreground/60 text-xs mt-4">🎤 {t('about.voice')}</p>
            </div>
          </div>

          {/* Content */}
          <div>
            <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">{t('about.title')}</span>
            <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3 mb-8">
              {t('about.heading')}
            </h2>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-12 h-12 bg-eco-yellow rounded-full flex items-center justify-center flex-shrink-0 text-xl">
                  🤖
                </div>
                <div>
                  <h4 className="font-heading text-lg font-bold text-foreground">{t('about.ai')}</h4>
                  <p className="text-muted-foreground text-sm mt-1">{t('about.ai_desc')}</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 bg-eco-yellow rounded-full flex items-center justify-center flex-shrink-0 text-xl">
                  🔍
                </div>
                <div>
                  <h4 className="font-heading text-lg font-bold text-foreground">{t('about.disease')}</h4>
                  <p className="text-muted-foreground text-sm mt-1">{t('about.disease_desc')}</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 bg-eco-yellow rounded-full flex items-center justify-center flex-shrink-0 text-xl">
                  🌤️
                </div>
                <div>
                  <h4 className="font-heading text-lg font-bold text-foreground">{t('about.weather')}</h4>
                  <p className="text-muted-foreground text-sm mt-1">{t('about.weather_desc')}</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 bg-eco-yellow rounded-full flex items-center justify-center flex-shrink-0 text-xl">
                  🎤
                </div>
                <div>
                  <h4 className="font-heading text-lg font-bold text-foreground">{t('about.voice_support')}</h4>
                  <p className="text-muted-foreground text-sm mt-1">{t('about.voice_support_desc')}</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
