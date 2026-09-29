'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  BookOpen,
  ArrowLeft,
  Search,
  Star,
  ShieldCheck,
  AlertCircle,
  Bookmark,
  Check,
  Sparkles,
  Headphones,
  Calendar,
  Volume2,
  Share2,
  CheckCircle2,
  Flame,
  ChevronRight,
} from 'lucide-react';

interface SurahMeta {
  number: number;
  name_ar: string;
  name_en: string;
  meaning: string;
  verses: number;
  type: string;
  category?: string;
}

interface Verse {
  num: number;
  ar: string;
  en: string;
  quality?: string;
}

interface SpecialVirtue {
  title: string;
  surah_number: number;
  classification: string;
  source: string;
  ruling: string;
  recommended_time: string;
}

const QUICK_SURAHS = [
  { num: 67, name: 'Al-Mulk', ar: 'الملك', desc: 'Nightly Protection', badge: 'Daily Sunnah' },
  { num: 36, name: 'Ya-Sin', ar: 'يس', desc: 'Heart of Quran', badge: 'Contemplation' },
  { num: 18, name: 'Al-Kahf', ar: 'الكهف', desc: 'Friday Light', badge: 'Friday Sunnah' },
  { num: 56, name: 'Al-Waqi\'ah', ar: 'الواقعة', desc: 'The Inevitable', badge: 'Akhirah' },
  { num: 55, name: 'Ar-Rahman', ar: 'الرحمن', desc: 'Divine Favors', badge: 'Gratitude' },
  { num: 2, name: 'Ayat al-Kursi', ar: 'آية الكرسي', desc: 'Greatest Ayah', badge: 'After Salah' },
  { num: 94, name: 'Ash-Sharh', ar: 'الشرح', desc: 'With Hardship Ease', badge: 'Comfort' },
  { num: 112, name: 'Al-Ikhlas', ar: 'الإخلاص', desc: '1/3 of Quran', badge: 'Protection' },
];

