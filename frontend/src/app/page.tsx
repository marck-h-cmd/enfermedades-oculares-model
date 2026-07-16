"use client";
import React, { useState, useEffect } from 'react';
import { translations } from '../i18n/translations';

// Importar Componentes
import ThemeToggle from '../components/ThemeToggle';
import LanguageSelector from '../components/LanguageSelector';
import ChatbotWidget from '../components/ChatbotWidget';
import DiagnosticTab from '../components/DiagnosticTab';
import AnalyticsTab from '../components/AnalyticsTab';
import StatsTab from '../components/StatsTab';
import ReportsTab from '../components/ReportsTab';

// SVG Icons
const Activity = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const BarChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

const SlidersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="4" y1="21" x2="4" y2="14" />
    <line x1="4" y1="10" x2="4" y2="3" />
    <line x1="12" y1="21" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12" y2="3" />
    <line x1="20" y1="21" x2="20" y2="16" />
    <line x1="20" y1="12" x2="20" y2="3" />
    <line x1="2" y1="14" x2="6" y2="14" />
    <line x1="10" y1="8" x2="14" y2="8" />
    <line x1="18" y1="16" x2="22" y2="16" />
  </svg>
);

const FileTextIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="10" y1="13" x2="14" y2="13" />
    <line x1="10" y1="17" x2="14" y2="17" />
    <line x1="10" y1="9" x2="12" y2="9" />
  </svg>
);

const LogOutIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

const CheckCircle2 = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="m9 11 3 3 6-6" />
  </svg>
);

