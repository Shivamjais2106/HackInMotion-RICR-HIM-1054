import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Volume2, Copy, Loader, Trash2, Plus, MessageCircle, Paperclip, X, ChevronRight, Menu } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { getAPIBaseURL } from '@/utils/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  language?: string;
  feature?: string;
  attachments?: Array<{
    type: 'image' | 'pdf';
    name: string;
    data?: string;
  }>;
}

interface Conversation {
  id: string;
  title: string;
  timestamp: Date;
}

const UnifiedChatbot: React.FC = () => {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<Array<{ type: 'image' | 'pdf'; name: string; data: string }>>([]);
  const [userName, setUserName] = useState('Farmer');
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputText(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() && attachedFiles.length === 0) return;

    const userMessage: Message = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: inputText || (attachedFiles.length > 0 ? `Sent ${attachedFiles.length} file(s)` : ''),
      timestamp: new Date(),
      attachments: attachedFiles,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setAttachedFiles([]);
    setIsLoading(true);

    try {
      const conversation_history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch(`${getAPIBaseURL()}/chatbot/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputText || `Analyzing ${attachedFiles.length} file(s)`,
          conversation_history: conversation_history,
          attachments: attachedFiles,
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: `a-${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          language: data.language,
          feature: data.feature,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        speakText(data.response);
      } else {
        const errorMessage: Message = {
          id: `e-${Date.now()}`,
          role: 'assistant',
          content: data.error || 'Error processing message',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (err) {
      console.error(err);
      const errorMessage: Message = {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: 'Error connecting to server',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const detectLanguage = (text: string): string => {
    const hindiPattern = /[\u0900-\u097F]/;
    return hindiPattern.test(text) ? 'hi-IN' : 'en-IN';
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

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const clearChat = () => {
    if (window.confirm('Clear all messages?')) {
      setMessages([]);
    }
  };

  const startNewConversation = () => {
    const newId = `conv-${Date.now()}`;
    const newConv: Conversation = {
      id: newId,
      title: 'New Conversation',
      timestamp: new Date(),
    };
    setConversations([newConv, ...conversations]);
    setCurrentConversationId(newId);
    setMessages([]);
  };

  const loadConversation = (convId: string) => {
    setCurrentConversationId(convId);
    setMessages([]);
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const isImage = file.type.startsWith('image/');
      const isPdf = file.type === 'application/pdf';

      if (!isImage && !isPdf) {
        alert('Please upload only images or PDF files');
        continue;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const data = e.target?.result as string;
        setAttachedFiles((prev) => [
          ...prev,
          {
            type: isImage ? 'image' : 'pdf',
            name: file.name,
            data: data,
          },
        ]);
      };
      reader.readAsDataURL(file);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeAttachment = (index: number) => {
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const getFeatureIcon = (feature?: string) => {
    switch (feature) {
      case 'crop_recommendation':
        return '🌾';
      case 'fertilizer':
        return '🧪';
      case 'disease':
        return '🔍';
      case 'weather':
        return '🌤️';
      case 'reminders':
        return '📅';
      default:
        return '💬';
    }
  };

  return (
    <div 
      className="min-h-screen flex flex-col md:flex-row bg-gradient-to-br from-blue-900 via-teal-800 to-blue-800 relative overflow-hidden"
      style={{
        backgroundImage: `linear-gradient(135deg, #0f172a 0%, #134e5e 50%, #0f172a 100%)`,
        backgroundSize: 'cover',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-green-400/10 to-transparent rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-yellow-400/10 to-transparent rounded-full blur-3xl"></div>

      {/* Left Sidebar - File Attachments (Hidden on mobile) */}
      <div className={`hidden md:flex md:w-64 lg:w-72 transition-all duration-300 bg-blue-950/40 backdrop-blur-md border-r border-white/10 flex-col overflow-hidden`}>
        <div className="p-4 md:p-6 border-b border-white/10">
          <h3 className="text-white font-semibold text-base md:text-lg">Attachments</h3>
          <p className="text-white/60 text-xs mt-1">Add files to your conversation</p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-2 md:space-y-3">
          {attachedFiles.length === 0 ? (
            <p className="text-white/40 text-xs md:text-sm text-center py-8">No files attached</p>
          ) : (
            attachedFiles.map((file, idx) => (
              <div key={idx} className="p-2 md:p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition">
                <div className="flex items-center gap-2">
                  {file.type === 'image' ? (
                    <img src={file.data} alt={file.name} className="w-6 md:w-8 h-6 md:h-8 rounded object-cover" />
                  ) : (
                    <div className="w-6 md:w-8 h-6 md:h-8 bg-red-500/20 rounded flex items-center justify-center text-red-400 text-xs font-bold">PDF</div>
                  )}
                  <span className="text-white/80 text-xs truncate flex-1">{file.name}</span>
                  <button onClick={() => removeAttachment(idx)} className="text-white/40 hover:text-white/80">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative z-10 w-full">
        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="text-center max-w-2xl px-4">
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">Hi {userName},</h2>
                <p className="text-lg md:text-xl lg:text-2xl text-white/80 mb-8 md:mb-12">what should we dive into today?</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4 max-w-2xl mb-8">
                  {[
                    { icon: '🌾', title: 'Crop Selection', desc: 'Get crop recommendations' },
                    { icon: '🧪', title: 'Fertilizer Guide', desc: 'Fertilizer recommendations' },
                    { icon: '🔍', title: 'Disease Detection', desc: 'Identify plant diseases' },
                    { icon: '🌤️', title: 'Weather Advice', desc: 'Weather-based guidance' },
                    { icon: '📊', title: 'Yield Prediction', desc: 'Predict crop yield' },
                    { icon: '💧', title: 'Soil Analysis', desc: 'Soil health insights' },
                  ].map((item, i) => (
                    <button
                      key={i}
                      onClick={() => setInputText(item.desc)}
                      className="p-3 md:p-4 bg-white/5 hover:bg-white/10 backdrop-blur-md rounded-lg md:rounded-xl text-left transition border border-white/20 hover:border-white/40 group"
                    >
                      <div className="text-2xl md:text-3xl mb-2 group-hover:scale-110 transition">{item.icon}</div>
                      <div className="font-semibold text-white text-xs md:text-sm">{item.title}</div>
                      <div className="text-xs text-white/60">{item.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3 md:space-y-4 max-w-4xl mx-auto w-full">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs sm:max-w-sm md:max-w-2xl px-3 md:px-5 py-2 md:py-3 rounded-lg md:rounded-2xl backdrop-blur-md text-sm md:text-base ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-br-none'
                        : 'bg-white/10 text-white rounded-bl-none border border-white/20'
                    }`}
                  >
                    <div className="flex items-start gap-2 md:gap-3">
                      {message.role === 'assistant' && (
                        <span className="text-lg md:text-xl flex-shrink-0 mt-0.5">
                          {getFeatureIcon(message.feature)}
                        </span>
                      )}
                      <div className="flex-1">
                        <p className="text-xs md:text-sm leading-relaxed">{message.content}</p>
                        {message.attachments && message.attachments.length > 0 && (
                          <div className="mt-2 md:mt-3 flex flex-wrap gap-2">
                            {message.attachments.map((att, idx) => (
                              <div key={idx} className="relative">
                                {att.type === 'image' && att.data ? (
                                  <img
                                    src={att.data}
                                    alt={att.name}
                                    className="max-w-xs max-h-48 rounded-lg border border-white/20"
                                  />
                                ) : (
                                  <div className="px-2 md:px-3 py-1 md:py-2 bg-white/10 rounded-lg border border-white/20 text-xs text-white/80">
                                    📄 {att.name}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {message.role === 'assistant' && (
                      <div className="flex gap-2 md:gap-3 mt-2 md:mt-3 pt-2 md:pt-3 border-t border-white/10">
                        <button
                          onClick={() => speakText(message.content)}
                          className="text-xs opacity-70 hover:opacity-100 flex items-center gap-1 transition text-white/80 hover:text-white"
                        >
                          <Volume2 className="w-3 h-3" /> Speak
                        </button>
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="text-xs opacity-70 hover:opacity-100 flex items-center gap-1 transition text-white/80 hover:text-white"
                        >
                          <Copy className="w-3 h-3" /> Copy
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 text-white px-3 md:px-5 py-2 md:py-3 rounded-lg md:rounded-2xl rounded-bl-none border border-white/20">
                    <Loader className="w-5 h-5 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-gradient-to-t from-blue-950/60 to-transparent backdrop-blur-md border-t border-white/10 p-3 md:p-4 lg:p-6">
          <div className="max-w-4xl mx-auto">
            {attachedFiles.length > 0 && (
              <div className="mb-3 md:mb-4 flex flex-wrap gap-2">
                {attachedFiles.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 px-2 md:px-3 py-1 md:py-2 bg-white/10 rounded-lg border border-white/20 text-xs md:text-sm"
                  >
                    {file.type === 'image' ? (
                      <img
                        src={file.data}
                        alt={file.name}
                        className="w-6 md:w-8 h-6 md:h-8 rounded object-cover"
                      />
                    ) : (
                      <div className="w-6 md:w-8 h-6 md:h-8 bg-red-500/20 rounded flex items-center justify-center text-red-400 text-xs font-bold">
                        PDF
                      </div>
                    )}
                    <span className="text-white/80 truncate max-w-xs">
                      {file.name}
                    </span>
                    <button
                      onClick={() => removeAttachment(idx)}
                      className="ml-auto text-white/40 hover:text-white/80"
                    >
                      <X className="w-3 md:w-4 h-3 md:h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-2 md:gap-3 items-center flex-wrap md:flex-nowrap">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept="image/*,.pdf"
                multiple
                className="hidden"
              />

              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2 md:p-3 bg-white/10 hover:bg-white/20 text-white rounded-full transition flex items-center justify-center border border-white/20 hover:border-white/40"
                title="Upload file"
              >
                <Paperclip className="w-4 md:w-5 h-4 md:h-5" />
              </button>

              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Message KisanSathi..."
                className="flex-1 px-3 md:px-5 py-2 md:py-3 bg-white/10 text-white rounded-full focus:ring-2 focus:ring-green-400 focus:border-transparent placeholder-white/40 border border-white/20 focus:bg-white/15 transition text-sm md:text-base"
              />

              <button
                onClick={isListening ? stopListening : startListening}
                className={`p-2 md:p-3 rounded-full font-semibold transition flex items-center justify-center ${
                  isListening
                    ? 'bg-red-500/80 text-white hover:bg-red-600'
                    : 'bg-white/20 text-white hover:bg-white/30 border border-white/20'
                }`}
              >
                <Mic className="w-4 md:w-5 h-4 md:h-5" />
              </button>

              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() && attachedFiles.length === 0 || isLoading}
                className="p-2 md:p-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full hover:brightness-110 disabled:from-gray-600 disabled:to-gray-600 transition flex items-center justify-center"
              >
                <Send className="w-4 md:w-5 h-4 md:h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Recent Conversations (Hidden on mobile) */}
      <div className={`hidden lg:flex lg:w-72 transition-all duration-300 bg-blue-950/40 backdrop-blur-md border-l border-white/10 flex-col overflow-hidden`}>
        <div className="p-4 md:p-6 border-b border-white/10">
          <h3 className="text-white font-semibold text-base md:text-lg">Recent</h3>
          <p className="text-white/60 text-xs mt-1">Keep talking to KisanSathi</p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-2 md:space-y-3">
          {conversations.length === 0 ? (
            <div className="text-white/40 text-xs md:text-sm text-center py-8">
              <p>No conversations yet</p>
              <button
                onClick={startNewConversation}
                className="mt-4 px-3 md:px-4 py-1 md:py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-xs font-semibold transition border border-green-500/30"
              >
                Start New Chat
              </button>
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => loadConversation(conv.id)}
                className={`w-full text-left px-3 md:px-4 py-2 md:py-3 rounded-lg transition flex items-center gap-2 md:gap-3 group text-sm ${
                  currentConversationId === conv.id
                    ? 'bg-green-500/20 border border-green-500/30'
                    : 'bg-white/5 border border-white/10 hover:bg-white/10'
                }`}
              >
                <MessageCircle className="w-3 md:w-4 h-3 md:h-4 flex-shrink-0 text-white/60 group-hover:text-white/80" />
                <div className="flex-1 min-w-0">
                  <p className="text-white/80 text-xs md:text-sm truncate group-hover:text-white">{conv.title}</p>
                  <p className="text-white/40 text-xs">{conv.timestamp.toLocaleDateString()}</p>
                </div>
                <ChevronRight className="w-3 md:w-4 h-3 md:h-4 text-white/40 group-hover:text-white/80 flex-shrink-0" />
              </button>
            ))
          )}
        </div>

        <div className="p-3 md:p-4 border-t border-white/10">
          <button
            onClick={startNewConversation}
            className="w-full px-3 md:px-4 py-2 md:py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-semibold text-xs md:text-sm hover:brightness-110 transition flex items-center justify-center gap-2"
          >
            <Plus className="w-3 md:w-4 h-3 md:h-4" /> New Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default UnifiedChatbot;
