'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Phone,
  Sparkles,
  Compass,
  Type,
  X,
  Check,
  Heart,
  Palette,
  BarChart3,
  Moon,
  Sun,
  Flame,
} from 'lucide-react';

interface HeaderProps {
  onDevModeTrigger?: () => void;
}

const THEMES = [
  { id: 'theme-default', name: 'Emerald Gold', class: '', color: '#D4A853', rgb: '212, 168, 83', dark: '#A07A30', bg: '#0A0B09', deep: '#111210', surface: '#181917', raised: '#21221F', dot: 'bg-amber' },
  { id: 'theme-sakura', name: 'Sakura Kawaii', class: 'theme-sakura', color: '#F472B6', rgb: '244, 114, 182', dark: '#DB2777', bg: '#140810', deep: '#1C0D18', surface: '#271422', raised: '#341C2E', dot: 'bg-pink-400' },
  { id: 'theme-emerald', name: 'Deep Oasis', class: 'theme-emerald', color: '#10B981', rgb: '16, 185, 129', dark: '#059669', bg: '#040D09', deep: '#081611', surface: '#0E2019', raised: '#152C23', dot: 'bg-emerald-400' },
  { id: 'theme-obsidian', name: 'Obsidian Silver', class: 'theme-obsidian', color: '#E2E8F0', rgb: '226, 232, 240', dark: '#94A3B8', bg: '#000000', deep: '#080808', surface: '#121212', raised: '#1C1C1C', dot: 'bg-slate-300' },
  { id: 'theme-indigo', name: 'Royal Indigo', class: 'theme-indigo', color: '#818CF8', rgb: '129, 140, 248', dark: '#4F46E5', bg: '#070914', deep: '#0C1021', surface: '#13172E', raised: '#1B2140', dot: 'bg-indigo-400' },
  { id: 'theme-amber', name: 'Cyber Amber', class: 'theme-amber', color: '#F59E0B', rgb: '245, 158, 11', dark: '#D97706', bg: '#0E0B07', deep: '#16120C', surface: '#211C13', raised: '#2D261B', dot: 'bg-amber-500' },
];

const FONTS = [
  { id: 'font-jakarta', name: 'Plus Jakarta Sans', family: "'Plus Jakarta Sans', sans-serif", preview: 'Modern Clean' },
  { id: 'font-inter', name: 'Inter', family: "'Inter', sans-serif", preview: 'Neutral Sans' },
  { id: 'font-outfit', name: 'Outfit', family: "'Outfit', sans-serif", preview: 'Geometric Sans' },
  { id: 'font-serif', name: 'Instrument Serif', family: "'Instrument Serif', serif", preview: 'Editorial Luxury' },
  { id: 'font-amiri', name: 'Amiri (Arabic)', family: "'Amiri', serif", preview: 'Calligraphic Arabic' },
  { id: 'font-mono', name: 'JetBrains Mono', family: "'JetBrains Mono', monospace", preview: 'Technical Mono' },
];

const FONT_SCALES = [
  { id: 'scale-sm', label: 'Small', value: '0.88', pct: '88%' },
  { id: 'scale-md', label: 'Normal', value: '1.0', pct: '100%' },
  { id: 'scale-lg', label: 'Large', value: '1.12', pct: '112%' },
  { id: 'scale-xl', label: 'Extra Large', value: '1.25', pct: '125%' },
];

const REGION_TZ_MAP: Record<string, { tz: string; code: string }> = {
  UK: { tz: 'Europe/London', code: 'BST' },
  PK: { tz: 'Asia/Karachi', code: 'PKT' },
  US_EAST: { tz: 'America/New_York', code: 'ET' },
  US_WEST: { tz: 'America/Los_Angeles', code: 'PT' },
  CA: { tz: 'America/Toronto', code: 'ET' },
  MU: { tz: 'Indian/Mauritius', code: 'MUT' },
  AE: { tz: 'Asia/Dubai', code: 'GST' },
  SA: { tz: 'Asia/Riyadh', code: 'AST' },
  EU: { tz: 'Europe/Berlin', code: 'CET' },
  IN: { tz: 'Asia/Kolkata', code: 'IST' },
  MY: { tz: 'Asia/Kuala_Lumpur', code: 'MYT' },
  AU: { tz: 'Australia/Sydney', code: 'AEST' },
};

