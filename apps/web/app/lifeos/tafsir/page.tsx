'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  BookOpen, 
  Sparkles, 
  ChevronRight, 
  ChevronLeft, 
  Compass, 
  CheckCircle2, 
  Share2, 
  Bell, 
  Bookmark, 
  ScrollText,
  HeartHandshake,
  Lightbulb,
  Check,
  Search,
  Sliders,
  Filter
} from 'lucide-react';

interface DailyAyah {
  id: string;
  surah_number: number;
  surah_name: string;
  ayah_number: any;
  theme?: string;
  category?: string;
  arabic: string;
  translation: string;
  scholar_commentary: string;
  hanafi_tafsir?: string;
  why_it_matters_today: string;
  contemporary_relevance?: string;
  practical_implementation: string[];
  actionable_steps?: string[];
  tafsir_source: string;
}

interface DailyHadith {
  id: string;
  collection: string;
  hadith_number: any;
  grade: string;
  narrator: string;
  theme?: string;
  category?: string;
  arabic: string;
  translation: string;
  scholar_commentary: string;
  hanafi_commentary?: string;
  why_it_matters_today: string;
  contemporary_relevance?: string;
  practical_implementation: string[];
  actionable_steps?: string[];
  sharh_source: string;
}

interface TafsirBundle {
  date: string;
  daily_ayah: DailyAyah;
  daily_hadith: DailyHadith;
  total_ayat_available: number;
  total_hadith_available: number;
  categories?: { id: string; name: string }[];
}

const CATEGORIES = [
  { id: 'all', name: 'All Themes' },
  { id: 'hope_and_ease', name: 'Hope & Ease' },
  { id: 'tawakkul_and_rizq', name: 'Tawakkul & Rizq' },
  { id: 'gratitude_and_sabr', name: 'Gratitude & Sabr' },
  { id: 'character_and_akhlaq', name: 'Noble Character' },
  { id: 'knowledge_and_wisdom', name: 'Knowledge & Wisdom' },
  { id: 'mercy_and_tawbah', name: 'Mercy & Forgiveness' },
  { id: 'dua_and_tahajjud', name: "Du'a & Tahajjud" },
  { id: 'family_and_parents', name: 'Parents & Family' },
  { id: 'dhikr_and_peace', name: 'Dhikr & Peace' },
];

