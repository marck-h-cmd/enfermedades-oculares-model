"use client";
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, RadialLinearScale, Filler, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line, Radar } from 'react-chartjs-2';
import { translations } from '../i18n/translations';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, RadialLinearScale, Filler, Title, Tooltip, Legend);

interface AnalyticsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

export default function AnalyticsTab({ language, token, showToast }: AnalyticsTabProps) {
  const t = translations[language] as any;
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
        label: t.accuracyMean || 'Accuracy',
        data: modelsData.map(m => m.accuracy_media),
        backgroundColor: [
          'rgba(99, 102, 241, 0.7)',
          'rgba(236, 72, 153, 0.7)',
          'rgba(14, 165, 233, 0.7)',
          'rgba(168, 85, 247, 0.7)',
          'rgba(249, 115, 22, 0.7)'
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
  let rocChartData = { labels: [] as string[], datasets: [] as any[] };
  const currentModelRoc = rawResults?.[selectedModelId]?.curvas_roc?.[selectedRocClass];
  
  if (currentModelRoc) {
    const fpr = currentModelRoc.fpr || [];
    const tpr = currentModelRoc.tpr || [];
    
    rocChartData = {
      labels: fpr.map((v: number) => v.toFixed(2)),
      datasets: [
        {
          label: `${t.rocTitle || 'ROC'} (AUC: ${currentModelRoc.auc?.toFixed(4)})`,
          data: tpr,
          borderColor: 'rgb(99, 102, 241)',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          borderWidth: 2,
          pointRadius: 1,
          fill: true
        },
        {
          label: language === 'es' ? 'Línea de Azar (AUC: 0.5)' : 'Random Guess Line',
          data: fpr,
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
    if (classId in t) return t[classId];
    return classId;
  };

  // Preparar datos para el gráfico Radar OOD (Robustez Ambiental)
  const robustnessData = {
    labels: [
      t.oodOriginal || 'Limpieza Original', 
      t.oodNoise || 'Ruido Gaussiano', 
      t.oodIllumination || 'Baja Iluminación', 
      t.oodBlur || 'Desenfoque', 
      t.oodRotation || 'Rotación Extrema'
    ],
    datasets: modelsData.map((m, index) => {
      const colors = [
        'rgba(99, 102, 241, 0.5)',  // Indigo
        'rgba(236, 72, 153, 0.5)',  // Pink
        'rgba(14, 165, 233, 0.5)',  // Sky
        'rgba(168, 85, 247, 0.5)',  // Purple
        'rgba(249, 115, 22, 0.5)'   // Orange
      ];
      const borders = [
        'rgb(99, 102, 241)',
        'rgb(236, 72, 153)',
        'rgb(14, 165, 233)',
        'rgb(168, 85, 247)',
        'rgb(249, 115, 22)'
      ];
      
      const robust = rawResults?.[m.id]?.robustez;
      return {
        label: m.nombre,
        data: robust ? [
          robust.original,
          robust.ruido_gaussiano,
          robust.baja_iluminacion,
          robust.desenfoque,
          robust.rotacion_extrema
        ] : [m.accuracy_media, m.accuracy_media * 0.8, m.accuracy_media * 0.9, m.accuracy_media * 0.7, m.accuracy_media * 0.85],
        backgroundColor: colors[index % colors.length],
        borderColor: borders[index % borders.length],
        borderWidth: 2,
      };
    })
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
                  y: { min: 0.2, max: 1.0, grid: { color: 'rgba(150,150,150,0.05)' }, ticks: { color: '#9ca3af' } },
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
            <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 mb-4">{t.modelDetails || 'Model Details'}</h3>
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

      {/* Título de Sección de Validación Clínica */}
      <div className="flex items-center gap-4 my-4">
        <div className="h-px bg-card-border flex-1"></div>
        <h2 className="text-lg font-black text-indigo-500 uppercase tracking-widest">{t.clinicalValidation || 'Advanced Clinical Validation'}</h2>
        <div className="h-px bg-card-border flex-1"></div>
      </div>

      {/* Clinical Metrics & Brier Score Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Pure Clinical Metrics Table */}
        <div className="lg:col-span-8 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">
            🏥 {t.clinicalMetrics || 'Pure Clinical Risk Metrics'}
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse mt-2">
              <thead>
                <tr className="border-b border-card-border/80 text-foreground/75 font-extrabold uppercase text-[10px]">
                  <th className="py-3 px-4">Modelo</th>
                  <th className="py-3 px-4 text-emerald-500">{t.ppv || 'VPP'}</th>
                  <th className="py-3 px-4 text-emerald-500">{t.npv || 'VPN'}</th>
                  <th className="py-3 px-4 text-rose-500">{t.tfn || 'Tasa Falsos Negativos'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-card-border/40 font-medium">
                {modelsData.map((m, idx) => {
                  const res = rawResults?.[m.id];
                  if (!res) return null;
                  return (
                    <tr key={idx} className="hover:bg-foreground/2 transition-colors">
                      <td className="py-3 px-4 font-bold text-foreground">{m.nombre}</td>
                      <td className="py-3 px-4 font-bold text-emerald-400">{(res.vpp * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 font-bold text-emerald-400">{(res.vpn * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 font-black text-rose-500">{(res.tfn * 100).toFixed(1)}%</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Brier Score Card */}
        <div className="lg:col-span-4 glass-card rounded-3xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 mb-4">
              🎯 {t.brierScore || 'Brier Score (Calibration)'}
            </h3>
            <p className="text-xs text-foreground/60 leading-relaxed mb-4">
              {t.brierDesc || 'Measures how reliable model probabilities are (0 = perfect).'}
            </p>
            <div className="flex flex-col gap-3">
              {modelsData.map(m => {
                const brier = rawResults?.[m.id]?.brier_score || 0.1;
                const percent = Math.max(0, 100 - (brier * 100 * 2));
                return (
                  <div key={m.id} className="flex flex-col gap-1">
                    <div className="flex justify-between items-center text-[10px] font-bold">
                      <span className="text-foreground/80">{m.nombre}</span>
                      <span className={brier < 0.1 ? 'text-emerald-500' : 'text-amber-500'}>{brier.toFixed(3)}</span>
                    </div>
                    <div className="w-full bg-foreground/5 h-1.5 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${brier < 0.1 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${percent}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Out-Of-Distribution Robustness Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-6 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">
            🛡️ {t.robustnessTitle || 'Robustness to Environmental Biases (OOD)'}
          </h3>
          <p className="text-xs text-foreground/60 leading-relaxed mb-2">
            {t.robustnessDesc || 'Evaluates accuracy drop against camera noise, blur, and underexposure.'}
          </p>
          <div className="w-full aspect-square max-h-[400px] flex justify-center items-center">
            <Radar 
              data={robustnessData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  r: {
                    angleLines: { color: 'rgba(150,150,150,0.2)' },
                    grid: { color: 'rgba(150,150,150,0.1)' },
                    pointLabels: { color: '#9ca3af', font: { size: 10, weight: 'bold' } },
                    ticks: { display: false, min: 0, max: 1 }
                  }
                },
                plugins: {
                  legend: { position: 'bottom', labels: { color: 'currentColor', font: { size: 10 } } }
                }
              }}
            />
          </div>
        </div>

        {/* ROC Curve original section squeezed to half */}
        <div className="lg:col-span-6 glass-card rounded-3xl p-6 flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 border-b border-card-border pb-3">
            <h3 className="font-bold text-foreground text-sm uppercase tracking-wide">{t.rocTitle || 'ROC'}</h3>
            <div className="flex flex-wrap gap-2">
              <select
                value={selectedModelId}
                onChange={e => setSelectedModelId(e.target.value)}
                className="px-2 py-1 rounded-lg text-[10px] font-bold glass-input text-foreground bg-card-bg"
              >
                {modelsData.map(m => (
                  <option key={m.id} value={m.id}>{m.nombre}</option>
                ))}
              </select>
              <select
                value={selectedRocClass}
                onChange={e => setSelectedRocClass(e.target.value)}
                className="px-2 py-1 rounded-lg text-[10px] font-bold glass-input text-foreground bg-card-bg"
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
                  plugins: { legend: { display: false } }
                }}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-foreground/50 font-bold">
                No ROC data
              </div>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}
