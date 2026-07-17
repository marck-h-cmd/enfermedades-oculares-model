"use client";
import React, { useState, useEffect } from 'react';
import { translations } from '../i18n/translations';

interface StatsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

// Helpers para validación estadística robusta
const getSeverityGroup = (key: string) => {
  if (key === 'lagrange_multiplier') return 'ALERTA';
  if (key === 'mann_whitney' || key === 'pitman_morgan') return 'INFORMATIVO';
  return 'ESTABLE';
};

const getRecommendation = (key: string, lang: string) => {
  const isEs = lang === 'es';
  switch (key) {
    case 'lagrange_multiplier':
      return isEs 
        ? "Recomendación: evaluar desempeño segmentado por calidad de imagen/iluminación."
        : "Recommendation: evaluate performance segmented by image quality/illumination.";
    case 'pitman_morgan':
      return isEs
        ? "Recomendación: priorizar el modelo con menor varianza de error para mayor consistencia clínica."
        : "Recommendation: prioritize the model with lower error variance for clinical consistency.";
    case 'mann_whitney':
      return isEs
        ? "Recomendación: usar el modelo superior como base para producción."
        : "Recommendation: use the superior model as the production baseline.";
    default:
      return isEs
        ? "No se requiere acción adicional."
        : "No additional action required.";
  }
};

const getComparedModels = (key: string, value: any, lang: string) => {
  const isEs = lang === 'es';
  if (key === 'mann_whitney' || key === 'pitman_morgan') {
    const modelA = value?.modelo_a;
    const modelB = value?.modelo_b;
    
    // Función para obtener nombre amigable en el componente React
    const getFriendlyName = (id: string) => {
      const names: Record<string, string> = {
        'mobilenet': 'MobileNetV2',
        'resnet': 'ResNet50V2',
        'efficientnet': 'EfficientNetV2',
        'fusion_net': 'Fusión ResNet+MobileNet',
        'cnn_rf': 'CNN + Random Forest'
      };
      return names[id] || id;
    };
    
    const nameA = modelA ? getFriendlyName(modelA) : 'N/A';
    const nameB = modelB ? getFriendlyName(modelB) : 'N/A';
    
    return isEs 
      ? `Modelos comparados: ${nameA} vs ${nameB}` 
      : `Compared models: ${nameA} vs ${nameB}`;
  }
  return null;
};

const formatPValue = (pval: any) => {
  if (typeof pval === 'number') {
    if (pval < 0.0001) {
      return "< 0.0001";
    }
    return pval.toFixed(4);
  }
  return pval;
};

