"use client";
import React, { useState, useRef, useEffect } from 'react';

export type SupportedLanguage = 'es' | 'en' | 'pt' | 'fr' | 'zh';

interface LanguageSelectorProps {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
}

const LANGUAGES = [
  { code: 'es', label: 'Español', img: '/img/spain.png' },
  { code: 'en', label: 'English', img: '/img/united-states.png' },
  { code: 'pt', label: 'Português', img: '/img/brazil-.png' },
  { code: 'fr', label: 'Français', img: '/img/france.png' },
  { code: 'zh', label: '中文', img: '/img/china.png' },
] as const;

export default function LanguageSelector({ language, setLanguage }: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        className="flex items-center gap-2 bg-card-bg border border-card-border px-3 py-1.5 rounded-xl text-sm font-medium text-foreground hover:bg-foreground/5 transition-colors focus:outline-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <img src={currentLang.img} alt={currentLang.label} className="w-5 h-5 object-cover rounded-full shadow-sm" />
        <span className="hidden sm:inline">{currentLang.label}</span>
        <svg className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 origin-top-right rounded-xl bg-card-bg border border-card-border shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50 overflow-hidden">
          <div className="py-1">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code as SupportedLanguage);
                  setIsOpen(false);
                }}
                className={`flex w-full items-center gap-3 px-4 py-2 text-sm transition-colors hover:bg-indigo-50 hover:text-indigo-700 dark:hover:bg-indigo-900/30 dark:hover:text-indigo-300 ${
                  language === lang.code ? 'bg-indigo-50/50 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400 font-semibold' : 'text-foreground'
                }`}
              >
                <img src={lang.img} alt={lang.label} className="w-5 h-5 object-cover rounded-full shadow-sm" />
                {lang.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
