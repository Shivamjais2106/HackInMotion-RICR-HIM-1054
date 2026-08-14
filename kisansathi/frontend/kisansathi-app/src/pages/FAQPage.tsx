import { useState } from "react";
import { ChevronDown } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useLanguage } from "@/context/LanguageContext";

import img_pcb5yTRmmPb3AD4e14mWz1oMukM_jpg from "../assets/external/pcb5yTRmmPb3AD4e14mWz1oMukM.jpg";

const faqs = [
  {
    question: "What types of produce do you grow?",
    answer: "We grow a wide range of fresh produce, including fruits like strawberries and grapes, vegetables such as tomatoes, carrots, and leafy greens, as well as herbs and specialty crops like microgreens and gourmet vegetables.",
  },
  {
    question: "How can I purchase your products?",
    answer: "You can purchase our products directly from our farm, at local farmers' markets, or through our online store. We also offer subscription boxes for regular deliveries of fresh, seasonal produce.",
  },
  {
    question: "Do you offer farm tours?",
    answer: "Yes! We offer guided farm tours where you can see our sustainable farming practices in action. Tours are available on weekends and can be booked through our website or by calling us directly.",
  },
  {
    question: "Do you use any chemicals or pesticides?",
    answer: "No, we are committed to 100% organic farming practices. We use natural pest control methods, companion planting, and organic fertilizers to ensure our produce is chemical-free and safe for consumption.",
  },
  {
    question: "Do you sell organic seeds or plants?",
    answer: "Yes, we sell a variety of organic seeds and starter plants. Visit our shop section or come to the farm to browse our selection of heirloom and organic varieties perfect for home gardening.",
  },
  {
    question: "How do I market my farm's produce effectively?",
    answer: "Effective marketing includes building a strong online presence, participating in local farmers' markets, creating a CSA program, and leveraging social media to share your farm's story and connect with customers.",
  },
  {
    question: "What are the benefits of composting on a farm?",
    answer: "Composting enriches soil with essential nutrients, improves soil structure and water retention, reduces the need for chemical fertilizers, and helps divert organic waste from landfills, contributing to a more sustainable farming cycle.",
  },
  {
    question: "How do I manage pests organically?",
    answer: "Organic pest management includes using beneficial insects, companion planting, crop rotation, natural sprays like neem oil, and maintaining healthy soil to build plant resistance against pests and diseases.",
  },
];

const FAQPage = () => {
  const { t } = useLanguage();
  const [openIndex, setOpenIndex] = useState<number>(0);

  const faqs = [
    {
      question: t('faqpage.q1'),
      answer: t('faqpage.a1'),
    },
    {
      question: t('faqpage.q2'),
      answer: t('faqpage.a2'),
    },
    {
      question: t('faqpage.q3'),
      answer: t('faqpage.a3'),
    },
    {
      question: t('faqpage.q4'),
      answer: t('faqpage.a4'),
    },
    {
      question: t('faqpage.q5'),
      answer: t('faqpage.a5'),
    },
    {
      question: t('faqpage.q6'),
      answer: t('faqpage.a6'),
    },
    {
      question: t('faqpage.q7'),
      answer: t('faqpage.a7'),
    },
    {
      question: t('faqpage.q8'),
      answer: t('faqpage.a8'),
    },
  ];

  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Banner */}
      <section className="relative h-[480px] flex items-center">
        <div className="absolute inset-0">
          <img
            src={img_pcb5yTRmmPb3AD4e14mWz1oMukM_jpg}
            alt="FAQ"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-eco-green-dark/50" />
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16 w-full">
          <h1 className="font-heading text-5xl md:text-7xl font-bold text-primary-foreground">{t('faqpage.title')}</h1>
          <p className="text-primary-foreground/80 text-lg mt-4">{t('faqpage.subtitle')}</p>
        </div>
      </section>

      {/* FAQ Accordion */}
      <section className="py-20 bg-background">
        <div className="max-w-3xl mx-auto px-6 lg:px-16">
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <div
                key={i}
                className="border border-eco-green/20 rounded-2xl overflow-hidden"
              >
                <button
                  onClick={() => setOpenIndex(openIndex === i ? -1 : i)}
                  className="w-full flex items-center justify-between p-6 text-left"
                >
                  <h3 className="font-heading text-lg font-bold text-foreground pr-4">{faq.question}</h3>
                  <div className={`w-10 h-10 rounded-full border-2 border-eco-green flex items-center justify-center flex-shrink-0 transition-transform ${openIndex === i ? "rotate-180" : ""}`}>
                    <ChevronDown className="w-5 h-5 text-eco-green" />
                  </div>
                </button>
                {openIndex === i && (
                  <>
                    <div className="mx-6 border-t border-dashed border-eco-green/30" />
                    <div className="px-6 pb-6 pt-4">
                      <p className="text-muted-foreground text-sm leading-relaxed">{faq.answer}</p>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default FAQPage;
