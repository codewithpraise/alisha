'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Sparkles,
  TrendingUp,
  Award,
  Download,
  Flame,
  Clock,
  Zap,
  BookOpen,
  Filter,
  BarChart3,
  Heart,
  Shield,
  Layers,
  Compass,
  Activity,
  Check,
  ChevronRight,
} from 'lucide-react';

interface HistorySummary {
  salah_adherence_pct: number;
  total_salah_completed: number;
  salah_streak_days: number;
  total_dhikr_count: number;
  dhikr_streak_days: number;
  tasks_completed_count: number;
  focus_minutes_total: number;
  signal_high_score: number;
  signal_avg_accuracy: number;
}

const DEFAULT_SUMMARY: HistorySummary = {
  salah_adherence_pct: 94.8,
  total_salah_completed: 142,
  salah_streak_days: 18,
  total_dhikr_count: 52400,
  dhikr_streak_days: 24,
  tasks_completed_count: 38,
  focus_minutes_total: 760,
  signal_high_score: 5420,
  signal_avg_accuracy: 98.4,
};

const WEEKLY_FOCUS = [
  { day: 'Mon', hours: 3.5, label: 'Biochem & Lab' },
  { day: 'Tue', hours: 4.2, label: 'Organic Mech' },
  { day: 'Wed', hours: 2.8, label: 'Calculus Rev' },
  { day: 'Thu', hours: 4.8, label: 'Quran & Tafsir' },
  { day: 'Fri', hours: 5.2, label: 'Jummah & Study' },
  { day: 'Sat', hours: 3.9, label: 'Signal Training' },
  { day: 'Sun', hours: 4.4, label: 'Weekly Review' },
];

const AKHLAQ_METRICS = [
  { trait: 'Sabr (Patience & Restraint)', score: 92, status: 'Consistent', color: 'bg-emerald-400' },
  { trait: 'Hilm (Gentleness & Forbearance)', score: 88, status: 'High', color: 'bg-amber' },
  { trait: 'Sidq (Absolute Truthfulness)', score: 96, status: 'Exemplary', color: 'bg-blue-400' },
  { trait: 'Ihsan (Excellence in Action)', score: 90, status: 'Strong', color: 'bg-purple-400' },
  { trait: 'Shukr (Continual Gratitude)', score: 94, status: 'High', color: 'bg-teal-400' },
];

const PRAYER_BREAKDOWN = [
  { name: 'Fajr', completed: 27, total: 28, pct: 96.4, color: 'text-amber' },
  { name: 'Dhuhr', completed: 28, total: 28, pct: 100.0, color: 'text-emerald-400' },
  { name: 'Asr', completed: 26, total: 28, pct: 92.8, color: 'text-blue-400' },
  { name: 'Maghrib', completed: 28, total: 28, pct: 100.0, color: 'text-indigo-400' },
  { name: 'Isha', completed: 27, total: 28, pct: 96.4, color: 'text-purple-400' },
];

const HEATMAP_DAYS = Array.from({ length: 28 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (27 - i));
  const score = i === 27 ? 4 : (i % 7 === 0 ? 4 : (i % 5 === 0 ? 3 : 5));
  return {
    date: d.toISOString().split('T')[0],
    dayNumber: d.getDate(),
    prayersCompleted: score,
    totalPrayers: 5,
  };
});

const DHIKR_BREAKDOWN = [
  { name: 'Astaghfirullah (Forgiveness & Relief)', count: 24500, target: 50000, color: 'from-amber-400 to-amber-600' },
  { name: 'SubhanAllah (Glory & Awe)', count: 11200, target: 20000, color: 'from-emerald-400 to-emerald-600' },
  { name: 'Alhamdulillah (Gratitude & Abundance)', count: 8600, target: 15000, color: 'from-blue-400 to-indigo-600' },
  { name: 'Salawat on Prophet ﷺ (Durood)', count: 5400, target: 10000, color: 'from-purple-400 to-pink-600' },
  { name: 'Ya Hayyu Ya Qayyum', count: 2700, target: 5000, color: 'from-teal-400 to-cyan-600' },
];

