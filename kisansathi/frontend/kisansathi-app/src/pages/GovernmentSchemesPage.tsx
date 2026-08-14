import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { ChevronDown, CheckCircle, Clock, FileText, ExternalLink } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const schemes = {
  upcoming: [
    {
      name: "Pradhan Mantri Fasal Bima Yojana 2.0",
      ministry: "Ministry of Agriculture",
      launchDate: "June 2026",
      budget: "₹5,000 Crore",
      description: "Enhanced crop insurance scheme with better coverage and lower premiums for farmers.",
      benefits: ["Up to 90% crop loss coverage", "Reduced premium rates", "Faster claim settlement"],
      eligibility: "All farmers with valid land records",
      applyLink: "https://pmfby.gov.in",
      applyMethod: "Online Portal",
    },
    {
      name: "Kisan Samman Nidhi Plus",
      ministry: "Ministry of Agriculture",
      launchDate: "July 2026",
      budget: "₹2,500 Crore",
      description: "Extended income support scheme with additional benefits for small and marginal farmers.",
      benefits: ["₹8,000 per year (increased from ₹6,000)", "Free crop insurance", "Pension benefits"],
      eligibility: "Farmers with land holdings up to 2 hectares",
      applyLink: "https://pmkisan.gov.in/PmksanRegistration.aspx",
      applyMethod: "Online Portal",
    },
    {
      name: "Organic Farming Promotion Scheme",
      ministry: "Ministry of Agriculture",
      launchDate: "August 2026",
      budget: "₹1,500 Crore",
      description: "Subsidy and support for farmers transitioning to organic farming practices.",
      benefits: ["50% subsidy on organic inputs", "Free training programs", "Certification support"],
      eligibility: "Farmers willing to adopt organic farming",
      applyLink: "https://www.nfsm.gov.in",
      applyMethod: "Online Portal",
    },
  ],
  ongoing: [
    {
      name: "Pradhan Mantri Krishi Sinchayee Yojana",
      ministry: "Ministry of Jal Shakti",
      startDate: "2015",
      budget: "₹50,000 Crore",
      description: "Irrigation infrastructure development for efficient water management in agriculture.",
      benefits: ["Drip irrigation subsidy (60%)", "Sprinkler systems support", "Water conservation"],
      eligibility: "All farmers with agricultural land",
      applicationStatus: "Open",
      applyLink: "https://pmksy.gov.in",
      applyMethod: "Online Portal / District Office",
    },
    {
      name: "Soil Health Card Scheme",
      ministry: "Ministry of Agriculture",
      startDate: "2015",
      budget: "₹568 Crore",
      description: "Free soil testing and health cards to help farmers make informed decisions.",
      benefits: ["Free soil testing", "Personalized recommendations", "Improved crop yield"],
      eligibility: "All farmers",
      applicationStatus: "Open",
      applyLink: "https://soilhealth.dac.gov.in",
      applyMethod: "Online Portal / Local Office",
    },
    {
      name: "Kisan Credit Card Scheme",
      ministry: "Ministry of Finance",
      startDate: "1998",
      budget: "Ongoing",
      description: "Easy credit facility for farmers at reasonable interest rates.",
      benefits: ["Low interest rates (4% for timely repayment)", "Flexible repayment", "No collateral needed"],
      eligibility: "Farmers with valid land records",
      applicationStatus: "Open",
      applyLink: "https://www.nabard.org",
      applyMethod: "Bank / NABARD Office",
    },
    {
      name: "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
      ministry: "Ministry of Agriculture",
      startDate: "2019",
      budget: "₹60,000 Crore",
      description: "Direct income support to all landholding farmers.",
      benefits: ["₹6,000 per year in 3 installments", "Direct bank transfer", "No conditions"],
      eligibility: "All farmers with land records",
      applicationStatus: "Open",
      applyLink: "https://pmkisan.gov.in/PmksanRegistration.aspx",
      applyMethod: "Online Portal",
    },
    {
      name: "Pradhan Mantri Fasal Bima Yojana",
      ministry: "Ministry of Agriculture",
      startDate: "2016",
      budget: "₹8,800 Crore",
      description: "Comprehensive crop insurance covering yield losses and natural calamities.",
      benefits: ["Crop loss coverage", "Affordable premiums", "Quick claim settlement"],
      eligibility: "All farmers (mandatory for loan borrowers)",
      applicationStatus: "Open",
      applyLink: "https://pmfby.gov.in",
      applyMethod: "Online Portal / Insurance Agent",
    },
  ],
};

