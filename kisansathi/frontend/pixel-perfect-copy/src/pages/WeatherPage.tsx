import React from 'react';
import WeatherForecast from '../components/WeatherForecast';
import IrrigationAdviceCard from '../components/IrrigationAdviceCard';

const WeatherPage: React.FC = () => {
  return (
    <div>
      <WeatherForecast />
      {/* Farm-profile-specific irrigation guidance below weather forecast */}
      <div className="max-w-6xl mx-auto px-2 sm:px-4 md:px-8 pb-8">
        <IrrigationAdviceCard />
      </div>
    </div>
  );
};

export default WeatherPage;
