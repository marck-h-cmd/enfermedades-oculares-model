"use client";
import React, { useState } from 'react';
import { translations } from '../i18n/translations';

interface ReportsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

export default function ReportsTab({ language, token, showToast }: ReportsTabProps) {
  const t = translations[language];
  const [downloading, setDownloading] = useState<Record<string, boolean>>({});

  const triggerDownload = async (format: string) => {
    setDownloading(prev => ({ ...prev, [format]: true }));
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/reports/download/${format}`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const ext = format === 'pdf' ? 'pdf' : format === 'word' ? 'docx' : 'xlsx';
        a.download = `reporte_diagnostico_consolidado.${ext}`;
        
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        showToast(
          language === 'es' ? `Reporte ${format.toUpperCase()} descargado.` : `Reporte ${format.toUpperCase()} downloaded.`,
          'success'
        );
      } else {
        const data = await res.json();
        showToast(data.detail || (language === 'es' ? 'Error al generar el reporte.' : 'Error generating report.'), 'error');
      }
    } catch (err) {
      showToast(language === 'es' ? 'Error de conexión con el servidor.' : 'Server connection error.', 'error');
    } finally {
      setDownloading(prev => ({ ...prev, [format]: false }));
    }
  };

  return (
    <div className="glass-card rounded-3xl p-8 max-w-4xl mx-auto flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-extrabold text-foreground">{t.reportsTitle}</h2>
        <p className="text-xs text-foreground/60 mt-1 leading-relaxed">{t.reportsHelp}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* PDF Card */}
        <div className="p-5 bg-foreground/3 border border-card-border rounded-2xl flex flex-col justify-between h-56">
          <div>
            <h4 className="font-extrabold text-sm text-foreground">{t.pdfTitle}</h4>
            <p className="text-[11px] text-foreground/60 mt-2 leading-relaxed">{t.pdfDesc}</p>
          </div>
          <button
            onClick={() => triggerDownload('pdf')}
            disabled={downloading['pdf']}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-55"
          >
            {downloading['pdf'] ? t.generating : t.downloadBtn}
          </button>
        </div>

        {/* Word Card */}
        <div className="p-5 bg-foreground/3 border border-card-border rounded-2xl flex flex-col justify-between h-56">
          <div>
            <h4 className="font-extrabold text-sm text-foreground">📄 {language === 'es' ? 'Reporte Clínico (DOCX)' : 'Clinical Report (DOCX)'}</h4>
            <p className="text-[11px] text-foreground/60 mt-2 leading-relaxed">
              {language === 'es' ? 'Genera un documento de Microsoft Word editable con el análisis detallado y tablas de exactitud.' : 'Generates an editable Microsoft Word document with detailed analysis and accuracy tables.'}
            </p>
          </div>
          <button
            onClick={() => triggerDownload('word')}
            disabled={downloading['word']}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-55"
          >
            {downloading['word'] ? t.generating : t.downloadBtn}
          </button>
        </div>

        {/* Excel Card */}
        <div className="p-5 bg-foreground/3 border border-card-border rounded-2xl flex flex-col justify-between h-56">
          <div>
            <h4 className="font-extrabold text-sm text-foreground">📊 {language === 'es' ? 'Reporte Comparativo (XLSX)' : 'Comparative Report (XLSX)'}</h4>
            <p className="text-[11px] text-foreground/60 mt-2 leading-relaxed">
              {language === 'es' ? 'Exporta la tabla completa de validación cruzada y métricas de desempeño de las redes para Microsoft Excel.' : 'Exports the full cross-validation and network performance metrics table to Microsoft Excel.'}
            </p>
          </div>
          <button
            onClick={() => triggerDownload('excel')}
            disabled={downloading['excel']}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-55"
          >
            {downloading['excel'] ? t.generating : t.downloadBtn}
          </button>
        </div>
      </div>
    </div>
  );
}