export default function QuranReaderPage() {
  const [catalog, setCatalog] = useState<SurahMeta[]>([]);
  const [selectedSurahNum, setSelectedSurahNum] = useState<number>(67); // Default to Surah Al-Mulk
  const [currentSurahData, setCurrentSurahData] = useState<{ surah: SurahMeta; verses: Verse[] } | null>(null);
  const [specialVirtues, setSpecialVirtues] = useState<Record<string, SpecialVirtue>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [bookmarkedVerses, setBookmarkedVerses] = useState<Record<number, boolean>>({});
  const [activeTab, setActiveTab] = useState<'reader' | 'special_virtues' | 'firdaus' | 'daily_plan'>('reader');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  const fetchCatalogAndVirtues = async () => {
    try {
      const res = await fetch('/api/lifeos/quran');
      if (res.ok) {
        const data = await res.json();
        setCatalog(data.catalog || []);
        setSpecialVirtues(data.special_virtues || {});
      }
    } catch (e) {
      console.error('Quran catalog fetch error:', e);
    }
  };

  const loadSurah = async (surahNumber: number) => {
    setLoading(true);
    setSelectedSurahNum(surahNumber);
    try {
      const res = await fetch(`/api/lifeos/quran?surah=${surahNumber}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentSurahData(data);
      }
    } catch (e) {
      console.error('Surah load error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalogAndVirtues();
    loadSurah(67); // Default to Surah Al-Mulk
  }, []);

  const toggleBookmark = (verseNum: number) => {
    setBookmarkedVerses((prev) => ({
      ...prev,
      [verseNum]: !prev[verseNum],
    }));
  };

  const filteredCatalog = catalog.filter((s) => {
    const matchesSearch =
      s.name_en.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.name_ar.includes(searchQuery) ||
      s.number.toString() === searchQuery.trim();

    if (selectedCategory === 'all') return matchesSearch;
    return matchesSearch && s.category === selectedCategory;
  });

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-28 select-none text-ivory scrollbar-none max-w-xl mx-auto w-full">
      {/* ── TOP NAVIGATION ── */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="flex items-center gap-1.5 text-xs text-muted hover:text-ivory transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>LifeOS Home</span>
        </Link>
        <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-500/20 font-mono flex items-center gap-1 shadow-sm">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          <span>Tanzil Text Integrity</span>
        </span>
      </div>

      {/* ── 4-TAB NAVIGATION SWITCHER ── */}
      <div className="grid grid-cols-4 bg-surface p-1 rounded-2xl border border-hairline/70 text-xs shadow-md">
        <button
          onClick={() => setActiveTab('reader')}
          className={`py-2 px-1 rounded-xl font-medium transition-all text-center truncate ${
            activeTab === 'reader'
              ? 'bg-amber text-black font-bold shadow-sm'
              : 'text-muted hover:text-ivory'
          }`}
        >
          Reader
        </button>
        <button
          onClick={() => setActiveTab('special_virtues')}
          className={`py-2 px-1 rounded-xl font-medium transition-all text-center truncate ${
            activeTab === 'special_virtues'
              ? 'bg-amber text-black font-bold shadow-sm'
              : 'text-muted hover:text-ivory'
          }`}
        >
          Virtues
        </button>
        <button
          onClick={() => setActiveTab('firdaus')}
          className={`py-2 px-1 rounded-xl font-medium transition-all text-center truncate ${
            activeTab === 'firdaus'
              ? 'bg-amber text-black font-bold shadow-sm'
              : 'text-muted hover:text-ivory'
          }`}
        >
          Firdaus
        </button>
        <button
          onClick={() => setActiveTab('daily_plan')}
          className={`py-2 px-1 rounded-xl font-medium transition-all text-center truncate ${
            activeTab === 'daily_plan'
              ? 'bg-amber text-black font-bold shadow-sm'
              : 'text-muted hover:text-ivory'
          }`}
        >
          Planner
        </button>
      </div>

      {/* ── TAB 1: FULL READER & SURAH CATALOG ── */}
      {activeTab === 'reader' && (
        <div className="space-y-4">
          {/* Quick Jump Essential Surahs Bar */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono text-muted uppercase tracking-wider block px-1">
              Essential Surahs Quick Jump
            </span>
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
              {QUICK_SURAHS.map((qs) => {
                const isSelected = selectedSurahNum === qs.num;
                return (
                  <button
                    key={qs.num}
                    onClick={() => loadSurah(qs.num)}
                    className={`p-2.5 rounded-2xl border flex flex-col text-left shrink-0 min-w-[130px] transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-amber/20 border-amber/50 text-ivory shadow-[0_0_12px_rgba(212,168,83,0.2)]'
                        : 'bg-surface/80 border-hairline/60 hover:bg-surface text-muted hover:text-ivory'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-[10px] font-mono text-amber font-semibold">#{qs.num}</span>
                      <span className="font-arabic text-sm text-ivory">{qs.ar}</span>
                    </div>
                    <span className="text-xs font-semibold text-ivory mt-0.5">{qs.name}</span>
                    <span className="text-[10px] text-muted truncate">{qs.desc}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Search & Surah Selector */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-muted absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search Surah by name or number (e.g. Mulk, Yasin, 67)..."
                className="w-full bg-surface border border-hairline/80 rounded-2xl pl-9 pr-3 py-2 text-xs text-ivory placeholder:text-muted/60 focus:border-amber/40 outline-none ring-0 shadow-none"
              />
            </div>

            <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none">
              {filteredCatalog.map((s) => (
                <button
                  key={s.number}
                  onClick={() => loadSurah(s.number)}
                  className={`px-3 py-1.5 rounded-xl text-xs whitespace-nowrap transition-all border shrink-0 cursor-pointer ${
                    selectedSurahNum === s.number
                      ? 'bg-amber text-black border-amber font-bold shadow-sm'
                      : 'bg-surface text-muted border-hairline/60 hover:text-ivory'
                  }`}
                >
                  <span>{s.number}. {s.name_en}</span>
                  <span className="ml-1.5 font-arabic text-[11px] opacity-80">{s.name_ar}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Surah Header Card */}
          {currentSurahData && (
            <div className="p-4 rounded-3xl bg-gradient-to-br from-[#1A1B18] via-surface to-[#121310] border border-amber/30 shadow-lg space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-lg font-serif tracking-wide text-ivory font-medium">
                      {currentSurahData.surah.name_en}
                    </h1>
                    <span className="font-arabic text-base text-amber">
                      {currentSurahData.surah.name_ar}
                    </span>
                  </div>
                  <p className="text-xs text-muted mt-0.5">
                    Surah {currentSurahData.surah.number} &bull; {currentSurahData.surah.meaning} &bull; {currentSurahData.surah.verses} Verses &bull; {currentSurahData.surah.type}
                  </p>
                </div>
                <div className="w-10 h-10 rounded-2xl bg-amber/15 border border-amber/30 flex items-center justify-center font-mono text-sm text-amber font-bold shrink-0">
                  {currentSurahData.surah.number}
                </div>
              </div>

              {currentSurahData.surah.number === 67 && (
                <div className="p-2.5 rounded-2xl bg-amber-950/30 border border-amber/30 text-xs text-amber leading-relaxed flex items-start gap-2">
                  <Star className="w-3.5 h-3.5 text-amber shrink-0 mt-0.5 fill-amber" />
                  <span>
                    <strong>Established Nightly Sunnah:</strong> The Prophet (ﷺ) would not sleep until he recited Surah Al-Mulk. It protects against punishment of the grave.
                  </span>
                </div>
              )}

              {currentSurahData.surah.number === 18 && (
                <div className="p-2.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-300 leading-relaxed flex items-start gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Friday Sunnah:</strong> Reciting Surah Al-Kahf illuminates light between the two Fridays and shields against the trials of Dajjal.
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Bismillah Opening */}
          {selectedSurahNum !== 9 && selectedSurahNum !== 1 && (
            <div className="text-center py-2 bg-black/20 rounded-2xl border border-white/[0.04] p-3 space-y-1">
              <p className="font-arabic text-2xl text-amber tracking-wide">
                بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
              </p>
              <p className="text-[11px] text-muted italic">
                In the name of Allah, the Entirely Merciful, the Especially Merciful.
              </p>
            </div>
          )}

          {/* Verses Stream */}
          <div className="space-y-3">
            {loading ? (
              <div className="space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-28 bg-surface rounded-3xl animate-pulse border border-hairline" />
                ))}
              </div>
            ) : (
              currentSurahData?.verses.map((verse) => {
                const isBookmarked = !!bookmarkedVerses[verse.num];

                return (
                  <div
                    key={verse.num}
                    className="p-4 rounded-3xl bg-surface/90 border border-hairline/70 hover:border-amber/30 transition-all space-y-2.5 shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="w-7 h-7 rounded-xl bg-deep border border-hairline flex items-center justify-center text-xs font-mono text-amber font-semibold">
                        {verse.num}
                      </span>
                      <button
                        onClick={() => toggleBookmark(verse.num)}
                        className={`p-1.5 rounded-xl transition-colors cursor-pointer ${
                          isBookmarked ? 'text-amber bg-amber/10' : 'text-muted hover:text-ivory'
                        }`}
                        title={isBookmarked ? 'Bookmarked' : 'Add Bookmark'}
                      >
                        <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber' : ''}`} />
                      </button>
                    </div>

                    {/* Arabic Text */}
                    <p className="font-arabic text-xl sm:text-2xl text-right text-ivory leading-loose tracking-wide pt-1">
                      {verse.ar}
                    </p>

                    {/* English Translation */}
                    <p className="text-xs sm:text-[13px] text-muted/90 leading-relaxed pt-2 border-t border-white/[0.04] font-sans">
                      {verse.en}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ── TAB 2: VERIFIED SPECIAL VIRTUES DIRECTORY ── */}
      {activeTab === 'special_virtues' && (
        <div className="space-y-3.5">
          <div className="p-3.5 rounded-2xl bg-surface border border-hairline text-xs text-muted leading-relaxed flex items-start gap-2 shadow-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-ivory">Authenticity Boundary:</strong> Sunnah practices authenticated by Sahih or Hasan hadiths are clearly distinguished from commonly circulated weak narrations.
            </div>
          </div>

          {Object.entries(specialVirtues).map(([key, item]) => {
            const isSahih = item.classification.includes('Sahih') || item.classification.includes('Hasan');

            return (
              <div
                key={key}
                className="p-4 rounded-3xl bg-surface border border-hairline hover:border-amber/30 transition-all space-y-2.5 shadow-md"
              >
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold text-ivory font-serif">{item.title}</h3>
                  <span
                    className={`text-[10px] px-2.5 py-0.5 rounded-full font-mono shrink-0 font-medium ${
                      isSahih
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'bg-amber-500/15 text-amber border border-amber-500/30'
                    }`}
                  >
                    {item.classification}
                  </span>
                </div>

                <p className="text-xs text-ivory/85 leading-relaxed font-sans">
                  {item.ruling}
                </p>

                <div className="pt-2 border-t border-white/[0.05] flex items-center justify-between text-[11px] text-muted font-mono">
                  <span className="truncate max-w-[200px]">Source: {item.source}</span>
                  <span className="text-amber font-medium">{item.recommended_time}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── TAB 3: FIRDAUS PATH (23:1-11) ── */}
      {activeTab === 'firdaus' && (
        <div className="space-y-3.5">
          <div className="p-4 rounded-3xl bg-gradient-to-br from-emerald-950/30 via-surface to-[#121310] border border-emerald-500/30 shadow-md">
            <h2 className="text-sm font-semibold text-emerald-400 font-serif">
              The Path to Al-Firdaus (Surah Al-Mu'minun 23:1-11)
            </h2>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              &ldquo;Those are the inheritors who will inherit al-Firdaus. They will abide therein eternally.&rdquo; (23:10-11)
            </p>
          </div>

          <div className="space-y-2.5">
            {[
              { num: 1, trait: "Khushu' in Salah", desc: "Humbly submissive presence in prayer, pausing between verses of Al-Fatiha.", ayah: "الَّذِينَ هُمْ فِي صَلَاتِهِمْ خَاشِعُونَ" },
              { num: 2, trait: "Guarding against Laghw", desc: "Turning away from frivolous, vanity-filled, or harmful speech.", ayah: "وَالَّذِينَ هُمْ عَنِ اللَّغْوِ مُعْرِضُونَ" },
              { num: 3, trait: "Observant of Zakah", desc: "Purifying wealth and actively extending charity to the needy.", ayah: "وَالَّذِينَ هُمْ لِلزَّكَاةِ فَاعِلُونَ" },
              { num: 4, trait: "Chastity & Modesty", desc: "Guarding private desires and digital exposure with moral dignity.", ayah: "وَالَّذِينَ هُمْ لِفُرُوجِهِمْ حَافِظُونَ" },
              { num: 5, trait: "Fulfilling Trusts & Promises", desc: "Strict adherence to word, appointments, and confidentiality.", ayah: "وَالَّذِينَ هُمْ لِأَمَانَاتِهِمْ وَعَهْدِهِمْ رَاعُونَ" },
              { num: 6, trait: "Preserving Salah on Time", desc: "Consistently safeguarding the five daily prayers in their valid windows.", ayah: "وَالَّذِينَ هُمْ عَلَىٰ صَلَوَاتِهِمْ يُحَافِظُونَ" },
            ].map((item) => (
              <div
                key={item.num}
                className="p-4 rounded-2xl bg-surface border border-hairline/80 space-y-1.5 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-ivory">{item.num}. {item.trait}</span>
                  <span className="font-arabic text-sm text-emerald-400">{item.ayah}</span>
                </div>
                <p className="text-[11.5px] text-muted leading-relaxed font-sans">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── TAB 4: DAILY SURAH PLANNER & AUDIO ── */}
      {activeTab === 'daily_plan' && (
        <div className="space-y-4">
          <div className="p-4 rounded-3xl bg-surface border border-hairline shadow-md space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-amber" />
                <h3 className="text-sm font-semibold text-ivory font-serif">Daily Surah Schedule</h3>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded-full border border-emerald-500/30">
                Active Routine
              </span>
            </div>
            <p className="text-xs text-muted">
              Structured daily and weekly Quran recitation habits based on authentic Sunnah.
            </p>
          </div>

          <div className="space-y-2.5">
            {[
              { title: 'Nightly Protection', surah: 'Surah Al-Mulk (67)', time: 'Before Sleep', duration: '5 mins', badge: 'Every Night' },
              { title: 'Morning Vitality', surah: 'Surah Ya-Sin (36)', time: 'After Fajr / Morning', duration: '12 mins', badge: 'Daily' },
              { title: 'Friday Light', surah: 'Surah Al-Kahf (18)', time: 'Thursday Maghrib - Friday Maghrib', duration: '25 mins', badge: 'Weekly' },
              { title: 'Daily Preservation', surah: 'Ayat al-Kursi (2:255)', time: 'After Every Fard Salah', duration: '1 min', badge: '5x Daily' },
              { title: 'Evening Protection', surah: 'Al-Mu\'awwidhat (112, 113, 114)', time: 'Morning & Evening Adhkar', duration: '3 mins', badge: 'Daily 3x' },
            ].map((plan, i) => (
              <div
                key={i}
                className="p-3.5 rounded-2xl bg-surface/90 border border-hairline hover:border-amber/30 transition-all flex items-center justify-between gap-3 shadow-sm"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-ivory">{plan.title}</span>
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-amber/10 border border-amber/20 text-amber font-medium">
                      {plan.badge}
                    </span>
                  </div>
                  <div className="text-[11px] text-amber font-medium mt-0.5">{plan.surah}</div>
                  <div className="text-[10px] text-muted mt-0.5">{plan.time} &bull; ~{plan.duration}</div>
                </div>

                <button
                  onClick={() => {
                    const match = plan.surah.match(/\((\d+)\)/);
                    if (match) {
                      loadSurah(parseInt(match[1], 10));
                      setActiveTab('reader');
                    }
                  }}
                  className="p-2 rounded-xl bg-white/[0.05] hover:bg-amber/20 hover:text-amber text-ivory transition-all shrink-0 cursor-pointer"
                  title="Open Surah"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
