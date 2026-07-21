"use client";
import React, { useState, useEffect } from 'react';
import { translations } from '../i18n/translations';

interface ReportsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

interface ChampionModel {
  name: string;
  accuracy_media: number;
  accuracy_std: number;
  f1_score: number;
  recall: number;
  tiempo_medio: number;
}

interface SummaryModel {
  model: string;
  accuracy_media: number;
  accuracy_std: number;
  f1_score: number;
  recall: number;
  tiempo_medio: number;
}

interface ClassMetric {
  clase: string;
  sensibilidad: number;
  especificidad: number;
  precision: number;
  f1_score: number;
  support: number;
}

interface FriedmanTest {
  estadistico?: number;
  p_valor?: number;
  significativo?: boolean;
  interpretacion?: string;
}

interface PreviewData {
  title: string;
  generated_at: string;
  methodology: string;
  champion_model: ChampionModel;
  summary_models: SummaryModel[];
  class_metrics: ClassMetric[];
  friedman: FriedmanTest;
  total_models: number;
}

export default function ReportsTab({ language, token, showToast }: ReportsTabProps) {
  const t = translations[language] || translations.es;
  const isEs = language === 'es';

  // Estados de carga y datos
  const [downloading, setDownloading] = useState<Record<string, boolean>>({});
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [loadingPreview, setLoadingPreview] = useState<boolean>(true);

  // Estados de Vista Previa PDF directo (Blob URL en Modal iFrame)
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null);
  const [loadingPdfPreview, setLoadingPdfPreview] = useState<boolean>(false);
  const [showPdfModal, setShowPdfModal] = useState<boolean>(false);

  // Estados de Personalización del Reporte
  const [physicianName, setPhysicianName] = useState<string>('Dr. Alex Morgan, MD - Oftalmología Diagnóstica');
  const [clinicalNotes, setClinicalNotes] = useState<string>(
    isEs 
      ? 'Evaluación preliminar por ensamblado de redes neuronales convolucionales. Hallazgos validados con técnica CLAHE y mapas de sensibilidad espacial Grad-CAM.'
      : 'Preliminary assessment via convolutional neural network ensemble. Findings validated with CLAHE enhancement and spatial Grad-CAM maps.'
  );
  const [includeFriedman, setIncludeFriedman] = useState<boolean>(true);
  const [includeClassMetrics, setIncludeClassMetrics] = useState<boolean>(true);

  // Estados de Visualización y Filtros
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [viewMode, setViewMode] = useState<'a4' | 'cards'>('a4');
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [isFullscreenModal, setIsFullscreenModal] = useState<boolean>(false);
  const [showConfigPanel, setShowConfigPanel] = useState<boolean>(false);

  const fetchPreview = async () => {
    setLoadingPreview(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports/preview', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPreviewData(data);
      } else {
        showToast(isEs ? 'No se pudo cargar la vista previa del reporte.' : 'Failed to load report preview.', 'error');
      }
    } catch (err) {
      showToast(isEs ? 'Error de conexión con el servidor.' : 'Server connection error.', 'error');
    } finally {
      setLoadingPreview(false);
    }
  };

  useEffect(() => {
    fetchPreview();
  }, [token]);

  const handlePdfPreview = async () => {
    setLoadingPdfPreview(true);
    setShowPdfModal(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reports/download/pdf', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        setPdfPreviewUrl(url);
      } else {
        showToast(isEs ? 'Error al generar la vista previa del PDF.' : 'Error generating PDF preview.', 'error');
        setShowPdfModal(false);
      }
    } catch (err) {
      showToast(isEs ? 'Error de conexión con el servidor.' : 'Server connection error.', 'error');
      setShowPdfModal(false);
    } finally {
      setLoadingPdfPreview(false);
    }
  };

  const closePdfModal = () => {
    if (pdfPreviewUrl) {
      window.URL.revokeObjectURL(pdfPreviewUrl);
    }
    setPdfPreviewUrl(null);
    setShowPdfModal(false);
  };

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
        
        const ext = format === 'pdf' ? 'pdf' : 'docx';
        a.download = `reporte_diagnostico_consolidado.${ext}`;
        
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        showToast(
          isEs ? `Reporte ${format.toUpperCase()} descargado exitosamente.` : `Report ${format.toUpperCase()} successfully downloaded.`,
          'success'
        );
      } else {
        const data = await res.json();
        showToast(data.detail || (isEs ? 'Error al generar el reporte.' : 'Error generating report.'), 'error');
      }
    } catch (err) {
      showToast(isEs ? 'Error de conexión con el servidor.' : 'Server connection error.', 'error');
    } finally {
      setDownloading(prev => ({ ...prev, [format]: false }));
    }
  };

  const copyJsonMetadata = () => {
    if (!previewData) return;
    const jsonString = JSON.stringify(
      {
        ...previewData,
        custom_physician: physicianName,
        custom_notes: clinicalNotes
      },
      null,
      2
    );
    navigator.clipboard.writeText(jsonString);
    showToast(isEs ? 'Metadatos JSON copiados al portapapeles.' : 'JSON metadata copied to clipboard.', 'success');
  };

  const copyMarkdownSummary = () => {
    if (!previewData) return;
    const summary = `
# ${previewData.title}
**Fecha:** ${previewData.generated_at}
**Especialista:** ${physicianName}
**Modelo Campeón:** ${previewData.champion_model.name} (Accuracy: ${(previewData.champion_model.accuracy_media * 100).toFixed(2)}%, F1-Score: ${previewData.champion_model.f1_score.toFixed(4)})

## Observaciones Clínicas:
${clinicalNotes}

## Resumen de Modelos:
${previewData.summary_models.map(m => `- **${m.model}**: Acc: ${(m.accuracy_media * 100).toFixed(2)}% | F1: ${m.f1_score.toFixed(4)} | Tiempo: ${m.tiempo_medio.toFixed(2)}s`).join('\n')}
    `.trim();

    navigator.clipboard.writeText(summary);
    showToast(isEs ? 'Resumen Markdown copiado al portapapeles.' : 'Markdown summary copied to clipboard.', 'success');
  };

  const handlePrint = () => {
    window.print();
  };

  // Filtrar modelos y métricas según el término de búsqueda
  const filteredModels = previewData?.summary_models.filter(m => 
    m.model.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const filteredClasses = previewData?.class_metrics.filter(c => 
    c.clase.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="flex flex-col gap-8 max-w-6xl mx-auto pb-12">
      {/* Estilos para impresión nativa (Ctrl+P o botón Imprimir) */}
      <style jsx global>{`
        @media print {
          @page {
            size: A4 portrait;
            margin: 10mm 15mm;
          }
          html, body {
            background: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: auto !important;
          }
          body * {
            visibility: hidden !important;
          }
          aside, nav, header, footer, .no-print {
            display: none !important;
          }
          #print-document-area, #print-document-area * {
            visibility: visible !important;
          }
          #print-document-area {
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 10px !important;
            background: #ffffff !important;
            color: #000000 !important;
            box-shadow: none !important;
            border: none !important;
            border-radius: 0 !important;
            z-index: 999999 !important;
          }
        }
      `}</style>

      {/* Encabezado Principal y Barra de Acciones */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card rounded-3xl p-6 border border-card-border shadow-sm no-print">
        <div>
          <span className="text-[10px] font-black uppercase text-indigo-500 tracking-widest block mb-1">
            {isEs ? 'MÓDULO DE INFORMES MÉDICOS & EXPORTACIÓN' : 'MEDICAL REPORTS & EXPORT MODULE'}
          </span>
          <h2 className="text-xl font-extrabold text-foreground flex items-center gap-2.5">
            📂 {t.reportsTitle}
          </h2>
          <p className="text-xs text-foreground/60 mt-1 leading-relaxed">{t.reportsHelp}</p>
        </div>

        <div className="flex items-center flex-wrap gap-2">
          <button
            onClick={() => setShowConfigPanel(!showConfigPanel)}
            className={`px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer border ${
              showConfigPanel 
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-md' 
                : 'bg-foreground/5 hover:bg-foreground/10 text-foreground border-card-border'
            }`}
            title={isEs ? 'Personalizar Firma y Notas' : 'Customize Signature & Notes'}
          >
            <span>⚙️</span>
            <span>{isEs ? 'Personalizar Reporte' : 'Customize Report'}</span>
          </button>

          <button
            onClick={() => setIsFullscreenModal(true)}
            className="px-4 py-2.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-500 dark:text-indigo-400 border border-indigo-500/20 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer"
          >
            <span>🔍</span>
            <span>{isEs ? 'Vista Previa A4 (Full Screen)' : 'A4 Fullscreen Preview'}</span>
          </button>

          <button
            onClick={fetchPreview}
            disabled={loadingPreview}
            className="p-2.5 bg-foreground/5 hover:bg-foreground/10 text-foreground/70 rounded-xl text-xs font-bold transition-all cursor-pointer border border-card-border"
            title={isEs ? 'Actualizar vista previa' : 'Refresh preview'}
          >
            🔄
          </button>
        </div>
      </div>

      {/* Panel de Personalización del Reporte (Colapsable) */}
      {showConfigPanel && (
        <div className="glass-card rounded-3xl p-6 border border-indigo-500/30 bg-indigo-500/5 flex flex-col gap-5 no-print animate-fadeIn">
          <div className="flex items-center justify-between border-b border-card-border pb-3">
            <h3 className="text-sm font-extrabold text-foreground flex items-center gap-2">
              📝 {isEs ? 'Parámetros de Personalización del Informe Clínico' : 'Clinical Report Customization Options'}
            </h3>
            <button 
              onClick={() => setShowConfigPanel(false)}
              className="text-xs text-foreground/50 hover:text-foreground font-bold cursor-pointer"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-foreground/80 mb-1">
                👨‍⚕️ {isEs ? 'Especialista Firmante / Firma Clínica:' : 'Signing Specialist / Clinical Signature:'}
              </label>
              <input
                type="text"
                value={physicianName}
                onChange={(e) => setPhysicianName(e.target.value)}
                placeholder="Ej: Dr. Juan Pérez - Oftalmólogo"
                className="w-full px-4 py-2.5 bg-background border border-card-border rounded-xl text-xs text-foreground focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>

            <div className="flex flex-col justify-end gap-2">
              <span className="text-xs font-bold text-foreground/80 mb-1">
                ⚙️ {isEs ? 'Secciones Incluidas en la Vista Previa:' : 'Sections Included in Preview:'}
              </span>
              <div className="flex items-center gap-4 text-xs text-foreground/80">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={includeFriedman}
                    onChange={(e) => setIncludeFriedman(e.target.checked)}
                    className="accent-indigo-600 rounded"
                  />
                  <span>{isEs ? 'Prueba de Friedman' : 'Friedman Test'}</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={includeClassMetrics}
                    onChange={(e) => setIncludeClassMetrics(e.target.checked)}
                    className="accent-indigo-600 rounded"
                  />
                  <span>{isEs ? 'Métricas por Clase' : 'Metrics by Class'}</span>
                </label>
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-foreground/80 mb-1">
                📌 {isEs ? 'Observaciones Clínicas y Recomendaciones Adicionales:' : 'Clinical Observations & Recommendations:'}
              </label>
              <textarea
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                rows={3}
                className="w-full px-4 py-2.5 bg-background border border-card-border rounded-xl text-xs text-foreground focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>
        </div>
      )}

      {/* Tarjetas de Descarga Rápida y Formatos (PDF con Vista Previa, Word, Metadata JSON) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 no-print">
        {/* PDF Card */}
        <div className="p-6 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/25 rounded-3xl flex flex-col justify-between gap-4 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start gap-3">
            <div className="p-3 bg-indigo-500/15 text-indigo-500 rounded-2xl text-2xl font-black">📄</div>
            <div>
              <h4 className="font-extrabold text-sm text-foreground">{t.pdfTitle}</h4>
              <p className="text-[11px] text-foreground/60 mt-1 leading-relaxed">{t.pdfDesc}</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handlePdfPreview}
              disabled={loadingPdfPreview}
              className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-lg shadow-indigo-600/20 active:scale-[0.98] disabled:opacity-55"
            >
              <span>👁️</span>
              {isEs ? 'Vista Previa PDF' : 'PDF Preview'}
            </button>
            
            <button
              onClick={() => triggerDownload('pdf')}
              disabled={downloading['pdf']}
              className="py-3 px-4 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-55"
              title={isEs ? 'Descargar directamente' : 'Direct download'}
            >
              <span>📥</span>
            </button>
          </div>
        </div>

        {/* Word Card */}
        <div className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/25 rounded-3xl flex flex-col justify-between gap-4 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start gap-3">
            <div className="p-3 bg-blue-500/15 text-blue-500 rounded-2xl text-2xl font-black">📝</div>
            <div>
              <h4 className="font-extrabold text-sm text-foreground">
                {isEs ? 'Reporte Clínico (DOCX)' : 'Clinical Report (DOCX)'}
              </h4>
              <p className="text-[11px] text-foreground/60 mt-1 leading-relaxed">
                {isEs ? 'Documento editable en Microsoft Word con gráficos, metodología y tablas completas de exactitud.' : 'Editable Word document with charts, methodology, and complete accuracy tables.'}
              </p>
            </div>
          </div>
          <button
            onClick={() => triggerDownload('word')}
            disabled={downloading['word']}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-blue-600/20 active:scale-[0.98] disabled:opacity-55"
          >
            <span>📥</span>
            {downloading['word'] ? t.generating : (isEs ? 'Descargar Word (.docx)' : 'Download Word (.docx)')}
          </button>
        </div>

        {/* JSON Metadata Card */}
        <div className="p-6 bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/25 rounded-3xl flex flex-col justify-between gap-4 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-start gap-3">
            <div className="p-3 bg-amber-500/15 text-amber-500 rounded-2xl text-2xl font-black">⚙️</div>
            <div>
              <h4 className="font-extrabold text-sm text-foreground">{t.jsonTitle}</h4>
              <p className="text-[11px] text-foreground/60 mt-1 leading-relaxed">{t.jsonDesc}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={copyJsonMetadata}
              className="flex-1 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-lg shadow-amber-600/20 active:scale-[0.98]"
            >
              <span>📋</span>
              {isEs ? 'Copiar JSON' : 'Copy JSON'}
            </button>
            <button
              onClick={copyMarkdownSummary}
              className="px-3.5 py-3 bg-amber-500/20 hover:bg-amber-500/30 text-amber-600 dark:text-amber-300 rounded-xl text-xs font-bold transition-all flex items-center justify-center cursor-pointer"
              title={isEs ? 'Copiar Resumen Markdown' : 'Copy Markdown Summary'}
            >
              <span>📝</span>
            </button>
          </div>
        </div>
      </div>

      {/* Barra de Filtros, Impresión y Selector de Vistas de Previa */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-card-bg/60 border border-card-border p-4 rounded-2xl no-print">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={isEs ? 'Filtrar por arquitectura o clase...' : 'Filter by architecture or class...'}
              className="w-full pl-9 pr-4 py-2 bg-background border border-card-border rounded-xl text-xs text-foreground focus:outline-none focus:border-indigo-500"
            />
            <span className="absolute left-3 top-2.5 text-foreground/40 text-xs">🔍</span>
          </div>

          <div className="flex items-center gap-1 bg-foreground/5 p-1 rounded-xl border border-card-border">
            <button
              onClick={() => setViewMode('a4')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                viewMode === 'a4' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground/70 hover:text-foreground'
              }`}
            >
              📄 {isEs ? 'Vista A4' : 'A4 View'}
            </button>
            <button
              onClick={() => setViewMode('cards')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                viewMode === 'cards' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground/70 hover:text-foreground'
              }`}
            >
              📊 {isEs ? 'Tarjetas Resumen' : 'Summary Cards'}
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto justify-end">
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shadow-sm hover:opacity-90"
          >
            <span>🖨️</span>
            <span>{isEs ? 'Imprimir Documento' : 'Print Document'}</span>
          </button>
        </div>
      </div>

      {/* ÁREA DE VISTA PREVIA DEL DOCUMENTO CLÍNICO */}
      {loadingPreview ? (
        <div className="glass-card rounded-3xl p-16 flex flex-col items-center justify-center gap-4 text-center border border-card-border">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-foreground/70 font-semibold">
            {isEs ? 'Generando vista previa consolidada con análisis de modelos...' : 'Generating consolidated preview with model analysis...'}
          </p>
        </div>
      ) : previewData ? (
        <div className="flex flex-col gap-6">
          {/* MODO A4: DOCUMENTO CLÍNICO TIPO INFORME OFICIAL */}
          {viewMode === 'a4' && (
            <div 
              id="print-document-area"
              className="bg-white text-slate-900 rounded-3xl p-8 md:p-12 border-2 border-indigo-500/20 shadow-2xl relative flex flex-col gap-8 transition-all font-sans"
              style={{
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
                minHeight: '842px'
              }}
            >
              {/* Marca de Agua / Sello Oficial en Fondo */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-[0.03] pointer-events-none select-none text-center">
                <span className="text-9xl font-black uppercase tracking-widest text-indigo-900 block">OCULAR</span>
                <span className="text-7xl font-bold uppercase tracking-widest text-indigo-900 block">DIAGNOSE</span>
              </div>

              {/* Membrete e Identificación del Hospital/Laboratorio */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b-2 border-slate-900/10 pb-6 gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-650 flex items-center justify-center text-white text-2xl font-black shadow-md">
                    👁️
                  </div>
                  <div>
                    <h1 className="text-xl font-black tracking-tight text-indigo-950 uppercase leading-none">
                      OcularDiagnose AI System
                    </h1>
                    <p className="text-[11px] font-extrabold text-indigo-600 uppercase tracking-widest mt-1">
                      {isEs ? 'Centro de Investigación & Diagnóstico Oftálmico' : 'Ophthalmic Research & Diagnostic Center'}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right text-[11px] text-slate-600">
                  <p className="font-bold text-slate-900">{isEs ? 'Fecha de Emisión:' : 'Issued Date:'} <span className="font-semibold">{previewData.generated_at}</span></p>
                  <p><span className="font-bold text-slate-900">{isEs ? 'ID de Validación:' : 'Validation ID:'}</span> Ocular-CV5-2026</p>
                  <p><span className="font-bold text-slate-900">{isEs ? 'Estado:' : 'Status:'}</span> <span className="text-emerald-700 font-bold">VERIFICADO</span></p>
                </div>
              </div>

              {/* Título y Metodología */}
              <div className="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <span className="text-[9px] font-black text-indigo-600 uppercase tracking-widest block mb-0.5">
                    {isEs ? 'INFORME CLÍNICO TÉCNICO CONSOLIDADO' : 'CONSOLIDATED CLINICAL TECHNICAL REPORT'}
                  </span>
                  <h2 className="text-base font-black text-slate-900">{previewData.title}</h2>
                  <p className="text-xs text-slate-600 mt-1">
                    <span className="font-bold">{isEs ? 'Metodología:' : 'Methodology:'}</span> {previewData.methodology}
                  </p>
                </div>
                <div className="bg-white px-4 py-2 rounded-xl border border-indigo-100 text-center shadow-sm">
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">{isEs ? 'Total Modelos' : 'Total Models'}</span>
                  <span className="text-lg font-black text-indigo-700">{previewData.total_models} Redes</span>
                </div>
              </div>

              {/* Bloque del Modelo Campeón Destacado */}
              <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-900 to-slate-900 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-lg">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-amber-400 text-slate-950 flex items-center justify-center text-3xl shadow-md">
                    🏆
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-black text-amber-300 tracking-widest block">
                      {isEs ? 'MODELO CAMPEÓN RECOMENDADO' : 'RECOMMENDED CHAMPION MODEL'}
                    </span>
                    <h3 className="text-lg font-extrabold text-white">
                      {previewData.champion_model.name}
                    </h3>
                    <p className="text-xs text-slate-300 mt-0.5">
                      {isEs ? 'Mayor desempeño general en validación cruzada estratificada (5-folds).' : 'Highest overall performance in stratified cross-validation (5-folds).'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/15 text-center">
                    <span className="text-[9px] font-bold text-slate-300 uppercase block">Accuracy</span>
                    <span className="text-base font-black text-amber-300">{(previewData.champion_model.accuracy_media * 100).toFixed(2)}%</span>
                  </div>
                  <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/15 text-center">
                    <span className="text-[9px] font-bold text-slate-300 uppercase block">F1-Score</span>
                    <span className="text-base font-black text-emerald-300">{previewData.champion_model.f1_score.toFixed(4)}</span>
                  </div>
                  <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl border border-white/15 text-center">
                    <span className="text-[9px] font-bold text-slate-300 uppercase block">{isEs ? 'Sensibilidad' : 'Recall'}</span>
                    <span className="text-base font-black text-cyan-300">{(previewData.champion_model.recall * 100).toFixed(2)}%</span>
                  </div>
                </div>
              </div>

              {/* Tabla Comparativa de Arquitecturas */}
              <div>
                <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2">
                  📊 {isEs ? 'Resumen Comparativo de Arquitecturas Evaluadas' : 'Comparative Architecture Summary'}
                </h4>
                <div className="overflow-x-auto rounded-xl border border-slate-200">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100 text-slate-700 font-black uppercase text-[10px] border-b border-slate-200">
                      <tr>
                        <th className="p-3">Modelo</th>
                        <th className="p-3">Accuracy Promedio</th>
                        <th className="p-3">Desviación Estándar</th>
                        <th className="p-3">F1-Score (Weighted)</th>
                        <th className="p-3">Sensibilidad (Recall)</th>
                        <th className="p-3">Tiempo Medio/Fold</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-800 font-medium">
                      {filteredModels.map((m) => (
                        <tr key={m.model} className={m.model === previewData.champion_model.name ? 'bg-indigo-50 font-extrabold text-indigo-950' : ''}>
                          <td className="p-3 flex items-center gap-2">
                            {m.model === previewData.champion_model.name && <span>🏆</span>}
                            <span>{m.model}</span>
                          </td>
                          <td className="p-3">{(m.accuracy_media * 100).toFixed(2)}%</td>
                          <td className="p-3 text-slate-500">±{m.accuracy_std.toFixed(4)}</td>
                          <td className="p-3 text-indigo-700">{m.f1_score.toFixed(4)}</td>
                          <td className="p-3">{(m.recall * 100).toFixed(2)}%</td>
                          <td className="p-3 text-slate-600">{m.tiempo_medio.toFixed(2)}s</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Métricas por Clase Diagnóstica */}
              {includeClassMetrics && (
                <div>
                  <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2">
                    🔬 {isEs ? 'Desglose Clínico por Patología Ocular (Modelo Campeón)' : 'Clinical Breakdown by Pathology (Champion Model)'}
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                    {filteredClasses.map((c) => (
                      <div key={c.clase} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col gap-1.5">
                        <p className="font-black text-xs text-slate-900 capitalize border-b border-slate-200 pb-1">{c.clase}</p>
                        <div className="flex justify-between items-center text-[11px] text-slate-600">
                          <span>{isEs ? 'Sensibilidad:' : 'Sensitivity:'}</span>
                          <span className="font-bold text-emerald-700">{(c.sensibilidad * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between items-center text-[11px] text-slate-600">
                          <span>{isEs ? 'Especificidad Est:' : 'Specificity Est:'}</span>
                          <span className="font-bold text-indigo-700">{(c.especificidad * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between items-center text-[11px] text-slate-600">
                          <span>F1-Score:</span>
                          <span className="font-bold text-slate-800">{c.f1_score.toFixed(3)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Consenso Estadístico (Friedman) */}
              {includeFriedman && previewData.friedman && previewData.friedman.p_valor !== undefined && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                  <span className="text-2xl">🧪</span>
                  <div className="text-xs text-slate-800 leading-relaxed">
                    <p className="font-bold text-slate-950">
                      {isEs ? 'Consenso Estadístico (Test Global de Friedman):' : 'Statistical Consensus (Global Friedman Test):'}
                    </p>
                    <p className="mt-0.5 text-slate-700">
                      Chi-cuadrado: <span className="font-bold">{previewData.friedman.estadistico?.toFixed(4)}</span> | p-valor: <span className="font-bold">{previewData.friedman.p_valor?.toFixed(6)}</span> 
                      ({previewData.friedman.significativo ? (isEs ? 'Diferencia Significativa p < 0.05' : 'Significant Difference p < 0.05') : (isEs ? 'No Significativo' : 'Not Significant')}).
                    </p>
                  </div>
                </div>
              )}

              {/* Observaciones y Firma del Especialista */}
              <div className="border-t-2 border-slate-900/10 pt-6 mt-2 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div className="flex-1">
                  <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-700 mb-1">
                    📌 {isEs ? 'Observaciones Clínicas' : 'Clinical Observations'}
                  </h4>
                  <p className="text-xs text-slate-700 leading-relaxed italic bg-slate-50 p-3 rounded-xl border border-slate-200">
                    "{clinicalNotes}"
                  </p>
                </div>

                <div className="w-full md:w-64 flex flex-col items-center text-center border-t border-slate-400 pt-3">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{isEs ? 'FIRMA DIGITAL VALIDADA' : 'VALIDATED DIGITAL SIGNATURE'}</span>
                  <p className="font-extrabold text-xs text-slate-900">{physicianName}</p>
                  <span className="text-[10px] text-indigo-700 font-bold mt-0.5">{isEs ? 'OcularDiagnose Protocol' : 'OcularDiagnose Protocol'}</span>
                </div>
              </div>

              {/* Pie de Página A4 */}
              <div className="border-t border-slate-200 pt-3 flex justify-between items-center text-[10px] text-slate-400">
                <span>OcularDiagnose Medical Suite v1.0 • Confidential Clinical Document</span>
                <span>Page 1 of 1</span>
              </div>
            </div>
          )}

          {/* MODO CARDS: VISTA EN MÓDULOS INTERACTIVOS */}
          {viewMode === 'cards' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Tarjeta Campeón */}
              <div className="glass-card rounded-3xl p-6 border border-indigo-500/30 flex flex-col justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">🏆</span>
                  <div>
                    <h3 className="font-extrabold text-sm text-foreground">
                      {isEs ? 'Modelo Campeón:' : 'Champion Model:'} {previewData.champion_model.name}
                    </h3>
                    <p className="text-xs text-foreground/60">
                      {isEs ? 'Arquitectura recomendada por mayor precisión global' : 'Recommended architecture for highest global accuracy'}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2.5 bg-foreground/5 rounded-xl border border-card-border">
                    <span className="text-[9px] text-foreground/50 uppercase font-bold block">Accuracy</span>
                    <span className="text-sm font-black text-indigo-500">{(previewData.champion_model.accuracy_media * 100).toFixed(2)}%</span>
                  </div>
                  <div className="p-2.5 bg-foreground/5 rounded-xl border border-card-border">
                    <span className="text-[9px] text-foreground/50 uppercase font-bold block">F1-Score</span>
                    <span className="text-sm font-black text-emerald-500">{previewData.champion_model.f1_score.toFixed(4)}</span>
                  </div>
                  <div className="p-2.5 bg-foreground/5 rounded-xl border border-card-border">
                    <span className="text-[9px] text-foreground/50 uppercase font-bold block">{isEs ? 'Sensibilidad' : 'Recall'}</span>
                    <span className="text-sm font-black text-cyan-500">{(previewData.champion_model.recall * 100).toFixed(2)}%</span>
                  </div>
                </div>
              </div>

              {/* Tarjeta Estadísticas */}
              <div className="glass-card rounded-3xl p-6 border border-card-border flex flex-col justify-between gap-4">
                <div>
                  <h4 className="font-bold text-xs uppercase tracking-wider text-foreground/70 mb-2 flex items-center gap-2">
                    🧪 {isEs ? 'Evaluación de Consenso Estadístico' : 'Statistical Consensus Evaluation'}
                  </h4>
                  <p className="text-xs text-foreground/80 leading-relaxed">
                    {previewData.friedman.interpretacion || (isEs ? 'Modelos evaluados mediante 5-Fold Cross Validation con significancia comprobada.' : 'Models evaluated via 5-Fold Cross Validation with verified significance.')}
                  </p>
                </div>

                <div className="flex justify-between items-center text-xs text-foreground/60 border-t border-card-border pt-3">
                  <span>{isEs ? 'Total de Modelos:' : 'Total Models:'} <strong className="text-foreground">{previewData.total_models}</strong></span>
                  <span>{isEs ? 'Fecha:' : 'Date:'} <strong className="text-foreground">{previewData.generated_at}</strong></span>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : null}

      {/* MODAL FULLSCREEN VISTA PREVIA DIRECTA DEL ARCHIVO PDF OFICIAL */}
      {showPdfModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex flex-col justify-between p-3 md:p-6 overflow-hidden no-print">
          {/* Header del Modal PDF */}
          <div className="flex justify-between items-center bg-slate-900 border border-slate-800 text-white p-4 rounded-2xl shadow-xl max-w-6xl mx-auto w-full mb-3">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📄</span>
              <div>
                <h3 className="font-extrabold text-sm">
                  {isEs ? 'Vista Previa del Reporte PDF Oficial' : 'Official PDF Report Preview'}
                </h3>
                <span className="text-[10px] text-slate-400">
                  {isEs ? 'Documento PDF generado por el servidor, listo para revisión antes de guardar' : 'Server generated PDF document ready for review before saving'}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => triggerDownload('pdf')}
                disabled={downloading['pdf']}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-md"
              >
                <span>📥</span>
                <span>{isEs ? 'Descargar PDF' : 'Download PDF'}</span>
              </button>

              <button
                onClick={closePdfModal}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Visor iframe del PDF Blob */}
          <div className="flex-1 max-w-6xl mx-auto w-full bg-slate-950 rounded-2xl border border-slate-800 p-2 overflow-hidden flex flex-col items-center justify-center">
            {loadingPdfPreview ? (
              <div className="py-20 flex flex-col items-center justify-center gap-3">
                <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-xs text-slate-300 font-semibold">
                  {isEs ? 'Generando archivo PDF oficial y cargando visor...' : 'Generating official PDF file and loading viewer...'}
                </p>
              </div>
            ) : pdfPreviewUrl ? (
              <iframe
                src={pdfPreviewUrl}
                className="w-full h-full rounded-xl border-none shadow-inner"
                title="Vista Previa PDF Documento"
              />
            ) : (
              <p className="text-xs text-rose-400 font-semibold">
                {isEs ? 'No se pudo cargar la vista previa del archivo PDF.' : 'Could not load PDF file preview.'}
              </p>
            )}
          </div>
        </div>
      )}

      {/* MODAL FULLSCREEN DE INSPECCIÓN DE DATOS Y DISEÑO (MODO PANTALLA COMPLETA) */}
      {isFullscreenModal && previewData && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex flex-col justify-between p-4 md:p-8 overflow-y-auto no-print">
          {/* Controls Header */}
          <div className="flex justify-between items-center bg-slate-900 border border-slate-800 text-white p-4 rounded-2xl shadow-xl mb-4 max-w-5xl mx-auto w-full">
            <div className="flex items-center gap-3">
              <span className="text-xl">📄</span>
              <div>
                <h3 className="font-extrabold text-sm">{previewData.title}</h3>
                <span className="text-[10px] text-slate-400">{isEs ? 'Modo de Inspección A4' : 'A4 Inspection Mode'}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 bg-slate-800 p-1 rounded-xl">
                <button
                  onClick={() => setZoomLevel(Math.max(60, zoomLevel - 10))}
                  className="px-2.5 py-1 text-xs font-bold hover:bg-slate-700 rounded-lg cursor-pointer"
                >
                  -
                </button>
                <span className="text-xs font-mono font-bold px-2">{zoomLevel}%</span>
                <button
                  onClick={() => setZoomLevel(Math.min(150, zoomLevel + 10))}
                  className="px-2.5 py-1 text-xs font-bold hover:bg-slate-700 rounded-lg cursor-pointer"
                >
                  +
                </button>
              </div>

              <button
                onClick={handlePrint}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <span>🖨️</span>
                <span>{isEs ? 'Imprimir' : 'Print'}</span>
              </button>

              <button
                onClick={() => setIsFullscreenModal(false)}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Modal Document Body */}
          <div className="flex-1 flex justify-center items-start my-auto py-4">
            <div 
              style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center', transition: 'transform 0.2s ease' }}
              className="max-w-4xl w-full"
            >
              <div className="bg-white text-slate-900 rounded-3xl p-10 border border-slate-300 shadow-2xl flex flex-col gap-6">
                <div className="border-b pb-4 flex justify-between items-center">
                  <h2 className="text-base font-black text-indigo-950 uppercase">{previewData.title}</h2>
                  <span className="text-xs text-slate-500">{previewData.generated_at}</span>
                </div>

                <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100 flex justify-between items-center">
                  <div>
                    <h4 className="font-extrabold text-xs text-indigo-950">🏆 {previewData.champion_model.name}</h4>
                    <p className="text-[11px] text-indigo-800 mt-0.5">Accuracy: {(previewData.champion_model.accuracy_media * 100).toFixed(2)}% | F1: {previewData.champion_model.f1_score.toFixed(4)}</p>
                  </div>
                  <span className="text-xs font-bold text-indigo-600 uppercase">Campeón</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border border-slate-200 rounded-xl">
                    <thead className="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                      <tr>
                        <th className="p-2.5">Modelo</th>
                        <th className="p-2.5">Accuracy</th>
                        <th className="p-2.5">Std Dev</th>
                        <th className="p-2.5">F1-Score</th>
                        <th className="p-2.5">Recall</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-800">
                      {previewData.summary_models.map(m => (
                        <tr key={m.model} className={m.model === previewData.champion_model.name ? 'bg-indigo-50 font-bold' : ''}>
                          <td className="p-2.5">{m.model}</td>
                          <td className="p-2.5">{(m.accuracy_media * 100).toFixed(2)}%</td>
                          <td className="p-2.5">±{m.accuracy_std.toFixed(4)}</td>
                          <td className="p-2.5">{m.f1_score.toFixed(4)}</td>
                          <td className="p-2.5">{(m.recall * 100).toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="border-t pt-4 text-xs text-slate-600 italic">
                  "{clinicalNotes}"
                  <p className="font-extrabold text-slate-900 not-italic mt-2">— {physicianName}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