const GovernmentSchemesPage = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<"upcoming" | "ongoing">("ongoing");
  const [expandedScheme, setExpandedScheme] = useState<number | null>(null);

  const currentSchemes = activeTab === "upcoming" ? schemes.upcoming : schemes.ongoing;

  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Banner */}
      <section className="relative h-[400px] md:h-[480px] flex items-center">
        <img
          src="https://cdn.pixabay.com/photo/2016/09/21/04/46/barley-field-1684052_1280.jpg"
          alt="Government Schemes"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16 w-full">
          <h1 className="font-heading text-5xl md:text-7xl font-bold text-primary-foreground mb-4">
            {t('schemes.title')}
          </h1>
          <p className="text-primary-foreground/80 text-lg md:text-xl max-w-lg">
            {t('schemes.subtitle')}
          </p>
        </div>
      </section>

      {/* Tabs */}
      <section className="py-8 bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab("ongoing")}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === "ongoing"
                  ? "bg-gradient-to-r from-green-600 to-teal-600 text-white shadow-lg"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <CheckCircle className="w-5 h-5" />
              {t('schemes.ongoing')} ({schemes.ongoing.length})
            </button>
            <button
              onClick={() => setActiveTab("upcoming")}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === "upcoming"
                  ? "bg-gradient-to-r from-green-600 to-teal-600 text-white shadow-lg"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Clock className="w-5 h-5" />
              {t('schemes.upcoming')} ({schemes.upcoming.length})
            </button>
          </div>
        </div>
      </section>

      {/* Schemes List */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="space-y-4">
            {currentSchemes.map((scheme, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl border-2 border-gray-200 hover:border-green-500 transition-all shadow-md hover:shadow-lg"
              >
                {/* Scheme Header */}
                <button
                  onClick={() => setExpandedScheme(expandedScheme === index ? null : index)}
                  className="w-full p-6 flex items-start justify-between hover:bg-gray-50 transition"
                >
                  <div className="text-left flex-1">
                    <h3 className="text-xl font-bold text-eco-green-dark mb-2">{scheme.name}</h3>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <span className="font-semibold">{t('schemes.ministry')}:</span> {scheme.ministry}
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="font-semibold">{t('schemes.budget')}:</span> {scheme.budget}
                      </span>
                      {activeTab === "upcoming" && (
                        <span className="flex items-center gap-1 text-blue-600 font-semibold">
                          <Clock className="w-4 h-4" />
                          {t('schemes.launchDate')}: {(scheme as any).launchDate}
                        </span>
                      )}
                      {activeTab === "ongoing" && (
                        <span className="flex items-center gap-1 text-green-600 font-semibold">
                          <CheckCircle className="w-4 h-4" />
                          {(scheme as any).applicationStatus}
                        </span>
                      )}
                    </div>
                  </div>
                  <ChevronDown
                    className={`w-6 h-6 text-gray-400 transition-transform ${
                      expandedScheme === index ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {/* Expanded Content */}
                {expandedScheme === index && (
                  <div className="border-t-2 border-gray-200 p-6 bg-gray-50">
                    {/* Description */}
                    <div className="mb-6">
                      <h4 className="font-bold text-gray-800 mb-2">📋 {t('schemes.description')}</h4>
                      <p className="text-gray-700">{scheme.description}</p>
                    </div>

                    {/* Benefits */}
                    <div className="mb-6">
                      <h4 className="font-bold text-gray-800 mb-3">✅ {t('schemes.benefits')}</h4>
                      <ul className="space-y-2">
                        {scheme.benefits.map((benefit, i) => (
                          <li key={i} className="flex items-start gap-3">
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Eligibility */}
                    <div className="mb-6">
                      <h4 className="font-bold text-gray-800 mb-2">👥 {t('schemes.eligibility')}</h4>
                      <p className="text-gray-700 bg-blue-50 p-3 rounded-lg border-l-4 border-blue-500">
                        {scheme.eligibility}
                      </p>
                    </div>

                    {/* Application Method */}
                    <div className="mb-6">
                      <h4 className="font-bold text-gray-800 mb-2">📋 {t('schemes.applyMethod')}</h4>
                      <p className="text-gray-700 bg-green-50 p-3 rounded-lg border-l-4 border-green-500">
                        {(scheme as any).applyMethod}
                      </p>
                    </div>

                    {/* Apply Button */}
                    <div className="flex gap-3">
                      <a
                        href={(scheme as any).applyLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 inline-flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-bold py-3 px-6 rounded-lg transition-all shadow-md hover:shadow-lg"
                      >
                        <ExternalLink className="w-5 h-5" />
                        {t('schemes.applyNow')}
                      </a>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How to Apply Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <h2 className="text-4xl font-bold text-eco-green-dark mb-12 text-center">
            {t('schemes.howToApply')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: "1",
                title: t('schemes.checkEligibility'),
                description: t('schemes.checkEligibilityDesc'),
                icon: "✓",
              },
              {
                step: "2",
                title: t('schemes.gatherDocs'),
                description: t('schemes.gatherDocsDesc'),
                icon: "📄",
              },
              {
                step: "3",
                title: t('schemes.applyOnline'),
                description: t('schemes.applyOnlineDesc'),
                icon: "💻",
              },
              {
                step: "4",
                title: t('schemes.trackStatus'),
                description: t('schemes.trackStatusDesc'),
                icon: "📊",
              },
            ].map((item, index) => (
              <div key={index} className="bg-gradient-to-br from-green-50 to-teal-50 rounded-2xl p-6 border-2 border-green-200">
                <div className="text-4xl font-bold text-green-600 mb-3">{item.icon}</div>
                <h3 className="text-xl font-bold text-eco-green-dark mb-2">{t('schemes.step')} {item.step}</h3>
                <h4 className="font-semibold text-gray-800 mb-2">{item.title}</h4>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </div>
            ))}
          </div>

          {/* Required Documents */}
          <div className="mt-12 bg-blue-50 border-2 border-blue-200 rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-eco-green-dark mb-6 flex items-center gap-2">
              <FileText className="w-6 h-6" />
              {t('schemes.requiredDocs')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                t('schemes.doc1'),
                t('schemes.doc2'),
                t('schemes.doc3'),
                t('schemes.doc4'),
                t('schemes.doc5'),
                t('schemes.doc6'),
              ].map((doc, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="text-gray-700">{doc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Contact Info */}
          <div className="mt-12 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-2xl p-8">
            <h3 className="text-2xl font-bold mb-6">{t('schemes.needHelp')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="font-semibold mb-2">{t('schemes.helplineTitle')}</p>
                <p className="text-lg">{t('schemes.helplineNumber')}</p>
              </div>
              <div>
                <p className="font-semibold mb-2">{t('schemes.officialPortal')}</p>
                <p className="text-lg">{t('schemes.officialPortalUrl')}</p>
              </div>
              <div>
                <p className="font-semibold mb-2">{t('schemes.localOffice')}</p>
                <p className="text-lg">{t('schemes.localOfficeDesc')}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default GovernmentSchemesPage;
