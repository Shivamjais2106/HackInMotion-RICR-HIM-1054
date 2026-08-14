import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import FarmerCommunity from '@/components/FarmerCommunity';

const CommunityPage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-1">
        <FarmerCommunity />
      </div>
      <Footer />
    </div>
  );
};

export default CommunityPage;
