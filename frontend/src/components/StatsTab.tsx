/**
 * StatsTab.tsx
 *
 * Según la arquitectura oficial del sistema, las pruebas estadísticas
 * (Friedman, Nemenyi, Wilcoxon, McNemar, Holm-Bonferroni, Cohen's d)
 * forman parte del proceso científico/investigativo y pertenecen
 * exclusivamente al panel de Streamlit.
 *
 * Este componente informa al usuario final que debe acceder al
 * Panel Científico para consultar la validación estadística.
 *
 * Responsabilidad de Next.js: Inferencia clínica para el usuario final.
 * Responsabilidad de Streamlit: Investigación, entrenamiento y validación.
 */
"use client";
import React from 'react';
import { translations } from '../i18n/translations';

interface StatsTabProps {
  language: 'es' | 'en' | 'pt' | 'fr' | 'zh';
  token: string;
  showToast: (msg: string, type: 'success' | 'error' | 'info') => void;
}

/** URL por defecto del panel científico de Streamlit */
const STREAMLIT_URL = 'http://localhost:8501';

export default function StatsTab({ language }: StatsTabProps) {
  const t = translations[language];
  const isEs = language === 'es';

  const layers = [
    {
      icon: '🔬',
      name: isEs ? 'Streamlit — Panel Científico' : 'Streamlit — Scientific Panel',
      color: 'indigo',
      items: isEs
        ? ['Entrenamiento y Cross Validation', 'Friedman · Nemenyi · Wilcoxon', 'McNemar · Holm · Cohen', 'Matrices de confusión · ROC', 'Selección del mejor modelo', 'Reportes científicos']
        : ['Training & Cross Validation', 'Friedman · Nemenyi · Wilcoxon', 'McNemar · Holm · Cohen', 'Confusion matrices · ROC', 'Best model selection', 'Scientific reports'],
    },
    {
      icon: '⚡',
      name: isEs ? 'FastAPI — Inferencia' : 'FastAPI — Inference',
      color: 'emerald',
      items: isEs
        ? ['Carga automática del mejor modelo', 'Endpoints REST', 'Autenticación JWT', 'Grad-CAM y CLAHE', 'Estadísticas para UI']
        : ['Auto-load best model', 'REST Endpoints', 'JWT Authentication', 'Grad-CAM & CLAHE', 'Stats for UI'],
    },
    {
      icon: '🏥',
      name: isEs ? 'Next.js — Usuario Final (aquí)' : 'Next.js — End User (here)',
      color: 'violet',
      items: isEs
        ? ['Subir imágenes oculares', 'Recibir diagnóstico', 'Ver Grad-CAM', 'Descargar reportes clínicos', 'Resultados de comparación']
        : ['Upload eye images', 'Receive diagnosis', 'View Grad-CAM', 'Download clinical reports', 'Comparison results'],
    },
  ];

  const colorMap: Record<string, string> = {
    indigo: 'border-indigo-500/30 bg-indigo-500/5',
    emerald: 'border-emerald-500/30 bg-emerald-500/5',
    violet: 'border-violet-500/30 bg-violet-500/5',
  };

  const badgeMap: Record<string, string> = {
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    violet: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
  };

  return (
    <div className="flex flex-col gap-8">

      {/* Banner principal */}
      <div className="glass-card rounded-3xl p-8 border-2 border-indigo-500/20 flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🏗️</span>
          <div>
            <h2 className="font-extrabold text-foreground text-lg">
              {isEs ? 'Arquitectura del Sistema' : 'System Architecture'}
            </h2>
            <p className="text-xs text-foreground/50 font-bold uppercase tracking-wider mt-0.5">
              {isEs ? 'Separación de responsabilidades' : 'Separation of concerns'}
            </p>
          </div>
        </div>

        <p className="text-sm text-foreground/70 leading-relaxed">
          {isEs
            ? 'Las pruebas estadísticas (Friedman, Nemenyi, Wilcoxon, McNemar, Holm-Bonferroni, Cohen\'s d) forman parte del proceso científico de investigación y pertenecen exclusivamente al Panel Científico de Streamlit. Esta interfaz es exclusivamente para el personal clínico que realiza diagnósticos de pacientes.'
            : 'Statistical tests (Friedman, Nemenyi, Wilcoxon, McNemar, Holm-Bonferroni, Cohen\'s d) are part of the scientific research process and belong exclusively to the Streamlit Scientific Panel. This interface is exclusively for clinical staff performing patient diagnostics.'}
        </p>

        {/* CTA al panel científico */}
        <a
          href={STREAMLIT_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2.5 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-xs uppercase tracking-wider shadow-xl shadow-indigo-600/20 active:scale-[0.98] transition-all w-fit"
        >
          <span>🔬</span>
          {isEs ? 'Abrir Panel Científico (Streamlit)' : 'Open Scientific Panel (Streamlit)'}
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
      </div>

      {/* Diagrama de arquitectura mejorado */}
      <div className="glass-card rounded-3xl p-6 md:p-8 flex flex-col gap-6 border border-card-border/60 shadow-xl">
        <div>
          <h3 className="font-extrabold text-foreground text-base uppercase tracking-wide flex items-center gap-2">
            <span>📐</span> {isEs ? 'Diagrama de Arquitectura & Flujo del Sistema' : 'Official System Architecture & Data Flow'}
          </h3>
          <p className="text-xs text-foreground/60 mt-1 leading-relaxed">
            {isEs
              ? 'Entienda en 3 pasos cómo interactúan el laboratorio científico, el servidor de inferencia y la plataforma clínica.'
              : 'Understand in 3 simple steps how the scientific lab, inference server, and clinical platform interact.'}
          </p>
        </div>

        {/* Flujo de Capas */}
        <div className="flex flex-col gap-4 relative">
          
          {/* Layer 1: Streamlit */}
          <div className="rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-5 flex flex-col gap-3 relative transition-all hover:border-indigo-500/50">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-500/20 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20">🔬</span>
                <div>
                  <h4 className="font-black text-indigo-600 dark:text-indigo-400 text-sm">
                    {isEs ? '1. Streamlit — Panel Científico' : '1. Streamlit — Scientific Panel'}
                  </h4>
                  <p className="text-[11px] text-foreground/60">
                    {isEs ? 'Fase de Experimentación, Validación & Métricas' : 'Experimentation, Validation & Metrics Phase'}
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border border-indigo-500/30">
                {isEs ? 'Fase Científica (Offline)' : 'Scientific Phase (Offline)'}
              </span>
            </div>

            <p className="text-xs text-foreground/75 leading-relaxed">
              {isEs
                ? 'Donde los ingenieros de IA realizan el entrenamiento con Cross-Validation, comparan modelos mediante pruebas no paramétricas (Friedman, Nemenyi, Wilcoxon) y seleccionan el modelo ganador.'
                : 'Where AI engineers perform Cross-Validation training, compare models using non-parametric tests (Friedman, Nemenyi, Wilcoxon), and select the winning champion model.'}
            </p>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {(isEs
                ? ['Entrenamiento K-Fold', 'Friedman & Nemenyi', 'Matrices Confusión & ROC', 'Selección del Mejor Modelo', 'Reportes Científicos']
                : ['K-Fold Training', 'Friedman & Nemenyi', 'Confusion & ROC', 'Best Model Selection', 'Scientific Reports']
              ).map(item => (
                <span key={item} className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-800 dark:text-indigo-200 border border-indigo-500/30">
                  {item}
                </span>
              ))}
            </div>
          </div>

          {/* Flow Indicator 1 -> 2 */}
          <div className="flex items-center justify-center my-1">
            <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-foreground/5 border border-card-border text-[11px] font-bold text-foreground/70 shadow-sm">
              <span className="text-indigo-600 dark:text-indigo-400">⬇️</span>
              <span>{isEs ? 'Genera y guarda artefactos:' : 'Generates & exports artifacts:'}</span>
              <code className="text-[10px] bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/30 font-mono font-bold">best_ocular_model.h5</code>
            </div>
          </div>

          {/* Layer 2: FastAPI */}
          <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5 flex flex-col gap-3 relative transition-all hover:border-emerald-500/50">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-500/20 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20">⚡</span>
                <div>
                  <h4 className="font-black text-emerald-600 dark:text-emerald-400 text-sm">
                    {isEs ? '2. FastAPI — Servidor Backend & Motor de IA' : '2. FastAPI — Backend Server & AI Engine'}
                  </h4>
                  <p className="text-[11px] text-foreground/60">
                    {isEs ? 'Servicio REST de Inferencia en Tiempo Real' : 'Real-time REST Inference Service'}
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">
                {isEs ? 'Capa de Procesamiento (API)' : 'Processing Layer (API)'}
              </span>
            </div>

            <p className="text-xs text-foreground/75 leading-relaxed">
              {isEs
                ? 'El backend asíncrono que carga automáticamente el mejor modelo (.h5), aplica preprocesamiento de contraste CLAHE, calcula mapas térmicos Grad-CAM y responde las peticiones REST.'
                : 'Asynchronous backend that automatically loads the best model (.h5), applies CLAHE contrast preprocessing, calculates Grad-CAM heatmaps, and handles REST requests.'}
            </p>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {(isEs
                ? ['Carga Automática de Pesos (.h5)', 'Endpoints REST / Inferencia', 'Autenticación JWT', 'Mapa Térmico Grad-CAM', 'Mejora de Imagen CLAHE']
                : ['Auto Weight Load (.h5)', 'REST Inference Endpoints', 'JWT Authentication', 'Grad-CAM Heatmap', 'CLAHE Enhancement']
              ).map(item => (
                <span key={item} className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-800 dark:text-emerald-200 border border-emerald-500/30">
                  {item}
                </span>
              ))}
            </div>
          </div>

          {/* Flow Indicator 2 <-> 3 */}
          <div className="flex items-center justify-center my-1">
            <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-foreground/5 border border-card-border text-[11px] font-bold text-foreground/70 shadow-sm">
              <span className="text-emerald-600 dark:text-emerald-400">⇅</span>
              <span>{isEs ? 'Comunicación REST de Alta Velocidad (Solicitud / Respuesta JSON & Grad-CAM)' : 'High-Speed REST Protocol (JSON Request / Response & Grad-CAM)'}</span>
            </div>
          </div>

          {/* Layer 3: Next.js */}
          <div className="rounded-2xl border border-violet-500/40 bg-violet-500/10 p-5 flex flex-col gap-3 relative ring-2 ring-violet-500/20 transition-all hover:border-violet-500/60">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-violet-500/20 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl p-2 rounded-xl bg-violet-500/20 border border-violet-500/30">🏥</span>
                <div>
                  <h4 className="font-black text-violet-700 dark:text-violet-300 text-sm flex items-center gap-2">
                    {isEs ? '3. Next.js — Panel Clínico del Médico' : '3. Next.js — Doctor Clinical Panel'}
                    <span className="text-[9px] px-2 py-0.5 rounded bg-violet-600 text-white dark:bg-violet-500/30 dark:text-violet-200 font-extrabold shadow-sm">
                      {isEs ? 'ESTÁS AQUÍ' : 'YOU ARE HERE'}
                    </span>
                  </h4>
                  <p className="text-[11px] text-foreground/60">
                    {isEs ? 'Interfaz Médica para la Atención y Diagnóstico de Pacientes' : 'Medical UI for Patient Care & Diagnosis'}
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full bg-violet-500/20 text-violet-700 dark:text-violet-200 border border-violet-500/30">
                {isEs ? 'Frontend Usuario Final' : 'End User Frontend'}
              </span>
            </div>

            <p className="text-xs text-foreground/75 leading-relaxed">
              {isEs
                ? 'Plataforma clínica en tiempo real diseñada para oftalmólogos. Permite cargar retinografías, inspeccionar zonas lesionadas con el visor comparativo CLAHE/Grad-CAM y generar fichas clínicas en PDF.'
                : 'Real-time clinical platform designed for ophthalmologists. Allows uploading fundus photos, inspecting lesion zones with CLAHE/Grad-CAM viewers, and generating PDF clinical cards.'}
            </p>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {(isEs
                ? ['Diagnóstico Inmediato', 'Visor Interactivo Grad-CAM', 'Fichas Clínicas en PDF', 'Asistente Médico IA (Chat)', 'Comparativa Visual']
                : ['Immediate Diagnosis', 'Interactive Grad-CAM Viewer', 'PDF Clinical Reports', 'AI Medical Assistant', 'Visual Comparison']
              ).map(item => (
                <span key={item} className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-violet-500/15 text-violet-800 dark:text-violet-200 border border-violet-500/30">
                  {item}
                </span>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Qué hace cada sección del panel científico */}
      <div className="glass-card rounded-3xl p-6 flex flex-col gap-4">
        <h3 className="font-bold text-foreground text-sm uppercase tracking-wide border-b border-card-border pb-3 flex items-center gap-2">
          🔬 {isEs ? '¿Qué encontrará en el Panel Científico?' : 'What does the Scientific Panel contain?'}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              emoji: '📊', title: isEs ? 'EDA y Limpieza' : 'EDA & Cleaning',
              desc: isEs ? 'Análisis exploratorio del dataset, detección de imágenes corruptas, distribución de clases.' : 'Dataset exploratory analysis, corrupt image detection, class distribution.'
            },
            {
              emoji: '⚙️', title: isEs ? 'Ajuste de Hiperparámetros' : 'Hyperparameter Tuning',
              desc: isEs ? 'Búsqueda sistemática de learning rate, dropout y optimizador.' : 'Systematic search for learning rate, dropout, and optimizer.'
            },
            {
              emoji: '🔄', title: isEs ? 'Entrenamiento & Cross Validation' : 'Training & Cross Validation',
              desc: isEs ? '5 modelos (3 clásicos + 2 híbridos) con K-Fold estratificado, curvas ROC, matrices de confusión.' : '5 models (3 classic + 2 hybrid) with stratified K-Fold, ROC curves, confusion matrices.'
            },
            {
              emoji: '🧪', title: isEs ? 'Pruebas Estadísticas Completas' : 'Complete Statistical Tests',
              desc: isEs ? 'Friedman, Nemenyi, Wilcoxon, t-Student, McNemar, Shapiro-Wilk, Holm-Bonferroni, Cohen\'s d con interpretación automática.' : 'Friedman, Nemenyi, Wilcoxon, t-Student, McNemar, Shapiro-Wilk, Holm-Bonferroni, Cohen\'s d with automatic interpretation.'
            },
            {
              emoji: '🏆', title: isEs ? 'Selección del Mejor Modelo' : 'Best Model Selection',
              desc: isEs ? 'Identificación del modelo campeón con métricas completas y pruebas estadísticas que respaldan la decisión.' : 'Champion model identification with complete metrics and supporting statistical evidence.'
            },
            {
              emoji: '📤', title: isEs ? 'Reportes Científicos' : 'Scientific Reports',
              desc: isEs ? 'Exportación de reportes en PDF, Word y Excel con todos los resultados estadísticos.' : 'Export reports in PDF, Word, and Excel with all statistical results.'
            },
          ].map(item => (
            <div key={item.title} className="flex gap-3 p-3 rounded-xl bg-foreground/3 border border-card-border">
              <span className="text-xl shrink-0">{item.emoji}</span>
              <div>
                <p className="font-bold text-foreground text-xs">{item.title}</p>
                <p className="text-[11px] text-foreground/55 mt-0.5 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
