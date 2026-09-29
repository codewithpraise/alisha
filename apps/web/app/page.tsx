'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  MessageCircle,
  Phone,
  Clock,
  Compass,
  Sparkles,
  Headphones,
  Heart,
  Volume2,
  Calendar,
  Flame,
  ArrowRight,
  ShieldCheck,
  Moon,
  Coffee,
  CheckCircle2,
  Share2,
} from 'lucide-react';
import VoiceBubble from '@/components/chat/VoiceBubble';

export default function HomePage() {
  const [profile, setProfile] = useState<any>(null);
  const [salahToday, setSalahToday] = useState<any>(null);
  const [dailyAyah, setDailyAyah] = useState<any>(null);
  const [recentVoice, setRecentVoice] = useState<any>(null);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Fetch profile & day counter
    async function loadData() {
      try {
        const [profRes, lifeRes, voiceRes] = await Promise.all([
          fetch('/api/profile'),
          fetch('/api/lifeos/today'),
          fetch('/api/voice/notes'),
        ]);

        if (profRes.ok) {
          const profData = await profRes.json();
          setProfile(profData);
        }
        if (lifeRes.ok) {
          const lifeData = await lifeRes.json();
          setSalahToday(lifeData.salah);
          setDailyAyah(lifeData.daily_ayah);
        }
        if (voiceRes.ok) {
          const vData = await voiceRes.json();
          if (vData.voice_notes && vData.voice_notes.length > 0) {
            setRecentVoice(vData.voice_notes[0]);
          }
        }
      } catch (e) {
        console.error('Failed loading home data:', e);
      }
    }

    loadData();

    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, []);

  const handleInstallClick = () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choice: any) => {
        if (choice.outcome === 'accepted') {
          setIsInstalled(true);
        }
        setDeferredPrompt(null);
      });
    } else {
      alert("To install as standalone app:\n1. Tap browser menu (3 dots)\n2. Select 'Add to Home screen' or 'Install App'");
    }
  };

  const dayCounter = profile?.day_counter || 'day 47';
  const nextPrayer = salahToday?.next_prayer || { name: 'Dhuhr', formatted_time: '12:08 PM', time_remaining: 'in 32m' };

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 lg:px-10 py-6 pb-28 flex flex-col gap-6 scrollbar-none text-ivory select-none max-w-5xl mx-auto w-full">
      {/* ── TOP EDITORIAL HERO ── */}
      <div className="pt-1 flex flex-col gap-1.5">
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber/10 border border-amber/20 text-amber text-[10px] font-mono font-semibold tracking-widest uppercase shadow-[0_0_12px_rgba(212,168,83,0.12)]">
            <span className="w-1.5 h-1.5 rounded-full bg-amber animate-ping" />
            <span>Private Simulation Engine</span>
            <span>&bull;</span>
            <span className="text-ivory font-bold">{dayCounter}</span>
          </div>

          <span className="text-[11px] font-mono text-muted flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block shadow-[0_0_6px_#34d399]" />
            Active Presence
          </span>
        </div>

        <h1 className="font-serif text-[32px] sm:text-[38px] font-normal text-ivory leading-tight mt-1">
          alisha bubbzieee
        </h1>
        <p className="text-xs sm:text-sm text-muted leading-relaxed font-sans">
          Reconstructing natural text cadence, humor, voice notes, and proactive rhythm with deep emotional continuity.
        </p>
      </div>

      {/* ── PROFILE & PERSONA SNAPSHOT CARD ── */}
      <div className="bg-gradient-to-br from-[#1C1D1A] via-[#161714] to-[#121310] border border-amber/25 rounded-3xl p-4.5 sm:p-5 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-amber/5 rounded-full blur-2xl pointer-events-none" />
        
        <div className="flex items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3.5">
            <div className="relative">
              <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-amber/30 via-[#2A2B27] to-[#161714] border-2 border-amber/40 flex items-center justify-center font-serif text-2xl italic text-amber shadow-[0_0_16px_rgba(212,168,83,0.2)]">
                A
              </div>
              <span className="absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-[#161714] shadow-[0_0_8px_#34d399]" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-serif font-medium text-ivory">Alisha</h3>
                <span className="text-[10px] font-mono bg-amber/15 text-amber px-2 py-0.5 rounded-full border border-amber/30">
                  Verified Age 20
                </span>
              </div>
              <p className="text-xs text-muted flex items-center gap-1.5 mt-0.5">
                <span>Biochemistry &bull; UK</span>
                <span>&middot;</span>
                <span className="text-amber">active now</span>
              </p>
            </div>
          </div>

          <Link
            href="/chat"
            className="p-2.5 rounded-2xl bg-amber text-black hover:bg-amber-dark transition-transform active:scale-95 shadow-[0_0_12px_rgba(212,168,83,0.3)] shrink-0"
            aria-label="Start Conversation"
          >
            <MessageCircle className="w-5 h-5 fill-current" />
          </Link>
        </div>

        {/* Live Corpus Statistics Matrix */}
        <div className="grid grid-cols-3 gap-2.5 pt-3.5 border-t border-white/[0.08] text-center">
          <div className="bg-white/[0.02] rounded-2xl p-2 border border-white/[0.04]">
            <div className="text-base font-bold text-amber font-mono">13,653</div>
            <div className="text-[10px] text-muted uppercase font-medium">Msgs Analyzed</div>
          </div>
          <div className="bg-white/[0.02] rounded-2xl p-2 border border-white/[0.04]">
            <div className="text-base font-bold text-amber font-mono">87</div>
            <div className="text-[10px] text-muted uppercase font-medium">Voice Notes</div>
          </div>
          <div className="bg-white/[0.02] rounded-2xl p-2 border border-white/[0.04]">
            <div className="text-base font-bold text-amber font-mono">68</div>
            <div className="text-[10px] text-muted uppercase font-medium">Verified Facts</div>
          </div>
        </div>

        {/* Behavioral Cadence Badges */}
        <div className="flex flex-wrap gap-1.5 mt-3.5 pt-3 border-t border-white/[0.05]">
          <span className="text-[10.5px] px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 text-muted">
            💬 lowercase cadence
          </span>
          <span className="text-[10.5px] px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 text-muted">
            ☕ green tea rituals
          </span>
          <span className="text-[10.5px] px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 text-muted">
            🐾 cat obsessor
          </span>
          <span className="text-[10.5px] px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 text-muted">
            ⚡ rapid double-texts
          </span>
        </div>
      </div>

      {/* ── RESPONSIVE 2-COL WIDGET ROW (VOICE ARCHIVE & SPIRITUAL LIFEOS) ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* RECENT INSTAGRAM VOICE NOTE WIDGET */}
        {recentVoice ? (
          <div className="bg-surface border border-hairline rounded-3xl p-4 sm:p-5 flex flex-col justify-between gap-2.5 shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-amber/20 flex items-center justify-center text-amber">
                  <Volume2 className="w-3.5 h-3.5" />
                </div>
                <span className="text-xs font-semibold text-ivory font-serif">
                  Instagram Voice Note Archive
                </span>
              </div>
              <Link
                href="/memories"
                className="text-[11px] text-amber hover:underline flex items-center gap-0.5 font-medium"
              >
                <span>View all 87</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <VoiceBubble
              audioSrc={recentVoice.audio_url || `/voice/${recentVoice.media_path}`}
              durationLabel="0:17"
            />

            <p className="text-[11.5px] text-muted italic bg-black/25 px-3 py-1.5 rounded-xl border border-white/[0.04]">
              "{recentVoice.transcript || recentVoice.content}"
            </p>
          </div>
        ) : (
          <div className="bg-surface border border-hairline rounded-3xl p-4 sm:p-5 flex flex-col justify-center gap-2 text-center text-muted text-xs">
            Voice Note Archive Ready
          </div>
        )}

        {/* TODAY'S LIFEOS & SPIRITUAL FOCUS */}
        <div className="bg-surface border border-hairline rounded-3xl p-4 sm:p-5 flex flex-col gap-3 shadow-md justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Compass className="w-3.5 h-3.5" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-ivory font-serif">Spiritual Hub (Islamabad)</h4>
                <p className="text-[10px] text-muted">Dynamic Salah & daily wisdom</p>
              </div>
            </div>
            <Link
              href="/lifeos"
              className="text-[11px] text-amber hover:underline flex items-center gap-0.5 font-medium"
            >
              <span>Open LifeOS</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div className="bg-[#141512] border border-white/[0.05] rounded-2xl p-3 flex flex-col justify-between">
              <div className="text-[10px] font-mono text-muted uppercase">Next Salah</div>
              <div className="text-sm font-semibold text-ivory mt-1">
                {nextPrayer.name}
              </div>
              <div className="text-[11px] text-amber font-mono mt-0.5">
                {nextPrayer.formatted_time} ({nextPrayer.time_remaining})
              </div>
            </div>

            <div className="bg-[#141512] border border-white/[0.05] rounded-2xl p-3 flex flex-col justify-between">
              <div className="text-[10px] font-mono text-muted uppercase">Dhikr Goal</div>
              <div className="text-sm font-semibold text-ivory mt-1">
                SubhanAllah
              </div>
              <div className="text-[11px] text-emerald-400 font-mono mt-0.5">
                100 Target &bull; Active
              </div>
            </div>
          </div>

          {dailyAyah && (
            <div className="bg-black/30 border border-white/[0.04] rounded-2xl p-3 text-xs leading-relaxed space-y-1">
              <div className="flex items-center justify-between text-[10px] font-mono text-amber/80">
                <span>DAILY QURAN AYAH</span>
                <span>Surah {dailyAyah.surah_name} [{dailyAyah.surah}:{dailyAyah.ayah}]</span>
              </div>
              <p className="text-ivory font-serif text-[13px] italic">
                "{dailyAyah.translation}"
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ── CORE NAVIGATION MODULES ── */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/chat"
          className="bg-surface border border-hairline hover:border-amber/50 hover:bg-raised rounded-3xl p-4 flex flex-col gap-2.5 transition-all group shadow-sm"
        >
          <div className="w-10 h-10 rounded-2xl bg-amber/15 border border-amber/30 flex items-center justify-center text-amber group-hover:scale-105 transition-transform">
            <MessageCircle className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ivory group-hover:text-amber transition-colors">
              Burst Chat
            </h4>
            <p className="text-xs text-muted leading-tight mt-0.5">
              Multi-bubble cadence, typing delays & banter
            </p>
          </div>
        </Link>

        <Link
          href="/call"
          className="bg-surface border border-hairline hover:border-amber/50 hover:bg-raised rounded-3xl p-4 flex flex-col gap-2.5 transition-all group shadow-sm"
        >
          <div className="w-10 h-10 rounded-2xl bg-amber/15 border border-amber/30 flex items-center justify-center text-amber group-hover:scale-105 transition-transform">
            <Phone className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ivory group-hover:text-amber transition-colors">
              Voice Call
            </h4>
            <p className="text-xs text-muted leading-tight mt-0.5">
              Real-time speech with natural interruption
            </p>
          </div>
        </Link>

        <Link
          href="/memories"
          className="bg-surface border border-hairline hover:border-amber/50 hover:bg-raised rounded-3xl p-4 flex flex-col gap-2.5 transition-all group shadow-sm"
        >
          <div className="w-10 h-10 rounded-2xl bg-amber/15 border border-amber/30 flex items-center justify-center text-amber group-hover:scale-105 transition-transform">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ivory group-hover:text-amber transition-colors">
              Shared Vault
            </h4>
            <p className="text-xs text-muted leading-tight mt-0.5">
              68 Facts & 87 Instagram Voice Notes
            </p>
          </div>
        </Link>

        <Link
          href="/lifeos/history"
          className="bg-surface border border-hairline hover:border-amber/50 hover:bg-raised rounded-3xl p-4 flex flex-col gap-2.5 transition-all group shadow-sm"
        >
          <div className="w-10 h-10 rounded-2xl bg-amber/15 border border-amber/30 flex items-center justify-center text-amber group-hover:scale-105 transition-transform">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ivory group-hover:text-amber transition-colors">
              Dashboard & History
            </h4>
            <p className="text-xs text-muted leading-tight mt-0.5">
              Heatmaps, Dhikr dials & focus charts
            </p>
          </div>
        </Link>
      </div>

      {/* ── CLEAN PWA INSTALL BANNER (ZERO DEVICE SPECIFICITY) ── */}
      {!isInstalled && (
        <div className="bg-gradient-to-br from-[#1B1C19] to-[#141512] border border-amber/20 rounded-3xl p-4 flex items-center justify-between gap-3 shadow-lg">
          <div className="flex-1">
            <h4 className="text-xs font-semibold text-ivory">Install Standalone App</h4>
            <p className="text-[11px] text-muted mt-0.5">
              Add to Home Screen for fast offline access & background audio.
            </p>
          </div>
          <button
            onClick={handleInstallClick}
            className="bg-amber hover:bg-amber-dark text-[#111210] font-semibold text-xs py-2 px-3.5 rounded-xl shrink-0 transition-transform active:scale-95 cursor-pointer shadow-[0_4px_14px_rgba(212,168,83,0.2)]"
          >
            Install
          </button>
        </div>
      )}
    </div>
  );
}
