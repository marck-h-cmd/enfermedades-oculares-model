import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

// Helper SVG Icons to replace lucide-react and prevent bundler resolution issues
export const Activity = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

export const Upload = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

export const FileText = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="10" y1="13" x2="14" y2="13" />
    <line x1="10" y1="17" x2="14" y2="17" />
    <line x1="10" y1="9" x2="12" y2="9" />
  </svg>
);

export const BarChart2 = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

export const Sliders = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
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

export const LogOut = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

export const ShieldAlert = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l7-2a1 1 0 0 1 .48 0l7 2A1 1 0 0 1 20 6v7z" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

export const Loader2 = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

export const Download = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

export const CheckCircle2 = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10" />
    <path d="m9 11 3 3 6-6" />
  </svg>
);

export const Info = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);

export const Compass = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10" />
    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
  </svg>
);

export const Database = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
  </svg>
);

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('jwt_token'));
  const [username, setUsername] = useState<string | null>(localStorage.getItem('username'));
  const [activeTab, setActiveTab] = useState<'diagnostico' | 'analytics' | 'estadisticas' | 'reportes'>('diagnostico');
  const [toasts, setToasts] = useState<{ id: number; message: string; type: 'success' | 'error' | 'info' }[]>([]);

  // Función para lanzar notificaciones toast
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername(null);
    showToast('Sesión cerrada correctamente.', 'info');
  };

  if (!token) {
    return <LoginScreen setToken={setToken} setUsername={setUsername} showToast={showToast} />;
  }

  return (
    <div className="flex min-height-screen bg-dark-bg text-gray-200">
      {/* Toast Notification Container */}
      <div className="fixed top-5 right-5 z-50 flex flex-col gap-2">
        {toasts.map(t => (
          <div 
            key={t.id} 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border backdrop-blur-md transition-all duration-300 transform translate-x-0 ${
              t.type === 'success' ? 'bg-emerald-950/80 border-emerald-500/30 text-emerald-300' :
              t.type === 'error' ? 'bg-rose-950/80 border-rose-500/30 text-rose-300' :
              'bg-slate-900/80 border-slate-700/50 text-sky-300'
            }`}
          >
            {t.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
            {t.type === 'error' && <ShieldAlert className="w-5 h-5 text-rose-400" />}
            {t.type === 'info' && <Info className="w-5 h-5 text-sky-400" />}
            <span className="text-sm font-medium">{t.message}</span>
          </div>
        ))}
      </div>

      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-dark-border bg-slate-950/40 backdrop-blur-lg flex flex-col justify-between p-5 fixed h-full z-10">
        <div>
          {/* Hospital Header Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <h2 className="font-extrabold text-white text-lg tracking-tight leading-none">OcularDiagnose</h2>
              <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400">Clinical Suite</span>
            </div>
          </div>

          <nav className="flex flex-col gap-1.5">
            <button 
              onClick={() => setActiveTab('diagnostico')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'diagnostico' 
                  ? 'bg-indigo-600/15 text-indigo-300 border-l-4 border-indigo-500' 
                  : 'text-gray-400 hover:bg-slate-900/55 hover:text-gray-200'
              }`}
            >
              <Upload className="w-4 h-4" />
              Centro de Inferencia
            </button>

            <button 
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'analytics' 
                  ? 'bg-indigo-600/15 text-indigo-300 border-l-4 border-indigo-500' 
                  : 'text-gray-400 hover:bg-slate-900/55 hover:text-gray-200'
              }`}
            >
              <BarChart2 className="w-4 h-4" />
              Análisis Comparativo
            </button>

            <button 
              onClick={() => setActiveTab('estadisticas')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'estadisticas' 
                  ? 'bg-indigo-600/15 text-indigo-300 border-l-4 border-indigo-500' 
                  : 'text-gray-400 hover:bg-slate-900/55 hover:text-gray-200'
              }`}
            >
              <Sliders className="w-4 h-4" />
              Significancia
            </button>

            <button 
              onClick={() => setActiveTab('reportes')}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'reportes' 
                  ? 'bg-indigo-600/15 text-indigo-300 border-l-4 border-indigo-500' 
                  : 'text-gray-400 hover:bg-slate-900/55 hover:text-gray-200'
              }`}
            >
              <FileText className="w-4 h-4" />
              Exportar Reportes
            </button>
          </nav>
        </div>

        {/* User profile / LogOut */}
        <div className="border-t border-dark-border pt-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-dark-border flex items-center justify-center font-bold text-indigo-400">
              U
            </div>
            <div>
              <p className="text-sm font-bold text-white capitalize">{username}</p>
              <span className="text-[10px] text-gray-500 font-semibold uppercase">Clínico</span>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl border border-rose-500/25 bg-rose-950/10 hover:bg-rose-950/20 text-rose-400 font-bold text-xs tracking-wider uppercase transition-all duration-200"
          >
            <LogOut className="w-3.5 h-3.5" />
            Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content Layout Area */}
      <main className="flex-1 ml-64 min-h-screen p-8 relative flex flex-col justify-between">
        {/* Background gradient decorative blobs */}
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/5 rounded-full blur-[120px] pointer-events-none z-0"></div>
        <div className="absolute bottom-1/4 left-10 w-[400px] h-[400px] bg-pink-600/5 rounded-full blur-[100px] pointer-events-none z-0"></div>

        <div className="z-10 flex-1">
          {/* Breadcrumbs Navigation Headers */}
          <header className="mb-8 flex items-center justify-between border-b border-dark-border/50 pb-4">
            <div>
              <div className="flex items-center gap-2 text-xs text-gray-500 font-bold uppercase tracking-wider mb-1">
                <span>OcularDiagnose</span>
                <span>/</span>
                <span className="text-indigo-400 capitalize">{activeTab}</span>
              </div>
              <h1 className="text-2xl font-extrabold text-white leading-tight">
                {activeTab === 'diagnostico' && '🔬 Centro Clínico de Inferencia'}
                {activeTab === 'analytics' && '📊 Rendimiento y Análisis Comparativo'}
                {activeTab === 'estadisticas' && '🔬 Pruebas de Significancia Estadística'}
                {activeTab === 'reportes' && '📂 Centro de Descarga de Reportes'}
              </h1>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-xs text-gray-400 font-semibold">Servidor API Conectado</span>
            </div>
          </header>

          {/* Router Tab Views */}
          {activeTab === 'diagnostico' && <DiagnosticTab token={token} showToast={showToast} />}
          {activeTab === 'analytics' && <AnalyticsTab token={token} showToast={showToast} />}
          {activeTab === 'estadisticas' && <StatsTab token={token} showToast={showToast} />}
          {activeTab === 'reportes' && <ReportsTab token={token} showToast={showToast} />}
        </div>

        {/* Footer */}
        <footer className="z-10 mt-12 border-t border-dark-border/50 pt-5 text-center text-xs text-gray-500 font-medium">
          <p>© {new Date().getFullYear()} OcularDiagnose Clinical Suite. Todos los derechos reservados. Desarrollado para análisis clínico avanzado.</p>
        </footer>
      </main>
    </div>
  );
}

/* ==================== LOGIN SCREEN COMPONENT ==================== */
interface LoginProps {
  setToken: (token: string) => void;
  setUsername: (name: string) => void;
  showToast: (msg: string, type: 'success' | 'error') => void;
}
function LoginScreen({ setToken, setUsername, showToast }: LoginProps) {
  const [userVal, setUserVal] = useState('');
  const [passVal, setPassVal] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userVal || !passVal) {
      showToast('Por favor, complete todos los campos.', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: userVal, password: passVal })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('jwt_token', data.access_token);
        localStorage.setItem('username', data.username);
        setToken(data.access_token);
        setUsername(data.username);
        showToast('Inicio de sesión exitoso.', 'success');
      } else {
        showToast(data.detail || 'Credenciales inválidas.', 'error');
      }
    } catch (err) {
      showToast('Error de conexión con el servidor backend.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#04060b] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background radial effects */}
      <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md glass-card rounded-3xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex p-3.5 bg-indigo-600 rounded-2xl shadow-xl shadow-indigo-600/30 mb-4 justify-center items-center">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">OcularDiagnose</h2>
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mt-1">Portal de Acceso Clínico</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 tracking-wide">Usuario</label>
            <input 
              type="text"
              value={userVal}
              onChange={e => setUserVal(e.target.value)}
              placeholder="Ej. admin"
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2 tracking-wide">Contraseña</label>
            <input 
              type="password"
              value={passVal}
              onChange={e => setPassVal(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-white"
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold tracking-wide text-sm shadow-xl shadow-indigo-600/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Validando Acceso...
              </>
            ) : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="mt-8 text-center text-[10px] text-gray-500 font-bold uppercase tracking-wider">
          Credenciales por defecto: <span className="text-indigo-400">admin / admin</span>
        </div>
      </div>
    </div>
  );
}

/* ==================== DIAGNOSTIC TAB COMPONENT ==================== */
interface TabProps {
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}
function DiagnosticTab({ token, showToast }: TabProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [sliderVal, setSliderVal] = useState(50); // Controla el comparador de imágenes (0 a 100)
  const [activeCompareMode, setActiveCompareMode] = useState<'clahe' | 'gradcam'>('gradcam');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handlePredict = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${BACKEND_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
        showToast('Diagnóstico computado con éxito.', 'success');
      } else {
        showToast(data.detail || 'Error procesando la imagen ocular.', 'error');
      }
    } catch (err) {
      showToast('Error de conexión con el backend de inferencia.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 z-10">
      {/* Left panel: upload & action */}
      <div className="xl:col-span-5 flex flex-col gap-6">
        <div 
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="glass-card rounded-3xl p-8 border-dashed border-2 border-slate-700/60 hover:border-indigo-500/50 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 aspect-square group"
          onClick={() => document.getElementById('file-upload-input')?.click()}
        >
          <input 
            type="file" 
            id="file-upload-input" 
            className="hidden" 
            accept="image/*"
            onChange={handleFileChange}
          />
          {imagePreview ? (
            <img 
              src={imagePreview} 
              alt="Preview" 
              className="w-full h-full object-cover rounded-2xl shadow-lg border border-dark-border"
            />
          ) : (
            <div className="flex flex-col items-center">
              <div className="p-4 bg-slate-900 rounded-full mb-4 border border-dark-border group-hover:scale-110 group-hover:bg-indigo-650/15 group-hover:text-indigo-400 transition-all duration-300">
                <Upload className="w-8 h-8 text-gray-400 group-hover:text-indigo-400" />
              </div>
              <p className="text-base font-bold text-white mb-1">Arrastre una Imagen Ocular</p>
              <p className="text-xs text-gray-500 font-semibold mb-4">O haga clic para explorar archivos</p>
              <span className="px-3.5 py-1.5 bg-slate-900 border border-dark-border rounded-lg text-[10px] font-bold tracking-wider text-gray-400 uppercase group-hover:border-indigo-500/30">Formatos: JPG, PNG, BMP</span>
            </div>
          )}
        </div>

        {selectedFile && (
          <button 
            onClick={handlePredict}
            disabled={loading}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold tracking-wide text-sm shadow-xl shadow-indigo-600/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Ejecutando Modelos & Grad-CAM...
              </>
            ) : 'Iniciar Diagnóstico de Consenso'}
          </button>
        )}
      </div>

      {/* Right panel: Results */}
      <div className="xl:col-span-7 flex flex-col gap-6">
        {loading && (
          <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px]">
            <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
            <p className="text-base font-bold text-white">Analizando retina...</p>
            <p className="text-xs text-gray-500 font-semibold mt-1">Ejecutando MobileNet, ResNet, EfficientNet, Fusion y Grad-CAM</p>
            <div className="w-48 bg-slate-800 h-1 rounded-full overflow-hidden mt-5 border border-dark-border/40">
              <div className="bg-indigo-500 h-full animate-[loading-bar_1.5s_infinite]"></div>
            </div>
          </div>
        )}

        {!loading && !result && (
          <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px] text-center border-dashed border border-dark-border">
            <Compass className="w-12 h-12 text-slate-600 mb-4" />
            <p className="text-base font-bold text-gray-400">Esperando imagen ocular</p>
            <p className="text-xs text-gray-500 max-w-xs mt-1">Cargue una imagen de fondo de ojo a la izquierda para procesar las clasificaciones diagnósticas.</p>
          </div>
        )}

        {!loading && result && (
          <div className="flex flex-col gap-6">
            {/* Visual comparison Slider (CLAHE vs GradCAM) */}
            <div className="glass-card rounded-3xl p-5 flex flex-col gap-4">
              <div className="flex justify-between items-center border-b border-dark-border pb-3">
                <h3 className="font-bold text-white text-sm uppercase tracking-wide">🔬 Visualizador Retinal Interactivo</h3>
                <div className="flex bg-slate-900 border border-dark-border p-1 rounded-xl gap-1">
                  <button 
                    onClick={() => setActiveCompareMode('gradcam')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      activeCompareMode === 'gradcam' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    Grad-CAM
                  </button>
                  <button 
                    onClick={() => setActiveCompareMode('clahe')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      activeCompareMode === 'clahe' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    Filtro CLAHE
                  </button>
                </div>
              </div>

              {/* Slider image component */}
              <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-dark-border flex items-center justify-center bg-slate-950">
                <img 
                  src={result.imagenes.original} 
                  alt="Original" 
                  className="absolute inset-0 w-full h-full object-cover"
                />
                
                <div 
                  className="absolute inset-0 w-full h-full object-cover overflow-hidden"
                  style={{ clipPath: `polygon(${sliderVal}% 0, 100% 0, 100% 100%, ${sliderVal}% 100%)` }}
                >
                  <img 
                    src={activeCompareMode === 'gradcam' ? result.imagenes.gradcam : result.imagenes.clahe} 
                    alt="Processed" 
                    className="absolute inset-0 w-full h-full object-cover"
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>

                {/* Vertical slider control */}
                <div 
                  className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)] z-10 cursor-ew-resize"
                  style={{ left: `${sliderVal}%` }}
                >
                  <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white text-slate-900 border-2 border-indigo-600 shadow-xl flex items-center justify-center font-bold text-xs pointer-events-none select-none">
                    ↔
                  </div>
                </div>

                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={sliderVal}
                  onChange={e => setSliderVal(Number(e.target.value))}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
                />

                {/* Dynamic Label Overlays */}
                <span className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-bold text-white tracking-wider uppercase select-none border border-white/5">
                  Original
                </span>
                <span className="absolute bottom-3 right-3 bg-indigo-600/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-bold text-white tracking-wider uppercase select-none border border-indigo-400/20">
                  {activeCompareMode === 'gradcam' ? 'Grad-CAM' : 'CLAHE'}
                </span>
              </div>
              <p className="text-[10px] text-gray-500 text-center font-medium italic">
                {activeCompareMode === 'gradcam' ? 'El mapa de calor rojo indica las anomalías en las que el modelo enfocó el diagnóstico.' : 'CLAHE realza los contrastes de los vasos sanguíneos y lesiones retinales.'}
              </p>
            </div>

            {/* Histograma antes/después de CLAHE */}
            {result.histogramas && (
              <div className="glass-card rounded-3xl p-5 flex flex-col gap-4">
                <h3 className="font-bold text-white text-sm uppercase tracking-wide border-b border-dark-border pb-3">📊 Histograma de Luminancia (Original vs CLAHE)</h3>
                <div className="aspect-[21/9] w-full">
                  <Line 
                    data={{
                      labels: result.histogramas.bins,
                      datasets: [
                        {
                          label: 'Luminancia Original',
                          data: result.histogramas.original,
                          borderColor: 'rgba(156, 163, 175, 0.7)',
                          backgroundColor: 'rgba(156, 163, 175, 0.08)',
                          borderWidth: 2,
                          pointRadius: 1,
                          fill: true,
                          tension: 0.4
                        },
                        {
                          label: 'Luminancia CLAHE (Ecualizada)',
                          data: result.histogramas.clahe,
                          borderColor: 'rgb(99, 102, 241)',
                          backgroundColor: 'rgba(99, 102, 241, 0.08)',
                          borderWidth: 2,
                          pointRadius: 1,
                          fill: true,
                          tension: 0.4
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: { 
                        y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } } },
                        x: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 8 } } }
                      },
                      plugins: {
                        legend: { labels: { color: '#e5e7eb', font: { size: 10 } } }
                      }
                    }}
                  />
                </div>
                <p className="text-[10px] text-gray-500 text-center font-medium italic">
                  Muestra la distribución de frecuencias de los niveles de brillo. CLAHE redistribuye las intensidades para mejorar el contraste local.
                </p>
              </div>
            )}

            {/* Diagnostic Details */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className={`inline-flex px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-widest border mb-2 ${
                    result.diagnostico_principal.gravedad === 'Alta' ? 'bg-rose-950/40 border-rose-500/30 text-rose-300' :
                    result.diagnostico_principal.gravedad === 'Moderada' ? 'bg-amber-950/40 border-amber-500/30 text-amber-300' :
                    'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                  }`}>
                    Severidad: {result.diagnostico_principal.gravedad}
                  </span>
                  <h3 className="text-xl font-extrabold text-white">{result.diagnostico_principal.clase_nombre}</h3>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-gray-500 font-bold uppercase block mb-1">Confianza</span>
                  <span className="text-2xl font-black text-indigo-400">{(result.diagnostico_principal.confianza * 100).toFixed(2)}%</span>
                </div>
              </div>

              <div className="bg-slate-900/40 border border-dark-border/40 rounded-2xl p-4 text-sm text-gray-300 leading-relaxed">
                {result.diagnostico_principal.descripcion}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900/30 border border-dark-border/30 rounded-2xl">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wide block mb-1">Tratamiento Clínico</span>
                  <p className="text-xs text-gray-300 font-semibold leading-relaxed">{result.diagnostico_principal.tratamiento}</p>
                </div>
                <div className="p-4 bg-slate-900/30 border border-dark-border/30 rounded-2xl">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wide block mb-1">Pronóstico Ocular</span>
                  <p className="text-xs text-gray-300 font-semibold leading-relaxed">{result.diagnostico_principal.pronostico}</p>
                </div>
              </div>
            </div>

            {/* Barras de probabilidad del diagnóstico (8 Clases) */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <h4 className="font-bold text-white text-sm uppercase tracking-wide border-b border-dark-border pb-3">Distribución de Probabilidades de Diagnóstico (8 Clases)</h4>
              <div className="flex flex-col gap-3">
                {Object.entries(result.modelos.champion.probabilidades_completas)
                  .sort((a: any, b: any) => b[1] - a[1]) // Ordenar de mayor a menor
                  .map(([claseId, prob]: any) => {
                    const nombreClase = 
                      claseId === 'ageDegeneration' ? 'Degeneración Macular (AMD)' :
                      claseId === 'cataract' ? 'Catarata' :
                      claseId === 'diabetes' ? 'Retinopatía Diabética' :
                      claseId === 'glaucoma' ? 'Glaucoma' :
                      claseId === 'hypertension' ? 'Retinopatía Hipertensiva' :
                      claseId === 'myopia' ? 'Miopía Patológica' :
                      claseId === 'normal' ? 'Ojo Sano / Normal' : 'Otras Patologías';
                    
                    return (
                      <div key={claseId}>
                        <div className="flex justify-between items-center text-xs font-semibold mb-1">
                          <span className="text-gray-300">{nombreClase}</span>
                          <span className="text-indigo-400 font-bold">{(prob * 100).toFixed(2)}%</span>
                        </div>
                        <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-dark-border/40">
                          <div 
                            className="bg-gradient-to-r from-indigo-500 to-indigo-650 h-full rounded-full transition-all duration-1000 ease-out" 
                            style={{ width: `${prob * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* Model grid comparisons */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <h4 className="font-bold text-white text-sm uppercase tracking-wide border-b border-dark-border pb-3">Comparativa por Arquitectura</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(result.modelos).map(([modelKey, modelInfo]: any) => (
                  <div key={modelKey} className="p-4 bg-slate-950/40 border border-dark-border/60 rounded-2xl flex flex-col justify-between">
                    <div>
                      <span className="text-[10px] text-gray-500 font-extrabold uppercase tracking-wider block mb-1">
                        {modelKey === 'mobilenet' ? 'MobileNetV2' :
                         modelKey === 'resnet' ? 'ResNet50V2' :
                         modelKey === 'efficientnet' ? 'EfficientNetV2-B0' :
                         modelKey === 'ensemble' ? 'Ensemble Consenso' : 'Champion CV'}
                      </span>
                      <p className="text-sm font-bold text-white truncate">{modelInfo.clase_nombre}</p>
                    </div>
                    
                    <div className="mt-3">
                      <div className="flex justify-between items-center text-[10px] font-semibold text-gray-400 mb-1">
                        <span>Confianza</span>
                        <span>{(modelInfo.confianza * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden border border-dark-border/40">
                        <div 
                          className="bg-indigo-500 h-full rounded-full" 
                          style={{ width: `${modelInfo.confianza * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ==================== ANALYTICS TAB COMPONENT ==================== */
function AnalyticsTab({ token, showToast }: TabProps) {
  const [loading, setLoading] = useState(true);
  const [modelsData, setModelsData] = useState<any[]>([]);
  const [rawResults, setRawResults] = useState<any>(null);

  // Selector states
  const [selectedModelId, setSelectedModelId] = useState<string>('fusion_net');
  const [selectedRocClass, setSelectedRocClass] = useState<string>('cataract');

  useEffect(() => {
    const fetchModelsAndResults = async () => {
      try {
        const resModels = await fetch(`${BACKEND_URL}/api/models`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dataModels = await resModels.json();

        const resResults = await fetch(`${BACKEND_URL}/api/models/results`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dataResults = await resResults.json();

        if (resModels.ok && resResults.ok) {
          setModelsData(dataModels);
          setRawResults(dataResults);
          // Auto select first available key in results
          const keys = Object.keys(dataResults);
          if (keys.length > 0) {
            setSelectedModelId(keys[0]);
          }
        } else {
          showToast('Error cargando métricas e históricos.', 'error');
        }
      } catch (err) {
        showToast('Error conectando al backend de análisis.', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchModelsAndResults();
  }, []);

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center min-h-[400px]">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
        <p className="text-sm font-bold text-white">Cargando métricas de validación...</p>
      </div>
    );
  }

  // 1. Configuración de Gráficos de Métricas Generales
  const labels = modelsData.map(m => m.nombre);
  
  const accuracyChartData = {
    labels,
    datasets: [{
      label: 'Accuracy Promedio (%)',
      data: modelsData.map(m => m.accuracy_media * 100),
      backgroundColor: 'rgba(99, 102, 241, 0.65)',
      borderColor: 'rgb(99, 102, 241)',
      borderWidth: 1,
      borderRadius: 8
    }]
  };

  // 2. Gráfico agrupado de tiempos (Entrenamiento vs Inferencia)
  // Nota: Multiplicamos el tiempo de inferencia (tiempo_medio) por 1000 para graficar en milisegundos
  // y mostramos el tiempo de entrenamiento en pliegues (tiempo de entrenamiento total es la suma de tiempos_folds)
  const timingChartData = {
    labels,
    datasets: [
      {
        label: 'Tiempo de Inferencia (ms)',
        data: modelsData.map(m => m.tiempo_medio * 1000), // de segundos a ms
        backgroundColor: 'rgba(236, 72, 153, 0.7)',
        borderColor: 'rgb(236, 72, 153)',
        borderWidth: 1,
        borderRadius: 6
      },
      {
        label: 'Tiempo de Entren. por Fold (s)',
        data: modelsData.map(m => {
          const rawM = rawResults?.[m.id];
          if (!rawM) return 0;
          const folds = rawM.tiempos_folds || [];
          return folds.length ? (folds.reduce((a: number, b: number) => a + b, 0) / folds.length) : 0;
        }),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        borderRadius: 6
      }
    ]
  };

  // 3. Gráfico de Estabilidad: Accuracy por Fold
  const foldAccuraciesChartData = {
    labels: ['Fold 1', 'Fold 2', 'Fold 3', 'Fold 4', 'Fold 5'],
    datasets: modelsData.map((m) => {
      const color = 
        m.id === 'mobilenet' ? 'rgb(59, 130, 246)' :
        m.id === 'resnet' ? 'rgb(239, 68, 68)' :
        m.id === 'efficientnet' ? 'rgb(16, 185, 129)' :
        m.id === 'fusion_net' ? 'rgb(139, 92, 246)' : 'rgb(236, 72, 153)';
      const raw = rawResults?.[m.id];
      const data = raw ? raw.accuracies_folds.map((v: number) => v * 100) : [];
      return {
        label: m.nombre,
        data,
        borderColor: color,
        backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.3
      };
    })
  };

  // 4. ROC Curve del Modelo y Patología seleccionados
  const getSelectedRocData = () => {
    const raw = rawResults?.[selectedModelId];
    if (!raw || !raw.curvas_roc || !raw.curvas_roc[selectedRocClass]) {
      return { labels: [], datasets: [] };
    }
    const roc = raw.curvas_roc[selectedRocClass];
    // Downsample para rendimiento si es muy grande
    const step = Math.max(1, Math.floor(roc.fpr.length / 50));
    const fprSampled = roc.fpr.filter((_: any, i: number) => i % step === 0);
    const tprSampled = roc.tpr.filter((_: any, i: number) => i % step === 0);
    
    // Asegurar que el final esté incluido
    if (fprSampled[fprSampled.length - 1] !== 1.0) {
      fprSampled.push(1.0);
      tprSampled.push(1.0);
    }

    return {
      labels: fprSampled.map((v: number) => v.toFixed(2)),
      datasets: [
        {
          label: `Curva ROC (AUC = ${roc.auc.toFixed(4)})`,
          data: tprSampled,
          borderColor: 'rgb(139, 92, 246)',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          fill: true,
          borderWidth: 2,
          pointRadius: 1,
          tension: 0.1
        },
        {
          label: 'Línea de Azar (AUC = 0.50)',
          data: fprSampled, // diagonal lineal
          borderColor: 'rgba(255,255,255,0.15)',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false
        }
      ]
    };
  };

  // 5. Renderizar Boxplot personalizado en SVG
  const renderBoxplot = () => {
    if (!rawResults) return null;
    const keys = Object.keys(rawResults);
    if (!keys.length) return null;
    const data = keys.map(key => {
      const accs = rawResults[key].accuracies_folds;
      const sorted = [...accs].sort((a, b) => a - b);
      const min = sorted[0];
      const q1 = sorted[1] !== undefined ? sorted[1] : sorted[0];
      const median = sorted[2] !== undefined ? sorted[2] : sorted[0];
      const q3 = sorted[3] !== undefined ? sorted[3] : sorted[sorted.length - 1];
      const max = sorted[sorted.length - 1];
      return { key, min, q1, median, q3, max };
    });

    const plotMinAcc = 0.50;
    const plotMaxAcc = 0.60;
    const height = 230;
    const width = 450;
    const getX = (index: number) => 60 + index * 80;
    const getY = (acc: number) => {
      const ratio = (acc - plotMinAcc) / (plotMaxAcc - plotMinAcc);
      return height - 40 - ratio * (height - 80);
    };

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full text-gray-400 select-none">
        {/* Líneas horizontales de rejilla */}
        {[0.50, 0.52, 0.54, 0.56, 0.58, 0.60].map(val => (
          <g key={val}>
            <line x1="45" y1={getY(val)} x2={width - 20} y2={getY(val)} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
            <text x="10" y={getY(val) + 4} className="text-[10px] font-bold fill-gray-500">{(val * 100).toFixed(0)}%</text>
          </g>
        ))}

        {/* Cajas y bigotes */}
        {data.map((item, idx) => {
          const x = getX(idx);
          const yMin = getY(item.min);
          const yQ1 = getY(item.q1);
          const yMed = getY(item.median);
          const yQ3 = getY(item.q3);
          const yMax = getY(item.max);
          const boxWidth = 32;

          const displayName = 
            item.key === 'mobilenet' ? 'Mobile' :
            item.key === 'resnet' ? 'ResNet' :
            item.key === 'efficientnet' ? 'EffNet' :
            item.key === 'fusion_net' ? 'Fusión' : 'CNN+RF';

          return (
            <g key={item.key}>
              {/* Bigotes */}
              <line x1={x} y1={yMin} x2={x} y2={yQ1} stroke="#6366f1" strokeWidth="2" strokeDasharray="3,3" />
              <line x1={x} y1={yMax} x2={x} y2={yQ3} stroke="#6366f1" strokeWidth="2" strokeDasharray="3,3" />
              <line x1={x - 8} y1={yMin} x2={x + 8} y2={yMin} stroke="#6366f1" strokeWidth="2" />
              <line x1={x - 8} y1={yMax} x2={x + 8} y2={yMax} stroke="#6366f1" strokeWidth="2" />
              {/* Caja principal */}
              <rect 
                x={x - boxWidth / 2} 
                y={yQ3} 
                width={boxWidth} 
                height={Math.max(2, yQ1 - yQ3)} 
                fill="rgba(99, 102, 241, 0.15)" 
                stroke="#6366f1" 
                strokeWidth="2" 
                rx="4"
              />
              {/* Mediana (Línea rosa brillante) */}
              <line x1={x - boxWidth / 2} y1={yMed} x2={x + boxWidth / 2} y2={yMed} stroke="#ec4899" strokeWidth="3" />
              
              {/* Texto de etiquetas */}
              <text x={x} y={height - 10} textAnchor="middle" className="text-[10px] font-extrabold fill-gray-400">{displayName}</text>
            </g>
          );
        })}
      </svg>
    );
  };

  // 6. Renderizar Radar Chart en SVG
  const renderRadarChart = () => {
    if (!rawResults || !modelsData.length) return null;
    
    const axes = [
      { name: 'Accuracy', getVal: (m: any) => m.accuracy_media / 0.60 },
      { name: 'Velocidad', getVal: (m: any) => Math.max(0.1, 1 - (m.tiempo_medio / 0.8)) }, // Inferencia
      { name: 'F1-Score', getVal: (m: any) => m.f1_score / 0.60 },
      { name: 'Eficiencia', getVal: (m: any) => {
          if (m.id === 'mobilenet') return 0.95;
          if (m.id === 'efficientnet') return 0.85;
          if (m.id === 'cnn_rf') return 0.70;
          if (m.id === 'resnet') return 0.35;
          return 0.20; // fusion_net
        }
      },
      { name: 'Estabilidad', getVal: (m: any) => {
          const std = rawResults[m.id]?.accuracy_std || 0.01;
          return Math.max(0.1, 1 - (std * 30));
        }
      }
    ];

    const center = 150;
    const radius = 80;
    const getCoordinates = (val: number, index: number) => {
      const angle = (index * 2 * Math.PI) / 5 - Math.PI / 2;
      const r = val * radius;
      return {
        x: center + r * Math.cos(angle),
        y: center + r * Math.sin(angle)
      };
    };

    return (
      <svg viewBox="0 0 300 300" className="w-full h-full text-gray-400 select-none">
        {/* Polígonos de rejilla */}
        {[0.2, 0.4, 0.6, 0.8, 1.0].map(level => {
          const points = Array.from({ length: 5 }).map((_, i) => {
            const coord = getCoordinates(level, i);
            return `${coord.x},${coord.y}`;
          }).join(' ');
          return (
            <polygon 
              key={level} 
              points={points} 
              fill="none" 
              stroke="rgba(255,255,255,0.04)" 
              strokeWidth="1" 
            />
          );
        })}

        {/* Ejes radiales */}
        {axes.map((axis, i) => {
          const outer = getCoordinates(1.0, i);
          const labelOffset = getCoordinates(1.22, i);
          return (
            <g key={axis.name}>
              <line x1={center} y1={center} x2={outer.x} y2={outer.y} stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
              <text 
                x={labelOffset.x} 
                y={labelOffset.y + 3} 
                textAnchor="middle" 
                className="text-[9px] font-bold fill-gray-500 uppercase tracking-wide"
              >
                {axis.name}
              </text>
            </g>
          );
        })}

        {/* Polígonos de los modelos */}
        {modelsData.map((m) => {
          const color = 
            m.id === 'mobilenet' ? 'rgb(59, 130, 246)' :
            m.id === 'resnet' ? 'rgb(239, 68, 68)' :
            m.id === 'efficientnet' ? 'rgb(16, 185, 129)' :
            m.id === 'fusion_net' ? 'rgb(139, 92, 246)' : 'rgb(236, 72, 153)';
          
          const rawRes = rawResults[m.id];
          if (!rawRes) return null;
          
          const points = axes.map((axis, i) => {
            const val = Math.min(1.0, Math.max(0.1, axis.getVal(m)));
            const coord = getCoordinates(val, i);
            return `${coord.x},${coord.y}`;
          }).join(' ');

          return (
            <g key={m.id}>
              <polygon 
                points={points} 
                fill={color.replace('rgb', 'rgba').replace(')', ', 0.12)')} 
                stroke={color} 
                strokeWidth="1.5" 
              />
              {axes.map((axis, i) => {
                const val = Math.min(1.0, Math.max(0.1, axis.getVal(m)));
                const coord = getCoordinates(val, i);
                return (
                  <circle 
                    key={i} 
                    cx={coord.x} 
                    cy={coord.y} 
                    r="3" 
                    fill={color} 
                    stroke="#0f172a" 
                    strokeWidth="1" 
                  />
                );
              })}
            </g>
          );
        })}

        {/* Leyenda del Radar */}
        <g transform="translate(5, 280)" className="text-[8px] font-bold">
          {modelsData.map((m, i) => {
            const color = 
              m.id === 'mobilenet' ? 'rgb(59, 130, 246)' :
              m.id === 'resnet' ? 'rgb(239, 68, 68)' :
              m.id === 'efficientnet' ? 'rgb(16, 185, 129)' :
              m.id === 'fusion_net' ? 'rgb(139, 92, 246)' : 'rgb(236, 72, 153)';
            const displayName = 
              m.id === 'mobilenet' ? 'Mobile' :
              m.id === 'resnet' ? 'ResNet' :
              m.id === 'efficientnet' ? 'EffNet' :
              m.id === 'fusion_net' ? 'Fusión' : 'CNN+RF';
            
            return (
              <g key={m.id} transform={`translate(${i * 58}, 0)`}>
                <rect x="0" y="-5" width="6" height="6" fill={color} rx="1" />
                <text x="10" y="1" className="fill-gray-400 font-semibold">{displayName}</text>
              </g>
            );
          })}
        </g>
      </svg>
    );
  };

  // 7. Obtener la matriz de confusión del modelo seleccionado
  const selectedConfusionMatrix = rawResults?.[selectedModelId]?.matriz_confusion || [];

  const ENFERMEDADES_LABELS = [
    'Degeneración (AMD)', 'Catarata', 'Diabetes', 'Glaucoma', 
    'Hipertensión', 'Miopía', 'Normal', 'Otras'
  ];

  return (
    <div className="flex flex-col gap-8 z-10">
      {/* Metrics Cards row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="glass-card rounded-3xl p-6">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4">🎯 Precisión de Modelos en 5-Fold CV</h3>
          <div className="aspect-video w-full">
            <Bar 
              data={accuracyChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                  y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                  x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                }
              }}
            />
          </div>
        </div>

        <div className="glass-card rounded-3xl p-6">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4">⚡ Perfil de Tiempos (Entrenamiento vs Inferencia)</h3>
          <div className="aspect-video w-full">
            <Bar 
              data={timingChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                  y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                  x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                },
                plugins: {
                  legend: { labels: { color: '#9ca3af', font: { size: 10 } } }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Model-specific detail section */}
      <div className="glass-card rounded-3xl p-6 flex flex-col gap-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-dark-border pb-4 gap-4">
          <div>
            <h3 className="font-extrabold text-white text-base">🔍 Inspector de Matriz de Confusión y Curva ROC</h3>
            <p className="text-xs text-gray-500 mt-0.5">Analice los errores locales y las curvas ROC de cada modelo entrenado.</p>
          </div>
          <div className="flex bg-slate-900 border border-dark-border p-1.5 rounded-xl gap-2 w-full md:w-auto">
            <select
              value={selectedModelId}
              onChange={e => setSelectedModelId(e.target.value)}
              className="bg-transparent text-xs font-bold text-gray-200 outline-none cursor-pointer py-1 px-2 border-r border-dark-border"
            >
              {Object.keys(rawResults || {}).map(key => (
                <option key={key} value={key} className="bg-slate-950 text-gray-200">
                  {key === 'mobilenet' ? 'MobileNetV2' :
                   key === 'resnet' ? 'ResNet50V2' :
                   key === 'efficientnet' ? 'EfficientNetV2-B0' :
                   key === 'fusion_net' ? 'Fusión ResNet+MobileNet' : 'MobileNet+RF (Híbrido)'}
                </option>
              ))}
            </select>

            <select
              value={selectedRocClass}
              onChange={e => setSelectedRocClass(e.target.value)}
              className="bg-transparent text-xs font-bold text-gray-200 outline-none cursor-pointer py-1 px-2"
            >
              <option value="ageDegeneration" className="bg-slate-950">Degeneración Macular (AMD)</option>
              <option value="cataract" className="bg-slate-950">Catarata</option>
              <option value="diabetes" className="bg-slate-950">Retinopatía Diabética</option>
              <option value="glaucoma" className="bg-slate-950">Glaucoma</option>
              <option value="hypertension" className="bg-slate-950">Retinopatía Hipertensiva</option>
              <option value="myopia" className="bg-slate-950">Miopía Patológica</option>
              <option value="normal" className="bg-slate-950">Ojo Sano / Normal</option>
              <option value="others" className="bg-slate-950">Otras Patologías</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          {/* Left: Confusion Heatmap */}
          <div className="xl:col-span-6 flex flex-col gap-4">
            <h4 className="font-bold text-white text-xs uppercase tracking-wide">🗺️ Matriz de Confusión (Predicho vs Real)</h4>
            <div className="overflow-x-auto w-full border border-dark-border/40 rounded-2xl p-4 bg-slate-950/20">
              <div className="grid grid-cols-9 gap-1 text-center min-w-[380px]">
                {/* Header corner */}
                <div className="text-[8px] font-bold text-gray-500 self-center">Real \ Pred</div>
                {ENFERMEDADES_LABELS.map(lbl => (
                  <div key={lbl} className="text-[7px] font-extrabold text-gray-400 self-center truncate py-1" title={lbl}>
                    {lbl.split(' ')[0]}
                  </div>
                ))}

                {/* Grid rows */}
                {selectedConfusionMatrix.map((row: number[], rIdx: number) => {
                  const rowSum = row.reduce((a, b) => a + b, 0) || 1;
                  return (
                    <React.Fragment key={rIdx}>
                      {/* Row header */}
                      <div className="text-[8px] font-extrabold text-gray-400 text-left self-center truncate pr-1" title={ENFERMEDADES_LABELS[rIdx]}>
                        {ENFERMEDADES_LABELS[rIdx].split(' ')[0]}
                      </div>
                      
                      {/* Grid cells */}
                      {row.map((val: number, cIdx: number) => {
                        const ratio = val / rowSum;
                        // Escalado del color de fondo del heatmap (azul para aciertos en diagonal, rojo/naranja para errores)
                        const isDiagonal = rIdx === cIdx;
                        const bgStyle = isDiagonal
                          ? `rgba(99, 102, 241, ${0.15 + ratio * 0.8})` // Indigo
                          : val > 0 
                            ? `rgba(239, 68, 68, ${0.1 + ratio * 0.7})`  // Red (Error)
                            : 'transparent';
                        
                        const borderStyle = isDiagonal && ratio > 0.5 
                          ? 'border border-indigo-500/35'
                          : 'border border-dark-border/10';

                        return (
                          <div 
                            key={cIdx} 
                            style={{ backgroundColor: bgStyle }}
                            className={`aspect-square flex items-center justify-center rounded text-[9px] font-bold text-white transition-all hover:scale-105 ${borderStyle}`}
                            title={`Real: ${ENFERMEDADES_LABELS[rIdx]}, Predicho: ${ENFERMEDADES_LABELS[cIdx]}, Cantidad: ${val}`}
                          >
                            {val}
                          </div>
                        );
                      })}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>
            <p className="text-[9px] text-gray-500 italic text-center">La diagonal en azul representa las clasificaciones correctas. Los cuadros rojos indican errores del modelo.</p>
          </div>

          {/* Right: Class ROC Curve */}
          <div className="xl:col-span-6 flex flex-col gap-4">
            <h4 className="font-bold text-white text-xs uppercase tracking-wide">📈 Curva ROC (Sensibilidad vs 1 - Especificidad)</h4>
            <div className="aspect-video w-full border border-dark-border/40 rounded-2xl p-4 bg-slate-950/20">
              <Line 
                data={getSelectedRocData()}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: { 
                    y: { min: 0.0, max: 1.05, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } } },
                    x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } } }
                  },
                  plugins: {
                    legend: { labels: { color: '#e5e7eb', font: { size: 9 } } }
                  }
                }}
              />
            </div>
            <p className="text-[9px] text-gray-500 italic text-center">Un AUC cercano a 1.0 indica un rendimiento perfecto. La línea punteada representa una clasificación al azar.</p>
          </div>
        </div>
      </div>

      {/* Stability, dispersion, and multidimensional comparison */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Accuracy per fold line chart */}
        <div className="glass-card rounded-3xl p-6">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4">📈 Estabilidad: Accuracy por Pliegue (Fold)</h3>
          <div className="aspect-video w-full">
            <Line 
              data={foldAccuraciesChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                  y: { min: 45, max: 62, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } } },
                  x: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 9 } } }
                },
                plugins: {
                  legend: { labels: { color: '#9ca3af', font: { size: 9 } } }
                }
              }}
            />
          </div>
        </div>

        {/* Boxplot performance distribution */}
        <div className="glass-card rounded-3xl p-6 flex flex-col justify-between">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4">📦 Dispersión: Boxplot de Rendimiento por Modelo</h3>
          <div className="flex-1 flex items-center justify-center">
            {renderBoxplot()}
          </div>
          <p className="text-[9px] text-gray-500 italic text-center mt-2">La línea rosa representa la mediana de exactitud. Los bigotes muestran los rangos extremos de los folds.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        {/* Radar Chart */}
        <div className="xl:col-span-5 glass-card rounded-3xl p-6 flex flex-col justify-between items-center text-center">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide self-start mb-4">🧭 Análisis de Consenso Multidimensional (Radar)</h3>
          <div className="w-full max-w-[260px] aspect-square flex items-center justify-center">
            {renderRadarChart()}
          </div>
          <p className="text-[9px] text-gray-500 italic mt-2">El gráfico balancea la exactitud, velocidad de inferencia, F1-Score, eficiencia en parámetros y robustez general.</p>
        </div>

        {/* Main comparative grid table */}
        <div className="xl:col-span-7 glass-card rounded-3xl p-6 overflow-hidden flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4 flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-400" />
              Tabla de Comparativa Técnica Completa
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-dark-border text-gray-400 font-bold uppercase tracking-wider">
                    <th className="py-4 px-4">Modelo</th>
                    <th className="py-4 px-4 text-center">Accuracy Promedio</th>
                    <th className="py-4 px-4 text-center">F1-Score (W)</th>
                    <th className="py-4 px-4 text-center">Precision (W)</th>
                    <th className="py-4 px-4 text-center">Recall (W)</th>
                    <th className="py-4 px-4 text-center">Inferencia (ms)</th>
                    <th className="py-4 px-4 text-center">Nº Parámetros</th>
                  </tr>
                </thead>
                <tbody>
                  {modelsData.map(m => (
                    <tr key={m.id} className="border-b border-dark-border/40 hover:bg-slate-900/25 transition-all">
                      <td className="py-4 px-4 font-bold text-white">{m.nombre}</td>
                      <td className="py-4 px-4 text-center text-indigo-400 font-extrabold">{(m.accuracy_media * 100).toFixed(2)}%</td>
                      <td className="py-4 px-4 text-center">{(m.f1_score).toFixed(4)}</td>
                      <td className="py-4 px-4 text-center">{(m.precision).toFixed(4)}</td>
                      <td className="py-4 px-4 text-center">{(m.recall).toFixed(4)}</td>
                      <td className="py-4 px-4 text-center text-pink-400 font-bold">{(m.tiempo_medio * 1000).toFixed(1)}ms</td>
                      <td className="py-4 px-4 text-center text-gray-400">{m.parametros}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <p className="text-[10px] text-gray-500 italic mt-4">Todos los valores provienen del archivo de auditoría técnica cruzada en tiempo de ejecución (`cv_metrics_results.json`).</p>
        </div>
      </div>
    </div>
  );
}

/* ==================== STATS TAB COMPONENT ==================== */
function StatsTab({ token, showToast }: TabProps) {
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState<any | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/models/statistics`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          setStatsData(data);
        } else {
          showToast(data.detail || 'Error cargando datos estadísticos.', 'error');
        }
      } catch (err) {
        showToast('Error conectando al backend para obtener estadísticas robustas.', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center min-h-[400px]">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mb-4" />
        <p className="text-sm font-bold text-white">Ejecutando validaciones estadísticas robustas...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 z-10">
      {/* Friedman Test Card */}
      {statsData && statsData.anova_friedman && (
        <div className="glass-card rounded-3xl p-6">
          <div className="flex justify-between items-start mb-4 border-b border-dark-border pb-3">
            <div>
              <span className="text-[10px] text-gray-500 font-extrabold uppercase tracking-wide block mb-1">Prueba Global No Paramétrica</span>
              <h3 className="font-extrabold text-white text-base">Prueba de Friedman</h3>
            </div>
            {statsData.anova_friedman.p_valor !== undefined && (
              <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                statsData.anova_friedman.significativo ? 'bg-emerald-950/50 border border-emerald-500/30 text-emerald-300' : 'bg-slate-900 border border-dark-border text-gray-400'
              }`}>
                {statsData.anova_friedman.significativo ? 'Significativo ✅' : 'No Significativo ❌'}
              </span>
            )}
          </div>

          {statsData.anova_friedman.info ? (
            <div className="bg-slate-950/40 border border-dark-border/60 rounded-2xl p-4 text-xs font-medium text-gray-300 leading-relaxed flex items-start gap-3">
              <Info className="w-5 h-5 text-indigo-400 shrink-0" />
              <p className="mt-0.5">{statsData.anova_friedman.info}</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                <div className="p-4 bg-slate-900/30 border border-dark-border/40 rounded-2xl">
                  <span className="text-[10px] text-gray-500 font-bold block uppercase mb-1">Estadístico Chi-cuadrado</span>
                  <span className="text-2xl font-black text-white">
                    {statsData.anova_friedman.estadistico !== undefined ? statsData.anova_friedman.estadistico.toFixed(4) : ''}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/30 border border-dark-border/40 rounded-2xl">
                  <span className="text-[10px] text-gray-500 font-bold block uppercase mb-1">p-valor</span>
                  <span className="text-2xl font-black text-indigo-400">
                    {statsData.anova_friedman.p_valor !== undefined ? statsData.anova_friedman.p_valor.toExponential(4) : ''}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/30 border border-dark-border/40 rounded-2xl">
                  <span className="text-[10px] text-gray-500 font-bold block uppercase mb-1">Número de Folds (N)</span>
                  <span className="text-2xl font-black text-white">{statsData.n_folds}</span>
                </div>
              </div>

              <div className="bg-slate-950/40 border border-dark-border/60 rounded-2xl p-4 text-xs font-medium text-gray-300 leading-relaxed flex items-start gap-3">
                <Info className="w-5 h-5 text-indigo-400 shrink-0" />
                <p className="mt-0.5">{statsData.anova_friedman.interpretacion}</p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Pairwise comparisons table */}
      {statsData && statsData.comparaciones_pares && (
        <div className="glass-card rounded-3xl p-6">
          <h3 className="font-bold text-white text-sm uppercase tracking-wide mb-4">🔬 Comparaciones Múltiples por Pares (Holm-Bonferroni y Cohen)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-dark-border text-gray-400 font-bold uppercase tracking-wider">
                  <th className="py-4 px-4">Comparación</th>
                  <th className="py-4 px-4 text-center">Shapiro p-val</th>
                  <th className="py-4 px-4 text-center">Distribución</th>
                  <th className="py-4 px-4 text-center">t-Student (Orig / Holm)</th>
                  <th className="py-4 px-4 text-center">Wilcoxon (Orig / Holm)</th>
                  <th className="py-4 px-4 text-center">d de Cohen</th>
                  <th className="py-4 px-4 text-center">Significativo (Holm)</th>
                </tr>
              </thead>
              <tbody>
                {statsData.comparaciones_pares.map((comp: any, idx: number) => {
                  const isNormal = comp.shapiro.normal;
                  const finalSig = isNormal ? comp.t_student.significativo : comp.wilcoxon.significativo;
                  return (
                    <tr key={idx} className="border-b border-dark-border/40 hover:bg-slate-900/25 transition-all">
                      <td className="py-4 px-4 font-bold text-white uppercase">{comp.modelo1} vs {comp.modelo2}</td>
                      <td className="py-4 px-4 text-center">{comp.shapiro.p_valor.toFixed(4)}</td>
                      <td className="py-4 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isNormal ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/25' : 'bg-amber-950/40 text-amber-400 border border-amber-500/25'
                        }`}>
                          {isNormal ? 'Normal' : 'No Normal'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center">{comp.t_student.p_valor_original.toFixed(3)} / <span className="text-indigo-400 font-bold">{comp.t_student.p_valor_corregido.toFixed(3)}</span></td>
                      <td className="py-4 px-4 text-center">{comp.wilcoxon.p_valor_original.toFixed(3)} / <span className="text-indigo-400 font-bold">{comp.wilcoxon.p_valor_corregido.toFixed(3)}</span></td>
                      <td className="py-4 px-4 text-center font-bold text-pink-400">
                        {comp.cohens_d.valor.toFixed(2)} ({comp.cohens_d.interpretacion})
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                          finalSig ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-900 text-gray-500 border border-dark-border'
                        }`}>
                          {finalSig ? 'Sí' : 'No'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

/* ==================== REPORTS TAB COMPONENT ==================== */
function ReportsTab({ token, showToast }: TabProps) {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (format: 'pdf' | 'word' | 'excel') => {
    setDownloading(format);
    try {
      const res = await fetch(`${BACKEND_URL}/api/reports/download/${format}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = format === 'pdf' ? 'Reporte_Diagnostico_Clinico.pdf' :
                     format === 'word' ? 'Reporte_Diagnostico_Clinico.docx' : 'Reporte_Comparativo.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast(`Reporte ${format.toUpperCase()} descargado con éxito.`, 'success');
      } else {
        const errData = await res.json();
        showToast(errData.detail || 'Error al generar el reporte.', 'error');
      }
    } catch (err) {
      showToast('Error de conexión al descargar el reporte.', 'error');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 z-10">
      {/* Card PDF */}
      <div className="glass-card rounded-3xl p-6 flex flex-col justify-between items-center text-center glass-card-hover min-h-[300px]">
        <div className="flex flex-col items-center">
          <div className="p-4 bg-red-950/20 border border-red-500/20 rounded-2xl mb-4 text-red-400">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="font-extrabold text-white text-lg mb-2">Reporte PDF</h3>
          <p className="text-xs text-gray-400 leading-relaxed max-w-xs">Informe clínico institucional con curvas ROC, caja de pliegues y resultados de significancia Holm-Bonferroni firmado digitalmente.</p>
        </div>
        <button 
          onClick={() => handleDownload('pdf')}
          disabled={downloading !== null}
          className="w-full mt-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold text-xs tracking-wider uppercase transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {downloading === 'pdf' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generando...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Descargar PDF
            </>
          )}
        </button>
      </div>

      {/* Card Word */}
      <div className="glass-card rounded-3xl p-6 flex flex-col justify-between items-center text-center glass-card-hover min-h-[300px]">
        <div className="flex flex-col items-center">
          <div className="p-4 bg-sky-950/20 border border-sky-500/20 rounded-2xl mb-4 text-sky-400">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="font-extrabold text-white text-lg mb-2">Reporte Word (.docx)</h3>
          <p className="text-xs text-gray-400 leading-relaxed max-w-xs">Informe clínico editable que incluye tablas de 6 columnas de significancia estadística robusta y secciones de conclusión y recomendaciones médicas.</p>
        </div>
        <button 
          onClick={() => handleDownload('word')}
          disabled={downloading !== null}
          className="w-full mt-6 py-3 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-xs tracking-wider uppercase transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {downloading === 'word' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generando...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Descargar Word
            </>
          )}
        </button>
      </div>

      {/* Card Excel */}
      <div className="glass-card rounded-3xl p-6 flex flex-col justify-between items-center text-center glass-card-hover min-h-[300px]">
        <div className="flex flex-col items-center">
          <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded-2xl mb-4 text-emerald-400">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="font-extrabold text-white text-lg mb-2">Reporte Excel (.xlsx)</h3>
          <p className="text-xs text-gray-400 leading-relaxed max-w-xs">Base de datos técnica y de proceso con el rendimiento crudo detallado fold por fold y tiempos transcurridos de inferencia.</p>
        </div>
        <button 
          onClick={() => handleDownload('excel')}
          disabled={downloading !== null}
          className="w-full mt-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs tracking-wider uppercase transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {downloading === 'excel' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generando...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Descargar Excel
            </>
          )}
        </button>
      </div>
    </div>
  );
}
