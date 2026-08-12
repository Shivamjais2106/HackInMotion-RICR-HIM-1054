import { useState, useEffect } from "react";
import { Menu, X, ChevronDown, LogOut, User } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import NotificationCenter from "./NotificationCenter";
import { TTSToggle } from "./TTSToggle";

import img_img_4rNEIMZl5loHoK9yMLJIIMimC4_svg from "../assets/external/WhatsApp Image 2026-04-19 at 15.08.47 (1)-Photoroom.png";

const Navbar = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token");
    const name = localStorage.getItem("user_name");
    if (token && name) {
      setIsLoggedIn(true);
      setUserName(name);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("username");
    setIsLoggedIn(false);
    navigate("/");
  };

  const handleProtectedNavigation = (href: string) => {
    if (!isLoggedIn) {
      toast({
        title: "Login Required",
        description: "Please login to access this feature",
        variant: "destructive",
      });
      navigate("/auth");
      return;
    }
    navigate(href);
  };

  const essentialPages = [
    { label: t('nav.gallery'), href: "/gallery", protected: false },
    { label: t('nav.schemes'), href: "/schemes", protected: false },
    { label: t('nav.faq'), href: "/faq", protected: false },
    { label: t('nav.resources'), href: "/resources", protected: false },
    { label: "👥 Community", href: "/community", protected: true },
    { label: "🏥 Livestock Disease", href: "/livestock", protected: true },
  ];

  return (
    <nav className="absolute top-0 left-0 right-0 z-50 px-3 sm:px-6 lg:px-16 py-3 sm:py-5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="flex items-center gap-1 sm:gap-2">
          <img
            src={img_img_4rNEIMZl5loHoK9yMLJIIMimC4_svg}
            alt="KisanSathi"
            className="h-8 sm:h-10 w-8 sm:w-10"
          />
          <div className="flex flex-col">
            <span className="text-primary-foreground font-heading text-lg sm:text-2xl font-bold">KisanSathi</span>
            <span className="text-eco-yellow text-xs font-semibold hidden sm:block">AI Assistant</span>
          </div>
        </a>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-10">
          <a href="/" className="text-eco-yellow font-semibold text-sm tracking-wide">{t('nav.home')}</a>
          <a href="/about" className="text-primary-foreground/80 hover:text-primary-foreground text-sm font-medium transition-colors">{t('nav.chatbot')}</a>
          <div
            className="relative group"
            onMouseEnter={() => setDropdownOpen(true)}
            onMouseLeave={() => setDropdownOpen(false)}
          >
            <button className="flex items-center gap-1 text-primary-foreground/80 hover:text-primary-foreground text-sm font-medium transition-colors">
              {t('nav.essentialPages')} <ChevronDown className={`w-4 h-4 transition-transform ${dropdownOpen ? "rotate-180" : ""}`} />
            </button>
            {dropdownOpen && (
              <div className="absolute top-full left-0 mt-2 bg-eco-green-dark/95 backdrop-blur-md rounded-xl py-3 min-w-[200px] shadow-xl border border-primary-foreground/10">
                {essentialPages.map((page) => (
                  <button
                    key={page.href}
                    onClick={() => {
                      if (page.protected) {
                        handleProtectedNavigation(page.href);
                      } else {
                        navigate(page.href);
                      }
                      setDropdownOpen(false);
                    }}
                    className="w-full text-left px-5 py-2.5 text-primary-foreground/80 hover:text-eco-yellow hover:bg-primary-foreground/5 text-sm font-medium transition-colors"
                  >
                    {page.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          <a href="/shop" className="text-primary-foreground/80 hover:text-primary-foreground text-sm font-medium transition-colors">{t('nav.shop')}</a>
        </div>

        {/* CTA / User Profile */}
        {isLoggedIn ? (
          <div className="hidden lg:flex items-center gap-4">
            <TTSToggle />
            <NotificationCenter />
            <div
              className="relative"
              onMouseEnter={() => setUserDropdownOpen(true)}
              onMouseLeave={() => setUserDropdownOpen(false)}
            >
              <button className="flex items-center gap-2 bg-eco-green text-white font-semibold px-6 py-3 rounded-full text-sm hover:brightness-110 transition-all">
                <User className="w-4 h-4" />
                {userName}
                <ChevronDown className={`w-4 h-4 transition-transform ${userDropdownOpen ? "rotate-180" : ""}`} />
              </button>
              {userDropdownOpen && (
                <div className="absolute top-full right-0 mt-2 bg-eco-green-dark/95 backdrop-blur-md rounded-xl py-3 min-w-[200px] shadow-xl border border-primary-foreground/10">
                  <a
                    href="/dashboard"
                    className="block px-5 py-2.5 text-primary-foreground/80 hover:text-eco-yellow hover:bg-primary-foreground/5 text-sm font-medium transition-colors"
                  >
                    📊 Dashboard
                  </a>
                  <a
                    href="/profile"
                    className="block px-5 py-2.5 text-primary-foreground/80 hover:text-eco-yellow hover:bg-primary-foreground/5 text-sm font-medium transition-colors"
                  >
                    👤 Profile
                  </a>
                  <a
                    href="/community"
                    className="block px-5 py-2.5 text-primary-foreground/80 hover:text-eco-yellow hover:bg-primary-foreground/5 text-sm font-medium transition-colors"
                  >
                    👥 Community
                  </a>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-5 py-2.5 text-primary-foreground/80 hover:text-eco-yellow hover:bg-primary-foreground/5 text-sm font-medium transition-colors flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <a
            href="/auth"
            className="hidden lg:flex items-center gap-2 bg-eco-yellow text-eco-green-dark font-semibold px-6 py-3 rounded-full text-sm hover:brightness-110 transition-all"
          >
            {t('nav.getStarted')}
            <span className="bg-eco-green-dark text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs">→</span>
          </a>
        )}

        {/* Mobile Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden text-primary-foreground"
        >
          {mobileOpen ? <X className="w-5 sm:w-6 h-5 sm:h-6" /> : <Menu className="w-5 sm:w-6 h-5 sm:h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="lg:hidden mt-3 sm:mt-4 bg-eco-green-dark/95 backdrop-blur-md rounded-2xl p-4 sm:p-6 flex flex-col gap-2 sm:gap-4">
          <div className="flex justify-center mb-2">
            <TTSToggle />
          </div>
          <button onClick={() => { navigate("/"); setMobileOpen(false); }} className="text-eco-yellow font-semibold text-left text-sm sm:text-base py-2">{t('nav.home')}</button>
          <button onClick={() => { navigate("/about"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">{t('nav.chatbot')}</button>
          <button onClick={() => { navigate("/gallery"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">{t('nav.gallery')}</button>
          <button onClick={() => { navigate("/schemes"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">{t('nav.schemes')}</button>
          <button onClick={() => { navigate("/faq"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">{t('nav.faq')}</button>
          <button 
            onClick={() => { 
              handleProtectedNavigation("/livestock"); 
              setMobileOpen(false); 
            }} 
            className="text-primary-foreground/80 text-left text-sm sm:text-base py-2"
          >
            🏥 Livestock Disease
          </button>
          <button onClick={() => { navigate("/shop"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">{t('nav.shop')}</button>
          {isLoggedIn ? (
            <>
              <button onClick={() => { navigate("/dashboard"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">📊 Dashboard</button>
              <button onClick={() => { navigate("/profile"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">👤 Profile</button>
              <button onClick={() => { navigate("/community"); setMobileOpen(false); }} className="text-primary-foreground/80 text-left text-sm sm:text-base py-2">👥 Community</button>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white font-semibold px-4 sm:px-6 py-2 sm:py-3 rounded-full text-sm text-center flex items-center justify-center gap-2 mt-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </>
          ) : (
            <button onClick={() => { navigate("/auth"); setMobileOpen(false); }} className="bg-eco-yellow text-eco-green-dark font-semibold px-4 sm:px-6 py-2 sm:py-3 rounded-full text-sm text-center mt-2">
              {t('nav.getStarted')}
            </button>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
