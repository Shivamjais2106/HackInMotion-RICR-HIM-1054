import { Link } from 'react-router-dom';
import { ArrowRight, Heart, Zap, Globe } from 'lucide-react';
import animalsImg from '@/assets/external/animals-pair.jpg';

const PetHealthAdvisorSection = () => {
  return (
    <section className="py-12 sm:py-16 md:py-20 lg:py-24 bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Card */}
        <div className="grid lg:grid-cols-2 gap-6 sm:gap-8 md:gap-10 lg:gap-16 items-center bg-white rounded-2xl sm:rounded-3xl p-6 sm:p-8 md:p-10 lg:p-14 shadow-lg border border-orange-100">
          {/* Left Content */}
          <div className="flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-3 sm:mb-4">
              <Heart className="w-5 h-5 sm:w-6 sm:h-6 text-red-500" />
              <p className="text-xs sm:text-sm font-bold uppercase tracking-[0.15em] text-red-600">Pet Health Advisor</p>
            </div>
            
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight text-gray-800 mb-4 sm:mb-6">
              Worried about your <span className="text-red-600">livestock?</span>
            </h2>
            
            <p className="text-sm sm:text-base md:text-lg text-gray-600 leading-relaxed mb-4">
              Don't wait for symptoms to worsen. Our AI analyzes photos and symptoms to suggest the most likely diseases along with first-aid steps you can take immediately.
            </p>
            
            <p className="text-sm sm:text-base md:text-lg text-gray-600 leading-relaxed mb-6 sm:mb-8">
              From foot-and-mouth in cattle to coccidiosis in poultry — fast guidance whenever you need it, in your own language.
            </p>

            {/* Features */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-6 sm:mb-8">
              <div className="flex items-start gap-3">
                <Zap className="w-5 h-5 text-orange-500 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold text-gray-800 text-sm sm:text-base">Instant Diagnosis</p>
                  <p className="text-xs sm:text-sm text-gray-600">AI-powered analysis in seconds</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Globe className="w-5 h-5 text-blue-500 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold text-gray-800 text-sm sm:text-base">Multi-Language</p>
                  <p className="text-xs sm:text-sm text-gray-600">Support in your language</p>
                </div>
              </div>
            </div>

            {/* CTA Button */}
            <Link
              to="/livestock"
              className="inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-semibold rounded-lg sm:rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg w-full sm:w-auto text-sm sm:text-base"
            >
              Diagnose Now
              <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
            </Link>
          </div>

          {/* Right Image */}
          <div className="relative">
            <img
              src={animalsImg}
              alt="Healthy livestock - cow and goat"
              loading="lazy"
              className="rounded-xl sm:rounded-2xl w-full object-cover aspect-[5/4] shadow-lg"
            />
            <div className="absolute -bottom-4 sm:-bottom-5 -left-4 sm:-left-5 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg sm:rounded-2xl px-4 sm:px-5 py-3 sm:py-4 shadow-lg hidden sm:block">
              <div className="font-bold text-2xl sm:text-3xl">12k+</div>
              <div className="text-xs uppercase tracking-wider opacity-90">Animals Helped</div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 mt-10 sm:mt-12 md:mt-16">
          {[
            { label: 'Diseases Detected', value: '50+' },
            { label: 'Accuracy Rate', value: '95%' },
            { label: 'Response Time', value: '<5s' },
            { label: 'Languages', value: '5+' }
          ].map((stat, idx) => (
            <div key={idx} className="bg-white rounded-lg sm:rounded-xl p-4 sm:p-6 text-center shadow-md border border-orange-100">
              <p className="text-2xl sm:text-3xl font-bold text-red-600 mb-1 sm:mb-2">{stat.value}</p>
              <p className="text-xs sm:text-sm text-gray-600 font-medium">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PetHealthAdvisorSection;
