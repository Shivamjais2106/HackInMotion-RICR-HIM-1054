import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import About from "@/components/About";
import HowWeWork from "@/components/HowWeWork";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";
import KisanSathiServicesSection from "@/components/KisanSathiServicesSection";
import ShopPreview from "@/components/ShopPreview";
import PetHealthAdvisorSection from "@/components/PetHealthAdvisorSection";
import ResourcesPreviewSection from "@/components/ResourcesPreviewSection";
import TTSTestSection from "@/components/TTSTestSection";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <TTSTestSection />
      <KisanSathiServicesSection />
      <PetHealthAdvisorSection />
      <ResourcesPreviewSection />
      <ShopPreview />
      <About />
      <HowWeWork />
      <FAQ />
      <Footer />
    </div>
  );
};

export default Index;
