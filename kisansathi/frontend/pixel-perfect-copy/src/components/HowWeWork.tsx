import img_ylH1TySsTue8MjCcWn0lFAjBcI_jpg from "../assets/external/ylH1TySsTue8MjCcWn0lFAjBcI.jpg";
import { useLanguage } from "@/context/LanguageContext";

const HowWeWork = () => {
  const { t } = useLanguage();
  
  const steps = [
    { num: "01", title: t('howwe.step1'), desc: t('howwe.step1_desc') },
    { num: "02", title: t('howwe.step2'), desc: t('howwe.step2_desc') },
    { num: "03", title: t('howwe.step3'), desc: t('howwe.step3_desc') },
    { num: "04", title: t('howwe.step4'), desc: t('howwe.step4_desc') },
  ];

  return (
    <section className="py-20 bg-eco-cream">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-4">
          <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">KisanSathi Process</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3">
            {t('howwe.title')}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto mt-4 text-sm">
            {t('howwe.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mt-12 items-center">
          {/* Image */}
          <div className="rounded-3xl overflow-hidden">
            <img
              src={img_ylH1TySsTue8MjCcWn0lFAjBcI_jpg}
              alt="Working"
              className="w-full h-[450px] object-cover rounded-3xl"
            />
          </div>

          {/* Steps */}
          <div className="space-y-8">
            {steps.map((step, i) => (
              <div key={i} className="flex gap-6 items-start">
                <span className="font-heading text-5xl font-bold text-eco-green/20">{step.num}</span>
                <div>
                  <h5 className="font-heading text-lg font-bold text-foreground">{step.title}</h5>
                  <p className="text-muted-foreground text-sm mt-1">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowWeWork;
