'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  Sparkles, 
  ArrowLeft, 
  Volume2, 
  VolumeX, 
  RotateCcw, 
  CheckCircle, 
  BookOpen, 
  Heart, 
  ShieldCheck, 
  Info, 
  Sliders, 
  Check,
  Flame,
  ChevronRight,
  Layers,
  X
} from 'lucide-react';

interface LinguisticBreakdown {
  word: string;
  meaning: string;
  root_concept: string;
}

interface DhikrItem {
  id: string;
  arabic: string;
  transliteration: string;
  translation: string;
  target_daily: number;
  benefits_category: string;
  virtue: string;
  category: string;
  hadith_reference?: string;
  linguistic_breakdown?: LinguisticBreakdown[];
  theological_significance?: string;
  psychological_spiritual_effect?: string;
  khushu_visualization?: string;
  count: number;
  target: number;
  percentage: number;
  completed: boolean;
}

const EMBEDDED_ADHKAR: DhikrItem[] = [
  {
    id: "istighfar",
    arabic: "أَسْتَغْفِرُ اللَّهَ وَأَتُوبُ إِلَيْهِ",
    transliteration: "Astaghfirullaha wa atubu ilayh",
    translation: "I seek the forgiveness of Allah and I repent unto Him.",
    target_daily: 100,
    benefits_category: "Wealth, Well-being & Forgiveness",
    virtue: "The Prophet (ﷺ) sought forgiveness over 70 to 100 times daily (Sahih al-Bukhari 6307).",
    category: "istighfar",
    hadith_reference: "Sahih al-Bukhari (6307); Sahih Muslim (2702)",
    linguistic_breakdown: [
      { word: "أَسْتَغْفِرُ (Astaghfiru)", meaning: "I seek forgiveness & shielding", root_concept: "From Gh-F-R meaning 'Mighfar' (battle helmet). Asks Allah to conceal the sin and shield one from toxic consequences." },
      { word: "اللَّهَ (Allah)", meaning: "Allah", root_concept: "The All-Encompassing Divine Name." },
      { word: "وَأَتُوبُ (wa atubu)", meaning: "And I return in repentance", root_concept: "From T-W-B meaning to turn back from a detour and return home to the Straight Path." },
      { word: "إِلَيْهِ (ilayh)", meaning: "Unto Him exclusively", root_concept: "Direct surrender without intermediary." }
    ],
    theological_significance: "Istighfar cleanses spiritual rust (Rayn). In Surah Nuh (71:10-12), Allah links continuous Istighfar with economic expansion, rain, sustained wealth, children, and physical vitality.",
    psychological_spiritual_effect: "Dissolves subconscious guilt and replaces mental anxiety with divine peace.",
    khushu_visualization: "Visualize a dark speck of error dissolving in an ocean of infinite Light with each count.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  },
  {
    id: "subhanallah",
    arabic: "سُبْحَانَ اللَّهِ",
    transliteration: "SubhanAllah",
    translation: "Glory be to Allah (Far removed is He from any imperfection).",
    target_daily: 100,
    benefits_category: "Inner Peace & Divine Awe",
    virtue: "1,000 good deeds are recorded or 1,000 sins wiped away (Sahih Muslim 2698).",
    category: "tasbih",
    hadith_reference: "Sahih Muslim (2698)",
    linguistic_breakdown: [
      { word: "سُبْحَانَ (Subhan)", meaning: "Exalted, swimming far above defect", root_concept: "From S-B-H meaning swift graceful swimming above water. Declares Allah is elevated above any defect or limitation." },
      { word: "اللَّهِ (Allah)", meaning: "Allah", root_concept: "The Absolute Reality." }
    ],
    theological_significance: "Connects with Al-Quddus (The Pure) and As-Salam (The Source of Peace). Removes grievances about Allah's decree.",
    psychological_spiritual_effect: "Frees the mind from cynicism and instills deep awe.",
    khushu_visualization: "Picture the cosmos in pristine cosmic order without a single flaw.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  },
  {
    id: "alhamdulillah",
    arabic: "الْحَمْدُ لِلَّهِ",
    transliteration: "Alhamdulillah",
    translation: "All perfect praise and gratitude belong exclusively to Allah.",
    target_daily: 100,
    benefits_category: "Gratitude & Multiplication of Blessings",
    virtue: "Fills the Cosmic Scale of good deeds to overflowing (Sahih Muslim 223).",
    category: "tahmeed",
    hadith_reference: "Sahih Muslim (223)",
    linguistic_breakdown: [
      { word: "الْحَمْدُ (Al-Hamd)", meaning: "All universal praise with love", root_concept: "From H-M-D combining profound love, reverence, and gratitude for both essence and gifts." },
      { word: "لِلَّهِ (Lillah)", meaning: "Belongs exclusively to Allah", root_concept: "The Lam expresses absolute divine possession." }
    ],
    theological_significance: "The catalyst of expansion (Surah Ibrahim 14:7: 'If you are grateful, I will surely increase you').",
    psychological_spiritual_effect: "Eliminates depressive scarcity mindsets by flooding neuro-pathways with gratitude.",
    khushu_visualization: "Every heartbeat, every breath of oxygen, every answered prayer lighting up as a golden bead.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  },
  {
    id: "allahuakbar",
    arabic: "اللَّهُ أَكْبَرُ",
    transliteration: "Allahu Akbar",
    translation: "Allah is Greater than all things, thoughts, fears, and obstacles.",
    target_daily: 100,
    benefits_category: "Overcoming Fear & Anxiety",
    virtue: "Fills the space between the heavens and the earth (Sahih Muslim 223).",
    category: "takbir",
    hadith_reference: "Sahih Muslim (223)",
    linguistic_breakdown: [
      { word: "اللَّهُ (Allah)", meaning: "The One True God", root_concept: "The Absolute Sovereign." },
      { word: "أَكْبَرُ (Akbar)", meaning: "Greater than everything imaginable", root_concept: "Superlative without object, signifying He is greater than any challenge." }
    ],
    theological_significance: "Shrinks worldly giants (stress, bosses, exams, fears) down to insignificance.",
    psychological_spiritual_effect: "Instills fearless courage and unshakeable confidence in divine support.",
    khushu_visualization: "See your biggest problem becoming smaller and smaller under the immense throne of Allah.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  },
  {
    id: "la_hawla",
    arabic: "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
    transliteration: "La hawla wa la quwwata illa billah",
    translation: "There is no movement, transformation, or power except through Allah.",
    target_daily: 100,
    benefits_category: "Depression Relief & Divine Energy",
    virtue: "A treasure from beneath the Arsh (Throne) of Allah (Sahih al-Bukhari 4205).",
    category: "tawakkul",
    hadith_reference: "Sahih al-Bukhari (4205); Sahih Muslim (2704)",
    linguistic_breakdown: [
      { word: "لَا حَوْلَ (La hawla)", meaning: "No shift or transformation from state to state", root_concept: "From H-W-L meaning turning, changing state from weakness to strength." },
      { word: "وَلَا قُوَّةَ (wa la quwwata)", meaning: "And no power or ability to act", root_concept: "Muscular, mental, and spiritual energy." },
      { word: "إِلَّا بِاللَّهِ (illa billah)", meaning: "Except by and through Allah", root_concept: "Complete reliance on the Creator." }
    ],
    theological_significance: "Total liberation from human ego (Nafs) and self-reliance.",
    psychological_spiritual_effect: "Recharges depleted nervous systems by transferring weight to the Almighty.",
    khushu_visualization: "Feel divine energy revitalizing your veins as you release control.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  },
  {
    id: "durud",
    arabic: "اللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ وَعَلَىٰ آلِ مُحَمَّدٍ",
    transliteration: "Allahumma salli 'ala Muhammadin wa 'ala ali Muhammad",
    translation: "O Allah, send peace, blessings, and honor upon Muhammad and the family of Muhammad.",
    target_daily: 100,
    benefits_category: "Relief of All Worries & Forgiveness",
    virtue: "Whoever sends blessings upon the Prophet once, Allah blesses them tenfold (Sahih Muslim 384).",
    category: "salawat",
    hadith_reference: "Sahih Muslim (384); Jami' at-Tirmidhi (2457)",
    theological_significance: "Ubayy ibn Ka'b asked: 'Should I dedicate all my dua to sending Salawat upon you?' The Prophet (ﷺ) replied: 'Then all your worries will be removed and your sins forgiven.'",
    psychological_spiritual_effect: "Softens the heart with intense divine love and emotional warmth.",
    khushu_visualization: "A rain of ten divine mercies descending on your head with every single blessing.",
    count: 0,
    target: 100,
    percentage: 0,
    completed: false
  }
];

export default function DhikrPage() {
  const [adhkar, setAdhkar] = useState<DhikrItem[]>(EMBEDDED_ADHKAR);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [hapticCount, setHapticCount] = useState(0);
  const [ripples, setRipples] = useState<{ id: number; size: number }[]>([]);
  const rippleIdRef = useRef(0);

  const currentDhikr = adhkar[selectedIndex] || adhkar[0];

  // Sync with API
  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const res = await fetch('/api/lifeos/dhikr');
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.adhkar && Array.isArray(data.adhkar) && data.adhkar.length > 0) {
            const todayMap = new Map();
            if (data.today && Array.isArray(data.today)) {
              data.today.forEach((t: any) => {
                todayMap.set(t.dhikr_id, t.count || 0);
              });
            }
            const normalized = data.adhkar.map((a: any) => {
              const cnt = Number(todayMap.get(a.id) ?? a.count ?? 0);
              const tgt = Number(a.target || a.target_daily || 100);
              return {
                ...a,
                count: cnt,
                target: tgt,
                target_daily: tgt,
                percentage: Math.min(100, Math.round((cnt / tgt) * 100)),
                completed: cnt >= tgt,
              };
            });
            setAdhkar(normalized);
          }
        }
      } catch (e) {}
    }
    loadData();
    return () => { isMounted = false; };
  }, []);

  const playChime = () => {
    if (!soundEnabled || typeof window === 'undefined') return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(528, ctx.currentTime); // 528Hz Solfeggio Transformation Tone
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15);

      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } catch (e) {}
  };

  const handleTap = () => {
    playChime();
    setHapticCount((prev) => prev + 1);

    // Spawn theme-adaptive wave ripple
    const newId = ++rippleIdRef.current;
    setRipples((prev) => [...prev.slice(-5), { id: newId, size: 176 }]);
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== newId));
    }, 1000);

    setAdhkar((prev) =>
      prev.map((item, idx) => {
        if (idx === selectedIndex) {
          const newCount = item.count + 1;
          const target = item.target || item.target_daily || 100;
          return {
            ...item,
            count: newCount,
            percentage: Math.min(100, Math.round((newCount / target) * 100)),
            completed: newCount >= target,
          };
        }
        return item;
      })
    );

    // Sync to backend asynchronously
    fetch('/api/lifeos/dhikr/increment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dhikr_id: currentDhikr.id, delta: 1 }),
    }).catch(() => {});
  };

  const handleReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setAdhkar((prev) =>
      prev.map((item, idx) =>
        idx === selectedIndex ? { ...item, count: 0, percentage: 0, completed: false } : item
      )
    );
  };

  const handleSetCustomGoal = (newTarget: number) => {
    if (newTarget <= 0) return;
    setAdhkar((prev) =>
      prev.map((item, idx) => {
        if (idx === selectedIndex) {
          const count = item.count;
          return {
            ...item,
            target: newTarget,
            target_daily: newTarget,
            percentage: Math.min(100, Math.round((count / newTarget) * 100)),
            completed: count >= newTarget,
          };
        }
        return item;
      })
    );
    setIsGoalModalOpen(false);
  };

  const categories = [
    { id: 'all', name: 'All' },
    { id: 'istighfar', name: 'Istighfar' },
    { id: 'tasbih', name: 'Tasbih' },
    { id: 'tahmeed', name: 'Tahmeed' },
    { id: 'takbir', name: 'Takbir' },
    { id: 'tawakkul', name: 'Tawakkul' },
    { id: 'salawat', name: 'Salawat' },
  ];

  const filteredAdhkar = adhkar.filter(
    (item) => selectedCategory === 'all' || item.category === selectedCategory
  );

  const count = Number(currentDhikr?.count) || 0;
  const target = Number(currentDhikr?.target || currentDhikr?.target_daily) || 100;
  const percentage = Math.max(0, Math.min(100, Math.round((count / target) * 100)));
  const circumference = 2 * Math.PI * 80;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 text-ivory select-none pb-24 scrollbar-none">
      {/* Top Header */}
      <div className="flex items-center justify-between shrink-0">
        <Link
          href="/lifeos"
          className="w-8 h-8 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>
        <div className="text-center">
          <span className="text-[9.5px] font-mono tracking-widest text-emerald-400 uppercase font-semibold">
            Heart Transformation Engine
          </span>
          <h1 className="font-serif text-lg text-ivory">Dhikr & Contemplation</h1>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setIsGoalModalOpen(true)}
            className="w-8 h-8 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 text-ivory/80"
            title="Custom Goal"
          >
            <Sliders className="w-3.5 h-3.5 text-amber" />
          </button>
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="w-8 h-8 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 text-ivory/80"
            title="Toggle Chime"
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-emerald-400" /> : <VolumeX className="w-3.5 h-3.5 text-ivory/40" />}
          </button>
        </div>
      </div>

      {/* Main Single Zikr Display Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-950/40 via-surface to-deep border border-emerald-500/25 p-4 shadow-xl backdrop-blur-md text-center space-y-2">
        <div className="flex items-center justify-between text-[11px] text-ivory/70 font-mono">
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[10px]">
            {currentDhikr?.benefits_category || 'Remembrance'}
          </span>
          <button
            onClick={() => setIsDetailModalOpen(true)}
            className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer"
          >
            <Info className="w-3 h-3" />
            <span>Root Significance</span>
          </button>
        </div>

        {/* Arabic Calligraphy */}
        <div className="py-1">
          <p className="font-serif text-2xl sm:text-3xl text-ivory tracking-wide leading-relaxed drop-shadow-[0_0_12px_rgba(52,211,153,0.3)]">
            {currentDhikr?.arabic}
          </p>
        </div>

        {/* Transliteration & Translation */}
        <div className="space-y-0.5">
          <p className="text-xs font-semibold text-amber font-sans">
            {currentDhikr?.transliteration}
          </p>
          <p className="text-[11px] text-ivory/75 font-sans italic leading-snug line-clamp-2">
            "{currentDhikr?.translation}"
          </p>
        </div>
      </div>

      {/* Interactive Luxury Digital Counter with Circular Ring & Radiating Waves in All Themes */}
      <div className="flex flex-col items-center justify-center py-2 relative">
        <div
          onClick={handleTap}
          className="relative w-44 h-44 rounded-full bg-gradient-to-br from-[#132219] via-[#0d1712] to-[#080d0a] border border-emerald-500/30 shadow-[0_0_40px_rgba(52,211,153,0.2)] flex items-center justify-center cursor-pointer active:scale-95 transition-all select-none group"
        >
          {/* Radiating Theme Waves on Press (Adaptive across all themes) */}
          {ripples.map((ripple) => (
            <div
              key={ripple.id}
              className="absolute rounded-full pointer-events-none animate-ping duration-1000"
              style={{
                width: '100%',
                height: '100%',
                border: '2px solid var(--theme-accent, #34d399)',
                boxShadow: '0 0 20px var(--theme-accent, rgba(52,211,153,0.5))'
              }}
            />
          ))}

          {/* Animated SVG Progress Ring */}
          <svg className="absolute w-44 h-44 -rotate-90 transform pointer-events-none">
            <circle
              cx="88"
              cy="88"
              r="80"
              className="stroke-white/[0.06]"
              strokeWidth="6"
              fill="transparent"
            />
            <circle
              cx="88"
              cy="88"
              r="80"
              stroke="var(--theme-accent, #34d399)"
              className="transition-all duration-300"
              strokeWidth="6"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
            />
          </svg>

          {/* Inner Core */}
          <div className="w-32 h-32 rounded-full bg-deep/90 border border-white/10 flex flex-col items-center justify-center space-y-0.5 shadow-inner backdrop-blur-md">
            <span className="font-mono text-4xl font-bold tracking-tight text-ivory drop-shadow-sm">
              {currentDhikr?.count || 0}
            </span>
            <span className="font-mono text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">
              Goal: {(currentDhikr?.target || 100).toLocaleString()}
            </span>
            <span className="text-[9px] font-mono text-ivory/50">
              {percentage}% Done
            </span>
          </div>

          <span className="absolute bottom-2 text-[9px] font-mono text-emerald-400/60 uppercase tracking-widest group-hover:text-emerald-300 transition-colors">
            Tap to Count
          </span>
        </div>

        {/* Counter Action Controls */}
        <div className="flex items-center gap-3 mt-3">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 text-[11px] text-ivory/70 hover:text-ivory hover:bg-white/[0.08] transition-all cursor-pointer"
          >
            <RotateCcw className="w-3 h-3 text-amber" />
            <span>Reset</span>
          </button>
          <button
            onClick={() => setIsGoalModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-[11px] text-emerald-300 hover:bg-emerald-500/20 transition-all cursor-pointer"
          >
            <Sliders className="w-3 h-3 text-emerald-400" />
            <span>Set Goal</span>
          </button>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none py-1">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCategory(c.id)}
            className={`px-3 py-1 rounded-full text-[11px] font-semibold transition-all whitespace-nowrap cursor-pointer ${
              selectedCategory === c.id
                ? 'bg-emerald-500 text-black shadow-[0_0_12px_rgba(52,211,153,0.3)]'
                : 'bg-surface text-ivory/70 border border-hairline hover:border-emerald-500/30'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Available Adhkar Library */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-muted font-mono px-1">
          <span>Adhkar Library ({filteredAdhkar.length})</span>
          <span className="text-emerald-400">Select to focus</span>
        </div>

        <div className="grid grid-cols-1 gap-2">
          {filteredAdhkar.map((item) => {
            const originalIndex = adhkar.findIndex((a) => a.id === item.id);
            const isSelected = selectedIndex === originalIndex;

            return (
              <div
                key={item.id}
                onClick={() => setSelectedIndex(originalIndex)}
                className={`p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-3 ${
                  isSelected
                    ? 'bg-emerald-950/30 border-emerald-500/50 shadow-md'
                    : 'bg-surface/70 border-hairline hover:border-emerald-500/25'
                }`}
              >
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-serif text-ivory truncate font-medium">
                      {item.transliteration}
                    </span>
                    {item.completed && (
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-muted/80 truncate">
                    {item.arabic}
                  </p>
                  {/* Progress bar */}
                  <div className="w-full bg-white/[0.06] rounded-full h-1 overflow-hidden mt-1">
                    <div
                      className="bg-emerald-400 h-full rounded-full transition-all duration-300"
                      style={{ width: `${item.percentage || 0}%` }}
                    />
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="font-mono text-sm font-bold text-ivory">
                    {Number(item.count) || 0}
                  </span>
                  <span className="text-[10px] font-mono text-muted block">
                    /{item.target || 100}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Root Significance Detail Modal */}
      {isDetailModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-deep border border-emerald-500/30 rounded-3xl p-5 space-y-4 max-h-[85vh] overflow-y-auto scrollbar-none shadow-2xl animate-fade-in">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <h3 className="font-serif text-base text-ivory">Linguistic & Spiritual Roots</h3>
              </div>
              <button
                onClick={() => setIsDetailModalOpen(false)}
                className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-ivory/80 hover:bg-white/20"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-center py-2 space-y-1">
              <p className="font-serif text-2xl text-ivory">{currentDhikr?.arabic}</p>
              <p className="text-xs font-semibold text-amber">{currentDhikr?.transliteration}</p>
              <p className="text-xs text-ivory/80 italic">"{currentDhikr?.translation}"</p>
            </div>

            {/* Hadith & Virtue */}
            <div className="p-3 rounded-2xl bg-surface border border-hairline space-y-1 text-xs">
              <span className="font-mono text-[10px] text-emerald-400 uppercase font-semibold block">Hadith Virtue</span>
              <p className="text-ivory/90 leading-relaxed">{currentDhikr?.virtue}</p>
              {currentDhikr?.hadith_reference && (
                <span className="text-[10px] font-mono text-muted/70 block mt-1">Source: {currentDhikr.hadith_reference}</span>
              )}
            </div>

            {/* Linguistic Breakdown */}
            {currentDhikr?.linguistic_breakdown && (
              <div className="space-y-2">
                <span className="font-mono text-[10px] text-amber uppercase font-semibold block">Linguistic Root Analysis</span>
                {currentDhikr.linguistic_breakdown.map((l, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06] text-xs space-y-0.5">
                    <span className="font-semibold text-emerald-300">{l.word}:</span>
                    <p className="text-ivory/80 text-[11px]">{l.root_concept}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Theological Significance */}
            {currentDhikr?.theological_significance && (
              <div className="p-3 rounded-2xl bg-emerald-950/20 border border-emerald-500/20 text-xs space-y-1">
                <span className="font-mono text-[10px] text-emerald-400 uppercase font-semibold block">Theological Impact</span>
                <p className="text-ivory/85 leading-relaxed">{currentDhikr.theological_significance}</p>
              </div>
            )}

            {/* Khushu Visualization */}
            {currentDhikr?.khushu_visualization && (
              <div className="p-3 rounded-2xl bg-amber-950/20 border border-amber-500/20 text-xs space-y-1">
                <span className="font-mono text-[10px] text-amber uppercase font-semibold block">Khushu' Visualization</span>
                <p className="text-ivory/85 leading-relaxed italic">{currentDhikr.khushu_visualization}</p>
              </div>
            )}

            <button
              onClick={() => setIsDetailModalOpen(false)}
              className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black text-xs font-bold transition-all cursor-pointer"
            >
              Back to Contemplation
            </button>
          </div>
        </div>
      )}

      {/* Set Custom Goal Modal */}
      {isGoalModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-xs bg-deep border border-emerald-500/30 rounded-3xl p-5 space-y-4 shadow-2xl animate-fade-in text-center">
            <h3 className="font-serif text-base text-ivory">Set Daily Goal</h3>
            <p className="text-xs text-muted">Choose a daily target for {currentDhikr?.transliteration}:</p>

            <div className="grid grid-cols-2 gap-2">
              {[33, 100, 300, 500, 1000, 5000].map((t) => (
                <button
                  key={t}
                  onClick={() => handleSetCustomGoal(t)}
                  className={`py-2 px-3 rounded-xl border text-xs font-mono font-bold transition-all cursor-pointer ${
                    (currentDhikr?.target || 100) === t
                      ? 'bg-emerald-500 text-black border-emerald-400 shadow-md'
                      : 'bg-surface text-ivory border-hairline hover:border-emerald-500/30'
                  }`}
                >
                  {t.toLocaleString()}x
                </button>
              ))}
            </div>

            <button
              onClick={() => setIsGoalModalOpen(false)}
              className="w-full py-2 rounded-xl bg-white/10 hover:bg-white/20 text-ivory text-xs font-semibold"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
