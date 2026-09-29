'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Wind, 
  Sparkles, 
  Volume2, 
  VolumeX, 
  Play, 
  Pause, 
  RotateCcw, 
  Heart, 
  Compass, 
  Gamepad2, 
  Feather,
  Layers,
  CheckCircle2,
  Moon,
  Sun
} from 'lucide-react';

const TADABBUR_CHAINS = [
  {
    theme: 'Ascent to Peace',
    prompt: 'Connect the pathway from patience to divine tranquility',
    words: [
      { id: 'w1', ar: 'صَبْرٌ', tr: 'Sabr', meaning: 'Dignified Patience', quote: 'Indeed, Allah is with the patient (2:153)' },
      { id: 'w2', ar: 'تَوَكُّلٌ', tr: 'Tawakkul', meaning: 'Absolute Reliance', quote: 'And upon Allah let the believers rely (14:11)' },
      { id: 'w3', ar: 'رِضًا', tr: 'Rida', meaning: 'Heartfelt Contentment', quote: 'Allah is pleased with them, and they with Him (98:8)' },
      { id: 'w4', ar: 'سَكِينَةٌ', tr: 'Sakinah', meaning: 'Deep Serenity', quote: 'He sent down tranquility into the hearts (48:4)' },
    ]
  },
  {
    theme: 'The Wealth of the Soul',
    prompt: 'Trace the path from remembrance to overflowing gratitude',
    words: [
      { id: 'w5', ar: 'ذِكْرٌ', tr: 'Dhikr', meaning: 'Remembrance of God', quote: 'Unquestionably, by the remembrance of Allah hearts find rest (13:28)' },
      { id: 'w6', ar: 'شُكْرٌ', tr: 'Shukr', meaning: 'Active Gratitude', quote: 'If you are grateful, I will surely increase you (14:7)' },
      { id: 'w7', ar: 'بَرَكَةٌ', tr: 'Barakah', meaning: 'Divine Increase', quote: 'Blessed are those who turn to their Lord in purity' },
      { id: 'w8', ar: 'غِنَىٰ', tr: 'Ghina', meaning: 'Soul Sufficiency', quote: 'True wealth is the self-sufficiency of the soul (Bukhari 6446)' },
    ]
  },
  {
    theme: 'Purification of Heart',
    prompt: 'Connect the journey of repentance to divine light',
    words: [
      { id: 'w9', ar: 'إِخْلَاصٌ', tr: 'Ikhlas', meaning: 'Pure Intention', quote: 'Worship Allah, keeping religion pure for Him (39:2)' },
      { id: 'w10', ar: 'تَوْبَةٌ', tr: 'Tawbah', meaning: 'Warm Turning Back', quote: 'Indeed, Allah loves those who constantly repent (2:222)' },
      { id: 'w11', ar: 'طَهَارَةٌ', tr: 'Taharah', meaning: 'Inner Sanctity', quote: 'Allah loves those who purify themselves (2:222)' },
      { id: 'w12', ar: 'نُورٌ', tr: 'Nur', meaning: 'Radiant Light', quote: 'Allah is the Light of the heavens and the earth (24:35)' },
    ]
  }
];

