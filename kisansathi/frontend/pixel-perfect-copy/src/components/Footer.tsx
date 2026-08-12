import img_TfVsdEorI3M6CtwPPcnMUstJ5Q_png from "../assets/external/TfVsdEorI3M6CtwPPcnMUstJ5Q.png";
import img_IaiXPcjhnjzr1iVhFOtYldWJlAw_svg from "../assets/external/IaiXPcjhnjzr1iVhFOtYldWJlAw.svg";
import img_FkkZQ21lbczJIWxigYbEQD75uI_svg from "../assets/external/FkkZQ21lbczJIWxigYbEQD75uI.svg";
import img_aGyF36iTVtlRHvmLXOHcT54MK3I_svg from "../assets/external/aGyF36iTVtlRHvmLXOHcT54MK3I.svg";
import img_img_4rNEIMZl5loHoK9yMLJIIMimC4_svg from "../assets/external/WhatsApp Image 2026-04-19 at 15.08.47 (1)-Photoroom.png";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";

const Footer = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <footer id="contact">
      {/* Dark Green Footer */}
      <div className="bg-eco-green-dark py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
            {/* Logo & Description */}
            <div>
              <a href="/" className="flex items-center gap-2 mb-4">
                <span className="text-eco-yellow font-heading text-2xl font-bold">🌾</span>
                <span className="text-primary-foreground font-heading text-2xl font-bold">KisanSathi</span>
              </a>
              <p className="text-primary-foreground/60 text-sm leading-relaxed mb-6">
                Smart farming assistant providing AI-powered guidance for crop recommendations, disease detection, and fertilizer suggestions.
              </p>
              <div className="flex gap-3">
                {["facebook", "twitter", "instagram", "linkedin"].map((social) => (
                  <a
                    key={social}
                    href="#"
                    className="w-8 h-8 rounded-full border border-primary-foreground/20 flex items-center justify-center text-primary-foreground/60 hover:text-eco-yellow hover:border-eco-yellow transition-colors text-xs"
                  >
                    {social[0].toUpperCase()}
                  </a>
                ))}
              </div>
            </div>

            {/* Features */}
            <div>
              <h4 className="font-heading text-lg font-bold text-primary-foreground mb-6">{t('footer.features')}</h4>
              <ul className="space-y-3">
                {[t('nav.chatbot'), t('services.crop'), t('services.disease'), t('services.fertilizer')].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-primary-foreground/60 text-sm hover:text-eco-yellow transition-colors">{item}</a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-heading text-lg font-bold text-primary-foreground mb-6">{t('footer.quickLinks')}</h4>
              <ul className="space-y-3">
                <li>
                  <button onClick={() => navigate("/shop")} className="text-primary-foreground/60 text-sm hover:text-eco-yellow transition-colors">{t('footer.shop')}</button>
                </li>
                <li>
                  <button onClick={() => navigate("/schemes")} className="text-primary-foreground/60 text-sm hover:text-eco-yellow transition-colors">{t('nav.schemes')}</button>
                </li>
                <li>
                  <button onClick={() => navigate("/resources")} className="text-primary-foreground/60 text-sm hover:text-eco-yellow transition-colors">{t('nav.resources')}</button>
                </li>
                <li>
                  <a href="#" className="text-primary-foreground/60 text-sm hover:text-eco-yellow transition-colors">{t('footer.contact')}</a>
                </li>
              </ul>
            </div>

            {/* Subscribe Newsletter */}
            <div>
              <h4 className="font-heading text-lg font-bold text-primary-foreground mb-6">{t('footer.subscribe')}</h4>
              <p className="text-primary-foreground/60 text-sm mb-4">{t('footer.subscribe_desc')}</p>
              <div className="mb-4">
                <input
                  type="email"
                  placeholder={t('footer.email')}
                  className="w-full bg-primary-foreground/5 border border-primary-foreground/10 rounded-xl px-4 py-3 text-primary-foreground text-sm placeholder:text-primary-foreground/30 focus:outline-none focus:border-eco-yellow"
                />
              </div>
              <button className="w-full flex items-center justify-center gap-2 bg-eco-yellow text-eco-green-dark font-semibold px-6 py-3 rounded-full text-sm hover:brightness-110 transition-all">
                {t('footer.subscribeBtn')}
                <span className="bg-eco-green-dark text-eco-yellow rounded-full w-5 h-5 flex items-center justify-center text-xs">→</span>
              </button>
            </div>
          </div>

          <div className="border-t border-eco-green-light/20 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-primary-foreground/40 text-sm">{t('footer.copyright')}</p>
            <div className="flex gap-6">
              <a href="#" className="text-primary-foreground/40 text-sm hover:text-eco-yellow transition-colors">{t('footer.privacy')}</a>
              <span className="text-primary-foreground/20">|</span>
              <a href="#" className="text-primary-foreground/40 text-sm hover:text-eco-yellow transition-colors">{t('footer.terms')}</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
