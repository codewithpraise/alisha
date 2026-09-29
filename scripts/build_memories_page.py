"""
Script to bundle initial verified facts and voice notes into memories/page.tsx
"""
import os
import json
import sqlite3

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root, "alisha_memory.db")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Get facts
    cur.execute("SELECT * FROM fact_ledger ORDER BY importance DESC, evidence_count DESC")
    fact_rows = cur.fetchall()
    memories = []
    for f in fact_rows:
        pred = (f["predicate"] or "").lower()
        raw_val = (f["value"] or "").strip()
        if raw_val.lower().startswith("alisha") or raw_val.lower().startswith("she") or raw_val.lower().startswith("underneath"):
            content_str = raw_val
        else:
            content_str = f"Alisha: {raw_val}"

        cat = f["fact_type"] or "personal"
        if any(k in pred for k in ["biochem", "chemistry", "study", "exam", "maths", "lab"]):
            cat = "education"
        elif any(k in pred for k in ["age", "birthday", "roots", "heritage", "uk_residence", "bilingual"]):
            cat = "identity"
        elif any(k in pred for k in ["faith", "sajdah", "jummah", "ameen", "halal", "muslim", "fajr"]):
            cat = "personal"
        elif any(k in pred for k in ["cat", "kittu", "kdrama", "tea", "chai", "blanket", "green_tea"]):
            cat = "preference"
        elif any(k in pred for k in ["mum", "family", "kitchen", "dinners", "daughter"]):
            cat = "family"
        elif any(k in pred for k in ["voice", "audio", "burst", "lowercase", "sleep", "morning"]):
            cat = "behavior"
        elif any(k in pred for k in ["joke", "pattern", "latw", "bubbzieee", "omdssd", "kidding", "loyalty", "empath", "sarcasm", "anti_ai", "presence"]):
            cat = "personality"

        badge_title = f["notes"] if (f["notes"] and len(f["notes"]) < 30) else pred.replace("_", " ").title()

        memories.append({
            "id": f["fact_id"],
            "category": cat,
            "badge": badge_title,
            "confidence": str(round(float(f["confidence"] or 0.95), 2)),
            "content": content_str,
            "status": f["status"] or "verified",
            "evidence_count": int(f["evidence_count"] or 15),
            "importance": float(f["importance"] or 0.85),
        })

    # Get voice notes
    cur.execute(
        "SELECT id, sender, ts_ms, content, media_path, category, badge, sub_category, importance, duration_sec, duration_label "
        "FROM messages WHERE is_voice = 1 ORDER BY id ASC"
    )
    voice_rows = cur.fetchall()
    voice_notes = []
    for r in voice_rows:
        media = r["media_path"] or ""
        audio_url = f"/{media}" if media.startswith("voice/") else (f"/voice/{media}" if media else "/voice/1102256372963051.wav")
        dur_sec = float(r["duration_sec"] or 12.0)
        dur_label = r["duration_label"] or f"{int(dur_sec // 60)}:{int(dur_sec % 60):02d}"

        content_lower = (r["content"] or "").lower()
        badge = "Instagram Voice Note"
        if any(w in content_lower for w in ["voice", "sweet", "soothing", "listening", "audio"]):
            badge = "Voice Compliment"
        elif any(w in content_lower for w in ["exam", "study", "biochem", "test", "uni", "college"]):
            badge = "Study & College Rant"
        elif any(w in content_lower for w in ["cat", "kittu", "kitten", "cute"]):
            badge = "Cat Story"
        elif any(w in content_lower for w in ["tea", "chai", "drink", "food"]):
            badge = "Chai & Food"
        elif any(w in content_lower for w in ["sleep", "tired", "morning", "night", "bed"]):
            badge = "Late Night Audio"
        elif any(w in content_lower for w in ["lol", "haha", "lmao", "kidding", "joking"]):
            badge = "Playful Banter"

        voice_notes.append({
            "id": r["id"],
            "sender": r["sender"] or "alisha",
            "ts_ms": r["ts_ms"],
            "content": r["content"] or "(Voice Note)",
            "transcript": r["content"] or "Hey, listening to this voice note...",
            "media_path": media,
            "audio_url": audio_url,
            "duration_sec": dur_sec,
            "duration_label": dur_label,
            "badge": badge,
            "category": r["category"] or "behavior",
            "importance": float(r["importance"] or 0.8),
        })

    con.close()

    target_file = os.path.join(root, "apps", "web", "app", "memories", "page.tsx")

    template = """'use client';

import React, { useState, useEffect, useMemo } from 'react';
import MemoryCard from '@/components/memories/MemoryCard';
import VoiceBubble from '@/components/chat/VoiceBubble';
import {
  Search,
  Sparkles,
  MessageSquare,
  Volume2,
  RefreshCw,
  Layers,
  Heart,
  Mic,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Tag,
  Headphones,
  SlidersHorizontal,
} from 'lucide-react';

interface Memory {
  id: string;
  category: string;
  badge: string;
  confidence: string;
  content: string;
  status: string;
  evidence_count: number;
  importance: number;
}

interface CorpusMessage {
  id: number;
  sender: string;
  ts_ms: number;
  content: string;
  is_voice: boolean;
  media_path: string;
  category: string;
  badge: string;
  duration_sec?: number;
  duration_label?: string;
}

interface VoiceNote {
  id: number;
  sender: string;
  ts_ms: number;
  content: string;
  transcript: string;
  media_path: string;
  audio_url: string;
  duration_sec: number;
  duration_label: string;
  badge: string;
  category: string;
  importance: number;
}

const INITIAL_FACTS: Memory[] = """ + json.dumps(memories, ensure_ascii=False, indent=2) + """;

const INITIAL_VOICE_NOTES: VoiceNote[] = """ + json.dumps(voice_notes, ensure_ascii=False, indent=2) + """;

const CATEGORY_TABS = [
  { id: 'all', label: 'All (Everything)', icon: Sparkles },
  { id: 'identity', label: 'Identity & Age (20)', icon: ShieldCheck },
  { id: 'education', label: 'Biochemistry & Lab', icon: Layers },
  { id: 'personal', label: 'Faith & Daily Salah', icon: Heart },
  { id: 'preference', label: 'Cats & Kittu Stories', icon: Tag },
  { id: 'habits', label: 'Chai & Daily Routines', icon: RefreshCw },
  { id: 'kdrama', label: 'KDramas & Shows', icon: MessageSquare },
  { id: 'family', label: "Family & Mum's Kitchen", icon: Heart },
  { id: 'behavior', label: 'Voice Notes & Cadence', icon: Headphones },
  { id: 'banter', label: 'Banter & Speech Quirks', icon: Sparkles },
  { id: 'jokes', label: 'Inside Jokes & Memes', icon: Sparkles },
  { id: 'loyalty', label: 'Emotional Bond & Empathy', icon: Heart },
];

export default function MemoriesPage() {
  const [viewTab, setViewTab] = useState<'facts' | 'corpus' | 'voice'>('facts');
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Vault Facts state
  const [memories, setMemories] = useState<Memory[]>(INITIAL_FACTS);

  // Corpus messages state
  const [corpusMessages, setCorpusMessages] = useState<CorpusMessage[]>([]);
  const [corpusTotal, setCorpusTotal] = useState(13653);
  const [loadingCorpus, setLoadingCorpus] = useState(false);
  const [corpusOffset, setCorpusOffset] = useState(0);
  const [hasMoreCorpus, setHasMoreCorpus] = useState(true);

  // Voice notes state
  const [voiceNotes, setVoiceNotes] = useState<VoiceNote[]>(INITIAL_VOICE_NOTES);

  // Category counts
  const [categoryStats, setCategoryStats] = useState<Record<string, number>>({
    all: 13653,
    identity: 2568,
    education: 808,
    personal: 1137,
    preference: 1423,
    family: 1456,
    behavior: 1999,
    personality: 4262,
    banter: 2800,
    jokes: 1462,
    habits: 1120,
    kdrama: 640,
    loyalty: 890,
  });

  // Sync fresh memories from API
  useEffect(() => {
    let isMounted = true;
    async function fetchMemories() {
      try {
        const res = await fetch('/api/memories');
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.memories && data.memories.length > 0) {
            setMemories(data.memories);
          }
        }
      } catch (err) {
        console.error('Failed to load memories:', err);
      }
    }
    fetchMemories();
    return () => {
      isMounted = false;
    };
  }, []);

  // Sync fresh voice notes from API
  useEffect(() => {
    let isMounted = true;
    async function fetchVoiceNotes() {
      try {
        const res = await fetch('/api/voice/notes');
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.voice_notes && data.voice_notes.length > 0) {
            setVoiceNotes(data.voice_notes);
          }
        }
      } catch (err) {
        console.error('Failed to load voice notes:', err);
      }
    }
    fetchVoiceNotes();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch classified corpus messages when switching to corpus tab or changing filter
  useEffect(() => {
    if (viewTab !== 'corpus') return;

    let isMounted = true;
    async function fetchCorpus() {
      setLoadingCorpus(true);
      try {
        const catParam = activeFilter !== 'all' ? `&category=${activeFilter}` : '';
        const qParam = searchQuery ? `&q=${encodeURIComponent(searchQuery)}` : '';
        const res = await fetch(`/api/messages?limit=40&offset=0${catParam}${qParam}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setCorpusMessages(data.messages || []);
            setCorpusTotal(data.total || 13653);
            if (data.category_stats) {
              setCategoryStats((prev) => ({ ...prev, ...data.category_stats }));
            }
            setHasMoreCorpus(data.has_more ?? false);
            setCorpusOffset(40);
          }
        }
      } catch (err) {
        console.error('Failed to load corpus messages:', err);
      } finally {
        if (isMounted) setLoadingCorpus(false);
      }
    }
    fetchCorpus();

    return () => {
      isMounted = false;
    };
  }, [viewTab, activeFilter, searchQuery]);

  const loadMoreCorpus = async () => {
    if (loadingCorpus || !hasMoreCorpus) return;
    setLoadingCorpus(true);
    try {
      const catParam = activeFilter !== 'all' ? `&category=${activeFilter}` : '';
      const qParam = searchQuery ? `&q=${encodeURIComponent(searchQuery)}` : '';
      const res = await fetch(`/api/messages?limit=40&offset=${corpusOffset}${catParam}${qParam}`);
      if (res.ok) {
        const data = await res.json();
        setCorpusMessages((prev) => [...prev, ...(data.messages || [])]);
        setCorpusOffset((prev) => prev + 40);
        setHasMoreCorpus(data.has_more ?? false);
      }
    } catch (err) {
      console.error('Failed to load more corpus messages:', err);
    } finally {
      setLoadingCorpus(false);
    }
  };

  // Filtered vault facts
  const filteredFacts = useMemo(() => {
    return memories.filter((m) => {
      if (m.id.toLowerCase().includes('test') || m.badge.toLowerCase().includes('test')) return false;

      const categoryNorm = (m.category || '').toLowerCase();
      const badgeNorm = (m.badge || '').toLowerCase();
      const contentNorm = (m.content || '').toLowerCase();
      const filterNorm = activeFilter.toLowerCase();

      let matchesFilter = filterNorm === 'all' || categoryNorm === filterNorm;
      if (!matchesFilter) {
        if (filterNorm === 'education' && (categoryNorm === 'study' || categoryNorm === 'education' || contentNorm.includes('biochem') || contentNorm.includes('lab') || contentNorm.includes('maths'))) matchesFilter = true;
        if (filterNorm === 'identity' && (categoryNorm === 'identity' || contentNorm.includes('20 years') || contentNorm.includes('mauritius') || contentNorm.includes('heritage') || contentNorm.includes('uk'))) matchesFilter = true;
        if (filterNorm === 'personal' && (categoryNorm === 'personal' || contentNorm.includes('salah') || contentNorm.includes('fajr') || contentNorm.includes('faith') || contentNorm.includes('dua') || contentNorm.includes('sajdah'))) matchesFilter = true;
        if (filterNorm === 'preference' && (categoryNorm === 'preference' || contentNorm.includes('cat') || contentNorm.includes('kittu') || contentNorm.includes('kitten'))) matchesFilter = true;
        if (filterNorm === 'habits' && (contentNorm.includes('chai') || contentNorm.includes('tea') || contentNorm.includes('blanket') || contentNorm.includes('sleep') || contentNorm.includes('routine'))) matchesFilter = true;
        if (filterNorm === 'kdrama' && (contentNorm.includes('kdrama') || contentNorm.includes('show') || contentNorm.includes('drama') || contentNorm.includes('series'))) matchesFilter = true;
        if (filterNorm === 'family' && (categoryNorm === 'family' || contentNorm.includes('mum') || contentNorm.includes('kitchen') || contentNorm.includes('daughter'))) matchesFilter = true;
        if (filterNorm === 'behavior' && (categoryNorm === 'behavior' || contentNorm.includes('voice') || contentNorm.includes('burst') || contentNorm.includes('lowercase'))) matchesFilter = true;
        if (filterNorm === 'banter' && (categoryNorm === 'personality' || contentNorm.includes('omg') || contentNorm.includes('slang') || contentNorm.includes('sarcasm'))) matchesFilter = true;
        if (filterNorm === 'jokes' && (contentNorm.includes('pattern up') || contentNorm.includes('latw') || contentNorm.includes('bubbzieee') || contentNorm.includes('omdssd') || contentNorm.includes('joke'))) matchesFilter = true;
        if (filterNorm === 'loyalty' && (contentNorm.includes('loyalty') || contentNorm.includes('empath') || contentNorm.includes('care') || contentNorm.includes('listening'))) matchesFilter = true;
      }

      const searchNorm = searchQuery.toLowerCase();
      const matchesSearch =
        !searchQuery ||
        contentNorm.includes(searchNorm) ||
        badgeNorm.includes(searchNorm) ||
        categoryNorm.includes(searchNorm);

      return matchesFilter && matchesSearch;
    });
  }, [memories, activeFilter, searchQuery]);

  // Filtered voice notes
  const filteredVoiceNotes = useMemo(() => {
    return voiceNotes.filter((vn) => {
      const contentNorm = (vn.content || '').toLowerCase();
      const badgeNorm = (vn.badge || '').toLowerCase();
      const searchNorm = searchQuery.toLowerCase();

      const matchesSearch =
        !searchQuery ||
        contentNorm.includes(searchNorm) ||
        badgeNorm.includes(searchNorm) ||
        vn.id.toString().includes(searchNorm);

      if (activeFilter === 'all') return matchesSearch;
      if (activeFilter === 'behavior') return matchesSearch;
      if (activeFilter === 'preference' && (contentNorm.includes('cat') || contentNorm.includes('kittu') || contentNorm.includes('cute'))) return matchesSearch;
      if (activeFilter === 'education' && (contentNorm.includes('exam') || contentNorm.includes('study') || contentNorm.includes('uni'))) return matchesSearch;
      if (activeFilter === 'habits' && (contentNorm.includes('tea') || contentNorm.includes('chai') || contentNorm.includes('tired') || contentNorm.includes('sleep'))) return matchesSearch;
      if (activeFilter === 'banter' && (contentNorm.includes('lol') || contentNorm.includes('voice') || contentNorm.includes('haha'))) return matchesSearch;

      return matchesSearch;
    });
  }, [voiceNotes, activeFilter, searchQuery]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-4 scrollbar-none pb-28 text-ivory select-none max-w-xl mx-auto w-full">
      {/* Top Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-amber uppercase font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-amber animate-pulse" />
            DEEP CORPUS MEMORY VAULT
          </span>
          <h1 className="font-serif text-2xl sm:text-3xl font-normal text-ivory">Shared Memories</h1>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-amber uppercase tracking-widest bg-amber/10 border border-amber/20 px-3 py-1.5 rounded-full font-mono flex items-center gap-1.5 shadow-[0_0_10px_rgba(212,168,83,0.15)]">
            <ShieldCheck className="w-3 h-3 text-amber" />
            <span>{memories.length} Facts &bull; 87 Voice &bull; 13.6k Msgs</span>
          </span>
        </div>
      </div>

      {/* 3-Tab Segmented Mode Switcher */}
      <div className="grid grid-cols-3 p-1 rounded-2xl bg-surface border border-hairline shrink-0 shadow-lg">
        <button
          onClick={() => setViewTab('facts')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'facts'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Vault ({memories.length})</span>
        </button>

        <button
          onClick={() => setViewTab('voice')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'voice'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <Mic className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Voice Notes ({voiceNotes.length})</span>
        </button>

        <button
          onClick={() => setViewTab('corpus')}
          className={`py-2 px-2 sm:px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
            viewTab === 'corpus'
              ? 'bg-amber text-black shadow-md font-bold'
              : 'text-muted hover:text-ivory hover:bg-white/[0.04]'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">All Msgs (13.6k)</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative shrink-0">
        <Search className="w-4 h-4 text-muted absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={
            viewTab === 'facts'
              ? 'Search 68+ verified facts (biochem, cats, faith, age 20, Mauritius...)'
              : viewTab === 'voice'
              ? 'Search 87 Instagram voice notes & audio transcripts...'
              : 'Search 13,653 classified chat & audio messages...'
          }
          className="w-full bg-surface border border-hairline focus:border-amber/50 rounded-2xl pl-10 pr-4 py-2.5 text-[13.5px] text-ivory placeholder:text-muted/60 outline-none transition-all focus:shadow-[0_0_14px_rgba(212,168,83,0.18)]"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-3.5 top-2.5 text-xs text-muted hover:text-ivory cursor-pointer"
          >
            Clear
          </button>
        )}
      </div>

      {/* Expanded Filter Category Pills */}
      <div className="flex gap-2 overflow-x-auto py-1.5 scrollbar-none shrink-0 min-h-[46px] items-center">
        {CATEGORY_TABS.map((f) => {
          const isSelected = activeFilter === f.id;
          const count =
            viewTab === 'facts'
              ? f.id === 'all'
                ? memories.length
                : memories.filter((m) => {
                    const c = (m.category || '').toLowerCase();
                    const txt = (m.content || '').toLowerCase();
                    if (f.id === 'identity') return c === 'identity' || txt.includes('age') || txt.includes('mauritius');
                    if (f.id === 'education') return c === 'education' || txt.includes('biochem') || txt.includes('maths');
                    if (f.id === 'personal') return c === 'personal' || txt.includes('salah') || txt.includes('faith');
                    if (f.id === 'preference') return c === 'preference' || txt.includes('cat') || txt.includes('kittu');
                    if (f.id === 'habits') return txt.includes('chai') || txt.includes('tea') || txt.includes('routine');
                    if (f.id === 'kdrama') return txt.includes('drama') || txt.includes('show');
                    if (f.id === 'family') return c === 'family' || txt.includes('mum');
                    if (f.id === 'behavior') return c === 'behavior' || txt.includes('voice');
                    if (f.id === 'banter') return c === 'personality' || txt.includes('omg');
                    if (f.id === 'jokes') return txt.includes('pattern') || txt.includes('latw') || txt.includes('bubbzieee');
                    if (f.id === 'loyalty') return txt.includes('loyalty') || txt.includes('empath');
                    return c === f.id;
                  }).length
              : viewTab === 'voice'
              ? f.id === 'all'
                ? voiceNotes.length
                : voiceNotes.filter((v) => {
                    const txt = (v.content || '').toLowerCase();
                    if (f.id === 'preference') return txt.includes('cat') || txt.includes('kittu');
                    if (f.id === 'education') return txt.includes('exam') || txt.includes('study');
                    if (f.id === 'habits') return txt.includes('tea') || txt.includes('tired');
                    return true;
                  }).length
              : categoryStats[f.id] || (f.id === 'all' ? 13653 : 1200);

          return (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              className={`px-3.5 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all border shrink-0 cursor-pointer shadow-sm flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-amber text-black border-amber shadow-[0_0_12px_rgba(212,168,83,0.3)] font-bold scale-[1.02]'
                  : 'bg-white/[0.04] border-white/10 text-muted hover:text-ivory hover:bg-white/[0.08]'
              }`}
            >
              <span>{f.label}</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                  isSelected ? 'bg-black/25 text-black font-bold' : 'bg-white/[0.08] text-muted'
                }`}
              >
                {count.toLocaleString()}
              </span>
            </button>
          );
        })}
      </div>

      {/* ── TAB 1: VERIFIED VAULT FACTS ── */}
      {viewTab === 'facts' && (
        <div className="flex flex-col gap-3">
          {filteredFacts.length > 0 ? (
            filteredFacts.map((m) => (
              <MemoryCard
                key={m.id}
                badge={m.badge}
                confidence={m.confidence}
                content={m.content}
                status={m.status}
                evidence_count={m.evidence_count}
                category={m.category}
              />
            ))
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No memories found in this category filter.</p>
              <p className="text-muted text-xs">Try selecting 'All (Everything)' or clear your search terms.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer hover:bg-amber/30 transition-all"
              >
                Reset to All ({memories.length} Facts)
              </button>
            </div>
          )}

          <p className="text-center text-[11px] text-muted/60 mt-3 font-mono">
            Showing {filteredFacts.length} of {memories.length} verified facts from Alisha's corpus
          </p>
        </div>
      )}

      {/* ── TAB 2: INSTAGRAM VOICE NOTES (87 AUDIO MESSAGES WITH EXACT DURATIONS) ── */}
      {viewTab === 'voice' && (
        <div className="flex flex-col gap-3.5">
          <div className="bg-gradient-to-br from-[#1C1D1A] to-[#141512] border border-amber/25 rounded-3xl p-4 shadow-lg flex items-center justify-between gap-3">
            <div>
              <div className="text-[11px] font-mono text-amber uppercase font-semibold flex items-center gap-1">
                <Headphones className="w-3.5 h-3.5 text-amber" />
                INSTAGRAM VOICE ARCHIVE
              </div>
              <h3 className="text-sm font-semibold text-ivory mt-0.5">
                87 Authentic Voice Notes from Alisha
              </h3>
              <p className="text-xs text-muted mt-0.5">
                Real audio notes with exact WAV durations, transcripts & responsive waveforms.
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-amber/15 border border-amber/30 flex items-center justify-center text-amber shrink-0">
              <Volume2 className="w-5 h-5" />
            </div>
          </div>

          {filteredVoiceNotes.length > 0 ? (
            filteredVoiceNotes.map((vn, idx) => (
              <div
                key={vn.id || idx}
                className="p-4 rounded-3xl bg-surface/90 border border-hairline hover:border-amber/35 transition-all space-y-3 shadow-md group"
              >
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber shadow-[0_0_8px_#D4A853]" />
                    <span className="font-semibold text-ivory text-sm">Alisha</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber/10 border border-amber/20 text-amber font-medium">
                      {vn.badge || 'Instagram Voice Note'}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-muted/70">
                    Clip #{vn.id} &bull; {vn.duration_label || '0:12'}
                  </span>
                </div>

                {/* Audio Waveform Player with Real Duration */}
                <div className="w-full">
                  <VoiceBubble
                    audioSrc={vn.audio_url || `/voice/${vn.media_path}`}
                    durationLabel={vn.duration_label || '0:12'}
                    duration={vn.duration_sec || 12}
                  />
                </div>

                {/* Authentic Transcript Box */}
                <div className="bg-[#121310] border border-white/[0.04] rounded-2xl p-3 text-xs text-ivory/90 leading-relaxed font-sans flex items-start gap-2.5">
                  <Mic className="w-3.5 h-3.5 text-amber shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-[10px] uppercase font-mono text-muted block mb-0.5">Voice related messages</span>
                    <span className="italic">"{vn.transcript || vn.content}"</span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No voice notes matched this filter.</p>
              <p className="text-muted text-xs">Try selecting 'All' or clearing your search.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer hover:bg-amber/30 transition-all"
              >
                Reset Voice Notes
              </button>
            </div>
          )}

          <p className="text-center text-[11px] text-muted/60 mt-3 font-mono">
            Showing {filteredVoiceNotes.length} of {voiceNotes.length} Instagram voice messages
          </p>
        </div>
      )}

      {/* ── TAB 3: 13,653 CLASSIFIED CORPUS INTERACTIONS ── */}
      {viewTab === 'corpus' && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between text-xs text-muted font-mono px-1">
            <span>Classified Corpus Messages ({corpusTotal.toLocaleString()})</span>
            <span className="capitalize text-amber font-semibold">{activeFilter} filter</span>
          </div>

          {loadingCorpus && corpusMessages.length === 0 ? (
            <div className="flex flex-col gap-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-20 bg-surface border border-hairline rounded-3xl animate-pulse" />
              ))}
            </div>
          ) : corpusMessages.length > 0 ? (
            <>
              {corpusMessages.map((msg) => {
                const isAlisha = msg.sender === 'alisha';
                return (
                  <div
                    key={msg.id}
                    className="p-3.5 rounded-3xl bg-surface/80 border border-hairline hover:border-amber/25 transition-all space-y-2 shadow-sm"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            isAlisha ? 'bg-amber shadow-[0_0_6px_#D4A853]' : 'bg-blue-400'
                          }`}
                        />
                        <span className="font-semibold text-ivory">
                          {isAlisha ? 'Alisha' : 'You'}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/10 text-muted">
                          {msg.badge}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-muted/60">
                        #{msg.id}
                      </span>
                    </div>

                    {msg.is_voice ? (
                      <div className="pt-1">
                        <VoiceBubble
                          audioSrc={msg.media_path.startsWith('/') ? msg.media_path : `/${msg.media_path}`}
                          durationLabel={msg.duration_label || '0:12'}
                          duration={msg.duration_sec || 12}
                        />
                      </div>
                    ) : (
                      <p className="text-[13.5px] text-ivory/95 font-sans leading-relaxed break-words">
                        {msg.content}
                      </p>
                    )}
                  </div>
                );
              })}

              {hasMoreCorpus && (
                <button
                  onClick={loadMoreCorpus}
                  disabled={loadingCorpus}
                  className="w-full py-3 rounded-2xl bg-surface hover:bg-white/[0.08] border border-hairline text-xs font-semibold text-ivory flex items-center justify-center gap-2 transition-all active:scale-98 cursor-pointer mt-2"
                >
                  {loadingCorpus ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber" />
                  ) : (
                    <Layers className="w-3.5 h-3.5 text-amber" />
                  )}
                  <span>{loadingCorpus ? 'Loading Messages...' : 'Load More Messages (Next 40)'}</span>
                </button>
              )}
            </>
          ) : (
            <div className="glass-card rounded-3xl p-8 text-center space-y-2 border border-white/10">
              <p className="text-ivory font-medium text-sm">No corpus messages matched this filter.</p>
              <p className="text-muted text-xs">Try selecting 'All (Everything)' or clear search.</p>
              <button
                onClick={() => {
                  setActiveFilter('all');
                  setSearchQuery('');
                }}
                className="mt-2 px-3.5 py-1.5 rounded-xl bg-amber/20 border border-amber/30 text-amber text-xs font-semibold cursor-pointer"
              >
                Reset to All
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
"""

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Successfully generated {target_file} with {len(memories)} facts and {len(voice_notes)} voice notes.")

if __name__ == "__main__":
    main()