const ShieldAlert = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l7-2a1 1 0 0 1 .48 0l7 2A1 1 0 0 1 20 6v7z" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const Info = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [language, setLanguage] = useState<'es' | 'en' | 'pt' | 'fr' | 'zh'>('es');
  const [activeTab, setActiveTab] = useState<'diagnostico' | 'analytics' | 'estadisticas' | 'reportes'>('diagnostico');
  const [toasts, setToasts] = useState<{ id: number; message: string; type: 'success' | 'error' | 'info' }[]>([]);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    setToken(localStorage.getItem('jwt_token'));
    setUsername(localStorage.getItem('username'));
    const savedLang = localStorage.getItem('language') as 'es' | 'en' | null;
    if (savedLang) setLanguage(savedLang);
  }, []);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const handleLanguageChange = (lang: 'es' | 'en') => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername(null);
    showToast(language === 'es' ? 'Sesión cerrada correctamente.' : 'Successfully logged out.', 'info');
  };

  if (!isMounted) return null; // Previene fallos de hidratación

  const t = translations[language];

  if (!token) {
    return (
      <LoginScreen 
        setToken={(t) => { setToken(t); localStorage.setItem('jwt_token', t); }}
        setUsername={(u) => { setUsername(u); localStorage.setItem('username', u); }}
        showToast={showToast}
        language={language}
        handleLanguageChange={handleLanguageChange}
      />
    );
  }

  return (
    <div className="flex min-height-screen bg-background text-foreground transition-all duration-300">
      {/* Toast Notification Container */}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border backdrop-blur-md transition-all duration-350 transform translate-x-0 ${
              toast.type === 'success' ? 'bg-emerald-950/90 border-emerald-500/30 text-emerald-300' :
              toast.type === 'error' ? 'bg-rose-950/90 border-rose-500/30 text-rose-300' :
              'bg-slate-900/90 border-slate-700/50 text-sky-300'
            }`}
          >
            {toast.type === 'success' && <CheckCircle2 />}
            {toast.type === 'error' && <ShieldAlert />}
            {toast.type === 'info' && <Info />}
            <span className="text-xs font-semibold">{toast.message}</span>
          </div>
        ))}
      </div>

      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-card-border bg-sidebar-bg backdrop-blur-lg flex flex-col justify-between p-5 fixed h-full z-10">
        <div>
          {/* logo header */}
          <div className="flex items-center gap-3.5 mb-8">
            <div className="p-2.5 bg-indigo-650 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center text-white">
              <Activity />
            </div>
            <div>
              <h2 className="font-extrabold text-foreground text-base tracking-tight leading-none">{t.title}</h2>
              <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-500 dark:text-indigo-400 mt-1 block">{t.subtitle}</span>
            </div>
          </div>

          {/* Menú */}
          <nav className="flex flex-col gap-1.5">
            <button 
              onClick={() => setActiveTab('diagnostico')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-xs transition-all duration-200 cursor-pointer ${
                activeTab === 'diagnostico' 
                  ? 'bg-indigo-600/15 text-indigo-650 dark:text-indigo-400 border-l-4 border-indigo-600' 
                  : 'text-foreground/60 hover:bg-foreground/5 hover:text-foreground'
              }`}
            >
              <UploadIcon />
              {t.tabInference}
            </button>

            <button 
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-xs transition-all duration-200 cursor-pointer ${
                activeTab === 'analytics' 
                  ? 'bg-indigo-600/15 text-indigo-650 dark:text-indigo-400 border-l-4 border-indigo-600' 
                  : 'text-foreground/60 hover:bg-foreground/5 hover:text-foreground'
              }`}
            >
              <BarChartIcon />
              {t.tabComparison}
            </button>

            <button 
              onClick={() => setActiveTab('estadisticas')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-xs transition-all duration-200 cursor-pointer ${
                activeTab === 'estadisticas' 
                  ? 'bg-indigo-600/15 text-indigo-650 dark:text-indigo-400 border-l-4 border-indigo-600' 
                  : 'text-foreground/60 hover:bg-foreground/5 hover:text-foreground'
              }`}
            >
              <SlidersIcon />
              {t.tabSignificance}
            </button>

            <button 
              onClick={() => setActiveTab('reportes')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-xs transition-all duration-200 cursor-pointer ${
                activeTab === 'reportes' 
                  ? 'bg-indigo-600/15 text-indigo-650 dark:text-indigo-400 border-l-4 border-indigo-600' 
                  : 'text-foreground/60 hover:bg-foreground/5 hover:text-foreground'
              }`}
            >
              <FileTextIcon />
              {t.tabReports}
            </button>
          </nav>
        </div>

        {/* User profile / settings / LogOut */}
        <div className="border-t border-card-border pt-4 flex flex-col gap-4">
          <div className="flex justify-end items-center px-1">
            <ThemeToggle />
          </div>

          <div className="flex items-center gap-3 bg-card-bg border border-card-border rounded-xl p-3 shadow-sm">
            <div className="w-9 h-9 rounded-full bg-indigo-650/15 border border-indigo-500/20 flex items-center justify-center font-black text-indigo-650 dark:text-indigo-450 text-sm">
              {username?.slice(0, 2).toUpperCase() || 'U'}
            </div>
            <div className="truncate flex-1">
              <p className="text-xs font-bold text-foreground capitalize truncate">{username}</p>
              <span className="text-[9px] text-foreground/50 font-bold uppercase tracking-wide block">
                {language === 'es' ? 'Personal Clínico' : 'Clinical Staff'}
              </span>
            </div>
          </div>

          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-rose-500/25 bg-rose-500/5 hover:bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold text-xs tracking-wider uppercase transition-all duration-200 cursor-pointer"
          >
            <LogOutIcon />
            {t.logout}
          </button>
        </div>
      </aside>

      {/* Main Content Layout Area */}
      <main className="flex-1 ml-64 min-h-screen p-8 relative flex flex-col justify-between z-0">
        {/* Background gradient decorative blobs */}
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/5 dark:bg-indigo-600/3 rounded-full blur-[120px] pointer-events-none z-0"></div>
        <div className="absolute bottom-1/4 left-10 w-[400px] h-[400px] bg-pink-600/5 dark:bg-pink-600/3 rounded-full blur-[100px] pointer-events-none z-0"></div>

        <div className="z-10 flex-1">
          {/* Header */}
          <header className="mb-8 flex items-center justify-between border-b border-card-border pb-4">
            <div>
              <div className="flex items-center gap-2 text-[10px] text-foreground/50 font-bold uppercase tracking-wider mb-1">
                <span>{t.title}</span>
                <span>/</span>
                <span className="text-indigo-650 dark:text-indigo-400 capitalize">{activeTab}</span>
              </div>
              <h1 className="text-2xl font-extrabold text-foreground leading-tight">
                {activeTab === 'diagnostico' && t.titleInference}
                {activeTab === 'analytics' && t.titleComparison}
                {activeTab === 'estadisticas' && t.titleSignificance}
                {activeTab === 'reportes' && t.titleReports}
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              <LanguageSelector language={language} setLanguage={handleLanguageChange} />
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-[10px] text-foreground/50 font-bold uppercase tracking-wider">{t.connected}</span>
              </div>
            </div>
          </header>

          {/* Render Active Tab */}
          {activeTab === 'diagnostico' && <DiagnosticTab token={token} showToast={showToast} language={language} />}
          {activeTab === 'analytics' && <AnalyticsTab token={token} showToast={showToast} language={language} />}
          {activeTab === 'estadisticas' && <StatsTab token={token} showToast={showToast} language={language} />}
          {activeTab === 'reportes' && <ReportsTab token={token} showToast={showToast} language={language} />}
        </div>

        {/* Footer */}
        <footer className="z-10 mt-12 border-t border-card-border/50 pt-5 text-center text-[10px] text-foreground/45 font-bold uppercase tracking-wider">
          <p>© {new Date().getFullYear()} OcularDiagnose Clinical Suite. {language === 'es' ? 'Todos los derechos reservados. Desarrollado para análisis clínico avanzado.' : 'All rights reserved. Developed for advanced clinical analysis.'}</p>
        </footer>
      </main>

      {/* Chatbot flotante de ayuda */}
      <ChatbotWidget language={language} token={token} />
    </div>
  );
}

/* ==================== LOGIN SCREEN COMPONENT ==================== */
interface LoginProps {
  setToken: (token: string) => void;
  setUsername: (name: string) => void;
  showToast: (msg: string, type: 'success' | 'error') => void;
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  handleLanguageChange: (lang: 'es' | 'en' | 'pt' | 'fr' | 'zh') => void;
}
function LoginScreen({ setToken, setUsername, showToast, language, handleLanguageChange }: LoginProps) {
  const [userVal, setUserVal] = useState('');
  const [passVal, setPassVal] = useState('');
  const [loading, setLoading] = useState(false);

  const t = translations[language];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userVal || !passVal) {
      showToast(language === 'es' ? 'Por favor, complete todos los campos.' : 'Please, fill in all fields.', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: userVal, password: passVal })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
        setUsername(data.username);
        showToast(language === 'es' ? 'Inicio de sesión exitoso.' : 'Successfully logged in.', 'success');
      } else {
        showToast(data.detail || (language === 'es' ? 'Credenciales inválidas.' : 'Invalid credentials.'), 'error');
      }
    } catch (err) {
      showToast(language === 'es' ? 'Error de conexión con el servidor backend.' : 'Connection error with backend server.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4 relative overflow-hidden transition-all duration-300">
      {/* Background radial effects */}
      <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-indigo-650/5 dark:bg-indigo-650/3 rounded-full blur-[140px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-650/5 dark:bg-purple-650/3 rounded-full blur-[120px] pointer-events-none"></div>

      {/* Floating global controls */}
      <div className="absolute top-5 right-5 flex items-center gap-3">
        <LanguageSelector language={language} setLanguage={handleLanguageChange} />
        <ThemeToggle />
      </div>

      <div className="w-full max-w-md glass-card rounded-3xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex p-3.5 bg-indigo-650 rounded-2xl shadow-xl shadow-indigo-650/30 mb-4 justify-center items-center text-white">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <h2 className="text-2xl font-extrabold text-foreground tracking-tight">{t.title}</h2>
          <p className="text-[10px] text-foreground/50 font-bold uppercase tracking-wider mt-1">{t.loginTitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div>
            <label className="block text-[10px] font-bold text-foreground/60 uppercase mb-2 tracking-wide">{t.username}</label>
            <input 
              type="text"
              value={userVal}
              onChange={e => setUserVal(e.target.value)}
              placeholder="admin"
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-foreground bg-input-bg border border-input-border"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-foreground/60 uppercase mb-2 tracking-wide">{t.password}</label>
            <input 
              type="password"
              value={passVal}
              onChange={e => setPassVal(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-foreground bg-input-bg border border-input-border"
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold tracking-wide text-xs uppercase shadow-xl shadow-indigo-600/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2 cursor-pointer"
          >
            {loading ? t.loggingIn : t.loginBtn}
          </button>
        </form>

        <div className="mt-8 text-center text-[10px] text-foreground/50 font-bold uppercase tracking-wider">
          {t.defaultCredentials}: <span className="text-indigo-600 dark:text-indigo-400">admin / admin</span>
        </div>
      </div>
    </div>
  );
}