const RECENT_FOCUS_LOGS = [
  { id: '1', title: 'Daily Quran & Tafsir Study', one_liner: 'Read Surah Al-Mulk 30 verses with Hanafi commentary', mins: 15, date: 'Today, 07:15 AM' },
  { id: '2', title: 'Review Organic Chemistry Mechanisms', one_liner: 'Draw 4 nucleophilic substitution mechanisms without tab switching', mins: 25, date: 'Today, 08:30 AM' },
  { id: '3', title: 'Physical Exercise & Mobility', one_liner: '30 pushups, 40 squats, 5m stretches before Maghrib', mins: 20, date: 'Yesterday, 05:40 PM' },
  { id: '4', title: 'Morning Dhikr & Astaghfirullah', one_liner: 'Complete 1,000 counts with root contemplation in quiet room', mins: 20, date: 'Yesterday, 06:45 AM' },
];

export default function HistoryReportsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | 'all'>('30d');
  const [summary, setSummary] = useState<HistorySummary>(DEFAULT_SUMMARY);
  const [heatmapDays, setHeatmapDays] = useState(HEATMAP_DAYS);
  const [dhikrBreakdown, setDhikrBreakdown] = useState(DHIKR_BREAKDOWN);
  const [recentFocusLogs, setRecentFocusLogs] = useState(RECENT_FOCUS_LOGS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const res = await fetch(`/api/lifeos/history?range=${timeRange}`);
        if (res.ok) {
          const data = await res.json();
          if (data.summary) setSummary(data.summary);
          if (data.salah_heatmap_28d) setHeatmapDays(data.salah_heatmap_28d);
          if (data.dhikr_volume) setDhikrBreakdown(data.dhikr_volume);
          if (data.recent_focus_tasks) setRecentFocusLogs(data.recent_focus_tasks);
        }
      } catch (err) {
        console.error('History load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [timeRange]);

  const handleExportJSON = () => {
    const reportData = {
      generated_at: new Date().toISOString(),
      time_range: timeRange,
      summary: summary,
      dhikr_volume: dhikrBreakdown,
      recent_focus_tasks: recentFocusLogs,
      salah_heatmap_28d: heatmapDays,
      weekly_focus: WEEKLY_FOCUS,
      akhlaq_metrics: AKHLAQ_METRICS,
    };
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lifeos-analytics-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    let csv = 'Type,Name,Metric,Date\n';
    DHIKR_BREAKDOWN.forEach((d) => {
      csv += `Dhikr,"${d.name}",${d.count},Current\n`;
    });
    RECENT_FOCUS_LOGS.forEach((t) => {
      csv += `Task,"${t.title} - ${t.one_liner}",${t.mins} mins,"${t.date}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lifeos-history-summary-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const maxHours = Math.max(...WEEKLY_FOCUS.map((w) => w.hours));

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6 text-ivory select-none pb-28 scrollbar-none max-w-xl mx-auto w-full">
      {/* ── TOP HEADER ── */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>

        <div className="text-center">
          <span className="text-[10px] font-mono tracking-widest text-amber uppercase flex items-center justify-center gap-1">
            <Activity className="w-3 h-3 text-amber" />
            LIFEOS ADVANCED ANALYTICS
          </span>
          <h1 className="text-base font-semibold text-ivory">Spiritual & Cognitive Dashboard</h1>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleExportJSON}
            title="Export JSON Report"
            className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-amber/20 hover:text-amber transition-colors"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── REPORT WINDOW SELECTOR ── */}
      <div className="flex items-center justify-between bg-surface/60 p-1.5 rounded-2xl border border-hairline backdrop-blur-md">
        <span className="text-xs text-muted font-medium px-2 flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-amber" />
          <span>Window:</span>
        </span>
        <div className="flex items-center gap-1">
          {(['7d', '30d', 'all'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className={`px-3 py-1 rounded-xl text-xs font-medium transition-all ${
                timeRange === r
                  ? 'bg-amber text-black font-semibold shadow-sm'
                  : 'text-muted hover:text-ivory hover:bg-white/[0.05]'
              }`}
            >
              {r === '7d' ? 'Last 7 Days' : r === '30d' ? 'Last 30 Days' : 'All Time'}
            </button>
          ))}
        </div>
      </div>

      {/* ── HIGH-IMPACT METRIC CARDS ── */}
      <div className="grid grid-cols-2 gap-3">
        {/* Salah Adherence Card with Circular Ring Visual */}
        <div className="glass-card rounded-3xl p-4 space-y-2 border-emerald-500/20 bg-emerald-950/10 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-emerald-300">Salah Adherence</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold font-mono text-emerald-100">{summary.salah_adherence_pct}%</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-200/70 font-mono">
            <Flame className="w-3.5 h-3.5 text-amber fill-amber" />
            <span>{summary.salah_streak_days} Day Streak</span>
          </div>
        </div>

        {/* Total Adhkar Count */}
        <div className="glass-card rounded-3xl p-4 space-y-2 border-amber/20 bg-amber-950/10 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-amber-300">Total Adhkar</span>
            <Sparkles className="w-4 h-4 text-amber" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold font-mono text-amber-100">{summary.total_dhikr_count.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-amber-200/70 font-mono">
            <Award className="w-3.5 h-3.5 text-amber" />
            <span>50k+ Goal Reached</span>
          </div>
        </div>

        {/* Focus Task Hours */}
        <div className="glass-card rounded-3xl p-4 space-y-2 border-blue-500/20 bg-blue-950/10">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-blue-300">Focus Hours</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold font-mono text-blue-100">{(summary.focus_minutes_total / 60).toFixed(1)}h</span>
          </div>
          <div className="text-[11px] text-blue-200/70 font-mono">
            <span>{summary.tasks_completed_count} One-Liners Completed</span>
          </div>
        </div>

        {/* SIGNAL Cognitive Agility */}
        <div className="glass-card rounded-3xl p-4 space-y-2 border-purple-500/20 bg-purple-950/10">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-purple-300">SIGNAL Score</span>
            <Zap className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold font-mono text-purple-100">{summary.signal_high_score.toLocaleString()}</span>
          </div>
          <div className="text-[11px] text-purple-200/70 font-mono">
            <span>{summary.signal_avg_accuracy}% Accuracy Rating</span>
          </div>
        </div>
      </div>

      {/* ── 28-DAY SALAH CONSISTENCY HEATMAP GRAPH ── */}
      <div className="glass-card rounded-3xl p-4 space-y-3.5 border-hairline shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-ivory">28-Day Salah Consistency Heatmap</h3>
          </div>
          <span className="text-[11px] font-mono text-amber">Islamabad (Hanafi)</span>
        </div>

        {/* Heatmap Grid */}
        <div className="grid grid-cols-7 gap-2 pt-1">
          {heatmapDays.map((day, idx) => {
            const intensity =
              day.prayersCompleted === 5
                ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.35)]'
                : day.prayersCompleted === 4
                ? 'bg-emerald-600/70'
                : day.prayersCompleted === 3
                ? 'bg-amber/60'
                : 'bg-white/10';
            return (
              <div
                key={idx}
                className="flex flex-col items-center gap-1 group relative cursor-pointer"
              >
                <div
                  className={`w-full aspect-square rounded-xl ${intensity} transition-transform group-hover:scale-110`}
                />
                <span className="text-[9px] font-mono text-muted/70">{day.dayNumber}</span>

                {/* Tooltip */}
                <div className="absolute -top-8 bg-[#141512] border border-hairline px-2 py-0.5 rounded-lg text-[9px] font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-10 shadow-lg pointer-events-none text-ivory">
                  {day.date}: {day.prayersCompleted}/5 Prayers
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between text-[10px] text-muted pt-2 border-t border-hairline/60">
          <span>Less Consistent</span>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded bg-white/10" />
            <div className="w-2.5 h-2.5 rounded bg-amber/60" />
            <div className="w-2.5 h-2.5 rounded bg-emerald-600/70" />
            <div className="w-2.5 h-2.5 rounded bg-emerald-500" />
          </div>
          <span>5/5 Prayers Done</span>
        </div>
      </div>

      {/* ── PRAYER-BY-PRAYER ADHERENCE BREAKDOWN ── */}
      <div className="glass-card rounded-3xl p-4 space-y-3 border-hairline shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-ivory">Individual Prayer Adherence</h3>
          </div>
          <span className="text-[11px] font-mono text-muted">28-Day Window</span>
        </div>

        <div className="grid grid-cols-5 gap-2 pt-1 text-center">
          {PRAYER_BREAKDOWN.map((p, idx) => (
            <div key={idx} className="bg-white/[0.02] border border-white/[0.05] rounded-2xl p-2.5 flex flex-col items-center">
              <span className="text-xs font-semibold text-ivory">{p.name}</span>
              <span className={`text-sm font-bold font-mono mt-1 ${p.color}`}>{p.pct}%</span>
              <span className="text-[9px] font-mono text-muted mt-0.5">{p.completed}/{p.total}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── WEEKLY FOCUS HOURS VISUAL BAR GRAPH ── */}
      <div className="glass-card rounded-3xl p-4 space-y-3.5 border-hairline shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-ivory">Weekly Focus Volume Graph</h3>
          </div>
          <span className="text-[11px] font-mono text-blue-300">28.5 hrs Total</span>
        </div>

        {/* Visual Bar Graph */}
        <div className="flex items-end justify-between gap-2 pt-4 pb-1 h-36 px-2">
          {WEEKLY_FOCUS.map((w, i) => {
            const heightPct = Math.round((w.hours / maxHours) * 100);
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group relative">
                <div className="absolute -top-7 bg-surface border border-hairline px-2 py-0.5 rounded-lg text-[9px] font-mono text-ivory opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-md pointer-events-none">
                  {w.hours}h &bull; {w.label}
                </div>
                <div
                  style={{ height: `${heightPct}%` }}
                  className="w-full rounded-xl bg-gradient-to-t from-blue-600/50 to-blue-400 group-hover:to-amber transition-all shadow-[0_0_8px_rgba(59,130,246,0.3)]"
                />
                <span className="text-[10px] font-mono text-muted font-medium">{w.day}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── DHIKR VOLUME PROGRESS BARS ── */}
      <div className="glass-card rounded-3xl p-4 space-y-3.5 border-hairline shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber" />
            <h3 className="text-sm font-semibold text-ivory">Dhikr Volume Breakdown</h3>
          </div>
          <Link
            href="/lifeos/dhikr"
            className="text-[11px] font-semibold text-amber hover:underline flex items-center gap-0.5"
          >
            <span>Open Counter</span>
            <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="space-y-3">
          {dhikrBreakdown.map((d, i) => {
            const pct = Math.min(100, Math.round((d.count / d.target) * 100));
            return (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-ivory/90 font-medium truncate max-w-[220px]">{d.name}</span>
                  <span className="font-mono text-muted text-[11px]">
                    {d.count.toLocaleString()} / {d.target.toLocaleString()}
                  </span>
                </div>
                <div className="h-2 w-full bg-white/[0.05] rounded-full overflow-hidden">
                  <div
                    style={{ width: `${pct}%` }}
                    className={`h-full bg-gradient-to-r ${d.color} rounded-full transition-all duration-500`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── AKHLAQ & CHARACTER GROWTH RADAR ── */}
      <div className="glass-card rounded-3xl p-4 space-y-3.5 border-hairline shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Heart className="w-4 h-4 text-rose-400" />
            <h3 className="text-sm font-semibold text-ivory">Akhlaq & Character Growth Index</h3>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded-full border border-emerald-500/30">
            92% Composite
          </span>
        </div>

        <div className="space-y-2.5">
          {AKHLAQ_METRICS.map((a, i) => (
            <div key={i} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-ivory/90">{a.trait}</span>
                <span className="font-mono text-xs font-bold text-amber">{a.score}%</span>
              </div>
              <div className="h-1.5 w-full bg-white/[0.05] rounded-full overflow-hidden">
                <div
                  style={{ width: `${a.score}%` }}
                  className={`h-full ${a.color} rounded-full transition-all duration-500`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── EXPORT CSV & JSON BUTTONS ── */}
      <div className="flex items-center gap-2 pt-2">
        <button
          onClick={handleExportCSV}
          className="flex-1 py-3 rounded-2xl bg-white/[0.05] hover:bg-white/10 border border-white/10 text-xs font-semibold text-ivory flex items-center justify-center gap-2 transition-all active:scale-95 cursor-pointer"
        >
          <Download className="w-3.5 h-3.5 text-muted" />
          <span>Export CSV Summary</span>
        </button>
        <button
          onClick={handleExportJSON}
          className="flex-1 py-3 rounded-2xl bg-gradient-to-r from-amber/25 to-amber/15 hover:from-amber/35 hover:to-amber/25 border border-amber/35 text-xs font-semibold text-amber flex items-center justify-center gap-2 transition-all active:scale-95 cursor-pointer shadow-md"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Full JSON</span>
        </button>
      </div>
    </div>
  );
}
