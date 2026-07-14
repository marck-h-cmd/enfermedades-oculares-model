"use client";
import React from 'react';

interface LanguageSelectorProps {
  language: 'es' | 'en';
  setLanguage: (lang: 'es' | 'en') => void;
}

export default function LanguageSelector({ language, setLanguage }: LanguageSelectorProps) {
  return (
    <div className="flex bg-card-bg border border-card-border p-1 rounded-xl gap-1">
      <button
        onClick={() => setLanguage('es')}
        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
          language === 'es' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground hover:bg-foreground/5'
        }`}
      >
        🇪🇸 ES
      </button>
      <button
        onClick={() => setLanguage('en')}
        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
          language === 'en' ? 'bg-indigo-600 text-white shadow-sm' : 'text-foreground hover:bg-foreground/5'
        }`}
      >
        🇬🇧 EN
      </button>
    </div>
  );
}
