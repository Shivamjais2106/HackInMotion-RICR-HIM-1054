import { useEffect, useState } from "react";
import { getAPIBaseURL } from "@/utils/api";
import chatbotBg from "@/assets/chatbot-bg.jpg";
import {
  PanelLeft,
  SquarePen,
  Boxes,
  CheckSquare,
  Compass,
  Images,
  FlaskConical,
  Plus,
  ChevronDown,
  Glasses,
  AudioLines,
  ExternalLink,
  Minus,
  Square,
  X,
  Paperclip,
  Info,
  MessageSquare,
  MoreHorizontal,
  FileText,
  Image as ImageIcon,
  Send,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const sidebarItems = [
  { icon: PanelLeft, label: "Toggle sidebar" },
  { icon: SquarePen, label: "New chat" },
  { icon: Boxes, label: "Apps" },
  { icon: CheckSquare, label: "Tasks" },
];

const sidebarItemsBottom = [
  { icon: Compass, label: "Discover" },
  { icon: Images, label: "Gallery" },
  { icon: FlaskConical, label: "Labs" },
];

const chipsRow1En = [
  "Crop recommendation",
  "Disease detection",
  "Fertilizer advice",
  "Weather forecast",
  "Pest management",
];

const chipsRow2En = [
  "Livestock health",
  "Soil analysis",
  "Market prices",
];

const chipsRow1Hi = [
  "फसल की सिफारिश",
  "रोग पहचान",
  "खाद की सलाह",
  "मौसम पूर्वानुमान",
  "कीट प्रबंधन",
];

const chipsRow2Hi = [
  "पशु स्वास्थ्य",
  "मिट्टी विश्लेषण",
  "बाजार भाव",
];

const ChatbotUI = () => {
  const { language } = useLanguage();
  const [showFeatures, setShowFeatures] = useState(true);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.title = language === 'en' 
      ? "KisanSathi AI - What can I help you with today?"
      : "किसान साथी AI - आज मैं आपकी कैसे मदद कर सकता हूँ?";
  }, [language]);

  const chipsRow1 = language === 'en' ? chipsRow1En : chipsRow1Hi;
  const chipsRow2 = language === 'en' ? chipsRow2En : chipsRow2Hi;

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;
    setMessages([...messages, { role: 'user', content: userMessage }]);
    setMessage("");
    setShowFeatures(false);
    setLoading(true);

    try {
      const response = await fetch(`${getAPIBaseURL()}/chatbot/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMessage, 
          language,
          conversation_history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage = data.response || "I'm here to help with farming advice!";
        setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);
        
        // Play audio response
        speakText(assistantMessage);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I couldn't process that. Please try again." }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Connection error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const language = detectLanguage(text);
      utterance.lang = language;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    }
  };

  const detectLanguage = (text: string): string => {
    const hindiPattern = /[\u0900-\u097F]/;
    return hindiPattern.test(text) ? 'hi-IN' : 'en-IN';
  };

  const handleChipClick = (chip: string) => {
    setMessage(chip);
  };

  const featureCards = [
    {
      icon: '🌾',
      titleEn: 'Crop Selection',
      titleHi: 'फसल चयन',
      descEn: 'Get crop recommendations',
      descHi: 'फसल की सिफारिशें प्राप्त करें'
    },
    {
      icon: '🧪',
      titleEn: 'Fertilizer Guide',
      titleHi: 'खाद गाइड',
      descEn: 'Fertilizer recommendations',
      descHi: 'खाद की सिफारिशें'
    },
    {
      icon: '🔍',
      titleEn: 'Disease Detection',
      titleHi: 'रोग पहचान',
      descEn: 'Identify plant diseases',
      descHi: 'पौधों की बीमारियों की पहचान करें'
    },
    {
      icon: '🌤️',
      titleEn: 'Weather Advice',
      titleHi: 'मौसम सलाह',
      descEn: 'Weather-based guidance',
      descHi: 'मौसम आधारित मार्गदर्शन'
    },
    {
      icon: '📊',
      titleEn: 'Yield Prediction',
      titleHi: 'उपज पूर्वानुमान',
      descEn: 'Predict crop yield',
      descHi: 'फसल की उपज का पूर्वानुमान'
    },
    {
      icon: '💧',
      titleEn: 'Soil Analysis',
      titleHi: 'मिट्टी विश्लेषण',
      descEn: 'Soil health insights',
      descHi: 'मिट्टी स्वास्थ्य अंतर्दृष्टि'
    }
  ];

  return (
    <div 
      className={`relative min-h-screen w-full overflow-hidden text-foreground transition-all ${
        messages.length > 0 ? 'bg-slate-900' : 'bg-cover bg-center'
      }`}
      style={messages.length === 0 ? { backgroundImage: `url(${chatbotBg})` } : {}}
    >
      {/* Sidebar */}
      <aside className={`fixed left-0 top-0 z-20 flex h-screen w-14 flex-col items-center justify-between py-4 border-r transition-all ${
        messages.length > 0 
          ? 'bg-slate-800 border-slate-700' 
          : 'bg-black/40 backdrop-blur-xl border-white/5'
      }`}>
        <div className="flex flex-col items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-emerald-600 text-white font-bold shadow-lg">
            <span className="text-sm">🌾</span>
          </div>
          {sidebarItems.map((it, i) => (
            <button
              key={i}
              aria-label={it.label}
              className="flex h-9 w-9 items-center justify-center rounded-md text-white/80 hover:bg-white/10 transition-colors"
            >
              <it.icon className="h-5 w-5" />
            </button>
          ))}
          <div className="my-2 h-px w-6 bg-white/15" />
          {sidebarItemsBottom.map((it, i) => (
            <button
              key={i}
              aria-label={it.label}
              className="flex h-9 w-9 items-center justify-center rounded-md text-white/80 hover:bg-white/10 transition-colors"
            >
              <it.icon className="h-5 w-5" />
            </button>
          ))}
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white text-sm font-medium">
          👨‍🌾
        </div>
      </aside>

      {/* Window controls */}
      <div className="fixed right-0 top-0 z-20 flex items-center">
        <button className="flex h-10 w-12 items-center justify-center text-white/85 hover:bg-white/10">
          <ExternalLink className="h-4 w-4" />
        </button>
        <button className="flex h-10 w-12 items-center justify-center text-white/85 hover:bg-white/10">
          <Minus className="h-4 w-4" />
        </button>
        <button className="flex h-10 w-12 items-center justify-center text-white/85 hover:bg-white/10">
          <Square className="h-3.5 w-3.5" />
        </button>
        <button className="flex h-10 w-12 items-center justify-center text-white/85 hover:bg-red-500/80">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Main */}
      <main className={`relative z-10 ml-14 flex min-h-screen flex-col transition-all ${
        messages.length > 0 
          ? 'justify-between px-6 py-6' 
          : 'justify-center items-center px-6 pt-24 pb-10'
      }`}>
        {messages.length === 0 ? (
          <>
            <h1 className="mb-8 text-center text-3xl md:text-4xl font-semibold tracking-tight text-white drop-shadow-lg">
              {language === 'en'
                ? "Hi Farmer, what should we dive into today?"
                : "नमस्ते किसान, आज हम क्या करें?"}
            </h1>

            {/* Feature Cards Grid */}
            {showFeatures && (
              <div className="mb-8 grid w-full max-w-4xl grid-cols-2 md:grid-cols-3 gap-4">
                {featureCards.map((card, i) => (
                  <button
                    key={i}
                    className="group rounded-2xl border border-white/20 bg-white/10 backdrop-blur-md p-4 hover:bg-white/20 transition-all hover:scale-105"
                  >
                    <div className="text-4xl mb-2">{card.icon}</div>
                    <h3 className="text-sm font-semibold text-white text-left">
                      {language === 'en' ? card.titleEn : card.titleHi}
                    </h3>
                    <p className="text-xs text-white/70 text-left mt-1">
                      {language === 'en' ? card.descEn : card.descHi}
                    </p>
                  </button>
                ))}
              </div>
            )}

            {/* Composer */}
            <div className="w-full max-w-3xl rounded-3xl border border-white/20 bg-white/10 backdrop-blur-2xl shadow-2xl">
              <div className="px-6 pt-5 pb-3">
                <p className="text-white/55 text-base">
                  {language === 'en' ? "Message KisanSathi AI" : "किसान साथी AI को संदेश भेजें"}
                </p>
              </div>
              <div className="flex items-center gap-3 px-3 pb-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={language === 'en' ? "Ask me anything..." : "कुछ भी पूछें..."}
                  className="flex-1 bg-white/5 border border-white/10 rounded-full px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:border-white/30 transition-colors"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !message.trim()}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Suggestion chips */}
            <div className="mt-6 flex w-full max-w-3xl flex-col items-center gap-3">
              <div className="flex flex-wrap justify-center gap-3">
                {chipsRow1.map((c) => (
                  <button
                    key={c}
                    onClick={() => handleChipClick(c)}
                    className="rounded-full border border-white/20 bg-white/10 backdrop-blur-md px-5 py-2 text-sm text-white/95 hover:bg-white/20 transition-colors"
                  >
                    {c}
                  </button>
                ))}
              </div>
              <div className="flex flex-wrap justify-center gap-3">
                {chipsRow2.map((c) => (
                  <button
                    key={c}
                    onClick={() => handleChipClick(c)}
                    className="rounded-full border border-white/20 bg-white/10 backdrop-blur-md px-5 py-2 text-sm text-white/95 hover:bg-white/20 transition-colors"
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Chat Messages */}
            <div className="w-full max-w-3xl flex-1 overflow-y-auto space-y-4 py-6">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-700 border border-slate-600 text-white/90'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-slate-700 border border-slate-600 rounded-2xl px-4 py-3">
                    <p className="text-sm text-white/70">Thinking...</p>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="w-full max-w-3xl rounded-3xl border border-slate-600 bg-slate-800 shadow-2xl">
              <div className="flex items-center gap-3 px-3 py-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={language === 'en' ? "Ask me anything..." : "कुछ भी पूछें..."}
                  className="flex-1 bg-slate-700 border border-slate-600 rounded-full px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:border-slate-500 transition-colors"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !message.trim()}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default ChatbotUI;