export default function StatsTab({ language, token, showToast }: StatsTabProps) {
  const t = translations[language];
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState<any>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/models/statistics', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        if (res.ok) {
          setStatsData(data);
        } else {
          showToast(language === 'es' ? 'Error cargando datos estadísticos inferenciales.' : 'Error loading inferential statistical data.', 'error');
        }
      } catch (err) {
        showToast(language === 'es' ? 'Error de conexión con el backend.' : 'Connection error with backend.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [language]);

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-8 flex flex-col justify-center items-center h-full min-h-[400px]">
        <svg className="animate-spin h-8 w-8 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="text-sm text-foreground/70 font-semibold">
          {language === 'es' ? 'Ejecutando pruebas de significancia robustas en el servidor...' : 'Running robust significance tests on server...'}
        </p>
      </div>
    );
  }

  // Mapear nombres de modelos
  const getFriendlyName = (id: string) => {
    const names: Record<string, string> = {
      'mobilenet': 'MobileNetV2',
      'resnet': 'ResNet50V2',
      'efficientnet': 'EfficientNetV2',
      'fusion_net': 'Fusión ResNet+MobileNet',
      'cnn_rf': 'CNN + Random Forest'
    };
    return names[id] || id;
  };

  const friedman = statsData?.anova_friedman;
  const nemenyi = statsData?.nemenyi;

  return (
    <div className="flex flex-col gap-8">
      
      {/* Friedman Test Card */}
      {friedman && (
        <div className={`glass-card rounded-3xl p-6 flex flex-col gap-4 border-2 ${friedman.significativo ? 'border-emerald-500/30' : 'border-card-border'}`}>
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 flex items-center gap-2">
            📊 {t.friedmanTitle || 'Global Friedman Test (Non-Parametric)'}
          </h3>
          
          <div className="flex flex-col md:flex-row items-center gap-6 p-4 bg-foreground/5 rounded-2xl">
            <div className="flex flex-col items-center justify-center min-w-[150px] p-4 rounded-xl bg-card-bg shadow-inner">
              <span className="text-[10px] font-black uppercase text-foreground/50 mb-1">P-Value</span>
              <span className={`text-3xl font-black ${friedman.significativo ? 'text-emerald-500' : 'text-amber-500'}`}>
                {friedman.p_valor?.toExponential(2)}
              </span>
            </div>
            
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground/80 mb-2">
                {t.interpretation || 'Interpretation:'}
              </p>
              <p className="text-sm text-foreground/70 leading-relaxed italic border-l-4 border-indigo-500/50 pl-4">
                {friedman.significativo ? t.friedmanSig : t.friedmanNotSig}
              </p>
              <div className="mt-3 inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-indigo-500/10 text-indigo-400">
                {t.statisticLabel || 'Statistic:'} {friedman.estadistico?.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Nemenyi Post-hoc Matrix Card */}
      {nemenyi && nemenyi.realizado && (
        <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 flex items-center gap-2">
            🎯 {t.nemenyiTitle || 'Nemenyi Post-Hoc Test (Critical Differences)'}
          </h3>
          <p className="text-xs text-foreground/60 leading-relaxed mb-2">
            {t.nemenyiDesc || 'P-value matrix adjusted for multiple comparisons.'}
          </p>

          <div className="overflow-x-auto rounded-xl border border-card-border">
            <table className="w-full text-center text-xs border-collapse">
              <thead>
                <tr className="bg-foreground/5 font-extrabold uppercase text-foreground/70">
                  <th className="py-4 px-4 border-b border-r border-card-border">{t.modelsLabel || 'Models'}</th>
                  {nemenyi.modelos.map((m: string) => (
                    <th key={m} className="py-4 px-4 border-b border-card-border">{getFriendlyName(m)}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="font-medium text-foreground/80">
                {nemenyi.modelos.map((mRow: string, idx: number) => (
                  <tr key={mRow} className={idx % 2 === 0 ? 'bg-transparent' : 'bg-foreground/2'}>
                    <td className="py-3 px-4 border-r border-card-border font-bold bg-foreground/5 text-left whitespace-nowrap">
                      {getFriendlyName(mRow)}
                    </td>
                    {nemenyi.modelos.map((mCol: string) => {
                      const pval = nemenyi.matriz_p_valores[mRow][mCol];
                      const isSignificant = pval < 0.05 && mRow !== mCol;
                      const isSame = mRow === mCol;
                      
                      return (
                        <td key={mCol} className={`py-3 px-4 font-black transition-colors ${
                          isSame ? 'bg-card-border/20 text-foreground/30' : 
                          isSignificant ? 'bg-emerald-500/10 text-emerald-500 dark:text-emerald-400' : 'text-foreground/50'
                        }`}>
                          {isSame ? '-' : pval < 0.001 ? '<0.001' : pval.toFixed(3)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Fallback if Nemenyi wasn't performed */}
      {nemenyi && !nemenyi.realizado && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-xs font-bold text-center">
          {t.posthocNotApplicable || 'Post-hoc test not applicable.'}
        </div>
      )}

      {/* Robust Statistical Tests Section */}
      {statsData?.pruebas_robustas && (
        <div className="glass-card rounded-3xl p-6 flex flex-col gap-6">
          <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 flex items-center gap-2">
            🛡️ {language === 'es' ? 'Pruebas Estadísticas Robustas Recomendadas' : 'Recommended Robust Statistical Tests'}
          </h3>
          
          {/* Grupos de Severidad */}
          {[
            {
              id: 'ALERTA',
              title: language === 'es' ? 'Requiere atención' : 'Attention Required',
              desc: language === 'es' ? 'Errores de especificación y desviaciones críticas que requieren acción inmediata.' : 'Specification errors and critical deviations requiring action.',
              titleClass: 'text-rose-500 dark:text-rose-400 font-extrabold flex items-center gap-2 text-xs uppercase tracking-wide',
              bgClass: 'bg-rose-500/[0.02] border border-rose-500/10 p-4 rounded-2xl flex flex-col gap-4'
            },
            {
              id: 'INFORMATIVO',
              title: language === 'es' ? 'Hallazgos informativos' : 'Informational Findings',
              desc: language === 'es' ? 'Información complementaria útil para facilitar la selección de modelos.' : 'Comparative metrics and logs to facilitate model selection.',
              titleClass: 'text-blue-500 dark:text-blue-400 font-extrabold flex items-center gap-2 text-xs uppercase tracking-wide',
              bgClass: 'bg-blue-500/[0.02] border border-blue-500/10 p-4 rounded-2xl flex flex-col gap-4'
            },
            {
              id: 'ESTABLE',
              title: language === 'es' ? 'Modelos estables' : 'Stable Models',
              desc: language === 'es' ? 'Validaciones de consistencia aprobadas con éxito.' : 'Approved consistency checks and safety validations.',
              titleClass: 'text-emerald-500 dark:text-emerald-400 font-extrabold flex items-center gap-2 text-xs uppercase tracking-wide',
              bgClass: 'bg-emerald-500/[0.02] border border-emerald-500/10 p-4 rounded-2xl flex flex-col gap-4'
            }
          ].map(group => {
            const groupTests = Object.entries(statsData.pruebas_robustas).filter(
              ([key]: any) => getSeverityGroup(key) === group.id
            );
            
            if (groupTests.length === 0) return null;
            
            return (
              <div key={group.id} className={group.bgClass}>
                <div className="border-b border-card-border pb-2">
                  <h4 className={group.titleClass}>
                    {group.id === 'ALERTA' ? '⚠️' : group.id === 'INFORMATIVO' ? 'ℹ️' : '✅'} {group.title}
                  </h4>
                  <p className="text-[10px] text-foreground/50 mt-0.5">{group.desc}</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {groupTests.map(([key, value]: any) => {
                    const compared = getComparedModels(key, value, language);
                    const reco = getRecommendation(key, language);
                    const isAlert = group.id === 'ALERTA';
                    const isInfo = group.id === 'INFORMATIVO';
                    
                    return (
                      <div key={key} className="p-4 rounded-2xl bg-foreground/3 border border-card-border flex flex-col gap-3 shadow-inner">
                        <div className="flex justify-between items-start gap-2">
                          <h5 className="font-bold text-foreground text-xs">{value.prueba}</h5>
                          <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-full border ${
                            isAlert ? 'bg-rose-500/10 text-rose-500 dark:text-rose-400 border-rose-500/20' :
                            isInfo ? 'bg-blue-500/10 text-blue-500 dark:text-blue-400 border-blue-500/20' :
                            'bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 border-emerald-500/20'
                          }`}>
                            {isAlert ? (language === 'es' ? 'Alerta ⚠️' : 'Alert ⚠️') :
                             isInfo ? (language === 'es' ? 'Informativo ℹ️' : 'Info ℹ️') :
                             (language === 'es' ? 'Estable ✅' : 'Stable ✅')}
                          </span>
                        </div>
                        
                        {compared && (
                          <p className="text-[10px] text-foreground/50 font-mono -mt-2">
                            {compared}
                          </p>
                        )}
                        
                        <p className="text-xs text-foreground/70 italic leading-relaxed pl-2 border-l-2 border-indigo-500/30">
                          {value.interpretacion}
                        </p>
                        
                        <p className={`text-xs font-semibold leading-relaxed pl-2 border-l-2 ${
                          isAlert ? 'border-rose-500/70 text-rose-500 dark:text-rose-400' :
                          isInfo ? 'border-blue-500/70 text-blue-500 dark:text-blue-400' :
                          'border-emerald-500/70 text-emerald-500 dark:text-emerald-400'
                        }`}>
                          {reco}
                        </p>
                        
                        <div className="flex flex-wrap gap-2 mt-1">
                          {value.p_valor !== undefined && (
                            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-card-bg text-foreground/60 border border-card-border/30">
                              p-val: {formatPValue(value.p_valor)}
                            </span>
                          )}
                          {value.e_value_acumulado !== undefined && (
                            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-card-bg text-foreground/60 border border-card-border/30">
                              E-val: {typeof value.e_value_acumulado === 'number' ? value.e_value_acumulado.toFixed(2) : value.e_value_acumulado}
                            </span>
                          )}
                          {value.media_trimmed !== undefined && (
                            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-card-bg text-foreground/60 border border-card-border/30">
                              Trimmed Mean: {value.media_trimmed.toFixed(3)}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
    </div>
  );
}
