"use client";
import React, { useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { translations } from '../i18n/translations';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface DiagnosticTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

export default function DiagnosticTab({ language, token, showToast }: DiagnosticTabProps) {
  const t = translations[language];
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [sliderVal, setSliderVal] = useState(50);
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
      const res = await fetch('http://127.0.0.1:8000/api/predict', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
        showToast(language === 'es' ? 'Diagnóstico computado con éxito.' : 'Diagnosis computed successfully.', 'success');
      } else {
        showToast(data.detail || (language === 'es' ? 'Error procesando la imagen ocular.' : 'Error processing eye image.'), 'error');
      }
    } catch (err) {
      showToast(language === 'es' ? 'Error de conexión con el backend de inferencia.' : 'Connection error with inference backend.', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Traducción dinámica de clases de enfermedades
  const translateClass = (classId: string) => {
    if (classId in t) {
      return (t as any)[classId];
    }
    return classId;
  };

  // Traducción dinámica de la severidad
  const translateSeverity = (severity: string) => {
    if (severity in t) {
      return (t as any)[severity];
    }
    return severity;
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 z-10">
      {/* Left Panel: Upload */}
      <div className="xl:col-span-5 flex flex-col gap-6">
        <div 
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="glass-card rounded-3xl p-8 border-dashed border-2 border-slate-400 dark:border-slate-700/60 hover:border-indigo-500/50 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 aspect-square group"
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
              className="w-full h-full object-cover rounded-2xl shadow-lg border border-card-border"
            />
          ) : (
            <div className="flex flex-col items-center">
              <div className="p-4 bg-card-bg rounded-full mb-4 border border-card-border group-hover:scale-110 group-hover:bg-indigo-600/10 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-foreground/60 group-hover:text-indigo-500 dark:group-hover:text-indigo-400">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <p className="text-base font-bold text-foreground mb-1">{t.dragActive}</p>
              <p className="text-xs text-foreground/50 font-semibold mb-4">{t.dragHelp}</p>
              <span className="px-3.5 py-1.5 bg-card-bg border border-card-border rounded-lg text-[10px] font-bold tracking-wider text-foreground/60 uppercase group-hover:border-indigo-500/30">{t.formats}</span>
            </div>
          )}
        </div>

        {selectedFile && (
          <button 
            onClick={handlePredict}
            disabled={loading}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold tracking-wide text-sm shadow-xl shadow-indigo-650/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t.predicting}
              </>
            ) : t.predictBtn}
          </button>
        )}
      </div>

      {/* Right Panel: Results */}
      <div className="xl:col-span-7 flex flex-col gap-6">
        {loading && (
          <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px]">
            <svg className="animate-spin h-10 w-10 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-base font-bold text-foreground">
              {language === 'es' ? 'Analizando retina...' : 'Analyzing retina...'}
            </p>
            <p className="text-xs text-foreground/50 font-semibold mt-1">
              {language === 'es' ? 'Ejecutando MobileNet, ResNet, EfficientNet, Fusión y Grad-CAM' : 'Running MobileNet, ResNet, EfficientNet, Fusion and Grad-CAM'}
            </p>
            <div className="w-48 bg-slate-200 dark:bg-slate-800 h-1 rounded-full overflow-hidden mt-5 border border-card-border/40">
              <div className="bg-indigo-500 h-full animate-[loading-bar_1.5s_infinite]" style={{ width: '60%' }}></div>
            </div>
          </div>
        )}

        {!loading && !result && (
          <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px] text-center border-dashed border border-card-border">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-foreground/40 mb-4">
              <circle cx="12" cy="12" r="10" />
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
            <p className="text-base font-bold text-foreground/75">{t.waitingImage}</p>
            <p className="text-xs text-foreground/50 max-w-xs mt-1">{t.waitingImageHelp}</p>
          </div>
        )}

        {!loading && result && (
          <div className="flex flex-col gap-6">
            {/* Visual comparison Slider (CLAHE vs GradCAM) */}
            <div className="glass-card rounded-3xl p-5 flex flex-col gap-4">
              <div className="flex justify-between items-center border-b border-card-border pb-3">
                <h3 className="font-bold text-foreground text-sm uppercase tracking-wide">{t.interactiveVisualizer}</h3>
                <div className="flex bg-card-bg border border-card-border p-1 rounded-xl gap-1">
                  <button 
                    onClick={() => setActiveCompareMode('gradcam')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      activeCompareMode === 'gradcam' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground/60 hover:text-foreground'
                    }`}
                  >
                    Grad-CAM
                  </button>
                  <button 
                    onClick={() => setActiveCompareMode('clahe')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      activeCompareMode === 'clahe' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground/60 hover:text-foreground'
                    }`}
                  >
                    {language === 'es' ? 'Filtro CLAHE' : 'CLAHE Filter'}
                  </button>
                </div>
              </div>

              {/* Slider image component */}
              <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-card-border flex items-center justify-center bg-black">
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
                  {t.original}
                </span>
                <span className="absolute bottom-3 right-3 bg-indigo-600/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-bold text-white tracking-wider uppercase select-none border border-indigo-400/20">
                  {activeCompareMode === 'gradcam' ? 'Grad-CAM' : 'CLAHE'}
                </span>
              </div>
              <p className="text-[10px] text-foreground/50 text-center font-medium italic">
                {activeCompareMode === 'gradcam' ? t.gradcamDesc : t.claheDesc}
              </p>
            </div>

            {/* Histograma antes/después de CLAHE */}
            {result.histogramas && (
              <div className="glass-card rounded-3xl p-5 flex flex-col gap-4">
                <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">{t.luminanceHistogram}</h3>
                <div className="h-44 w-full">
                  <Line 
                    data={{
                      labels: result.histogramas.bins,
                      datasets: [
                        {
                          label: language === 'es' ? 'Luminancia Original' : 'Original Luminance',
                          data: result.histogramas.original,
                          borderColor: 'rgba(156, 163, 175, 0.7)',
                          backgroundColor: 'rgba(156, 163, 175, 0.08)',
                          borderWidth: 2,
                          pointRadius: 1,
                          fill: true,
                          tension: 0.4
                        },
                        {
                          label: language === 'es' ? 'Luminancia CLAHE (Ecualizada)' : 'CLAHE Luminance (Equalized)',
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
                        y: { grid: { color: 'rgba(150,150,150,0.05)' }, ticks: { color: '#9ca3af', font: { size: 9 } } },
                        x: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 8 } } }
                      },
                      plugins: {
                        legend: { labels: { color: 'currentColor', font: { size: 10 } } }
                      }
                    }}
                  />
                </div>
                <p className="text-[10px] text-foreground/50 text-center font-medium italic">
                  {t.histogramDesc}
                </p>
              </div>
            )}

            {/* Diagnostic Details */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className={`inline-flex px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-widest border mb-2 ${
                    result.diagnostico_principal.gravedad === 'Alta' || result.diagnostico_principal.gravedad === 'Crítica'
                      ? 'bg-rose-950/40 border-rose-500/30 text-rose-450 dark:text-rose-300' 
                      : result.diagnostico_principal.gravedad === 'Moderada' 
                        ? 'bg-amber-950/40 border-amber-500/30 text-amber-650 dark:text-amber-300' 
                        : 'bg-emerald-950/40 border-emerald-500/30 text-emerald-650 dark:text-emerald-300'
                  }`}>
                    {t.severity}: {translateSeverity(result.diagnostico_principal.gravedad)}
                  </span>
                  <h3 className="text-xl font-extrabold text-foreground">{translateClass(result.diagnostico_principal.clase_id)}</h3>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-foreground/50 font-bold uppercase block mb-1">{t.confidence}</span>
                  <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">{(result.diagnostico_principal.confianza * 100).toFixed(2)}%</span>
                </div>
              </div>

              <div className="bg-foreground/5 border border-card-border/40 rounded-2xl p-4 text-sm text-foreground/80 leading-relaxed">
                {language === 'es' 
                  ? result.diagnostico_principal.descripcion 
                  : (t as any).descFallback?.replace('[CLASS]', translateClass(result.diagnostico_principal.clase_id))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-foreground/3 border border-card-border/30 rounded-2xl">
                  <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide block mb-1">{t.treatment}</span>
                  <p className="text-xs text-foreground/80 font-semibold leading-relaxed">
                    {language === 'es' 
                      ? (result.diagnostico_principal.treatment || result.diagnostico_principal.tratamiento)
                      : (t as any).treatmentFallback}
                  </p>
                </div>
                <div className="p-4 bg-foreground/3 border border-card-border/30 rounded-2xl">
                  <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide block mb-1">{t.prognosis}</span>
                  <p className="text-xs text-foreground/80 font-semibold leading-relaxed">
                    {language === 'es' 
                      ? result.diagnostico_principal.pronostico 
                      : (t as any).prognosisFallback}
                  </p>
                </div>
              </div>
            </div>

            {/* Barras de probabilidad del diagnóstico (8 Clases) */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <h4 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">{t.distributionTitle}</h4>
              <div className="flex flex-col gap-3">
                {Object.entries(result.modelos.champion.probabilidades_completas)
                  .sort((a: any, b: any) => b[1] - a[1])
                  .map(([claseId, prob]: any) => (
                    <div key={claseId}>
                      <div className="flex justify-between items-center text-xs font-semibold mb-1">
                        <span className="text-foreground/80">{translateClass(claseId)}</span>
                        <span className="text-indigo-600 dark:text-indigo-400 font-bold">{(prob * 100).toFixed(2)}%</span>
                      </div>
                      <div className="w-full bg-foreground/5 h-2 rounded-full overflow-hidden border border-card-border/40">
                        <div 
                          className="bg-gradient-to-r from-indigo-500 to-indigo-700 h-full rounded-full transition-all duration-1000 ease-out" 
                          style={{ width: `${prob * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Model grid comparisons */}
            <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
              <h4 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">{t.archComparison}</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(result.modelos).map(([modelKey, modelInfo]: any) => (
                  <div key={modelKey} className="p-4 bg-card-bg/40 border border-card-border rounded-2xl flex flex-col justify-between">
                    <div>
                      <span className="text-[10px] text-foreground/50 font-extrabold uppercase tracking-wider block mb-1">
                        {modelKey === 'mobilenet' ? 'MobileNetV2' :
                         modelKey === 'resnet' ? 'ResNet50V2' :
                         modelKey === 'efficientnet' ? 'EfficientNetV2-B0' :
                         modelKey === 'ensemble' ? 'Ensemble Consenso' : 'Champion CV'}
                      </span>
                      <p className="text-sm font-bold text-foreground truncate">{translateClass(modelInfo.clase_id)}</p>
                    </div>
                    
                    <div className="mt-3">
                      <div className="flex justify-between items-center text-[10px] font-semibold text-foreground/60 mb-1">
                        <span>{t.confidence}</span>
                        <span>{(modelInfo.confianza * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-foreground/5 h-1.5 rounded-full overflow-hidden border border-card-border/40">
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
