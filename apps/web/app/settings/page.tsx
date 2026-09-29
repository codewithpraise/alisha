'use client';

import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Volume2,
  Bell,
  Cpu,
  RefreshCw,
  ShieldCheck,
  Zap,
  Sparkles,
  Info,
  Layers,
  Clock,
  Moon,
  Sun,
  BookOpen,
  Calendar,
  CheckCircle2,
  Check,
  Heart,
  Droplet,
  VolumeX,
  Vibrate
} from 'lucide-react';

interface NotificationPrefs {
  salah_alerts: boolean;
  salah_advance_mins: number;
  salah_adhan_sound: boolean;
  fajr_wake_up: boolean;
  tahajjud_reminder: boolean;
  tahajjud_mins_before_fajr: number;
  morning_athkar: boolean;
  morning_athkar_offset_mins: number;
  evening_athkar: boolean;
  evening_athkar_offset_mins: number;
  daily_ayah_hadith: boolean;
  daily_ayah_time: string;
  night_muhasabah: boolean;
  night_muhasabah_time: string;
  sunnah_fasting_reminders: boolean;
  friday_kahf_reminder: boolean;
  dhikr_nudges: boolean;
  hydration_breaks: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  sound_enabled: boolean;
  vibration_enabled: boolean;
  max_daily: number;
}

const DEFAULT_PREFS: NotificationPrefs = {
  salah_alerts: true,
  salah_advance_mins: 10,
  salah_adhan_sound: true,
  fajr_wake_up: true,
  tahajjud_reminder: true,
  tahajjud_mins_before_fajr: 45,
  morning_athkar: true,
  morning_athkar_offset_mins: 20,
  evening_athkar: true,
  evening_athkar_offset_mins: 30,
  daily_ayah_hadith: true,
  daily_ayah_time: '08:30',
  night_muhasabah: true,
  night_muhasabah_time: '21:45',
  sunnah_fasting_reminders: true,
  friday_kahf_reminder: true,
  dhikr_nudges: true,
  hydration_breaks: true,
  quiet_hours_enabled: true,
  quiet_hours_start: '23:15',
  quiet_hours_end: '04:30',
  sound_enabled: true,
  vibration_enabled: true,
  max_daily: 8
};

