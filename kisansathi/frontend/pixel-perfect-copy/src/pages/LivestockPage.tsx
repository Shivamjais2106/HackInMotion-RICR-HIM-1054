import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LivestockDiseaseMain from '../components/LivestockDiseaseMain';

const LivestockPage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow">
        <LivestockDiseaseMain />
      </main>
      <Footer />
    </div>
  );
};

export default LivestockPage;
