'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Clock, 
  ShieldAlert, 
  AlertTriangle, 
  ArrowLeft, 
  Check, 
  RefreshCw, 
  Compass, 
  MapPin, 
  Sun, 
  Moon, 
  Sunrise, 
  Sunset,
  Sparkles,
  Zap
} from 'lucide-react';

interface TimelineItem {
  id: string;
  name: string;
  time: string;
  status: 'passed' | 'active' | 'upcoming';
}

interface SalahStatus {
  current_prayer: string;
  state: string;
  status_message: string;
  sun_phase?: string;
  valid_duration_formatted?: string;
  valid_duration_seconds?: number;
  elapsed_formatted?: string;
  elapsed_seconds?: number;
  remaining_formatted: string;
  remaining_friendly?: string;
  remaining_seconds: number;
  progress_pct?: number;
  next_prayer: string;
  next_in_formatted: string;
  next_in_friendly?: string;
  next_in_seconds: number;
  schedule: Record<string, string>;
  prohibited_windows: Record<string, string>;
  makruh_notes?: Record<string, string>;
  city?: string;
  madhhab: string;
  method: string;
  timeline?: TimelineItem[];
}

const PRESET_LOCATIONS = [
  { name: 'Pakistan (Islamabad)', lat: 33.6844, lng: 73.0479, tz: 5.0, method: 'karachi' },
  { name: 'Pakistan (Karachi)', lat: 24.8607, lng: 67.0011, tz: 5.0, method: 'karachi' },
  { name: 'Pakistan (Lahore)', lat: 31.5204, lng: 74.3587, tz: 5.0, method: 'karachi' },
  { name: 'Makkah, KSA', lat: 21.4225, lng: 39.8262, tz: 3.0, method: 'umm_al_qura' },
  { name: 'London, UK', lat: 51.5074, lng: -0.1278, tz: 1.0, method: 'mwl' },
];

