"use client";
import React, { useState, useEffect } from 'react';
import { translations } from '../i18n/translations';

interface StatsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

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
          {language === 'es' ? 'Ejecutando pruebas de significancia en el servidor...' : 'Running significance tests on server...'}
        </p>
      </div>
    );
  }

  // Mapear nombres de modelos para una lectura más amigable
  const getFriendlyName = (id: string) => {
    const names: Record<string, string> = {
      'mobilenet': 'MobileNetV2',
      'resnet': 'ResNet50V2',
      'efficientnet': 'EfficientNetV2-B0',
      'fusion_net': 'Fusión Híbrida 1',
      'cnn_rf': 'Híbrido 2 (CNN+RF)'
    };
    return names[id] || id;
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Shapiro & Paired Tests */}
      <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
        <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">
          {t.hypothesisTitle}
        </h3>
        <p className="text-xs text-foreground/60 leading-relaxed mb-2">
          {t.hypothesisDesc}
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-card-border/80 text-foreground/75 font-extrabold uppercase">
                <th className="py-3 px-4">{language === 'es' ? 'Modelo A' : 'Model A'}</th>
                <th className="py-3 px-4">{language === 'es' ? 'Modelo B' : 'Model B'}</th>
                <th className="py-3 px-4">Shapiro-Wilk (p-val)</th>
                <th className="py-3 px-4">{t.pvalue}</th>
                <th className="py-3 px-4">{t.significant}</th>
                <th className="py-3 px-4">{t.interpretation}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-card-border/40 font-medium">
              {statsData?.comparaciones_pares?.map((comp: any, idx: number) => {
                const normal = comp.shapiro.normal;
                const pValue = normal ? comp.t_student.p_valor_corregido : comp.wilcoxon.p_valor_corregido;
                const sig = normal ? comp.t_student.significativo : comp.wilcoxon.significativo;
                
                // Traducción dinámica de la interpretación para bilingüismo
                let friendlyInterpretation = comp.interpretacion;
                if (language === 'en') {
                  if (sig) {
                    const m1 = getFriendlyName(comp.modelo1);
                    const m2 = getFriendlyName(comp.modelo2);
                    const method = normal ? "adjusted t-Student" : "adjusted Wilcoxon";
                    friendlyInterpretation = `${m1} significantly outperforms ${m2} in accuracy (${method} p=${pValue.toFixed(4)}, Cohen's d=${comp.cohens_d.valor.toFixed(2)} [${comp.cohens_d.interpretacion}]).`;
                  } else {
                    friendlyInterpretation = `No statistically significant difference in accuracy between ${getFriendlyName(comp.modelo1)} and ${getFriendlyName(comp.modelo2)} (adjusted p=${pValue.toFixed(4)}).`;
                  }
                }

                return (
                  <tr key={idx} className="hover:bg-foreground/2 transition-colors">
                    <td className="py-3 px-4 font-bold text-foreground">{getFriendlyName(comp.modelo1)}</td>
                    <td className="py-3 px-4 font-bold text-foreground">{getFriendlyName(comp.modelo2)}</td>
                    <td className="py-3 px-4 text-foreground/80">
                      {comp.shapiro.p_valor.toFixed(4)} ({normal ? 'Normal' : 'No Normal'})
                    </td>
                    <td className="py-3 px-4 font-bold text-indigo-650 dark:text-indigo-400">{pValue.toFixed(6)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-md font-extrabold uppercase text-[10px] ${
                        sig ? 'bg-emerald-950/40 border border-emerald-500/30 text-emerald-600 dark:text-emerald-300' : 'bg-slate-900/40 border border-slate-700/50 text-foreground/50'
                      }`}>
                        {sig ? t.yes : t.no}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-foreground/70 max-w-sm leading-relaxed">{friendlyInterpretation}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cohen's d Effect Size Card */}
      <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
        <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3">
          {t.cohenTitle}
        </h3>
        <p className="text-xs text-foreground/60 leading-relaxed mb-2">
          {t.cohenDesc}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {statsData?.comparaciones_pares?.map((comp: any, idx: number) => {
            const dVal = comp.cohens_d.valor;
            const interpret = comp.cohens_d.interpretacion;
            
            // Traducir interpretación
            let friendlyInterpret = interpret;
            if (language === 'en') {
              if (interpret === 'Grande') friendlyInterpret = 'Large';
              else if (interpret === 'Mediana') friendlyInterpret = 'Medium';
              else if (interpret === 'Pequeña') friendlyInterpret = 'Small';
              else friendlyInterpret = 'Negligible';
            }

            return (
              <div key={idx} className="p-4 bg-foreground/3 border border-card-border rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-foreground/50 font-extrabold uppercase">
                    {getFriendlyName(comp.modelo1)} vs {getFriendlyName(comp.modelo2)}
                  </span>
                  <div className="text-sm font-bold text-foreground mt-1">d = {dVal.toFixed(3)}</div>
                </div>
                <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase ${
                  Math.abs(dVal) >= 0.8 
                    ? 'bg-rose-950/40 border border-rose-500/30 text-rose-600 dark:text-rose-300' 
                    : Math.abs(dVal) >= 0.5 
                      ? 'bg-amber-950/40 border border-amber-500/30 text-amber-600 dark:text-amber-300' 
                      : 'bg-indigo-950/40 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300'
                }`}>
                  {friendlyInterpret}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
