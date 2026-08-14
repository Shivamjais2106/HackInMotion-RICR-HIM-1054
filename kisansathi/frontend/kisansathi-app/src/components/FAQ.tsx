import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const FAQ = () => {
  const { t } = useLanguage();
  const [open, setOpen] = useState<number | null>(null);

  const faqs = [
    { q: t('faq.q1'), a: t('faq.a1') },
    { q: t('faq.q2'), a: t('faq.a2') },
    { q: t('faq.q3'), a: t('faq.a3') },
    { q: t('faq.q4'), a: t('faq.a4') },
    { q: t('faq.q5'), a: t('faq.a5') },
    { q: t('faq.q6'), a: t('faq.a6') },
  ];

  return (
    <section className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Image */}
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=500&h=500&fit=crop"
              alt="FAQ"
              className="w-full h-[500px] object-cover rounded-3xl"
            />
            <div className="absolute bottom-6 left-6 bg-eco-green text-primary-foreground rounded-2xl p-5 flex items-center gap-3">
              <span className="text-2xl">🌾</span>
              <div>
                <p className="font-bold text-lg">KisanSathi</p>
                <p className="text-primary-foreground/60 text-xs">{t('about.title')}</p>
              </div>
            </div>
          </div>

          {/* FAQ Content */}
          <div>
            <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">Frequently Asked Questions</span>
            <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3 mb-8">
              {t('faq.title')}
            </h2>

            <div className="space-y-4">
              {faqs.map((faq, i) => (
                <div
                  key={i}
                  className="border border-border rounded-xl overflow-hidden"
                >
                  <button
                    onClick={() => setOpen(open === i ? null : i)}
                    className="w-full flex items-center justify-between p-5 text-left"
                  >
                    <span className="font-heading text-base font-semibold text-foreground">{faq.q}</span>
                    <ChevronDown
                      className={`w-5 h-5 text-muted-foreground transition-transform ${open === i ? "rotate-180" : ""}`}
                    />
                  </button>
                  {open === i && (
                    <div className="px-5 pb-5 text-muted-foreground text-sm">
                      {faq.a}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQ;