export default function SalahTrackerPage() {
  const [selectedLocation, setSelectedLocation] = useState(PRESET_LOCATIONS[0]);
  const [madhhab, setMadhhab] = useState<'hanafi' | 'shafii'>('hanafi');
  const [status, setStatus] = useState<SalahStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [prayedPrayers, setPrayedPrayers] = useState<Record<string, boolean>>({});
  const [localSecondsRemaining, setLocalSecondsRemaining] = useState<number>(0);

  const fetchSalah = async () => {
    try {
      const q = new URLSearchParams({
        lat: selectedLocation.lat.toString(),
        lng: selectedLocation.lng.toString(),
        tz: selectedLocation.tz.toString(),
        madhhab: madhhab,
        method: selectedLocation.method
      });
      const res = await fetch(`/api/lifeos/salah?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setStatus(data.status);
        if (data.status?.remaining_seconds !== undefined) {
          setLocalSecondsRemaining(data.status.remaining_seconds);
        }
      }
    } catch (e) {
      // Offline fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSalah();
    const pollInterval = setInterval(fetchSalah, 30000);
    return () => clearInterval(pollInterval);
  }, [selectedLocation, madhhab]);

  // 1-second live countdown ticker
  useEffect(() => {
    const timer = setInterval(() => {
      setLocalSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatSecondsToHms = (totalSec: number) => {
    const hrs = Math.floor(totalSec / 3600);
    const mins = Math.floor((totalSec % 3600) / 60);
    const secs = totalSec % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const togglePrayed = (prayerName: string) => {
    setPrayedPrayers((prev) => ({
      ...prev,
      [prayerName]: !prev[prayerName]
    }));
  };

  const isProhibited = status?.state === 'prohibited';
  const isMakruh = status?.state === 'makruh_late';

  const scheduleList = status?.schedule ? [
    { key: 'fajr', name: 'Fajr', time: status.schedule.fajr, icon: Sunrise },
    { key: 'sunrise', name: 'Sunrise (Tulu\')', time: status.schedule.sunrise, icon: Sun, prohibited: true },
    { key: 'ishraq_duha', name: 'Duha (Chasht)', time: status.schedule.ishraq_duha || '06:14', icon: Sun },
    { key: 'dhuhr', name: 'Dhuhr', time: status.schedule.dhuhr, icon: Sun },
    { key: 'asr', name: 'Asr', time: status.schedule.asr, icon: Sun },
    { key: 'maghrib', name: 'Maghrib', time: status.schedule.maghrib, icon: Sunset },
    { key: 'isha', name: 'Isha', time: status.schedule.isha, icon: Moon },
  ] : [];

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6 text-ivory select-none pb-28 scrollbar-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>
        <div className="text-center">
          <span className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-semibold">
            Astronomical Fiqh Engine
          </span>
          <h1 className="font-serif text-xl text-ivory">Salah & Solar Arc</h1>
        </div>
        <button
          onClick={fetchSalah}
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors text-ivory/80"
          title="Recalculate Times"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Location & Madhhab Selector Bar */}
      <div className="flex items-center justify-between bg-white/[0.03] p-2 rounded-2xl border border-white/5 gap-2">
        <div className="flex items-center gap-1.5 flex-1 min-w-0 pl-1">
          <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <select
            value={selectedLocation.name}
            onChange={(e) => {
              const loc = PRESET_LOCATIONS.find((l) => l.name === e.target.value);
              if (loc) setSelectedLocation(loc);
            }}
            className="bg-transparent text-xs text-ivory font-medium focus:outline-none truncate w-full cursor-pointer"
          >
            {PRESET_LOCATIONS.map((loc) => (
              <option key={loc.name} value={loc.name} className="bg-[#121310] text-ivory">
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-1 bg-black/40 p-0.5 rounded-xl border border-white/5">
          <button
            onClick={() => setMadhhab('hanafi')}
            className={`px-2.5 py-1 rounded-lg text-[10px] font-mono uppercase font-semibold transition-all ${
              madhhab === 'hanafi'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-ivory/40 hover:text-ivory'
            }`}
          >
            Hanafi
          </button>
          <button
            onClick={() => setMadhhab('shafii')}
            className={`px-2.5 py-1 rounded-lg text-[10px] font-mono uppercase font-semibold transition-all ${
              madhhab === 'shafii'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-ivory/40 hover:text-ivory'
            }`}
          >
            Shafi'i
          </button>
        </div>
      </div>

      {/* Hero Live Countdown & Solar State Card */}
      <div
        className={`relative overflow-hidden rounded-3xl border p-6 space-y-4 shadow-2xl backdrop-blur-xl transition-all ${
          isProhibited
            ? 'bg-gradient-to-br from-rose-950/40 via-black/40 to-transparent border-rose-500/30 shadow-[0_0_30px_rgba(244,63,94,0.15)]'
            : isMakruh
            ? 'bg-gradient-to-br from-amber-950/40 via-black/40 to-transparent border-amber/30 shadow-[0_0_30px_rgba(212,168,83,0.15)]'
            : 'bg-gradient-to-br from-emerald-950/40 via-white/[0.02] to-transparent border-emerald-500/20 shadow-[0_0_30px_rgba(52,211,153,0.15)]'
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full animate-pulse ${
                isProhibited ? 'bg-rose-400' : isMakruh ? 'bg-amber' : 'bg-emerald-400'
              }`}
            />
            <span className="text-xs font-mono font-semibold uppercase tracking-widest text-ivory/80">
              {status?.current_prayer || 'Calculating...'}
            </span>
          </div>
          <span
            className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border uppercase tracking-wider ${
              isProhibited
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                : isMakruh
                ? 'bg-amber/20 border-amber/40 text-amber'
                : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
            }`}
          >
            {isProhibited ? 'Prohibited Window' : isMakruh ? 'Makruh Late Window' : 'Active Window'}
          </span>
        </div>

        {/* Live Big Countdown Timer */}
        <div className="space-y-1 py-1">
          <div className="text-4xl font-mono font-bold tracking-wider text-ivory flex items-baseline gap-2">
            <span>{formatSecondsToHms(localSecondsRemaining)}</span>
            <span className="text-xs font-mono text-ivory/40 uppercase font-normal">remaining</span>
          </div>
          <p className="text-xs text-ivory/70 font-sans leading-relaxed">
            {status?.status_message || 'Calculating active astronomical window...'}
          </p>
        </div>

        {/* Dynamic Progress Bar */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-[10px] font-mono text-ivory/50">
            <span>Elapsed: {status?.elapsed_formatted || '0m'}</span>
            <span>Total Valid Window: {status?.valid_duration_formatted || '1h 20m'}</span>
          </div>
          <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden">
            <div
              className={`h-full transition-all duration-1000 ease-out rounded-full ${
                isProhibited ? 'bg-rose-400' : isMakruh ? 'bg-amber' : 'bg-emerald-400'
              }`}
              style={{ width: `${status?.progress_pct || 35}%` }}
            />
          </div>
        </div>

        {/* Next Prayer Callout */}
        <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
          <span className="text-ivory/50">Upcoming Prayer:</span>
          <span className="font-medium text-emerald-400 flex items-center gap-1">
            <span>{status?.next_prayer}</span>
            <span className="text-ivory/40 font-mono text-[11px]">
              ({status?.next_in_friendly || status?.next_in_formatted})
            </span>
          </span>
        </div>
      </div>

      {/* Interactive Solar Arc Graph (SVG) */}
      <div className="rounded-3xl bg-white/[0.03] border border-white/10 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-mono font-semibold text-ivory/80 uppercase tracking-wider">
            <Sun className="w-4 h-4 text-amber" />
            <span>Solar Arc & Celestial Position</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
            {status?.sun_phase || 'Daylight Arc'}
          </span>
        </div>

        {/* Visual Arc SVG */}
        <div className="relative w-full h-28 flex items-center justify-center">
          <svg className="w-full h-full" viewBox="0 0 300 100" fill="none">
            {/* Horizon line */}
            <line x1="20" y1="80" x2="280" y2="80" stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
            {/* Solar Path Arc */}
            <path
              d="M 30 80 Q 150 10 270 80"
              stroke="url(#solarGradient)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            {/* Sunrise Point */}
            <circle cx="50" cy="72" r="4" fill="#D4A853" />
            <text x="50" y="93" fill="rgba(255,255,255,0.4)" fontSize="8" textAnchor="middle" fontFamily="monospace">
              Sunrise {status?.schedule.sunrise}
            </text>

            {/* Zenith Point */}
            <circle cx="150" cy="18" r="5" fill="#34d399" className="animate-pulse" />
            <text x="150" y="32" fill="#34d399" fontSize="8" textAnchor="middle" fontFamily="monospace">
              Dhuhr Zawal {status?.schedule.dhuhr}
            </text>

            {/* Sunset Point */}
            <circle cx="250" cy="72" r="4" fill="#f43f5e" />
            <text x="250" y="93" fill="rgba(255,255,255,0.4)" fontSize="8" textAnchor="middle" fontFamily="monospace">
              Maghrib {status?.schedule.maghrib}
            </text>

            <defs>
              <linearGradient id="solarGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#D4A853" />
                <stop offset="50%" stopColor="#34d399" />
                <stop offset="100%" stopColor="#f43f5e" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Prohibited Solar Windows Guidance */}
      <div className="rounded-3xl bg-rose-950/10 border border-rose-500/20 p-5 space-y-3">
        <div className="flex items-center gap-2 text-xs font-mono font-semibold text-rose-400 uppercase tracking-wider">
          <ShieldAlert className="w-4 h-4" />
          <span>Prohibited Prayer Windows (Fiqh Rule)</span>
        </div>
        <p className="text-xs text-ivory/60 leading-relaxed font-sans">
          All voluntary (Nafl) prayers are strictly prohibited during these 3 solar transitions:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
          <div className="p-2.5 rounded-xl bg-black/40 border border-rose-500/20 text-xs space-y-1">
            <span className="font-mono text-rose-300 font-semibold block text-[11px]">1. Sunrise (Tulu')</span>
            <span className="font-mono text-ivory/80 text-[11px] block">{status?.prohibited_windows.sunrise_prohibited}</span>
            <span className="text-[10px] text-ivory/40 block">From sunrise until sun rises 1 spear (~15m).</span>
          </div>

          <div className="p-2.5 rounded-xl bg-black/40 border border-rose-500/20 text-xs space-y-1">
            <span className="font-mono text-rose-300 font-semibold block text-[11px]">2. Zenith (Istiwa)</span>
            <span className="font-mono text-ivory/80 text-[11px] block">{status?.prohibited_windows.zenith_prohibited}</span>
            <span className="text-[10px] text-ivory/40 block">~10 min before transit until Zawal Dhuhr.</span>
          </div>

          <div className="p-2.5 rounded-xl bg-black/40 border border-rose-500/20 text-xs space-y-1">
            <span className="font-mono text-rose-300 font-semibold block text-[11px]">3. Sunset (Isfirar)</span>
            <span className="font-mono text-ivory/80 text-[11px] block">{status?.prohibited_windows.sunset_prohibited}</span>
            <span className="text-[10px] text-ivory/40 block">Yellowing of sun (~20m) until sunset.</span>
          </div>
        </div>
      </div>

      {/* Prayer Schedule Checklist */}
      <div className="space-y-3">
        <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-ivory/60 px-1">
          Daily Prayer Times & Checklist
        </h3>

        <div className="space-y-2">
          {scheduleList.map((p) => {
            const Icon = p.icon;
            const isDone = prayedPrayers[p.key] || false;
            const isCurrent = status?.current_prayer.toLowerCase().includes(p.key);

            return (
              <div
                key={p.key}
                onClick={() => !p.prohibited && togglePrayed(p.key)}
                className={`flex items-center justify-between p-3.5 rounded-2xl border transition-all ${
                  isCurrent
                    ? 'bg-emerald-500/10 border-emerald-500/30 shadow-[0_0_15px_rgba(52,211,153,0.1)]'
                    : p.prohibited
                    ? 'bg-rose-500/5 border-rose-500/20 opacity-70'
                    : isDone
                    ? 'bg-white/[0.02] border-white/5 opacity-60'
                    : 'bg-white/[0.04] border-white/10 hover:border-white/20'
                } ${p.prohibited ? 'cursor-default' : 'cursor-pointer'}`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isCurrent
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : p.prohibited
                        ? 'bg-rose-500/20 text-rose-300'
                        : 'bg-white/5 text-ivory/60'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-ivory flex items-center gap-2">
                      <span>{p.name}</span>
                      {isCurrent && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-400/20 text-emerald-300 uppercase">
                          Now
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-bold text-ivory/90 tracking-wide">
                    {p.time}
                  </span>
                  {!p.prohibited && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePrayed(p.key);
                      }}
                      className={`w-6 h-6 rounded-full border flex items-center justify-center transition-colors ${
                        isDone
                          ? 'bg-emerald-400 border-emerald-400 text-black'
                          : 'border-white/20 hover:border-emerald-400'
                      }`}
                    >
                      {isDone && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
