import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

import img_bRer0FkEydJg1pcxxm3ySCJmUW8_png from "../assets/external/bRer0FkEydJg1pcxxm3ySCJmUW8.png";
import img_DPeZE54kzc2js4Xf73KTcPrc_jpg from "../assets/external/DPeZE54kzc2js4Xf73KTcPrc.jpg";
import img_img_7TTGVQatUt6ZqPwPMgivWqDw0_jpg from "../assets/external/7TTGVQatUt6ZqPwPMgivWqDw0.jpg";
import img_bqaxUASa5A08yAw5qVEICzHOn4_jpg from "../assets/external/bqaxUASa5A08yAw5qVEICzHOn4.jpg";
import img_M8tI7NdRSgpiivxj9uyWX5PZI_jpg from "../assets/external/M8tI7NdRSgpiivxj9uyWX5PZI.jpg";
import img_iRKO0IDGnvtY3dHG1DSocvCs_jpg from "../assets/external/iRKO0IDGnvtY3dHG1DSocvCs.jpg";
import img_L5ZOf1bSsxnFo4iTDv3bamiEk_jpeg from "../assets/external/L5ZOf1bSsxnFo4iTDv3bamiEk.jpeg";
import img_TgRCmSQEBuWCS5PT6mj8xdMcHI_jpeg from "../assets/external/TgRCmSQEBuWCS5PT6mj8xdMcHI.jpeg";
import img_hIiFD3wHpCagiQZtgWVWY7EVU_jpeg from "../assets/external/hIiFD3wHpCagiQZtgWVWY7EVU.jpeg";
import img_pcb5yTRmmPb3AD4e14mWz1oMukM_jpg from "../assets/external/pcb5yTRmmPb3AD4e14mWz1oMukM.jpg";

const galleryImages = [
  img_bRer0FkEydJg1pcxxm3ySCJmUW8_png,
  img_DPeZE54kzc2js4Xf73KTcPrc_jpg,
  img_img_7TTGVQatUt6ZqPwPMgivWqDw0_jpg,
  img_bqaxUASa5A08yAw5qVEICzHOn4_jpg,
  img_M8tI7NdRSgpiivxj9uyWX5PZI_jpg,
  img_iRKO0IDGnvtY3dHG1DSocvCs_jpg,
  img_L5ZOf1bSsxnFo4iTDv3bamiEk_jpeg,
  img_TgRCmSQEBuWCS5PT6mj8xdMcHI_jpeg,
  img_hIiFD3wHpCagiQZtgWVWY7EVU_jpeg,
];

const GalleryPage = () => {
  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Banner */}
      <section className="relative h-[480px] flex items-center">
        <div className="absolute inset-0">
          <img
            src={img_pcb5yTRmmPb3AD4e14mWz1oMukM_jpg}
            alt="Our Gallery"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-eco-green-dark/50" />
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16 w-full">
          <h1 className="font-heading text-5xl md:text-7xl font-bold text-primary-foreground">Our Gallery</h1>
          <p className="text-primary-foreground/80 text-lg mt-4">A Visual Journey of Freshness, Sustainability, and Growth</p>
        </div>
      </section>

      {/* Gallery Grid */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {galleryImages.map((img, i) => (
              <div key={i} className="group cursor-pointer overflow-hidden rounded-2xl">
                <img
                  src={img}
                  alt={`Gallery image ${i + 1}`}
                  className="w-full h-72 object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default GalleryPage;