export default function SettingsPage() {
  const [proactiveFreq, setProactiveFreq] = useState('normal');
  const [voiceSpeed, setVoiceSpeed] = useState('1.0');
  const [ragDepth, setRagDepth] = useState('deep');
  const [showDevMode, setShowDevMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'notifications' | 'general'>('notifications');
  const [countryRegion, setCountryRegion] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('alisha_user_region') || 'UK';
    }
    return 'UK';
  });

  // Notification Preferences State
  const [prefs, setPrefs] = useState<NotificationPrefs>(DEFAULT_PREFS);
  const [todaySchedule, setTodaySchedule] = useState<any[]>([]);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load preferences from API
  useEffect(() => {
    const loadNotificationData = async () => {
      try {
        const res = await fetch('/api/lifeos/notifications');
        if (res.ok) {
          const data = await res.json();
          if (data.preferences) setPrefs(data.preferences);
          if (data.notifications) setTodaySchedule(data.notifications);
        }
      } catch (e) {
        console.error('Failed to load notification settings', e);
      } finally {
        setIsLoading(false);
      }
    };
    loadNotificationData();
  }, []);

  const updatePref = async (key: keyof NotificationPrefs, value: any) => {
    const updated = { ...prefs, [key]: value };
    setPrefs(updated);
    try {
      const res = await fetch('/api/lifeos/notifications/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated)
      });
      if (res.ok) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 2000);
        // Refresh today's scheduled alerts
        const notifRes = await fetch('/api/lifeos/notifications');
        if (notifRes.ok) {
          const notifData = await notifRes.json();
          if (notifData.notifications) setTodaySchedule(notifData.notifications);
        }
      }
    } catch (e) {
      console.error('Failed to save notification settings', e);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 lg:px-10 py-6 pb-28 flex flex-col gap-6 scrollbar-none text-ivory select-none max-w-4xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-amber uppercase font-semibold">
            SYSTEM & CADENCE PREFERENCES
          </span>
          <h1 className="font-serif text-2xl font-normal text-ivory">Preferences</h1>
        </div>
        <div className="flex items-center gap-2">
          {savedSuccess && (
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/30 px-2.5 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1 animate-in fade-in">
              <Check className="w-3 h-3" /> Saved
            </span>
          )}
          <div className="w-8 h-8 rounded-full bg-amber/15 flex items-center justify-center text-amber border border-amber/20">
            <Sliders className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 bg-white/[0.03] p-1 rounded-2xl border border-white/5">
        <button
          onClick={() => setActiveTab('notifications')}
          className={`flex-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
            activeTab === 'notifications'
              ? 'bg-amber text-black font-semibold shadow-sm'
              : 'text-ivory/50 hover:text-ivory'
          }`}
        >
          <Bell className="w-3.5 h-3.5" />
          <span>LifeOS Notifications</span>
        </button>

        <button
          onClick={() => setActiveTab('general')}
          className={`flex-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
            activeTab === 'general'
              ? 'bg-amber text-black font-semibold shadow-sm'
              : 'text-ivory/50 hover:text-ivory'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Voice & Persona</span>
        </button>
      </div>

      {/* ── NOTIFICATION CUSTOMIZATION CENTER ── */}
      {activeTab === 'notifications' && (
        <div className="space-y-4 animate-in fade-in duration-200">
          {/* Section 1: Salah & Tahajjud Timing Configuration */}
          <div className="bg-surface border border-hairline rounded-3xl overflow-hidden divide-y divide-white/[0.05] shadow-md">
            <div className="p-4 bg-white/[0.02]">
              <h3 className="text-xs font-mono font-semibold text-amber uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-amber" />
                <span>Salah & Night Worship Reminders</span>
              </h3>
            </div>

            {/* Salah Alerts Toggle */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Prayer Notifications</div>
                <div className="text-xs text-muted">Adhan & approaching expiration alerts</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.salah_alerts}
                onChange={(e) => updatePref('salah_alerts', e.target.checked)}
                className="w-5 h-5 accent-amber cursor-pointer"
              />
            </div>

            {/* Advance Prayer Offset */}
            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Advance Reminder Offset</div>
                <div className="text-xs text-muted">Notify {prefs.salah_advance_mins} mins before Adhan</div>
              </div>
              <select
                value={prefs.salah_advance_mins}
                onChange={(e) => updatePref('salah_advance_mins', parseInt(e.target.value))}
                className="bg-[#181916] text-ivory border border-hairline rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer focus:border-amber/50"
              >
                <option value={0}>At Exact Adhan</option>
                <option value={5}>5 mins before</option>
                <option value={10}>10 mins before (Recommended)</option>
                <option value={15}>15 mins before</option>
                <option value={20}>20 mins before</option>
              </select>
            </div>

            {/* Tahajjud Reminder */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Tahajjud Night Alert</div>
                <div className="text-xs text-muted">Pre-Fajr call during the last third of the night</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.tahajjud_reminder}
                onChange={(e) => updatePref('tahajjud_reminder', e.target.checked)}
                className="w-5 h-5 accent-amber cursor-pointer"
              />
            </div>

            {/* Tahajjud Minutes Before Fajr */}
            {prefs.tahajjud_reminder && (
              <div className="p-4 flex justify-between items-center gap-4 bg-black/20">
                <div>
                  <div className="text-sm font-medium text-ivory">Tahajjud Window</div>
                  <div className="text-xs text-muted">{prefs.tahajjud_mins_before_fajr} minutes before Fajr Adhan</div>
                </div>
                <select
                  value={prefs.tahajjud_mins_before_fajr}
                  onChange={(e) => updatePref('tahajjud_mins_before_fajr', parseInt(e.target.value))}
                  className="bg-[#181916] text-ivory border border-hairline rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer focus:border-amber/50"
                >
                  <option value={30}>30 mins before Fajr</option>
                  <option value={45}>45 mins before Fajr</option>
                  <option value={60}>1 hour before Fajr</option>
                </select>
              </div>
            )}
          </div>

          {/* Section 2: Daily Ayah, Hadith & Athkar */}
          <div className="bg-surface border border-hairline rounded-3xl overflow-hidden divide-y divide-white/[0.05] shadow-md">
            <div className="p-4 bg-white/[0.02]">
              <h3 className="text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
                <span>Qur'an, Hadith & Daily Athkar</span>
              </h3>
            </div>

            {/* Daily Ayah & Hadith */}
            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Daily Ayah & Hadith Reflection</div>
                <div className="text-xs text-muted">Daily morning insight with classical Hanafi commentary</div>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="time"
                  value={prefs.daily_ayah_time}
                  onChange={(e) => updatePref('daily_ayah_time', e.target.value)}
                  className="bg-[#181916] text-ivory border border-hairline rounded-xl px-2 py-1 text-xs outline-none cursor-pointer focus:border-amber/50"
                />
                <input
                  type="checkbox"
                  checked={prefs.daily_ayah_hadith}
                  onChange={(e) => updatePref('daily_ayah_hadith', e.target.checked)}
                  className="w-5 h-5 accent-emerald-400 cursor-pointer"
                />
              </div>
            </div>

            {/* Morning Athkar */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Morning Athkar (Protection)</div>
                <div className="text-xs text-muted">20 minutes after Sunrise</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.morning_athkar}
                onChange={(e) => updatePref('morning_athkar', e.target.checked)}
                className="w-5 h-5 accent-emerald-400 cursor-pointer"
              />
            </div>

            {/* Evening Athkar */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Evening Athkar</div>
                <div className="text-xs text-muted">30 minutes after Asr prayer</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.evening_athkar}
                onChange={(e) => updatePref('evening_athkar', e.target.checked)}
                className="w-5 h-5 accent-emerald-400 cursor-pointer"
              />
            </div>

            {/* Friday Kahf */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Friday Surah Al-Kahf Alert</div>
                <div className="text-xs text-muted">Jumu'ah morning reminder to recite Surah 18</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.friday_kahf_reminder}
                onChange={(e) => updatePref('friday_kahf_reminder', e.target.checked)}
                className="w-5 h-5 accent-emerald-400 cursor-pointer"
              />
            </div>

            {/* Sunnah Fasting */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Sunnah Fasting Nudges (Mon/Thu)</div>
                <div className="text-xs text-muted">Suhoor reminders on Sunday and Wednesday evenings</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.sunnah_fasting_reminders}
                onChange={(e) => updatePref('sunnah_fasting_reminders', e.target.checked)}
                className="w-5 h-5 accent-emerald-400 cursor-pointer"
              />
            </div>
          </div>

          {/* Section 3: Mindfulness, Muhasabah & Quiet Hours */}
          <div className="bg-surface border border-hairline rounded-3xl overflow-hidden divide-y divide-white/[0.05] shadow-md">
            <div className="p-4 bg-white/[0.02]">
              <h3 className="text-xs font-mono font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                <Moon className="w-3.5 h-3.5 text-purple-400" />
                <span>Muhasabah & Respectful Quiet Hours</span>
              </h3>
            </div>

            {/* Night Muhasabah */}
            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Night Muhasabah Check-in</div>
                <div className="text-xs text-muted">Review today's intentions, slips & growth</div>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="time"
                  value={prefs.night_muhasabah_time}
                  onChange={(e) => updatePref('night_muhasabah_time', e.target.value)}
                  className="bg-[#181916] text-ivory border border-hairline rounded-xl px-2 py-1 text-xs outline-none cursor-pointer focus:border-amber/50"
                />
                <input
                  type="checkbox"
                  checked={prefs.night_muhasabah}
                  onChange={(e) => updatePref('night_muhasabah', e.target.checked)}
                  className="w-5 h-5 accent-purple-400 cursor-pointer"
                />
              </div>
            </div>

            {/* Quiet Hours Window */}
            <div className="p-4 space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-sm font-medium text-ivory">Quiet Hours (Do Not Disturb)</div>
                  <div className="text-xs text-muted">Mutes all low/medium alerts (Fajr/Tahajjud bypass)</div>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.quiet_hours_enabled}
                  onChange={(e) => updatePref('quiet_hours_enabled', e.target.checked)}
                  className="w-5 h-5 accent-purple-400 cursor-pointer"
                />
              </div>

              {prefs.quiet_hours_enabled && (
                <div className="flex items-center justify-between gap-3 p-3 bg-black/30 rounded-2xl border border-white/5 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-muted">From:</span>
                    <input
                      type="time"
                      value={prefs.quiet_hours_start}
                      onChange={(e) => updatePref('quiet_hours_start', e.target.value)}
                      className="bg-[#181916] text-ivory border border-hairline rounded-xl px-2 py-1 outline-none"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted">To:</span>
                    <input
                      type="time"
                      value={prefs.quiet_hours_end}
                      onChange={(e) => updatePref('quiet_hours_end', e.target.value)}
                      className="bg-[#181916] text-ivory border border-hairline rounded-xl px-2 py-1 outline-none"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Sound & Vibration */}
            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Audio Chimes & Tones</div>
                <div className="text-xs text-muted">Play gentle acoustic bell on active alerts</div>
              </div>
              <input
                type="checkbox"
                checked={prefs.sound_enabled}
                onChange={(e) => updatePref('sound_enabled', e.target.checked)}
                className="w-5 h-5 accent-amber cursor-pointer"
              />
            </div>
          </div>

          {/* Section 4: Today's Live Scheduled Notification Timeline */}
          <div className="bg-surface border border-white/10 rounded-3xl p-5 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-semibold text-ivory/80 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-amber" />
                <span>Today's Choreographed Alerts ({todaySchedule.length})</span>
              </h3>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded-full border border-emerald-500/30">
                Live Dynamic Feed
              </span>
            </div>

            <div className="space-y-2">
              {todaySchedule.map((n, idx) => (
                <div key={n.id || idx} className="flex items-center justify-between p-3 rounded-2xl bg-black/30 border border-white/5 text-xs">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-amber font-semibold text-[11px] bg-amber/10 px-2 py-0.5 rounded-lg border border-amber/20">
                      {n.scheduled_time}
                    </span>
                    <div>
                      <div className="font-medium text-ivory/90">{n.title}</div>
                      <div className="text-[11px] text-muted line-clamp-1">{n.body}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-ivory/40 uppercase bg-white/5 px-2 py-0.5 rounded-md">
                    {n.category}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── GENERAL VOICE & PERSONA PREFERENCES ── */}
      {activeTab === 'general' && (
        <div className="space-y-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-hairline rounded-3xl overflow-hidden divide-y divide-white/[0.05] shadow-md">
            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Country & Region Time</div>
                <div className="text-xs text-muted">Manages local clocks, prayer times & timestamps</div>
              </div>
              <select
                value={countryRegion}
                onChange={(e) => {
                  const val = e.target.value;
                  setCountryRegion(val);
                  if (typeof window !== 'undefined') {
                    localStorage.setItem('alisha_user_region', val);
                    window.dispatchEvent(new Event('alisha_region_change'));
                  }
                }}
                className="bg-[#181916] text-ivory border border-hairline rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer focus:border-amber/50"
              >
                <option value="UK">🇬🇧 United Kingdom (London - GMT/BST)</option>
                <option value="PK">🇵🇰 Pakistan (Islamabad / Karachi - PKT)</option>
                <option value="US_EAST">🇺🇸 United States (New York - Eastern)</option>
                <option value="US_WEST">🇺🇸 United States (Los Angeles - Pacific)</option>
                <option value="CA">🇨🇦 Canada (Toronto - Eastern)</option>
                <option value="MU">🇲🇺 Mauritius (Port Louis - MUT)</option>
                <option value="AE">🇦🇪 United Arab Emirates (Dubai - GST)</option>
                <option value="SA">🇸🇦 Saudi Arabia (Makkah / Riyadh - AST)</option>
                <option value="EU">🇩🇪 Europe (Berlin / Paris - CET)</option>
                <option value="IN">🇮🇳 India (New Delhi / Mumbai - IST)</option>
                <option value="MY">🇲🇾 Malaysia (Kuala Lumpur - MYT)</option>
                <option value="AU">🇦🇺 Australia (Sydney - AEST)</option>
              </select>
            </div>

            <div className="p-4 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-ivory">Proactive Cadence</div>
                <div className="text-xs text-muted">Frequency Alisha texts you first</div>
              </div>
              <select
                value={proactiveFreq}
                onChange={(e) => setProactiveFreq(e.target.value)}
                className="bg-[#181916] text-ivory border border-hairline rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer focus:border-amber/50"
              >
                <option value="normal">Natural Cadence (2-3/day)</option>
                <option value="frequent">Active (4-6/day)</option>
                <option value="quiet">Quiet (Prompt Only)</option>
              </select>
            </div>

            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Voice Speed</div>
                <div className="text-xs text-muted">Speaking tempo ({voiceSpeed}x)</div>
              </div>
              <input
                type="range"
                min="0.85"
                max="1.25"
                step="0.05"
                value={voiceSpeed}
                onChange={(e) => setVoiceSpeed(e.target.value)}
                className="accent-amber cursor-pointer w-28"
              />
            </div>

            <div className="p-4 flex justify-between items-center gap-4">
              <div>
                <div className="text-sm font-medium text-ivory">Context Retrieval Engine</div>
                <div className="text-xs text-muted">Memory search accuracy</div>
              </div>
              <select
                value={ragDepth}
                onChange={(e) => setRagDepth(e.target.value)}
                className="bg-[#181916] text-ivory border border-hairline rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer focus:border-amber/50"
              >
                <option value="deep">Temporal Hybrid Graph (Optimal)</option>
                <option value="fast">Direct FTS5 BM25</option>
                <option value="vault">Verified Vault Only</option>
              </select>
            </div>
          </div>

          <div className="bg-surface border border-hairline rounded-3xl overflow-hidden divide-y divide-white/[0.05] shadow-md">
            <div
              onClick={() => {
                if (confirm('Reset active session chat history?')) {
                  localStorage.removeItem('alisha_persisted_chat_history_v2');
                  alert('Active conversation turns reset.');
                }
              }}
              className="p-4 flex justify-between items-center cursor-pointer hover:bg-white/[0.03] transition-colors"
            >
              <div>
                <div className="text-sm font-medium text-rose-400">Reset Active Session</div>
                <div className="text-xs text-muted">Clears temporary context buffer without deleting memories</div>
              </div>
              <RefreshCw className="w-4 h-4 text-rose-400" />
            </div>
          </div>

          <div className="text-center pt-1">
            <button
              onClick={() => setShowDevMode(!showDevMode)}
              className="text-xs text-muted hover:text-amber transition-colors cursor-pointer font-mono"
            >
              {showDevMode ? '▲ Hide Diagnostics' : '▼ View Diagnostics & Telemetry'}
            </button>
          </div>

          {showDevMode && (
            <div className="bg-surface border border-amber/30 rounded-3xl p-4 animate-in fade-in duration-200 shadow-lg space-y-2.5">
              <div className="flex items-center justify-between">
                <h4 className="text-amber font-semibold text-xs font-mono uppercase tracking-wider flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber" />
                  Runtime Telemetry
                </h4>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded-full border border-emerald-500/30">
                  Optimal
                </span>
              </div>

              <div className="font-mono text-[11px] bg-[#121310] p-3 rounded-2xl text-ivory/80 space-y-1.5 border border-white/[0.04]">
                <div className="flex justify-between">
                  <span className="text-muted">Inference Model:</span>
                  <span className="text-amber">Groq Qwen 27B / Temporal RAG</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Voice Architecture:</span>
                  <span className="text-ivory">ExecuTorch INT8 (16 Codebooks)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Speech Corpus:</span>
                  <span className="text-ivory">87 Instagram WAV Notes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Avg TTFT:</span>
                  <span className="text-emerald-400">~339ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Fact Ledger:</span>
                  <span className="text-ivory">120 Verified Items</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
