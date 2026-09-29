'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowLeft, Heart, RotateCcw, Check, Sparkles, Feather } from 'lucide-react';

interface AkhlaqTrait {
  id: string;
  name: string;
  description: string;
}

interface LapseEntry {
  id: number;
  created_at: string;
  category: string;
  trigger_context: string;
  repair_plan: string;
}

export default function MuhasabahPage() {
  const [traits, setTraits] = useState<AkhlaqTrait[]>([]);
  const [recentLapses, setRecentLapses] = useState<LapseEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'recovery' | 'akhlaq'>('recovery');

  // Form states for private recovery flow
  const [category, setCategory] = useState('distraction');
  const [triggerContext, setTriggerContext] = useState('');
  const [repairPlan, setRepairPlan] = useState('');
  const [notes, setNotes] = useState('');
  const [recoveryMessage, setRecoveryMessage] = useState<string | null>(null);

  // Form states for Akhlaq trait reflection
  const [selectedTrait, setSelectedTrait] = useState('anger_control');
  const [observedBehavior, setObservedBehavior] = useState('');
  const [akhlaqSuccess, setAkhlaqSuccess] = useState(false);

  const fetchMuhasabahData = async () => {
    try {
      const res = await fetch('/api/lifeos/muhasabah');
      if (res.ok) {
        const data = await res.json();
        setTraits(data.akhlaq_traits || []);
        setRecentLapses(data.recent?.lapses || []);
      }
    } catch (e) {
      // Offline fallback
      setTraits([
        { id: 'anger_control', name: 'Anger Control', description: 'Pausing before replying when agitated, changing posture.' },
        { id: 'guarding_speech', name: 'Guarding Speech', description: 'Refraining from backbiting, gossip, or idle argumentation.' },
        { id: 'patience', name: 'Patience (Sabr)', description: 'Remaining dignified through delays and hardships.' },
        { id: 'gratitude', name: 'Gratitude (Shukr)', description: 'Acknowledging blessings and thanking people openly.' }
      ]);
    }
  };

  useEffect(() => {
    fetchMuhasabahData();
  }, []);

  const handleRecordRecovery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!triggerContext || !repairPlan) return;

    try {
      const res = await fetch('/api/lifeos/muhasabah/lapse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category,
          trigger: triggerContext,
          repair: repairPlan,
          notes
        })
      });
      if (res.ok) {
        const data = await res.json();
        setRecoveryMessage(data.message || 'You slipped. Return now. Continue from here.');
        setTriggerContext('');
        setRepairPlan('');
        setNotes('');
        fetchMuhasabahData();
      }
    } catch (err) {
      setRecoveryMessage('You slipped. Return now. Continue from here.');
    }
  };

  const handleRecordAkhlaq = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!observedBehavior) return;

    try {
      await fetch('/api/lifeos/muhasabah/akhlaq', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trait_id: selectedTrait,
          behavior: observedBehavior
        })
      });
      setAkhlaqSuccess(true);
      setObservedBehavior('');
      setTimeout(() => setAkhlaqSuccess(false), 3000);
    } catch (err) {
      setAkhlaqSuccess(true);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-28 select-none bg-void text-ivory scrollbar-none">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <Link href="/lifeos" className="flex items-center gap-1.5 text-xs text-muted hover:text-ivory transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>LifeOS Home</span>
        </Link>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-500/20 font-mono">
          Private &bull; Zero Shame
        </span>
      </div>

      {/* Header Description */}
      <div>
        <h1 className="text-xl font-serif text-ivory">Muhasabah & Akhlaq</h1>
        <p className="text-xs text-muted mt-0.5">Mercy-oriented self-reflection and character cultivation.</p>
      </div>

      {/* Mode Subtabs */}
      <div className="flex bg-surface p-1 rounded-2xl border border-hairline/70 text-xs">
        <button
          onClick={() => setActiveTab('recovery')}
          className={`flex-1 py-1.5 rounded-xl font-medium transition-all ${
            activeTab === 'recovery' ? 'bg-deep text-ivory shadow-sm' : 'text-muted hover:text-ivory'
          }`}
        >
          Lapse Recovery Flow
        </button>
        <button
          onClick={() => setActiveTab('akhlaq')}
          className={`flex-1 py-1.5 rounded-xl font-medium transition-all ${
            activeTab === 'akhlaq' ? 'bg-deep text-ivory shadow-sm' : 'text-muted hover:text-ivory'
          }`}
        >
          Character Cultivation
        </button>
      </div>

      {activeTab === 'recovery' ? (
        <div className="space-y-4">
          {/* Mercy Principle Banner */}
          <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-950/30 to-surface border border-emerald-500/25">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
              <Heart className="w-4 h-4" />
              <span>Mercy-Oriented Design</span>
            </div>
            <p className="text-xs text-ivory/90 mt-1.5 leading-relaxed font-serif italic">
              &ldquo;Say, O My servants who have transgressed against themselves, do not despair of the mercy of Allah. Indeed, Allah forgives all sins.&rdquo; (39:53)
            </p>
            <p className="text-[11px] text-muted mt-1">
              Do not dwell in shame or broken streaks. Recognize, turn back, and initiate an upright deed immediately.
            </p>
          </div>

          {recoveryMessage && (
            <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-xs text-emerald-300 flex items-center justify-between">
              <span>{recoveryMessage}</span>
              <button onClick={() => setRecoveryMessage(null)} className="text-muted hover:text-ivory">&times;</button>
            </div>
          )}

          {/* Private Recovery Form */}
          <form onSubmit={handleRecordRecovery} className="p-4 rounded-2xl bg-surface border border-hairline/70 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">Record Recovery & Mitigation</h3>

            <div>
              <label className="text-[11px] text-muted block mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-deep border border-hairline/80 rounded-xl px-3 py-2 text-xs text-ivory outline-none focus:border-emerald-500"
              >
                <option value="distraction">Digital Distraction / Time Loss</option>
                <option value="speech">Speech / Anger / Harshness</option>
                <option value="prayer_delay">Delayed Salah / Sluggishness</option>
                <option value="desire">Private Desires / Temptation</option>
                <option value="other">Other Lapse</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] text-muted block mb-1">What was the trigger or environment?</label>
              <input
                type="text"
                value={triggerContext}
                onChange={(e) => setTriggerContext(e.target.value)}
                placeholder="e.g. Late night browsing in bed, feeling stressed"
                className="w-full bg-deep border border-hairline/80 rounded-xl px-3 py-2 text-xs text-ivory outline-none focus:border-emerald-500 placeholder-muted"
                required
              />
            </div>

            <div>
              <label className="text-[11px] text-muted block mb-1">Immediate Recovery & Replacement Action</label>
              <input
                type="text"
                value={repairPlan}
                onChange={(e) => setRepairPlan(e.target.value)}
                placeholder="e.g. Made wudu, prayed 2 rak'ahs, put phone in other room"
                className="w-full bg-deep border border-hairline/80 rounded-xl px-3 py-2 text-xs text-ivory outline-none focus:border-emerald-500 placeholder-muted"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 font-medium text-xs transition-all active:scale-[0.99]"
            >
              Seal Tawbah & Continue Forward
            </button>
          </form>

          {/* Recent Recoveries */}
          {recentLapses.length > 0 && (
            <div className="p-4 rounded-2xl bg-surface border border-hairline/60 space-y-2">
              <h3 className="text-xs font-semibold text-muted">Recent Recoveries</h3>
              <div className="space-y-2">
                {recentLapses.slice(0, 3).map((lapse) => (
                  <div key={lapse.id} className="p-2.5 rounded-xl bg-deep/80 border border-white/[0.03] text-xs">
                    <div className="flex items-center justify-between text-muted text-[10px]">
                      <span className="capitalize">{lapse.category}</span>
                      <span>Recovered</span>
                    </div>
                    <p className="text-ivory mt-1 font-medium">{lapse.repair_plan}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Akhlaq Cultivation Tab */
        <div className="space-y-4">
          <form onSubmit={handleRecordAkhlaq} className="p-4 rounded-2xl bg-surface border border-hairline/70 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">Daily Akhlaq Practice</h3>

            <div>
              <label className="text-[11px] text-muted block mb-1">Select Character Trait</label>
              <select
                value={selectedTrait}
                onChange={(e) => setSelectedTrait(e.target.value)}
                className="w-full bg-deep border border-hairline/80 rounded-xl px-3 py-2 text-xs text-ivory outline-none focus:border-emerald-500"
              >
                {traits.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[11px] text-muted block mb-1">What did you observe or practice today?</label>
              <textarea
                value={observedBehavior}
                onChange={(e) => setObservedBehavior(e.target.value)}
                rows={3}
                placeholder="e.g. When interrupted, I paused before responding instead of snapping."
                className="w-full bg-deep border border-hairline/80 rounded-xl px-3 py-2 text-xs text-ivory outline-none focus:border-emerald-500 placeholder-muted"
                required
              />
            </div>

            {akhlaqSuccess && (
              <p className="text-xs text-emerald-400">Reflection recorded peacefully.</p>
            )}

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-amber/20 hover:bg-amber/30 text-amber border border-amber/30 font-medium text-xs transition-all active:scale-[0.99]"
            >
              Record Akhlaq Reflection
            </button>
          </form>

          {/* Traits Directory */}
          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted px-1">Foundational Akhlaq Traits</h3>
            {traits.map(t => (
              <div key={t.id} className="p-3 rounded-xl bg-surface border border-hairline/60">
                <span className="text-xs font-semibold text-ivory">{t.name}</span>
                <p className="text-[11px] text-muted mt-0.5">{t.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