export default function LayaOasisPage() {
  const [mode, setMode] = useState<'breath' | 'game' | 'reflection'>('breath');
  const [breathPhase, setBreathPhase] = useState<'inhale' | 'hold' | 'exhale' | 'rest'>('inhale');
  const [breathTimeLeft, setBreathTimeLeft] = useState(4);
  const [isBreathActive, setIsBreathActive] = useState(true);
  const [soundActive, setSoundActive] = useState(false);
  const [breathCycles, setBreathCycles] = useState(0);

  // Tadabbur Game States
  const [chainIndex, setChainIndex] = useState(0);
  const [selectedWordIds, setSelectedWordIds] = useState<string[]>([]);
  const [completedChains, setCompletedChains] = useState<number[]>([]);
  const [revealedInsight, setRevealedInsight] = useState<string | null>(null);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);

  // Solfeggio 432Hz ambient sound synthesis
  useEffect(() => {
    if (soundActive) {
      try {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        audioCtxRef.current = ctx;

        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(432, ctx.currentTime); // 432 Hz healing resonance
        gain.gain.setValueAtTime(0.001, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.035, ctx.currentTime + 2.0);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();

        oscillatorRef.current = osc;
        gainNodeRef.current = gain;
      } catch (err) {}
    } else {
      if (gainNodeRef.current && audioCtxRef.current) {
        try {
          gainNodeRef.current.gain.exponentialRampToValueAtTime(0.0001, audioCtxRef.current.currentTime + 0.5);
          setTimeout(() => {
            oscillatorRef.current?.stop();
            audioCtxRef.current?.close();
          }, 600);
        } catch (e) {}
      }
    }

    return () => {
      try {
        oscillatorRef.current?.stop();
        audioCtxRef.current?.close();
      } catch (e) {}
    };
  }, [soundActive]);

  // Breathing Loop Choreography
  useEffect(() => {
    if (!isBreathActive || mode !== 'breath') return;

    const interval = setInterval(() => {
      setBreathTimeLeft((prev) => {
        if (prev <= 1) {
          if (breathPhase === 'inhale') {
            setBreathPhase('hold');
            return 4;
          } else if (breathPhase === 'hold') {
            setBreathPhase('exhale');
            return 6;
          } else if (breathPhase === 'exhale') {
            setBreathPhase('rest');
            return 2;
          } else {
            setBreathPhase('inhale');
            setBreathCycles((c) => c + 1);
            return 4;
          }
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isBreathActive, breathPhase, mode]);

  // Handle Game Word Selection
  const currentChain = TADABBUR_CHAINS[chainIndex];

  const handleWordTap = (wordId: string) => {
    // Haptic
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try { window.navigator.vibrate(20); } catch (e) {}
    }

    const nextIndexNeeded = selectedWordIds.length;
    const expectedWord = currentChain.words[nextIndexNeeded];

    if (wordId === expectedWord.id) {
      const nextSelected = [...selectedWordIds, wordId];
      setSelectedWordIds(nextSelected);
      setRevealedInsight(expectedWord.quote);

      if (nextSelected.length === currentChain.words.length) {
        if (!completedChains.includes(chainIndex)) {
          setCompletedChains([...completedChains, chainIndex]);
        }
      }
    } else {
      // Gentle reset on wrong step
      setSelectedWordIds([]);
      setRevealedInsight('Focus gently and follow the divine progression.');
    }
  };

  const nextChain = () => {
    const nextIdx = (chainIndex + 1) % TADABBUR_CHAINS.length;
    setChainIndex(nextIdx);
    setSelectedWordIds([]);
    setRevealedInsight(null);
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-24 select-none bg-[#070806] text-ivory relative">
      {/* Bioluminescent Background Glow */}
      <div className="fixed inset-0 pointer-events-none opacity-25 bg-[radial-gradient(circle_at_50%_45%,#1c3628_0%,#070806_75%)]" />

      {/* Top Header */}
      <div className="flex items-center justify-between relative z-10">
        <Link 
          href="/lifeos" 
          className="flex items-center gap-1.5 text-xs text-muted hover:text-ivory transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>LifeOS Home</span>
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundActive(!soundActive)}
            className={`p-2 rounded-full border text-xs transition-all ${
              soundActive 
                ? 'text-emerald-400 border-emerald-500/40 bg-emerald-950/40 shadow-[0_0_12px_rgba(52,211,153,0.3)]' 
                : 'text-muted border-white/[0.08] hover:text-ivory'
            }`}
            title={soundActive ? '432Hz Calm Drone Active' : 'Sound Muted'}
          >
            {soundActive ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-950/70 text-emerald-300 border border-emerald-500/30 font-serif italic">
            Laya Serenity
          </span>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="flex bg-surface/90 p-1 rounded-2xl border border-white/[0.06] text-xs relative z-10">
        <button
          onClick={() => setMode('breath')}
          className={`flex-1 py-1.5 rounded-xl font-medium transition-all flex items-center justify-center gap-1.5 ${
            mode === 'breath' ? 'bg-deep text-emerald-400 shadow-sm border border-emerald-500/20' : 'text-muted hover:text-ivory'
          }`}
        >
          <Wind className="w-3.5 h-3.5" />
          <span>Sacred Breath</span>
        </button>
        <button
          onClick={() => setMode('game')}
          className={`flex-1 py-1.5 rounded-xl font-medium transition-all flex items-center justify-center gap-1.5 ${
            mode === 'game' ? 'bg-deep text-amber shadow-sm border border-amber/20' : 'text-muted hover:text-ivory'
          }`}
        >
          <Gamepad2 className="w-3.5 h-3.5" />
          <span>Tadabbur Flow</span>
        </button>
        <button
          onClick={() => setMode('reflection')}
          className={`flex-1 py-1.5 rounded-xl font-medium transition-all flex items-center justify-center gap-1.5 ${
            mode === 'reflection' ? 'bg-deep text-ivory shadow-sm border border-white/[0.1]' : 'text-muted hover:text-ivory'
          }`}
        >
          <Feather className="w-3.5 h-3.5" />
          <span>Laya Musings</span>
        </button>
      </div>

      {/* MODE 1: SACRED BREATH & MURAQABAH */}
      {mode === 'breath' && (
        <div className="space-y-4 relative z-10">
          <div className="p-6 rounded-3xl bg-surface/80 backdrop-blur-md border border-emerald-500/20 shadow-2xl flex flex-col items-center justify-center text-center relative overflow-hidden min-h-[380px]">
            
            {/* Phase Instructions */}
            <div className="space-y-1 mb-4">
              <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-mono">
                {breathPhase === 'inhale' && 'Inhale with Al-Hayy (The Ever-Living)'}
                {breathPhase === 'hold' && 'Hold with Al-Qayyum (The Sustainer)'}
                {breathPhase === 'exhale' && 'Release with Al-Hamd (Praise & Relief)'}
                {breathPhase === 'rest' && 'Rest in Sakinah (Inner Stillness)'}
              </span>
              <h2 className="text-2xl font-serif text-ivory tracking-wide font-medium">
                {breathPhase === 'inhale' && 'Breathe In Light'}
                {breathPhase === 'hold' && 'Stillness in the Heart'}
                {breathPhase === 'exhale' && 'Let Go of All Worry'}
                {breathPhase === 'rest' && 'Pure Peace'}
              </h2>
            </div>

            {/* Hypnotic Pulsing Breathing Circle */}
            <div className="relative w-64 h-64 flex items-center justify-center my-4">
              {/* Expanding Wave Rings */}
              <div 
                className={`absolute rounded-full border border-emerald-500/30 transition-all duration-1000 ease-in-out ${
                  breathPhase === 'inhale' ? 'w-64 h-64 opacity-80 scale-100' :
                  breathPhase === 'hold' ? 'w-64 h-64 opacity-90 scale-105' :
                  breathPhase === 'exhale' ? 'w-36 h-36 opacity-30 scale-75' :
                  'w-36 h-36 opacity-15 scale-70'
                }`}
                style={{
                  background: 'radial-gradient(circle, rgba(52, 211, 153, 0.15) 0%, transparent 70%)'
                }}
              />

              {/* Core Luminous Orb */}
              <div 
                className={`w-36 h-36 rounded-full bg-gradient-to-br from-[#1b3a2a] via-[#10241a] to-deep border border-emerald-400/40 shadow-[0_0_30px_rgba(52,211,153,0.3)] flex flex-col items-center justify-center transition-all duration-1000 ease-in-out ${
                  breathPhase === 'inhale' ? 'scale-110 shadow-[0_0_40px_rgba(52,211,153,0.5)]' :
                  breathPhase === 'hold' ? 'scale-110 shadow-[0_0_45px_rgba(212,168,83,0.4)] border-amber/40' :
                  breathPhase === 'exhale' ? 'scale-90 shadow-[0_0_15px_rgba(52,211,153,0.2)]' :
                  'scale-85'
                }`}
              >
                <span className="font-mono text-4xl font-bold text-ivory">
                  {breathTimeLeft}s
                </span>
                <span className="text-[10px] text-emerald-300 uppercase tracking-widest mt-1">
                  {breathPhase}
                </span>
              </div>
            </div>

            {/* Cycle Counter & Controls */}
            <div className="mt-4 flex items-center justify-between w-full max-w-[260px] text-xs pt-3 border-t border-white/[0.04]">
              <span className="text-muted font-mono">
                Completed: <strong className="text-emerald-400">{breathCycles}</strong> cycles
              </span>
              <button
                onClick={() => setIsBreathActive(!isBreathActive)}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/[0.06] hover:bg-white/[0.1] text-ivory font-medium transition-all"
              >
                {isBreathActive ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
                <span>{isBreathActive ? 'Pause' : 'Resume'}</span>
              </button>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-deep/90 border border-white/[0.06] text-xs text-muted leading-relaxed space-y-1.5">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <Compass className="w-3.5 h-3.5" />
              <span>Laya's Presence Note:</span>
            </div>
            <p>
              &ldquo;When thoughts wander toward what is missing or broken, anchor the breath in the remembrance of the Living God who never sleeps. Every inhale is a fresh gift of life; every exhale is an act of trust.&rdquo;
            </p>
          </div>
        </div>
      )}

      {/* MODE 2: TADABBUR FLOW COGNITIVE GAME */}
      {mode === 'game' && (
        <div className="space-y-4 relative z-10">
          <div className="p-5 rounded-3xl bg-surface/90 backdrop-blur-md border border-amber/25 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-amber font-mono">
                  Theme {chainIndex + 1} of {TADABBUR_CHAINS.length}
                </span>
                <h3 className="text-base font-serif text-ivory font-semibold">{currentChain.theme}</h3>
              </div>
              <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-amber-950/60 text-amber border border-amber/30">
                {selectedWordIds.length}/{currentChain.words.length} Connected
              </span>
            </div>

            <p className="text-xs text-muted/95 italic">
              {currentChain.prompt} (Tap in the natural spiritual order)
            </p>

            {/* Interactive Word Water-Lilies Grid */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              {currentChain.words.map((w, idx) => {
                const isSelected = selectedWordIds.includes(w.id);

                return (
                  <button
                    key={w.id}
                    onClick={() => handleWordTap(w.id)}
                    className={`p-4 rounded-2xl border text-left transition-all active:scale-95 flex flex-col justify-between min-h-[90px] ${
                      isSelected
                        ? 'bg-gradient-to-br from-amber-950/50 to-surface border-amber/60 shadow-[0_0_15px_rgba(212,168,83,0.3)] ring-1 ring-amber/40'
                        : 'bg-deep/80 border-white/[0.05] hover:border-white/[0.15] hover:bg-deep'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-arabic text-xl font-bold text-ivory">{w.ar}</span>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    </div>
                    <div>
                      <div className="text-xs font-serif font-medium text-amber/90">{w.tr}</div>
                      <div className="text-[10px] text-muted">{w.meaning}</div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Revealed Insight Box */}
            {revealedInsight && (
              <div className="p-3.5 rounded-xl bg-deep/95 border border-amber/30 text-xs space-y-1 animate-fade-in">
                <span className="text-[10px] text-amber uppercase font-semibold">Qur'anic Anchor:</span>
                <p className="text-ivory font-serif italic text-sm leading-relaxed">&ldquo;{revealedInsight}&rdquo;</p>
              </div>
            )}

            {/* Chain Completed State */}
            {selectedWordIds.length === currentChain.words.length && (
              <div className="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 text-center space-y-2">
                <h4 className="text-sm font-semibold text-emerald-400">✨ Constellation Complete!</h4>
                <button
                  onClick={nextChain}
                  className="px-5 py-2 rounded-xl bg-amber text-black font-semibold text-xs shadow-md active:scale-95 transition-all"
                >
                  Next Wisdom Journey &rarr;
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODE 3: LAYA CONTEMPLATIVE MUSINGS */}
      {mode === 'reflection' && (
        <div className="space-y-3 relative z-10">
          {[
            {
              title: "On Wealth and True Abundance (Al-Ghina)",
              arabic: "لَيْسَ الْغِنَى عَنْ كَثْرَةِ الْعَرَضِ ، وَلَكِنَّ الْغِنَى غِنَى النَّفْسِ",
              trans: "True wealth does not come from a surplus of material goods, but rather true wealth is the self-sufficiency of the soul. (Sahih al-Bukhari 6446)",
              insight: "When you repeat 'Astaghfirullah' and 'Alhamdulillah', you are not merely reciting words; you are untying the subconscious knot of scarcity that causes human desperation. Abundance flows toward grateful, quiet vessels."
            },
            {
              title: "On Security in Times of Turbulence",
              arabic: "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
              trans: "Allah is sufficient for us, and He is the best Disposer of affairs.",
              insight: "You do not need to orchestrate every tomorrow. You only need to place your sincere intention into the current hour, perform your duty with excellence (Ihsan), and leave the cosmic outcomes to the One who commands the stars."
            },
            {
              title: "On Beautiful Character (Husn al-Khuluq)",
              arabic: "أَكْمَلُ الْمُؤْمِنِينَ إِيمَانًا أَحْسَنُهُمْ خُلُقًا",
              trans: "The most complete of believers in faith are those with the best character. (Jami' at-Tirmidhi 1162)",
              insight: "Good character is not weak compliance; it is supreme emotional mastery. It is the ability to absorb harshness from people and return kindness, knowing your transaction is exclusively with the Almighty."
            }
          ].map((item, idx) => (
            <div key={idx} className="p-4 rounded-2xl bg-surface border border-white/[0.06] space-y-2">
              <h3 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">{item.title}</h3>
              <p className="font-arabic text-lg text-ivory text-right leading-loose">{item.arabic}</p>
              <p className="text-xs font-serif italic text-amber/90">{item.trans}</p>
              <p className="text-xs text-muted/95 leading-relaxed pt-1 border-t border-white/[0.04]">
                {item.insight}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
