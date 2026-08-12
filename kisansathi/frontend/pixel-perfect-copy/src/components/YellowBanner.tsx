import img_TfVsdEorI3M6CtwPPcnMUstJ5Q_png from "../assets/external/TfVsdEorI3M6CtwPPcnMUstJ5Q.png";
import img_Mhw4Eau4SAtUmFkxH5ewmAEaQ_png from "../assets/external/Mhw4Eau4SAtUmFkxH5ewmAEaQ.png";
import img_n0ubmpXvD4ICvgzDIZrK5K9M34_png from "../assets/external/n0ubmpXvD4ICvgzDIZrK5K9M34.png";
import img_img_3asBCYsTkBpYP2kVZvdwZvz2sA_png from "../assets/external/3asBCYsTkBpYP2kVZvdwZvz2sA.png";
import img_img_8oxMLPshpp29p0ct5o4EsY6q0_jpg from "../assets/external/8oxMLPshpp29p0ct5o4EsY6q0.jpg";
import { useLanguage } from "@/context/LanguageContext";

const YellowBanner = () => {
  const { t } = useLanguage();
  return (
    <section className="relative bg-eco-yellow py-10 overflow-hidden">
      {/* Decorative vegetable pattern overlay */}
      <img
        src={img_TfVsdEorI3M6CtwPPcnMUstJ5Q_png}
        alt=""
        className="absolute inset-0 w-full h-full object-cover opacity-20 pointer-events-none"
      />
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16 flex flex-col lg:flex-row items-center justify-between gap-8">
        {/* Left - Stat with profile images */}
        <div className="flex items-center gap-5">
          <div className="flex -space-x-3">
            <img src={img_Mhw4Eau4SAtUmFkxH5ewmAEaQ_png} alt="" className="w-12 h-12 rounded-full border-2 border-eco-yellow object-cover" />
            <img src={img_n0ubmpXvD4ICvgzDIZrK5K9M34_png} alt="" className="w-12 h-12 rounded-full border-2 border-eco-yellow object-cover" />
            <img src={img_img_3asBCYsTkBpYP2kVZvdwZvz2sA_png} alt="" className="w-12 h-12 rounded-full border-2 border-eco-yellow object-cover" />
          </div>
          <div>
            <h3 className="font-heading text-xl md:text-2xl font-bold text-eco-green-dark leading-tight">
              {t('banner.clientsReview')}
            </h3>
          </div>
        </div>

        {/* Center - Rotating Badge */}
        <div className="flex-shrink-0">
          <div className="w-28 h-28 md:w-32 md:h-32 rounded-full border-2 border-eco-green-dark/30 flex items-center justify-center relative">
            {/* Rotating text */}
            <div className="absolute inset-0 flex items-center justify-center">
              <svg viewBox="0 0 120 120" className="w-full h-full animate-spin" style={{ animationDuration: '10s' }}>
                <path
                  id="textCircle"
                  d="M 60, 60 m -45, 0 a 45,45 0 1,1 90,0 a 45,45 0 1,1 -90,0"
                  fill="none"
                />
                <text className="text-[11px] font-bold fill-eco-green-dark uppercase tracking-[3px]">
                  <textPath href="#textCircle" className="fill-current text-eco-green-dark">
                    ✦ {t('banner.organic')} ✦ {t('banner.farming')} ✦ {t('banner.vegetables')} ✦ {t('banner.agro')}
                  </textPath>
                </text>
              </svg>
            </div>
            <div className="bg-eco-green-dark text-eco-yellow w-12 h-12 rounded-xl flex items-center justify-center z-10">
              <span className="text-2xl">↗</span>
            </div>
          </div>
        </div>

        {/* Right - Video */}
        <div className="flex items-center gap-5">
          <div>
            <h3 className="font-heading text-xl md:text-2xl font-bold text-eco-green-dark leading-tight">
              {t('banner.healthyLife')}
            </h3>
          </div>
          <div className="relative w-44 h-28 rounded-xl overflow-hidden flex-shrink-0">
            <img
              src={img_img_8oxMLPshpp29p0ct5o4EsY6q0_jpg}
              alt="Video"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center bg-eco-green-dark/20">
              <div className="w-12 h-12 bg-eco-green-dark/80 rounded-full flex items-center justify-center">
                <span className="text-primary-foreground text-lg ml-0.5">▶</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default YellowBanner;
