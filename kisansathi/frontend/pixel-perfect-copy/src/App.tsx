import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { LanguageProvider } from "@/context/LanguageContext";
import { TextToSpeechProvider } from "@/context/TextToSpeechContext";
import LanguageToggle from "@/components/LanguageToggle";
import ProtectedRoute from "@/components/ProtectedRoute";
import Index from "./pages/Index.tsx";
import AboutPage from "./pages/AboutPage.tsx";
import ShopPage from "./pages/ShopPage.tsx";
import GalleryPage from "./pages/GalleryPage.tsx";
import TestimonialPage from "./pages/TestimonialPage.tsx";
import GovernmentSchemesPage from "./pages/GovernmentSchemesPage.tsx";
import FAQPage from "./pages/FAQPage.tsx";
import NotFound from "./pages/NotFound.tsx";
import CropCompletePage from "./pages/CropCompletePage.tsx";
import FertilizerPage from "./pages/FertilizerPage.tsx";
import DiseasePage from "./pages/DiseasePage.tsx";
import ServicesPage from "./pages/ServicesPage.tsx";
import WeatherPage from "./pages/WeatherPage.tsx";
import SmartRemindersPage from "./pages/SmartRemindersPage.tsx";
import VoiceAssistantPage from "./pages/VoiceAssistantPage.tsx";
import ResourcesPage from "./pages/ResourcesPage.tsx";
import AuthPage from "./pages/AuthPage.tsx";
import DashboardEnhanced from "./pages/DashboardEnhanced.tsx";
import LivestockPage from "./pages/LivestockPage.tsx";
import CommunityPage from "./pages/CommunityPage.tsx";
import MonitoringPage from "./pages/MonitoringPage.tsx";
import FileUploadPage from "./pages/FileUploadPage.tsx";
import SeasonalCropRecommendation from "./components/SeasonalCropRecommendation.tsx";
import WeatherTestPage from "./pages/WeatherTestPage.tsx";
import WeatherDebugPage from "./pages/WeatherDebugPage.tsx";
import SoilAnalysisPage from "./pages/SoilAnalysisPage.tsx";
import TTSTestPage from "./pages/TTSTestPage.tsx";

const queryClient = new QueryClient();

const App = () => (
  <LanguageProvider>
    <TextToSpeechProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <LanguageToggle />
          <BrowserRouter future={{ v7_startTransition: true }}>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/shop" element={<ShopPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/testimonial" element={<TestimonialPage />} />
            <Route path="/schemes" element={<GovernmentSchemesPage />} />
            <Route path="/faq" element={<FAQPage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/crop" element={<CropCompletePage />} />
            <Route path="/seasonal-crop" element={<ProtectedRoute element={<SeasonalCropRecommendation />} />} />
            <Route path="/fertilizer" element={<ProtectedRoute element={<FertilizerPage />} />} />
            <Route path="/disease" element={<ProtectedRoute element={<DiseasePage />} />} />
            <Route path="/weather" element={<ProtectedRoute element={<WeatherPage />} />} />
            <Route path="/weather-test" element={<WeatherTestPage />} />
            <Route path="/weather-debug" element={<WeatherDebugPage />} />
            <Route path="/soil-analysis" element={<ProtectedRoute element={<SoilAnalysisPage />} />} />
            <Route path="/reminders" element={<ProtectedRoute element={<SmartRemindersPage />} />} />
            <Route path="/voice-assistant" element={<ProtectedRoute element={<VoiceAssistantPage />} />} />
            <Route path="/resources" element={<ResourcesPage />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/dashboard" element={<ProtectedRoute element={<DashboardEnhanced />} />} />
            <Route path="/profile" element={<ProtectedRoute element={<DashboardEnhanced />} />} />
            <Route path="/livestock" element={<ProtectedRoute element={<LivestockPage />} />} />
            <Route path="/community" element={<ProtectedRoute element={<CommunityPage />} />} />
            <Route path="/monitoring" element={<ProtectedRoute element={<MonitoringPage />} />} />
            <Route path="/files" element={<ProtectedRoute element={<FileUploadPage />} />} />
            <Route path="/tts-test" element={<TTSTestPage />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </TextToSpeechProvider>
  </LanguageProvider>
);

export default App;