export default function TafsirHadithPage() {
  const [activeTab, setActiveTab] = useState<'ayah' | 'hadith' | 'search'>('ayah');
  const [dayOffset, setDayOffset] = useState(0);
  const [bundle, setBundle] = useState<TafsirBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  
  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchResults, setSearchResults] = useState<{ ayat: DailyAyah[]; hadiths: DailyHadith[] }>({ ayat: [], hadiths: [] });
  const [isSearching, setIsSearching] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Record<string, boolean>>({});

  // Restore completed steps from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('lifeos_tafsir_completed_steps');
      if (saved) setCompletedSteps(JSON.parse(saved));
    } catch {}
  }, []);

  const toggleStep = (stepKey: string) => {
    const updated = { ...completedSteps, [stepKey]: !completedSteps[stepKey] };
    setCompletedSteps(updated);
    try {
      localStorage.setItem('lifeos_tafsir_completed_steps', JSON.stringify(updated));
    } catch {}
  };

  const fetchBundle = async (offset: number) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/lifeos/tafsir?offset=${offset}`);
      if (res.ok) {
        const data = await res.json();
        setBundle(data);
      }
    } catch (e) {
      console.error('Failed to load tafsir bundle', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (q: string, cat: string) => {
    if (!q.trim() && cat === 'all') {
      setIsSearching(false);
      return;
    }
    setIsSearching(true);
    try {
      const res = await fetch(`/api/lifeos/tafsir?q=${encodeURIComponent(q)}&category=${cat}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults({ ayat: data.ayat || [], hadiths: data.hadiths || [] });
      }
    } catch (e) {
      console.error('Search error', e);
    }
  };

  useEffect(() => {
    fetchBundle(dayOffset);
  }, [dayOffset]);

  const ayah = bundle?.daily_ayah;
  const hadith = bundle?.daily_hadith;

  const handleShare = () => {
    const textToShare = activeTab === 'ayah' 
      ? `📖 Daily Ayah: Surah ${ayah?.surah_name} (${ayah?.surah_number}:${ayah?.ayah_number})\n\n"${ayah?.translation}"\n\nHanafi Tafsir: ${ayah?.scholar_commentary}`
      : `📜 Sahih Hadith: ${hadith?.collection} (${hadith?.hadith_number})\n\n"${hadith?.translation}"\n\nSharh: ${hadith?.scholar_commentary}`;
    
    if (navigator.clipboard) {
      navigator.clipboard.writeText(textToShare);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6 text-ivory select-none pb-28 scrollbar-none max-w-xl mx-auto w-full">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>
        <div className="text-center">
          <span className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-semibold">
            Verified Hanafi Scholarship
          </span>
          <h1 className="font-serif text-xl text-ivory">Daily Ayah & Hadith</h1>
        </div>
        <button
          onClick={handleShare}
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors text-ivory/80 cursor-pointer"
          title="Share Daily Insight"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
        </button>
      </div>

      {/* Corpus Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search entire Quran & Sahih Hadith corpus..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            handleSearch(e.target.value, selectedCategory);
          }}
          className="w-full bg-surface border border-hairline rounded-2xl pl-10 pr-4 py-2 text-xs text-ivory placeholder:text-muted/60 focus:outline-none focus:border-amber/50"
        />
      </div>

      {/* Thematic Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => {
              setSelectedCategory(cat.id);
              handleSearch(searchQuery, cat.id);
            }}
            className={`px-3 py-1 rounded-full text-[11px] font-medium whitespace-nowrap transition-all cursor-pointer ${
              selectedCategory === cat.id
                ? 'bg-amber text-black font-semibold shadow-sm'
                : 'bg-white/[0.04] text-ivory/70 hover:text-ivory border border-white/5'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Mode Switcher Tabs */}
      <div className="flex items-center gap-2 bg-white/[0.03] p-1 rounded-2xl border border-white/5">
        <button
          onClick={() => {
            setActiveTab('ayah');
            setIsSearching(false);
          }}
          className={`flex-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
            activeTab === 'ayah' && !isSearching
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow-sm'
              : 'text-ivory/50 hover:text-ivory'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Daily Ayah & Tafsir</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('hadith');
            setIsSearching(false);
          }}
          className={`flex-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
            activeTab === 'hadith' && !isSearching
              ? 'bg-amber/20 text-amber border border-amber/30 shadow-sm'
              : 'text-ivory/50 hover:text-ivory'
          }`}
        >
          <ScrollText className="w-3.5 h-3.5" />
          <span>Sahih Hadith & Sharh</span>
        </button>
      </div>

      {/* Date Navigator (Only when viewing daily selection) */}
      {!isSearching && (
        <div className="flex items-center justify-between bg-white/[0.03] p-2 rounded-2xl border border-white/5 text-xs">
          <button
            onClick={() => setDayOffset((prev) => prev - 1)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-ivory/70 transition-all cursor-pointer"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Previous</span>
          </button>

          <span className="font-mono text-ivory/80 text-[11px]">
            {dayOffset === 0 ? "Today's Selection" : dayOffset > 0 ? `+${dayOffset} Days Ahead` : `${Math.abs(dayOffset)} Days Ago`}
          </span>

          <button
            onClick={() => setDayOffset((prev) => prev + 1)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-ivory/70 transition-all cursor-pointer"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* ── SEARCH RESULTS VIEW ── */}
      {isSearching && (
        <div className="space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between text-xs text-muted font-mono">
            <span>Search Results</span>
            <span>{searchResults.ayat.length} Ayat • {searchResults.hadiths.length} Hadiths</span>
          </div>

          {searchResults.ayat.map((a) => (
            <div key={a.id} className="bg-surface border border-emerald-500/20 rounded-3xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                  Surah {a.surah_name} ({a.surah_number}:{a.ayah_number})
                </span>
                {a.theme && <span className="text-[10px] font-mono text-ivory/50">{a.theme}</span>}
              </div>
              <div className="text-right font-serif text-xl leading-relaxed text-ivory">{a.arabic}</div>
              <p className="text-xs font-serif italic text-ivory/90 leading-relaxed">"{a.translation}"</p>
              <p className="text-xs text-ivory/70 font-sans border-t border-white/5 pt-2">{a.scholar_commentary || a.hanafi_tafsir}</p>
            </div>
          ))}

          {searchResults.hadiths.map((h) => (
            <div key={h.id} className="bg-surface border border-amber/20 rounded-3xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-amber font-semibold bg-amber/10 px-2.5 py-0.5 rounded-full border border-amber/30">
                  {h.collection} #{h.hadith_number} • {h.grade}
                </span>
                <span className="text-[10px] font-mono text-ivory/50">Narrated by {h.narrator}</span>
              </div>
              <div className="text-right font-serif text-xl leading-relaxed text-ivory">{h.arabic}</div>
              <p className="text-xs font-serif italic text-ivory/90 leading-relaxed">"{h.translation}"</p>
              <p className="text-xs text-ivory/70 font-sans border-t border-white/5 pt-2">{h.scholar_commentary || h.hanafi_commentary}</p>
            </div>
          ))}
        </div>
      )}

      {/* ── DAILY AYAH VIEW ── */}
      {!isSearching && activeTab === 'ayah' && ayah && (
        <div className="space-y-4 animate-in fade-in duration-300">
          {/* Main Ayah Card */}
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-950/40 via-white/[0.03] to-transparent border border-emerald-500/20 p-6 space-y-4 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-emerald-400 uppercase tracking-widest bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30">
                Surah {ayah.surah_name} • Verse {ayah.ayah_number}
              </span>
              <span className="text-[11px] font-mono text-ivory/40">Surah #{ayah.surah_number}</span>
            </div>

            {/* Arabic Script */}
            <div className="text-right font-serif text-2xl leading-[2.2] text-ivory tracking-wide border-b border-white/5 pb-4 pt-2">
              {ayah.arabic}
            </div>

            {/* English Translation */}
            <div className="space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-ivory/40">English Translation</span>
              <p className="text-sm font-serif italic text-ivory/90 leading-relaxed">
                "{ayah.translation}"
              </p>
            </div>
          </div>

          {/* Classical Hanafi Scholarly Tafsir Card */}
          <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider">
              <Compass className="w-4 h-4" />
              <span>Classical Hanafi Commentary</span>
            </div>
            <p className="text-xs text-ivory/80 leading-relaxed font-sans">
              {ayah.scholar_commentary || ayah.hanafi_tafsir}
            </p>
            <div className="pt-1 text-[10px] font-mono text-emerald-400/60 flex items-center gap-1">
              <span>Source:</span>
              <span className="text-ivory/60">{ayah.tafsir_source}</span>
            </div>
          </div>

          {/* Contemporary Relevance ("Why It Matters Today") */}
          <div className="rounded-3xl bg-amber/5 border border-amber/20 p-5 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-amber uppercase tracking-wider">
              <Lightbulb className="w-4 h-4" />
              <span>Why This Matters Today</span>
            </div>
            <p className="text-xs text-amber-100/90 leading-relaxed">
              {ayah.why_it_matters_today || ayah.contemporary_relevance}
            </p>
          </div>

          {/* Practical Action Steps with Interactive Checkbox */}
          <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-ivory/80 uppercase tracking-wider">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Actionable Implementation in Daily Life</span>
            </div>
            <div className="space-y-2">
              {(ayah.practical_implementation || ayah.actionable_steps || []).map((step, idx) => {
                const stepKey = `${ayah.id}_step_${idx}`;
                const isDone = completedSteps[stepKey];
                return (
                  <div 
                    key={idx} 
                    onClick={() => toggleStep(stepKey)}
                    className={`flex items-start gap-2.5 text-xs leading-relaxed p-3 rounded-2xl border transition-all cursor-pointer select-none ${
                      isDone 
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200 line-through opacity-80' 
                        : 'bg-black/30 border-white/5 text-ivory/80 hover:border-amber/30'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] shrink-0 mt-0.5 transition-all ${
                      isDone ? 'bg-emerald-400 text-black font-bold' : 'bg-white/10 text-ivory/60'
                    }`}>
                      {isDone ? <Check className="w-3 h-3" /> : idx + 1}
                    </div>
                    <span>{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── DAILY HADITH VIEW ── */}
      {!isSearching && activeTab === 'hadith' && hadith && (
        <div className="space-y-4 animate-in fade-in duration-300">
          {/* Main Hadith Card */}
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-amber-950/40 via-white/[0.03] to-transparent border border-amber/30 p-6 space-y-4 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-amber uppercase tracking-widest bg-amber/10 px-2.5 py-1 rounded-full border border-amber/30">
                {hadith.collection} • #{hadith.hadith_number}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {hadith.grade}
              </span>
            </div>

            <div className="text-[11px] font-mono text-ivory/50">
              Narrated by: <span className="text-ivory/80 font-medium">{hadith.narrator}</span>
            </div>

            <div className="text-right font-serif text-2xl leading-[2.2] text-ivory tracking-wide border-b border-white/5 pb-4 pt-1">
              {hadith.arabic}
            </div>

            <div className="space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-ivory/40">English Translation</span>
              <p className="text-sm font-serif italic text-ivory/90 leading-relaxed">
                "{hadith.translation}"
              </p>
            </div>
          </div>

          {/* Classical Scholarly Sharh Card */}
          <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-amber uppercase tracking-wider">
              <Compass className="w-4 h-4" />
              <span>Classical Scholarly Sharh</span>
            </div>
            <p className="text-xs text-ivory/80 leading-relaxed font-sans">
              {hadith.scholar_commentary || hadith.hanafi_commentary}
            </p>
            <div className="pt-1 text-[10px] font-mono text-amber/70 flex items-center gap-1">
              <span>Source:</span>
              <span className="text-ivory/60">{hadith.sharh_source}</span>
            </div>
          </div>

          {/* Modern Practical Significance */}
          <div className="rounded-3xl bg-emerald-950/20 border border-emerald-500/20 p-5 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider">
              <Lightbulb className="w-4 h-4" />
              <span>Modern Practical Significance</span>
            </div>
            <p className="text-xs text-emerald-100/90 leading-relaxed">
              {hadith.why_it_matters_today || hadith.contemporary_relevance}
            </p>
          </div>

          {/* Practical Implementation with Interactive Checkboxes */}
          <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-ivory/80 uppercase tracking-wider">
              <HeartHandshake className="w-4 h-4 text-amber" />
              <span>Implementation in Everyday Life</span>
            </div>
            <div className="space-y-2">
              {(hadith.practical_implementation || hadith.actionable_steps || []).map((step, idx) => {
                const stepKey = `${hadith.id}_step_${idx}`;
                const isDone = completedSteps[stepKey];
                return (
                  <div 
                    key={idx} 
                    onClick={() => toggleStep(stepKey)}
                    className={`flex items-start gap-2.5 text-xs leading-relaxed p-3 rounded-2xl border transition-all cursor-pointer select-none ${
                      isDone 
                        ? 'bg-amber-950/20 border-amber/30 text-amber-200 line-through opacity-80' 
                        : 'bg-black/30 border-white/5 text-ivory/80 hover:border-amber/30'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[10px] shrink-0 mt-0.5 transition-all ${
                      isDone ? 'bg-amber text-black font-bold' : 'bg-white/10 text-ivory/60'
                    }`}>
                      {isDone ? <Check className="w-3 h-3" /> : idx + 1}
                    </div>
                    <span>{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Notification Preferences Footer Link */}
      <div className="rounded-2xl bg-white/[0.02] border border-white/5 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <Bell className="w-4 h-4" />
          </div>
          <div className="space-y-0.5">
            <div className="text-xs font-medium text-ivory">Daily Ayah & Hadith Notifications</div>
            <div className="text-[10px] text-ivory/40">Customizable morning alert with classical wisdom</div>
          </div>
        </div>
        <Link
          href="/settings"
          className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-white/5 hover:bg-white/10 text-amber border border-white/10 transition-all"
        >
          Customize
        </Link>
      </div>
    </div>
  );
}
