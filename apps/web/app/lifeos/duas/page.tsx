'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  HeartHandshake,
  ArrowLeft,
  Search,
  Copy,
  Check,
  ShieldCheck,
  Sparkles,
  Star,
  Volume2,
  RotateCcw,
  BookOpen,
  Compass,
  Coins,
  Activity,
  Moon,
  Sun,
  Users,
  Navigation,
  Shield,
  Heart,
  ChevronDown,
  ChevronUp,
  Bookmark,
  BookmarkCheck,
  SlidersHorizontal,
  X,
  VolumeX
} from 'lucide-react';

interface CategoryMeta {
  id: string;
  name: string;
  name_ar: string;
  icon?: string;
  count?: number;
}

interface DuaItem {
  id: string;
  title: string;
  category: string;
  category_name?: string;
  category_ar?: string;
  arabic: string;
  transliteration: string;
  translation: string;
  source_type: string;
  source_reference: string;
  authenticity_grade: string;
  recommended_context: string;
  repeat_count: number;
  notes: string;
}

export default function DuasPage() {
  const [duas, setDuas] = useState<DuaItem[]>([]);
  const [categories, setCategories] = useState<CategoryMeta[]>([]);
  const [featuredDua, setFeaturedDua] = useState<DuaItem | null>(null);
  const [selectedCat, setSelectedCat] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Interactive Repetition Tracker: { [dua_id]: count }
  const [counters, setCounters] = useState<Record<string, number>>({});
  
  // Bookmarks / Saved Duas
  const [bookmarks, setBookmarks] = useState<string[]>([]);
  
  // UI Display Options
  const [arabicFontSize, setArabicFontSize] = useState<'normal' | 'large' | 'xlarge'>('large');
  const [showTransliteration, setShowTransliteration] = useState<boolean>(true);
  const [expandedNotes, setExpandedNotes] = useState<Record<string, boolean>>({});

  // Load bookmarks & saved counters from localStorage on mount
  useEffect(() => {
    try {
      const savedBm = localStorage.getItem('alisha_duas_bookmarks');
      if (savedBm) setBookmarks(JSON.parse(savedBm));

      const savedCounters = localStorage.getItem('alisha_duas_counters');
      if (savedCounters) setCounters(JSON.parse(savedCounters));

      const savedSize = localStorage.getItem('alisha_duas_font_size');
      if (savedSize) setArabicFontSize(savedSize as any);
    } catch (e) {
      console.warn('Could not read local storage for duas preferences', e);
    }
  }, []);

  // Persist bookmarks
  const toggleBookmark = (id: string) => {
    setBookmarks((prev) => {
      const next = prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id];
      try {
        localStorage.setItem('alisha_duas_bookmarks', JSON.stringify(next));
      } catch (e) {}
      return next;
    });
  };

  // Increment counter for a specific dua
  const handleIncrement = (dua: DuaItem) => {
    setCounters((prev) => {
      const current = prev[dua.id] || 0;
      const target = dua.repeat_count || 1;
      const nextCount = current >= target ? 0 : current + 1;
      const next = { ...prev, [dua.id]: nextCount };
      try {
        localStorage.setItem('alisha_duas_counters', JSON.stringify(next));
      } catch (e) {}
      return next;
    });
  };

  const handleResetCounter = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setCounters((prev) => {
      const next = { ...prev, [id]: 0 };
      try {
        localStorage.setItem('alisha_duas_counters', JSON.stringify(next));
      } catch (e) {}
      return next;
    });
  };

  const toggleNotes = (id: string) => {
    setExpandedNotes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const fetchDuas = async () => {
    try {
      const q = new URLSearchParams();
      if (selectedCat !== 'all' && selectedCat !== 'saved') {
        q.set('category', selectedCat);
      }
      if (searchQuery.trim()) {
        q.set('q', searchQuery.trim());
      }

      const res = await fetch(`/api/lifeos/duas?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setDuas(data.duas || []);
        if (data.categories_detailed) {
          setCategories(data.categories_detailed);
        }
        if (data.featured) {
          setFeaturedDua(data.featured);
        }
      }
    } catch (e) {
      console.warn('Failed fetching duas from API, keeping existing state', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDuas();
  }, [selectedCat, searchQuery]);

  const handleCopy = (dua: DuaItem) => {
    const textToCopy = `🤲 ${dua.title}\n\n${dua.arabic}\n\n${dua.transliteration}\n\n"${dua.translation}"\n\n📖 Source: ${dua.source_reference} (${dua.authenticity_grade})\n⏳ Context: ${dua.recommended_context}`;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(textToCopy);
      setCopiedId(dua.id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const handlePlayAudio = (dua: DuaItem) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;

    if (playingId === dua.id) {
      window.speechSynthesis.cancel();
      setPlayingId(null);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(dua.arabic);
    utterance.lang = 'ar-SA';
    utterance.rate = 0.85; // deliberate, reverent pace

    utterance.onend = () => setPlayingId(null);
    utterance.onerror = () => setPlayingId(null);

    setPlayingId(dua.id);
    window.speechSynthesis.speak(utterance);
  };

  // Filtered duas (including Bookmarks tab)
  const displayedDuas = useMemo(() => {
    let list = duas;
    if (selectedCat === 'saved') {
      list = list.filter((d) => bookmarks.includes(d.id));
    }
    return list;
  }, [duas, selectedCat, bookmarks]);

  const renderCategoryIcon = (id: string) => {
    switch (id) {
      case 'all':
        return <Sparkles className="w-3.5 h-3.5" />;
      case 'saved':
        return <Star className="w-3.5 h-3.5" />;
      case 'morning_evening':
        return <Sun className="w-3.5 h-3.5" />;
      case 'anxiety_distress':
        return <HeartHandshake className="w-3.5 h-3.5" />;
      case 'forgiveness_repentance':
        return <ShieldCheck className="w-3.5 h-3.5" />;
      case 'sleep_waking':
        return <Moon className="w-3.5 h-3.5" />;
      case 'guidance_istikhara':
        return <Compass className="w-3.5 h-3.5" />;
      case 'rizq_debt':
        return <Coins className="w-3.5 h-3.5" />;
      case 'health_ruqyah':
        return <Activity className="w-3.5 h-3.5" />;
      case 'knowledge_exams':
      case 'knowledge':
        return <BookOpen className="w-3.5 h-3.5" />;
      case 'family_parents':
        return <Users className="w-3.5 h-3.5" />;
      case 'daily_travel_food':
        return <Navigation className="w-3.5 h-3.5" />;
      case 'patience_protection':
        return <Shield className="w-3.5 h-3.5" />;
      case 'gratitude_praise':
        return <Heart className="w-3.5 h-3.5" />;
      default:
        return <Sparkles className="w-3.5 h-3.5" />;
    }
  };

  const arabicSizeClass =
    arabicFontSize === 'xlarge'
      ? 'text-2xl sm:text-3xl leading-[2.6rem]'
      : arabicFontSize === 'large'
      ? 'text-xl sm:text-2xl leading-[2.3rem]'
      : 'text-lg sm:text-xl leading-loose';

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-32 select-none bg-void text-ivory scrollbar-none">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="flex items-center gap-1.5 text-xs text-muted hover:text-ivory transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          <span>LifeOS Sanctuary</span>
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 font-mono flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" />
            100% Authentic Citations
          </span>
        </div>
      </div>

      {/* Main Header & Subtitle */}
      <div className="space-y-1">
        <div className="flex items-baseline justify-between">
          <h1 className="text-2xl font-serif text-ivory font-bold tracking-tight">
            Curated Duas & Adhkar
          </h1>
          <span className="text-xs font-arabic text-amber/80 font-medium">
            الأدعية المأثورة
          </span>
        </div>
        <p className="text-xs text-muted leading-relaxed">
          Comprehensive, evidence-grounded prophetic & Qur'anic supplications with vocalized Arabic,
          scholarly grading, repetition targets, and practical contexts.
        </p>
      </div>

      {/* Featured Contextual Dua of the Moment */}
      {featuredDua && !searchQuery && selectedCat === 'all' && (
        <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-950/30 via-surface to-surface border border-amber-500/30 shadow-lg space-y-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-amber text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4 animate-pulse" />
              <span>Dua of the Moment • {featuredDua.category_name || 'Recommended'}</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber border border-amber-500/30 font-mono">
              {featuredDua.authenticity_grade}
            </span>
          </div>

          <h2 className="text-sm font-semibold text-ivory font-serif">
            {featuredDua.title}
          </h2>

          {/* Arabic */}
          <p
            dir="rtl"
            className={`font-arabic text-right text-ivory/95 font-medium ${arabicSizeClass} select-text`}
          >
            {featuredDua.arabic}
          </p>

          {/* Transliteration */}
          {showTransliteration && (
            <p className="text-xs font-serif italic text-amber/90 leading-snug">
              {featuredDua.transliteration}
            </p>
          )}

          {/* Translation */}
          <p className="text-xs text-muted/95 leading-relaxed italic">
            &ldquo;{featuredDua.translation}&rdquo;
          </p>

          {/* Actions & Repetition bar for Featured Dua */}
          <div className="pt-2 border-t border-hairline/80 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleIncrement(featuredDua)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all border ${
                  (counters[featuredDua.id] || 0) >= (featuredDua.repeat_count || 1)
                    ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40'
                    : 'bg-surface text-ivory border-hairline hover:border-amber-500/40'
                }`}
              >
                <span>Recited</span>
                <span className="font-mono font-bold">
                  {counters[featuredDua.id] || 0} / {featuredDua.repeat_count || 1}
                </span>
                {(counters[featuredDua.id] || 0) >= (featuredDua.repeat_count || 1) && (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </button>

              {(counters[featuredDua.id] || 0) > 0 && (
                <button
                  onClick={(e) => handleResetCounter(featuredDua.id, e)}
                  className="p-1.5 rounded-lg text-tertiary hover:text-ivory transition-colors"
                  title="Reset counter"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => handlePlayAudio(featuredDua)}
                className={`p-1.5 rounded-xl border transition-colors ${
                  playingId === featuredDua.id
                    ? 'bg-amber text-void border-amber'
                    : 'bg-surface text-tertiary hover:text-ivory border-hairline'
                }`}
                title="Listen to pronunciation"
              >
                {playingId === featuredDua.id ? (
                  <VolumeX className="w-4 h-4 animate-pulse" />
                ) : (
                  <Volume2 className="w-4 h-4" />
                )}
              </button>

              <button
                onClick={() => toggleBookmark(featuredDua.id)}
                className="p-1.5 rounded-xl bg-surface border border-hairline text-tertiary hover:text-amber transition-colors"
                title="Save Dua"
              >
                {bookmarks.includes(featuredDua.id) ? (
                  <BookmarkCheck className="w-4 h-4 text-amber fill-amber/20" />
                ) : (
                  <Bookmark className="w-4 h-4" />
                )}
              </button>

              <button
                onClick={() => handleCopy(featuredDua)}
                className="p-1.5 rounded-xl bg-surface border border-hairline text-tertiary hover:text-ivory transition-colors"
                title="Copy Dua"
              >
                {copiedId === featuredDua.id ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search & Customization Control Bar */}
      <div className="space-y-2">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 absolute left-3 text-muted pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by keyword, English translation, Arabic, or reference..."
            className="w-full bg-surface border border-hairline/90 rounded-2xl pl-9 pr-8 py-2.5 text-xs text-ivory placeholder-muted focus:border-amber-400/80 outline-none transition-all shadow-inner"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 text-muted hover:text-ivory"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Font & Transliteration Controls Bar */}
        <div className="flex items-center justify-between text-[11px] text-muted px-1">
          <div className="flex items-center gap-1.5">
            <span className="text-tertiary">Arabic Size:</span>
            {(['normal', 'large', 'xlarge'] as const).map((size) => (
              <button
                key={size}
                onClick={() => {
                  setArabicFontSize(size);
                  try {
                    localStorage.setItem('alisha_duas_font_size', size);
                  } catch (e) {}
                }}
                className={`px-2 py-0.5 rounded-md capitalize font-mono text-[10px] transition-all border ${
                  arabicFontSize === size
                    ? 'bg-amber/20 text-amber border-amber/40 font-bold'
                    : 'bg-surface text-muted border-hairline/60 hover:text-ivory'
                }`}
              >
                {size === 'normal' ? 'A' : size === 'large' ? 'A+' : 'A++'}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowTransliteration(!showTransliteration)}
            className={`px-2.5 py-0.5 rounded-md text-[10px] font-medium transition-all border ${
              showTransliteration
                ? 'bg-surface text-ivory border-hairline'
                : 'bg-surface/50 text-muted border-hairline/40 line-through'
            }`}
          >
            {showTransliteration ? 'Transliteration ON' : 'Transliteration OFF'}
          </button>
        </div>
      </div>

      {/* Category Pills Slider */}
      <div className="flex gap-2 overflow-x-auto pb-1.5 pt-0.5 scrollbar-none">
        {/* Saved / Bookmarks Tab */}
        <button
          onClick={() => setSelectedCat('saved')}
          className={`px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 whitespace-nowrap transition-all border ${
            selectedCat === 'saved'
              ? 'bg-amber/20 text-amber border-amber/50 font-semibold shadow-sm'
              : 'bg-surface text-muted border-hairline/70 hover:text-ivory'
          }`}
        >
          <Star className="w-3.5 h-3.5 text-amber" />
          <span>Saved ({bookmarks.length})</span>
        </button>

        {/* Dynamic Categories from Backend */}
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCat(cat.id)}
            className={`px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 whitespace-nowrap transition-all border ${
              selectedCat === cat.id
                ? 'bg-rose/20 text-rose border-rose/50 font-semibold shadow-sm'
                : 'bg-surface text-muted border-hairline/70 hover:text-ivory'
            }`}
          >
            {renderCategoryIcon(cat.id)}
            <span>{cat.name}</span>
            {cat.count !== undefined && (
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-deep text-tertiary font-mono">
                {cat.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Count summary */}
      <div className="flex items-center justify-between text-[11px] text-tertiary px-1">
        <span>Showing {displayedDuas.length} supplications</span>
        {selectedCat === 'saved' && displayedDuas.length === 0 && (
          <span className="text-amber">No bookmarks yet. Tap the bookmark icon to save any Dua.</span>
        )}
      </div>

      {/* Duas Cards Stream */}
      <div className="space-y-3.5">
        {displayedDuas.map((dua) => {
          const count = counters[dua.id] || 0;
          const target = dua.repeat_count || 1;
          const isComplete = count >= target;
          const isBookmarked = bookmarks.includes(dua.id);
          const isNotesExpanded = !!expandedNotes[dua.id];

          return (
            <div
              key={dua.id}
              className={`p-4 rounded-2xl bg-surface border transition-all space-y-3 ${
                isComplete
                  ? 'border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.05)]'
                  : 'border-hairline/80 hover:border-white/[0.14]'
              }`}
            >
              {/* Card Header: Category & Badges & Tools */}
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-rose bg-rose-950/40 px-2.5 py-0.5 rounded-full border border-rose-500/20">
                    {dua.category_name || dua.category}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-deep text-muted border border-hairline font-mono">
                    {dua.authenticity_grade}
                  </span>
                </div>

                {/* Right Action Icons */}
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handlePlayAudio(dua)}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      playingId === dua.id
                        ? 'bg-amber text-void border-amber'
                        : 'text-tertiary hover:text-ivory border-hairline/60'
                    }`}
                    title="Pronunciation audio"
                  >
                    {playingId === dua.id ? (
                      <VolumeX className="w-3.5 h-3.5 animate-pulse text-void" />
                    ) : (
                      <Volume2 className="w-3.5 h-3.5" />
                    )}
                  </button>

                  <button
                    onClick={() => toggleBookmark(dua.id)}
                    className="p-1.5 rounded-lg text-tertiary hover:text-amber transition-colors border border-hairline/60"
                    title="Bookmark"
                  >
                    {isBookmarked ? (
                      <BookmarkCheck className="w-3.5 h-3.5 text-amber fill-amber/20" />
                    ) : (
                      <Bookmark className="w-3.5 h-3.5" />
                    )}
                  </button>

                  <button
                    onClick={() => handleCopy(dua)}
                    className="p-1.5 rounded-lg text-tertiary hover:text-ivory transition-colors border border-hairline/60"
                    title="Copy full citation"
                  >
                    {copiedId === dua.id ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Dua Title */}
              <h2 className="text-sm font-semibold text-ivory/95 font-serif">
                {dua.title}
              </h2>

              {/* Vocalized Arabic Text */}
              <div className="pt-1 pb-1">
                <p
                  dir="rtl"
                  className={`font-arabic text-right text-ivory font-medium ${arabicSizeClass} select-text tracking-wide`}
                >
                  {dua.arabic}
                </p>
              </div>

              {/* Transliteration */}
              {showTransliteration && (
                <p className="text-xs font-serif italic text-amber/90 leading-snug">
                  {dua.transliteration}
                </p>
              )}

              {/* English Translation */}
              <p className="text-xs text-muted/95 leading-relaxed">
                &ldquo;{dua.translation}&rdquo;
              </p>

              {/* Interactive Counter & Recommended Timing Bar */}
              <div className="pt-2.5 border-t border-hairline/60 flex items-center justify-between flex-wrap gap-2 text-xs">
                {/* Repetition Target Button */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleIncrement(dua)}
                    className={`px-3 py-1 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all border ${
                      isComplete
                        ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40 shadow-sm'
                        : 'bg-deep text-ivory border-hairline hover:border-amber-500/40'
                    }`}
                  >
                    <span>{isComplete ? 'Complete' : 'Recite'}</span>
                    <span className="font-mono font-bold text-[11px]">
                      {count} / {target}
                    </span>
                    {isComplete && <Check className="w-3 h-3 text-emerald-400" />}
                  </button>

                  {count > 0 && (
                    <button
                      onClick={(e) => handleResetCounter(dua.id, e)}
                      className="p-1 text-tertiary hover:text-ivory transition-colors"
                      title="Reset counter"
                    >
                      <RotateCcw className="w-3 h-3" />
                    </button>
                  )}
                </div>

                {/* Timing Context Badge */}
                <div className="text-[11px] text-tertiary flex items-center gap-1">
                  <span className="text-muted font-medium">When:</span>
                  <span className="text-ivory/80">{dua.recommended_context}</span>
                </div>
              </div>

              {/* Scholarly Virtues & Hadith Commentary Accordion */}
              {dua.notes && (
                <div className="pt-1">
                  <button
                    onClick={() => toggleNotes(dua.id)}
                    className="flex items-center justify-between w-full text-[11px] text-amber/80 hover:text-amber transition-colors pt-1"
                  >
                    <span className="flex items-center gap-1 font-medium">
                      <Sparkles className="w-3 h-3" />
                      Scholarly Virtues & Hadith Context
                    </span>
                    {isNotesExpanded ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {isNotesExpanded && (
                    <div className="mt-2 p-3 rounded-xl bg-deep/80 border border-hairline/60 text-[11px] text-muted leading-relaxed space-y-1.5 animate-in fade-in duration-200">
                      <p>{dua.notes}</p>
                      <div className="pt-1.5 border-t border-hairline/40 flex items-center justify-between text-[10px] text-tertiary font-mono">
                        <span>Source: {dua.source_reference}</span>
                        <span>{dua.source_type}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
