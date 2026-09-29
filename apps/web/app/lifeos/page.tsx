'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Clock, 
  Sparkles, 
  BookOpen, 
  HeartHandshake, 
  ShieldAlert, 
  Gamepad2, 
  ArrowRight, 
  CheckCircle2, 
  ChevronRight, 
  RefreshCw, 
  Zap,
  ListTodo,
  ScrollText,
  Sun,
  Flame,
  Check
} from 'lucide-react';

interface SalahStatus {
  current_prayer: string;
  state: string;
  status_message: string;
  remaining_formatted: string;
  remaining_friendly?: string;
  next_prayer: string;
  next_in_formatted: string;
  next_in_friendly?: string;
  schedule: Record<string, string>;
  city?: string;
  madhhab: string;
}

interface DhikrItem {
  id: string;
  arabic: string;
  transliteration: string;
  translation: string;
  count: number;
  target: number;
  percentage: number;
  completed: boolean;
}

export default function LifeOSDashboard() {
  const [salah, setSalah] = useState<SalahStatus | null>(null);
  const [dhikrList, setDhikrList] = useState<DhikrItem[]>([]);
  const [tasksSummary, setTasksSummary] = useState<any>(null);
  const [dailyAyah, setDailyAyah] = useState<any>(null);
  const [dailyHadith, setDailyHadith] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [quickTappedId, setQuickTappedId] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const res = await fetch('/api/lifeos/today');
      if (res.ok) {
        const data = await res.json();
        setSalah(data.salah);
        setDhikrList(data.dhikr || []);
        setTasksSummary(data.tasks?.summary || null);
        setDailyAyah(data.daily_ayah || null);
        setDailyHadith(data.daily_hadith || null);
      }
    } catch (e) {
      // Offline fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleQuickDhikr = (dhikrId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setQuickTappedId(dhikrId);
    setTimeout(() => setQuickTappedId(null), 300);

    setDhikrList((prev) =>
      prev.map((item) => {
        if (item.id === dhikrId) {
          const newCount = item.count + 1;
          const target = item.target || 100;
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

    fetch('/api/lifeos/dhikr/increment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dhikr_id: dhikrId, delta: 1 }),
    }).catch(() => {});
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 lg:px-10 py-6 space-y-6 text-ivory select-none pb-28 scrollbar-none max-w-5xl mx-auto w-full">
      {/* Top Header Card */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-semibold">
            Personal Development & Islamic Practice
          </span>
          <h1 className="font-serif text-2xl text-ivory">Islamic LifeOS</h1>
        </div>
        <div className="flex items-center gap-1.5">
          <Link
            href="/lifeos/history"
            className="px-3 py-1.5 rounded-full bg-amber/15 border border-amber/30 text-amber text-xs font-semibold flex items-center gap-1.5 hover:bg-amber/25 transition-all shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Analytics</span>
          </Link>
          <button
            onClick={fetchData}
            className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors text-ivory/80"
            title="Refresh LifeOS Sync"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 1. Salah Live Card */}
      <Link href="/lifeos/salah" className="block group">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-950/40 via-white/[0.02] to-transparent border border-emerald-500/30 p-5 space-y-3 shadow-2xl backdrop-blur-xl group-hover:border-emerald-400/50 transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse" />
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-emerald-300">
                {salah?.current_prayer || 'Duha / Ishraq (Chasht)'}
              </span>
            </div>
            <span className="text-[10px] font-mono text-ivory/50">
              {salah?.city || 'Islamabad, Pakistan'} • {salah?.madhhab?.toUpperCase() || 'HANAFI'}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-2xl font-serif text-ivory">
                {salah?.remaining_friendly || salah?.remaining_formatted || 'Valid for 2 hr 45 min'}
              </div>
              <p className="text-xs text-ivory/60 font-sans mt-0.5">
                {salah?.status_message || 'Duha window active. Highly recommended Sunnah prayer.'}
              </p>
            </div>
            <ChevronRight className="w-5 h-5 text-ivory/40 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
          </div>

          {/* Times Mini Bar */}
          <div className="grid grid-cols-5 gap-1.5 pt-2 border-t border-white/5 text-center text-[10px] font-mono">
            {['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'].map((pKey) => (
              <div key={pKey} className="p-1.5 rounded-lg bg-black/30 border border-white/5">
                <span className="text-ivory/40 uppercase block text-[9px]">{pKey}</span>
                <span className="text-ivory/90 font-bold">{salah?.schedule?.[pKey] || '--:--'}</span>
              </div>
            ))}
          </div>
        </div>
      </Link>

      {/* 2. Daily Focus Tasks Widget */}
      <Link href="/lifeos/tasks" className="block group">
        <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-3 group-hover:border-white/20 transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-amber uppercase tracking-wider">
              <ListTodo className="w-4 h-4" />
              <span>Daily Focus Tasks</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber/10 text-amber border border-amber/20">
              One-Liner Rule
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-lg font-serif text-ivory">
                {tasksSummary?.completed || 0} of {tasksSummary?.total || 3} Completed
              </div>
              <p className="text-xs text-ivory/50">
                {tasksSummary?.est_minutes_total ? `${tasksSummary.est_minutes_total} mins estimated focus time` : 'Distraction-shield mode ready'}
              </p>
            </div>
            <ChevronRight className="w-5 h-5 text-ivory/40 group-hover:text-amber group-hover:translate-x-0.5 transition-all" />
          </div>
        </div>
      </Link>

      {/* 3. Daily Classical Tafsir & Hadith Widget */}
      <Link href="/lifeos/tafsir" className="block group">
        <div className="rounded-3xl bg-gradient-to-br from-emerald-950/20 via-white/[0.02] to-transparent border border-emerald-500/20 p-5 space-y-3 group-hover:border-emerald-400/40 transition-all">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider">
              <ScrollText className="w-4 h-4" />
              <span>Daily Ayah & Classical Hanafi Tafsir</span>
            </div>
            <ChevronRight className="w-4 h-4 text-ivory/40 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
          </div>

          <div className="space-y-1.5">
            <div className="font-serif text-lg text-ivory text-right whitespace-nowrap overflow-x-auto scrollbar-none">
              {dailyAyah?.arabic || 'لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا'}
            </div>
            <p className="text-xs text-ivory/70 italic line-clamp-2">
              "{dailyAyah?.translation || 'Allah does not burden a soul beyond that it can bear...'}"
            </p>
          </div>
        </div>
      </Link>

      {/* 4. Quick Dhikr Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-ivory/60">
            Daily Adhkar & Counter
          </h3>
          <Link href="/lifeos/dhikr" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
            <span>Open Wave Counter</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-2">
          {dhikrList.slice(0, 3).map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-3.5 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/10 transition-all"
            >
              <div className="min-w-0 flex-1">
                <div className="font-serif text-base text-ivory whitespace-nowrap overflow-x-auto scrollbar-none text-right">
                  {item.arabic}
                </div>
                <div className="text-xs font-medium text-emerald-400 truncate">
                  {item.transliteration}
                </div>
              </div>

              <button
                type="button"
                onClick={(e) => handleQuickDhikr(item.id, e)}
                className={`ml-4 px-4 py-2 rounded-xl border flex items-center gap-2 font-mono text-xs font-bold transition-all active:scale-95 ${
                  quickTappedId === item.id
                    ? 'bg-emerald-400 text-black border-emerald-400 scale-105 shadow-[0_0_15px_#34d399]'
                    : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20'
                }`}
              >
                <span>{item.count}</span>
                <span className="text-[10px] text-ivory/40">/ {item.target || 100}</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Navigation Grid (Quran, Duas, Muhasabah, Signal Game) */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/lifeos/quran"
          className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/15 transition-all space-y-2 group"
        >
          <BookOpen className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
          <div>
            <h4 className="text-sm font-medium text-ivory">Quran Library</h4>
            <p className="text-[11px] text-ivory/40">Mulk, Ya-Sin, Waqiah, Kahf</p>
          </div>
        </Link>

        <Link
          href="/lifeos/duas"
          className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/15 transition-all space-y-2 group"
        >
          <HeartHandshake className="w-5 h-5 text-amber group-hover:scale-110 transition-transform" />
          <div>
            <h4 className="text-sm font-medium text-ivory">Authentic Duas</h4>
            <p className="text-[11px] text-ivory/40">Hisn al-Muslim & Sunnah</p>
          </div>
        </Link>

        <Link
          href="/lifeos/muhasabah"
          className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/15 transition-all space-y-2 group"
        >
          <ShieldAlert className="w-5 h-5 text-rose-400 group-hover:scale-110 transition-transform" />
          <div>
            <h4 className="text-sm font-medium text-ivory">Muhasabah</h4>
            <p className="text-[11px] text-ivory/40">Daily Self-Accountability</p>
          </div>
        </Link>

        <Link
          href="/lifeos/game"
          className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/15 transition-all space-y-2 group"
        >
          <Gamepad2 className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
          <div>
            <h4 className="text-sm font-medium text-ivory">SIGNAL</h4>
            <p className="text-[11px] text-ivory/40">Cognitive Agility & Focus</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
