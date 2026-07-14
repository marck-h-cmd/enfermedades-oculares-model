"use client";
import React, { useState, useEffect, useRef } from 'react';
import { translations } from '../i18n/translations';

interface Message {
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
}

interface ChatbotWidgetProps {
  language: 'es' | 'en';
  token: string;
}

export default function ChatbotWidget({ language, token }: ChatbotWidgetProps) {
  const t = translations[language];
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speakResponse, setSpeakResponse] = useState(true);
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Inicializar mensaje de bienvenida
  useEffect(() => {
    setMessages([
      {
        sender: 'bot',
        text: t.chatWelcome,
        timestamp: new Date()
      }
    ]);
  }, [language]);

  // Hacer scroll automático al recibir nuevos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  // Inicializar Web Speech API para reconocimiento de voz
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = language === 'es' ? 'es-ES' : 'en-US';
      
      rec.onstart = () => {
        setIsListening(true);
      };
      
      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };
      
      rec.onerror = () => {
        setIsListening(false);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = rec;
    }
  }, [language]);

  const handleMicToggle = () => {
    if (!recognitionRef.current) {
      alert(language === 'es' ? 'Reconocimiento de voz no soportado en este navegador.' : 'Speech recognition not supported in this browser.');
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;
    
    // Agregar mensaje del usuario
    const userMsg: Message = { sender: 'user', text, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: text, language })
      });
      const data = await res.json();
      
      if (res.ok) {
        const botMsg: Message = { sender: 'bot', text: data.response, timestamp: new Date() };
        setMessages(prev => [...prev, botMsg]);
        
        // Síntesis de voz (Text-to-Speech)
        if (speakResponse) {
          speakText(data.response);
        }
      } else {
        setMessages(prev => [...prev, { 
          sender: 'bot', 
          text: language === 'es' ? 'Error al contactar con el chatbot clínico.' : 'Error contacting the clinical chatbot.', 
          timestamp: new Date() 
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: language === 'es' ? 'Error de conexión con el servidor.' : 'Server connection error.', 
        timestamp: new Date() 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Cancelar locución previa
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'es' ? 'es-ES' : 'en-US';
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end">
      {/* Ventana de chat */}
      {isOpen && (
        <div className="w-96 h-[500px] glass-card rounded-3xl shadow-2xl flex flex-col mb-4 overflow-hidden border border-card-border animate-fade-in">
          {/* Header */}
          <div className="bg-indigo-600 px-5 py-4 flex items-center justify-between text-white">
            <div className="flex items-center gap-3.5">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center font-bold text-sm">
                💬
              </div>
              <div>
                <h3 className="font-extrabold text-sm tracking-tight">{t.chatTitle}</h3>
                <span className="text-[9px] uppercase font-bold tracking-widest text-indigo-200">AI Assistant</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Toggle de Altavoz */}
              <button 
                onClick={() => setSpeakResponse(!speakResponse)}
                className={`p-1.5 rounded-lg hover:bg-white/10 transition-all cursor-pointer ${speakResponse ? 'text-emerald-300' : 'text-gray-300'}`}
                title={speakResponse ? t.chatVoiceResponse : t.chatVoiceResponseOff}
              >
                {speakResponse ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><line x1="22" y1="9" x2="16" y2="15"/><line x1="16" y1="9" x2="22" y2="15"/></svg>
                )}
              </button>

              <button 
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white font-bold text-lg p-1 cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Historial de mensajes */}
          <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3.5 bg-background/30">
            {messages.map((msg, idx) => (
              <div 
                key={idx} 
                className={`flex flex-col max-w-[80%] ${msg.sender === 'user' ? 'self-end items-end' : 'self-start items-start'}`}
              >
                <div 
                  className={`px-4 py-2.5 rounded-2xl text-xs font-semibold leading-relaxed ${
                    msg.sender === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : 'bg-card-bg border border-card-border text-foreground rounded-tl-none shadow-sm'
                  }`}
                >
                  {msg.text}
                </div>
                <span className="text-[9px] text-gray-500 mt-1 font-medium">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
            {loading && (
              <div className="self-start flex flex-col items-start max-w-[80%]">
                <div className="px-4 py-2.5 bg-card-bg border border-card-border rounded-2xl rounded-tl-none flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Panel */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="border-t border-card-border p-3 flex gap-2 bg-card-bg/50 backdrop-blur-md"
          >
            <input 
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={t.chatInputPlaceholder}
              className="flex-1 px-4 py-2 text-xs rounded-xl glass-input text-foreground"
            />
            
            {/* Botón Micrófono (Voz) */}
            <button
              type="button"
              onClick={handleMicToggle}
              className={`p-2 rounded-xl transition-all cursor-pointer ${
                isListening 
                  ? 'bg-rose-500 text-white animate-pulse' 
                  : 'bg-card-bg border border-card-border text-foreground hover:bg-foreground/5'
              }`}
              title={isListening ? t.chatMicOn : t.chatMicOff}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
              </svg>
            </button>

            {/* Botón Enviar */}
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white p-2 rounded-xl transition-all cursor-pointer flex items-center justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </form>
        </div>
      )}

      {/* Botón Flotante para abrir/cerrar */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-2xl flex items-center justify-center cursor-pointer transition-all hover:scale-105 active:scale-95 duration-200"
      >
        {isOpen ? (
          <span className="text-xl">✕</span>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )}
      </button>
    </div>
  );
}