export default function Header({ onDevModeTrigger }: HeaderProps) {
  const [tapCount, setTapCount] = useState(0);
  const [isFontModalOpen, setIsFontModalOpen] = useState(false);
  const [activeTheme, setActiveTheme] = useState('theme-default');
  const [activeFont, setActiveFont] = useState('font-jakarta');
  const [activeScale, setActiveScale] = useState('scale-md');
  const [isKawaiiMode, setIsKawaiiMode] = useState(false);
  const [regionTime, setRegionTime] = useState('');
  const [presenceState, setPresenceState] = useState('awake');

  const pathname = usePathname();
  const isLifeOS = pathname.startsWith('/lifeos');

  useEffect(() => {
    // Load persisted settings
    const savedTheme = localStorage.getItem('alisha_active_theme') || 'theme-default';
    const savedFont = localStorage.getItem('alisha_active_font') || 'font-jakarta';
    const savedScale = localStorage.getItem('alisha_active_scale') || 'scale-md';
    const savedKawaii = localStorage.getItem('alisha_kawaii_mode') === 'true';

    setActiveTheme(savedTheme);
    setActiveFont(savedFont);
    setActiveScale(savedScale);
    setIsKawaiiMode(savedKawaii);

    applyThemeAndTypography(savedTheme, savedFont, savedScale, savedKawaii);

    const updateTime = () => {
      const region = localStorage.getItem('alisha_user_region') || 'PK';
      const info = REGION_TZ_MAP[region] || REGION_TZ_MAP['PK'];
      try {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {
          timeZone: info.tz,
          hour: '2-digit',
          minute: '2-digit',
          hour12: false,
        });
        const hour = parseInt(
          now.toLocaleTimeString('en-US', { timeZone: info.tz, hour: 'numeric', hour12: false }),
          10
        );
        const pres = (hour >= 1 && hour <= 5) ? 'sleeping' : (hour >= 6 && hour <= 8) ? 'waking up' : 'awake';
        setRegionTime(`${timeStr} ${info.code}`);
        setPresenceState(pres);
      } catch (e) {
        setRegionTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
      }
    };

    updateTime();
    const interval = setInterval(updateTime, 10000);
    window.addEventListener('storage', updateTime);
    window.addEventListener('alisha_region_change', updateTime);
    return () => {
      clearInterval(interval);
      window.removeEventListener('storage', updateTime);
      window.removeEventListener('alisha_region_change', updateTime);
    };
  }, []);

  const applyThemeAndTypography = (themeId: string, fontId: string, scaleId: string, kawaii: boolean) => {
    const fontObj = FONTS.find((f) => f.id === fontId) || FONTS[0];
    const scaleObj = FONT_SCALES.find((s) => s.id === scaleId) || FONT_SCALES[1];
    const targetThemeId = kawaii ? 'theme-sakura' : themeId;
    const themeObj = THEMES.find((t) => t.id === targetThemeId) || THEMES[0];

    if (typeof document !== 'undefined') {
      // Remove all prior theme classes
      THEMES.forEach((t) => {
        if (t.class) document.documentElement.classList.remove(t.class);
      });
      document.documentElement.classList.remove('kawaii-theme');

      if (kawaii) {
        document.documentElement.classList.add('kawaii-theme');
      } else if (themeObj.class) {
        document.documentElement.classList.add(themeObj.class);
      }

      // Direct CSS Variable Injection
      const rootEl = document.documentElement;
      rootEl.style.setProperty('--theme-accent', themeObj.color);
      rootEl.style.setProperty('--theme-accent-rgb', themeObj.rgb);
      rootEl.style.setProperty('--theme-accent-dark', themeObj.dark);
      rootEl.style.setProperty('--theme-bg', themeObj.bg);
      rootEl.style.setProperty('--theme-deep', themeObj.deep);
      rootEl.style.setProperty('--theme-surface-solid', themeObj.surface);
      rootEl.style.setProperty('--theme-raised', themeObj.raised);
      rootEl.style.setProperty('--font-custom', fontObj.family);
      rootEl.style.setProperty('--font-scale', scaleObj.value);

      document.body.style.backgroundColor = themeObj.bg;
      document.body.style.fontFamily = fontObj.family;
      document.body.style.fontSize = `${Number(scaleObj.value) * 16}px`;

      window.dispatchEvent(new CustomEvent('alisha_theme_applied', { detail: { theme: themeObj, isKawaii: kawaii } }));
    }
  };

  const handleThemeChange = (themeId: string) => {
    setActiveTheme(themeId);
    localStorage.setItem('alisha_active_theme', themeId);
    applyThemeAndTypography(themeId, activeFont, activeScale, isKawaiiMode);
  };

  const handleFontChange = (fontId: string) => {
    setActiveFont(fontId);
    localStorage.setItem('alisha_active_font', fontId);
    applyThemeAndTypography(activeTheme, fontId, activeScale, isKawaiiMode);
  };

  const handleScaleChange = (scaleId: string) => {
    setActiveScale(scaleId);
    localStorage.setItem('alisha_active_scale', scaleId);
    applyThemeAndTypography(activeTheme, activeFont, scaleId, isKawaiiMode);
  };

  const handleKawaiiToggle = () => {
    const next = !isKawaiiMode;
    setIsKawaiiMode(next);
    localStorage.setItem('alisha_kawaii_mode', next ? 'true' : 'false');
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('alisha_kawaii_change', { detail: { isKawaii: next } }));
    }
    applyThemeAndTypography(activeTheme, activeFont, activeScale, next);
  };

  const handleTitleClick = () => {
    const nextCount = tapCount + 1;
    setTapCount(nextCount);
    if (nextCount >= 7) {
      setTapCount(0);
      if (onDevModeTrigger) {
        onDevModeTrigger();
      } else {
        alert("Dev Mode: Telemetry & Model Diagnostics Unlocked");
      }
    }
  };

  return (
    <>
      <header className="h-[60px] w-full border-b border-white/[0.06] bg-deep/90 backdrop-blur-md z-40 shrink-0 select-none">
        <div className="max-w-6xl mx-auto h-full px-4 sm:px-6 md:px-8 flex items-center justify-between">
          <div
            onClick={handleTitleClick}
            className="flex items-center gap-2.5 cursor-pointer transition-opacity hover:opacity-90 truncate"
          >
            <span
              className={`w-[8px] h-[8px] rounded-full inline-block shrink-0 ${
                isKawaiiMode
                  ? 'bg-pink-400 shadow-[0_0_8px_#f472b6] animate-pulse'
                  : isLifeOS
                  ? 'bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse'
                  : 'bg-amber shadow-[0_0_8px_#D4A853] animate-pulse-amber'
              }`}
            />
            <div className="flex flex-col min-w-0">
              <span className="font-serif text-[17px] sm:text-[19px] tracking-wide text-ivory leading-tight truncate">
                {isLifeOS ? 'Islamic LifeOS' : 'alisha bubbzieee'}
              </span>
              <span className="text-[10px] font-mono text-muted/80 leading-tight">
                {presenceState} • {regionTime || '23:08 PKT'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Analytics Dashboard Link */}
            <Link
              href="/lifeos/history"
              className="w-8 h-8 rounded-full bg-white/[0.05] hover:bg-white/10 text-ivory/80 flex items-center justify-center border border-white/10 transition-all hover:scale-105"
              title="Spiritual & Focus Analytics Dashboard"
            >
              <BarChart3 className="w-3.5 h-3.5 text-amber" />
            </Link>

            {/* Theme & Customizer Button */}
            <button
              onClick={() => setIsFontModalOpen(true)}
              className="w-8 h-8 rounded-full bg-white/[0.05] hover:bg-white/10 text-ivory/80 flex items-center justify-center border border-white/10 transition-all hover:scale-105"
              title="Customize Theme & Fonts"
            >
              <Palette className="w-3.5 h-3.5" />
            </button>

            {isLifeOS ? (
              <Link
                href="/chat"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-white/[0.05] hover:bg-white/[0.1] text-amber border border-amber/20 transition-all hover:scale-[1.02]"
                title="Switch to ALISHA BUBBZIEEE"
              >
                <Sparkles className="w-3 h-3" />
                <span className="text-[11px] font-semibold">ALISHA BUBBZIEEE</span>
              </Link>
            ) : (
              <Link
                href="/lifeos"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950/40 hover:bg-emerald-900/40 text-emerald-400 border border-emerald-500/20 transition-all hover:scale-[1.02]"
                title="Open Islamic LifeOS"
              >
                <Compass className="w-3 h-3" />
                <span className="text-[11px] font-semibold">LifeOS</span>
              </Link>
            )}

            {!isLifeOS && (
              <Link
                href="/call"
                className="p-1.5 rounded-full text-muted hover:text-ivory hover:bg-surface transition-colors"
                title="Voice Call"
              >
                <Phone className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Theme Studio & Customization Modal */}
      {isFontModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-sm max-h-[90vh] overflow-y-auto bg-[#121310] border border-white/10 rounded-3xl p-5 space-y-5 shadow-2xl animate-scale-in scrollbar-none text-ivory">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Palette className="w-4 h-4 text-amber" />
                <h3 className="font-serif text-lg text-ivory">Theme & Personalization</h3>
              </div>
              <button
                onClick={() => setIsFontModalOpen(false)}
                className="text-ivory/50 hover:text-ivory p-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>


            {/* Color Palette Selector */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block">
                Color Palette Theme
              </span>
              <div className="grid grid-cols-2 gap-2">
                {THEMES.map((t) => {
                  const isSelected = activeTheme === t.id && !isKawaiiMode;
                  return (
                    <button
                      key={t.id}
                      onClick={() => handleThemeChange(t.id)}
                      className={`p-2.5 rounded-xl border flex items-center gap-2.5 text-left transition-all ${
                        isSelected
                          ? 'bg-white/10 border-amber/50 shadow-[0_0_12px_rgba(212,168,83,0.15)] text-ivory'
                          : 'bg-white/[0.03] border-white/5 hover:bg-white/[0.06] text-ivory/80'
                      }`}
                    >
                      <div className={`w-3.5 h-3.5 rounded-full shrink-0 ${t.dot}`} />
                      <span className="text-xs font-medium truncate">{t.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Font Family Selector */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block">
                Font Family
              </span>
              <div className="space-y-1.5">
                {FONTS.map((f) => {
                  const isSelected = activeFont === f.id;
                  return (
                    <button
                      key={f.id}
                      onClick={() => handleFontChange(f.id)}
                      className={`w-full p-2.5 rounded-xl border flex items-center justify-between text-left transition-all ${
                        isSelected
                          ? 'bg-amber/20 border-amber/40 text-amber'
                          : 'bg-white/[0.03] border-white/5 hover:bg-white/[0.06] text-ivory/80'
                      }`}
                      style={{ fontFamily: f.family }}
                    >
                      <div className="min-w-0">
                        <div className="text-sm font-medium">{f.name}</div>
                        <span className="text-[10px] text-ivory/40 block font-sans">{f.preview}</span>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-amber shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Font Scaling Selector */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block">
                Font Size Scaling
              </span>
              <div className="grid grid-cols-4 gap-1.5">
                {FONT_SCALES.map((s) => {
                  const isSelected = activeScale === s.id;
                  return (
                    <button
                      key={s.id}
                      onClick={() => handleScaleChange(s.id)}
                      className={`py-2 rounded-xl text-xs font-mono font-medium border text-center transition-all ${
                        isSelected
                          ? 'bg-amber text-black border-amber font-bold'
                          : 'bg-white/5 border-white/10 text-ivory/70 hover:bg-white/10'
                      }`}
                    >
                      <span className="block text-[10px]">{s.label}</span>
                      <span className="text-[9px] opacity-70">{s.pct}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              onClick={() => setIsFontModalOpen(false)}
              className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-ivory font-semibold text-xs transition-all active:scale-95"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </>
  );
}

