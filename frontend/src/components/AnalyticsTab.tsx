"use client";
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { translations } from '../i18n/translations';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

interface AnalyticsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

export default function AnalyticsTab({ language, token, showToast }: AnalyticsTabProps) {
  const t = translations[language];
  const [loading, setLoading] = useState(true);
  const [modelsData, setModelsData] = useState<any[]>([]);
  const [rawResults, setRawResults] = useState<any>(null);

  // Selector states
  const [selectedModelId, setSelectedModelId] = useState<string>('fusion_net');
  const [selectedRocClass, setSelectedRocClass] = useState<string>('cataract');

  useEffect(() => {
    const fetchModelsAndResults = async () => {
      try {
        const resModels = await fetch('http://127.0.0.1:8000/api/models', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dataModels = await resModels.json();

        const resResults = await fetch('http://127.0.0.1:8000/api/models/results', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dataResults = await resResults.json();

        if (resModels.ok && resResults.ok) {
          setModelsData(dataModels);
          setRawResults(dataResults);
          
          const keys = Object.keys(dataResults);
          if (keys.length > 0) {
            setSelectedModelId(keys[0]);
          }
        } else {
          showToast(language === 'es' ? 'Error cargando datos comparativos.' : 'Error loading comparative data.', 'error');
        }
      } catch (err) {
        showToast(language === 'es' ? 'Error de conexión con el backend.' : 'Backend connection error.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchModelsAndResults();
  }, [language]);

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px]">
        <svg className="animate-spin h-8 w-8 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="text-sm text-foreground/70 font-semibold">
          {language === 'es' ? 'Cargando datos de validación cruzada...' : 'Loading cross-validation data...'}
        </p>
      </div>
    );
  }

  // Preparar datos para el gráfico de barras comparativo de exactitud
  const accuracyChartData = {
    labels: modelsData.map(m => m.nombre),
    datasets: [
      {
        label: t.accuracyMean,
        data: modelsData.map(m => m.accuracy_media),
        backgroundColor: [
          'rgba(99, 102, 241, 0.7)',  // Indigo
          'rgba(236, 72, 153, 0.7)',  // Pink
          'rgba(14, 165, 233, 0.7)',  // Sky
          'rgba(168, 85, 247, 0.7)',  // Purple
          'rgba(249, 115, 22, 0.7)'   // Orange
        ],
        borderColor: [
          'rgb(99, 102, 241)',
          'rgb(236, 72, 153)',
          'rgb(14, 165, 233)',
          'rgb(168, 85, 247)',
          'rgb(249, 115, 22)'
        ],
        borderWidth: 1.5,
        borderRadius: 8
      }
    ]
  };

  // Preparar datos para el gráfico de línea ROC
  let rocChartData = { labels: [] as number[], datasets: [] as any[] };
  const currentModelRoc = rawResults?.[selectedModelId]?.curvas_roc?.[selectedRocClass];
  
  if (currentModelRoc) {
    const fpr = currentModelRoc.fpr || [];
    const tpr = currentModelRoc.tpr || [];
    
    // Usar el FPR como etiquetas para el eje X
    rocChartData = {
      labels: fpr.map((v: number) => v.toFixed(2)),
      datasets: [
        {
          label: `${t.rocTitle} (AUC: ${currentModelRoc.auc?.toFixed(4)})`,
          data: tpr,
          borderColor: 'rgb(99, 102, 241)',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          borderWidth: 2,
          pointRadius: 1,
          fill: true
        },
        {
          label: language === 'es' ? 'Línea de Azar (AUC: 0.5)' : 'Random Guess Line (AUC: 0.5)',
          data: fpr, // diagonal y = x
          borderColor: 'rgba(156, 163, 175, 0.5)',
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false
        }
      ]
    };
  }

  // Traducción de clases
  const translateClass = (classId: string) => {
    if (classId in t) return (t as any)[classId];
    return classId;
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Accuracy & General Details Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">
            {language === 'es' ? 'Comparativa de Exactitud de Modelos (Cross-Validation)' : 'Models Accuracy Comparison (Cross-Validation)'}
          </h3>
          <div className="h-64 w-full">
            <Bar 
              data={accuracyChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: { min: 0.5, max: 1.0, grid: { color: 'rgba(150,150,150,0.05)' }, ticks: { color: '#9ca3af' } },
                  x: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 9 } } }
                },
                plugins: {
                  legend: { display: false }
                }
              }}
            />
          </div>
        </div>

        {/* Technical specifications */}
        <div className="lg:col-span-4 glass-card rounded-3xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 mb-4">{t.modelDetails}</h3>
            <div className="flex flex-col gap-4">
              {modelsData.map(m => (
                <div key={m.id} className="flex justify-between items-center text-xs font-semibold border-b border-card-border/30 pb-2">
                  <span className="text-foreground/80">{m.nombre}</span>
                  <div className="text-right">
                    <span className="text-indigo-650 dark:text-indigo-400 block font-bold">{(m.accuracy_media * 100).toFixed(2)}% ACC</span>
                    <span className="text-[10px] text-foreground/50">{m.parametros} params</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <p className="text-[10px] text-foreground/50 italic mt-4">
            {language === 'es' ? 'El promedio se calcula en base a una validación cruzada estratificada de 5 folds.' : 'The mean performance is calculated based on a 5-fold stratified cross-validation.'}
          </p>
        </div>
      </div>

      {/* ROC Curves Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 border-b border-card-border pb-3">
            <h3 className="font-bold text-foreground text-sm uppercase tracking-wide">{t.rocTitle}</h3>
            
            {/* ROC SELECTORS */}
            <div className="flex flex-wrap gap-2">
              <select
                value={selectedModelId}
                onChange={e => setSelectedModelId(e.target.value)}
                className="px-3 py-1.5 rounded-lg text-xs font-bold glass-input text-foreground bg-card-bg cursor-pointer"
              >
                {Object.keys(rawResults || {}).map(k => (
                  <option key={k} value={k}>{rawResults[k].nombre || k}</option>
                ))}
              </select>

              <select
                value={selectedRocClass}
                onChange={e => setSelectedRocClass(e.target.value)}
                className="px-3 py-1.5 rounded-lg text-xs font-bold glass-input text-foreground bg-card-bg cursor-pointer"
              >
                {Object.keys(rawResults?.[selectedModelId]?.curvas_roc || {}).map(c => (
                  <option key={c} value={c}>{translateClass(c)}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="h-64 w-full">
            {rocChartData.labels.length > 0 ? (
              <Line 
                data={rocChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: { min: 0.0, max: 1.0, grid: { color: 'rgba(150,150,150,0.05)' }, ticks: { color: '#9ca3af' } },
                    x: { grid: { color: 'rgba(150,150,150,0.05)' }, ticks: { color: '#9ca3af', font: { size: 9 } } }
                  },
                  plugins: {
                    legend: { labels: { color: 'currentColor', font: { size: 10 } } }
                  }
                }}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-foreground/50 font-bold">
                {language === 'es' ? 'No hay curvas ROC disponibles para este modelo.' : 'No ROC curves available for this model.'}
              </div>
            )}
          </div>
          <p className="text-[10px] text-foreground/50 text-center font-medium italic">
            {t.rocDesc}
          </p>
        </div>

        {/* Classification report metrics table */}
        <div className="lg:col-span-4 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">{t.metricsTitle}</h3>
          <div className="flex flex-col gap-4 flex-1 justify-center">
            {modelsData.map(m => (
              <div key={m.id} className="p-3 bg-foreground/3 border border-card-border rounded-2xl flex flex-col gap-1.5">
                <span className="text-[10px] text-foreground/50 font-extrabold uppercase">{m.nombre}</span>
                <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-bold">
                  <div className="p-1.5 bg-indigo-600/10 border border-indigo-500/20 rounded-lg text-indigo-650 dark:text-indigo-400">
                    <div>{t.f1Score}</div>
                    <div className="text-xs font-black mt-1">{(m.f1_score * 100).toFixed(1)}%</div>
                  </div>
                  <div className="p-1.5 bg-emerald-600/10 border border-emerald-500/20 rounded-lg text-emerald-650 dark:text-emerald-450">
                    <div>{t.precision}</div>
                    <div className="text-xs font-black mt-1">{(m.precision * 100).toFixed(1)}%</div>
                  </div>
                  <div className="p-1.5 bg-amber-600/10 border border-amber-500/20 rounded-lg text-amber-650 dark:text-amber-450">
                    <div>{t.recall}</div>
                    <div className="text-xs font-black mt-1">{(m.recall * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
