'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  Gamepad2, 
  ArrowLeft, 
  RotateCcw, 
  Zap, 
  Trophy, 
  Flame, 
  Send, 
  MessageCircle, 
  Calendar, 
  Share2, 
  Sparkles, 
  ShieldAlert, 
  Check, 
  BrainCircuit,
  Eye,
  Shuffle
} from 'lucide-react';

interface RoundData {
  level: number;
  mode?: string;
  sequence?: string[];
  stream?: string[];
  target_rule?: string;
  target_symbol?: string;
  active_rule?: string;
  expected?: string[];
  time_limit_ms: number;
  base_points: number;
}

const SYMBOLS = [
  { id: 'amber_pulse', label: 'Amber', color: 'bg-amber text-black border-amber/60', activeGlow: 'ring-4 ring-amber/50 shadow-[0_0_25px_#D4A853]' },
  { id: 'emerald_flash', label: 'Emerald', color: 'bg-emerald-500 text-black border-emerald-400/60', activeGlow: 'ring-4 ring-emerald-400/50 shadow-[0_0_25px_#10b981]' },
  { id: 'sapphire_glow', label: 'Sapphire', color: 'bg-blue-500 text-white border-blue-400/60', activeGlow: 'ring-4 ring-blue-400/50 shadow-[0_0_25px_#3b82f6]' },
  { id: 'ruby_flare', label: 'Ruby', color: 'bg-rose-500 text-white border-rose-400/60', activeGlow: 'ring-4 ring-rose-400/50 shadow-[0_0_25px_#f43f5e]' },
];

export default function SignalGamePage() {
  const [selectedMode, setSelectedMode] = useState<'memory' | 'focus' | 'switch'>('memory');
  const [gameState, setGameState] = useState<'idle' | 'memorizing' | 'input' | 'result'>('idle');
  const [level, setLevel] = useState(1);
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [accuracy, setAccuracy] = useState(100);
  const [reactionMs, setReactionMs] = useState(420);
  const [round, setRound] = useState<RoundData | null>(null);
  const [flashingIndex, setFlashingIndex] = useState<number>(-1);
  const [userInputs, setUserInputs] = useState<string[]>([]);
  const [roundMessage, setRoundMessage] = useState<string>('');
  const [alishaChallengeResult, setAlishaChallengeResult] = useState<any>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [isDailyChallenge, setIsDailyChallenge] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);

  const startNewGame = (mode: 'memory' | 'focus' | 'switch' = selectedMode, isDaily: boolean = false) => {
    setSelectedMode(mode);
    setIsDailyChallenge(isDaily);
    setLevel(1);
    setScore(0);
    setCombo(0);
    setAlishaChallengeResult(null);
    loadRound(1, 0, mode);
  };

  const loadRound = async (lvl: number, currentCombo: number, mode: string) => {
    setUserInputs([]);
    setRoundMessage('');
    setGameState('memorizing');

    try {
      const res = await fetch(`/api/lifeos/game/signal?level=${lvl}&mode=${mode}`);
      if (res.ok) {
        const data: RoundData = await res.json();
        setRound(data);
        if (data.mode === 'focus' && data.stream) {
          playFocusStream(data.stream);
        } else if (data.sequence) {
          playSequence(data.sequence);
        } else {
          setGameState('input');
        }
        return;
      }
    } catch (e) {
      // offline fallback
    }

    // Local deterministic sequence fallback
    const fallbackSeq = ['amber_pulse', 'emerald_flash', 'sapphire_glow'].slice(0, Math.min(6, 2 + lvl));
    const fallbackRound: RoundData = {
      level: lvl,
      mode: mode,
      sequence: fallbackSeq,
      expected: fallbackSeq,
      time_limit_ms: 15000,
      base_points: 100 * lvl
    };
    setRound(fallbackRound);
    playSequence(fallbackSeq);
  };

  const playSequence = (seq: string[]) => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < seq.length) {
        const symbolId = seq[i];
        const sIndex = SYMBOLS.findIndex((s) => s.id === symbolId);
        setFlashingIndex(sIndex);
        setTimeout(() => setFlashingIndex(-1), 400);
        i++;
      } else {
        clearInterval(interval);
        setFlashingIndex(-1);
        setGameState('input');
        setStartTime(Date.now());
      }
    }, 650);
  };

  const playFocusStream = (stream: string[]) => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < stream.length) {
        const symbolId = stream[i];
        const sIndex = SYMBOLS.findIndex((s) => s.id === symbolId);
        setFlashingIndex(sIndex);
        setTimeout(() => setFlashingIndex(-1), 400);
        i++;
      } else {
        clearInterval(interval);
        setFlashingIndex(-1);
        setGameState('input');
        setStartTime(Date.now());
      }
    }, 550);
  };

  const handleSymbolTap = (symbolId: string) => {
    if (gameState !== 'input' || !round) return;

    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try { window.navigator.vibrate(20); } catch (e) {}
    }

    const nextInputs = [...userInputs, symbolId];
    setUserInputs(nextInputs);

    const expected = round.expected || round.sequence || [];

    if (nextInputs.length === expected.length) {
      const elapsed = Date.now() - startTime;
      evaluateRound(nextInputs, expected, elapsed);
    }
  };

  const evaluateRound = async (inputs: string[], expected: string[], elapsedMs: number) => {
    setReactionMs(Math.round(elapsedMs / Math.max(1, inputs.length)));
    try {
      const res = await fetch('/api/lifeos/game/signal/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level,
          inputs,
          expected,
          elapsed_ms: elapsedMs,
          combo
        })
      });

      if (res.ok) {
        const result = await res.json();
        if (result.correct) {
          const newScore = score + result.score_earned;
          const newCombo = combo + 1;
          const nextLvl = result.next_level || (level + 1);

          setScore(newScore);
          setCombo(newCombo);
          if (newScore > highScore) setHighScore(newScore);

          if (isDailyChallenge && nextLvl > 7) {
            setGameState('result');
            setRoundMessage('🎉 Daily Challenge Mastered (7/7)!');
            triggerAlishaChallenge(newScore);
            return;
          }

          setRoundMessage(`Level ${level} Passed! +${result.score_earned} pts`);
          setLevel(nextLvl);
          setTimeout(() => loadRound(nextLvl, newCombo, selectedMode), 1000);
          return;
        }
      }
    } catch (e) {
      // offline check
    }

    // Check correctness locally
    const isCorrect = JSON.stringify(inputs) === JSON.stringify(expected);
    if (isCorrect) {
      const pts = 100 * level + Math.max(0, Math.floor((10000 - elapsedMs) / 100));
      const newScore = score + pts;
      setScore(newScore);
      setCombo(combo + 1);
      setLevel(level + 1);
      setRoundMessage(`Locked! +${pts} pts`);
      setTimeout(() => loadRound(level + 1, combo + 1, selectedMode), 1000);
    } else {
      setGameState('result');
      setRoundMessage('Signal Disrupted');
      triggerAlishaChallenge(score);
    }
  };

  const triggerAlishaChallenge = async (finalScore: number) => {
    try {
      const res = await fetch('/api/lifeos/game/signal/challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: finalScore })
      });
      if (res.ok) {
        const data = await res.json();
        setAlishaChallengeResult(data);
      }
    } catch (e) {
      setAlishaChallengeResult({
        alisha_score: Math.round(finalScore * 1.05),
        outcome: 'alisha_ahead',
        chat_response: 'lmao i got 4,200 😭 try harder bby'
      });
    }
  };

  const handleShareChallenge = () => {
    const code = `SIGNAL-${score}-${level}-${selectedMode.toUpperCase()}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(`Can you beat my SIGNAL score of ${score.toLocaleString()} in ${selectedMode.toUpperCase()} mode? Challenge Code: ${code}`);
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6 text-ivory select-none pb-28 scrollbar-none">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>
        <div className="text-center">
          <span className="text-[10px] font-mono tracking-widest text-amber uppercase font-semibold">
            Cognitive Agility Engine
          </span>
          <h1 className="font-serif text-xl text-ivory">SIGNAL</h1>
        </div>
        <button
          onClick={() => startNewGame(selectedMode)}
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors text-ivory/80"
          title="Restart Game"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Mode Selectors */}
      <div className="flex items-center gap-2 bg-white/[0.03] p-1 rounded-2xl border border-white/5">
        {[
          { id: 'memory', name: 'Memory', icon: BrainCircuit },
          { id: 'focus', name: 'Focus (Go/No-Go)', icon: Eye },
          { id: 'switch', name: 'Switch Rules', icon: Shuffle },
        ].map((m) => {
          const Icon = m.icon;
          return (
            <button
              key={m.id}
              onClick={() => startNewGame(m.id as any)}
              className={`flex-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 transition-all ${
                selectedMode === m.id
                  ? 'bg-amber/20 text-amber border border-amber/30 shadow-sm'
                  : 'text-ivory/50 hover:text-ivory'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{m.name}</span>
            </button>
          );
        })}
      </div>

      {/* Daily Challenge Card */}
      {gameState === 'idle' && (
        <div className="rounded-3xl bg-gradient-to-br from-emerald-950/40 via-white/[0.02] to-transparent border border-emerald-500/20 p-5 space-y-3 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-emerald-400 uppercase tracking-wider">
              <Calendar className="w-4 h-4" />
              <span>Daily Calibrated Challenge</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
              7 Levels
            </span>
          </div>

          <p className="text-xs text-ivory/70 leading-relaxed font-sans">
            Consistent date-seeded cognitive challenge testing working memory, inhibition, and rule flexibility.
          </p>

          <button
            onClick={() => startNewGame('memory', true)}
            className="w-full py-2.5 rounded-xl bg-emerald-400 text-black font-semibold text-xs hover:bg-emerald-300 transition-all shadow-[0_0_15px_rgba(52,211,153,0.3)] flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch Today's Signal Challenge</span>
          </button>
        </div>
      )}

      {/* Score & Multiplier HUD */}
      <div className="grid grid-cols-3 gap-2">
        <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/5 text-center">
          <span className="text-[10px] font-mono text-ivory/40 uppercase block">Level</span>
          <span className="text-lg font-mono font-bold text-emerald-400">{level}</span>
        </div>
        <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/5 text-center">
          <span className="text-[10px] font-mono text-ivory/40 uppercase block">Score</span>
          <span className="text-lg font-mono font-bold text-amber">{score.toLocaleString()}</span>
        </div>
        <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/5 text-center">
          <span className="text-[10px] font-mono text-ivory/40 uppercase block">Combo</span>
          <span className="text-lg font-mono font-bold text-blue-400">{combo}x</span>
        </div>
      </div>

      {/* Main Signal Display Area */}
      <div className="relative overflow-hidden rounded-3xl bg-black/40 border border-white/10 p-6 flex flex-col items-center justify-center min-h-[260px] shadow-2xl space-y-4">
        {gameState === 'idle' && (
          <div className="text-center space-y-3">
            <Gamepad2 className="w-12 h-12 text-amber mx-auto animate-pulse" />
            <h3 className="font-serif text-lg text-ivory">Ready to Lock Signal?</h3>
            <p className="text-xs text-ivory/50 max-w-xs leading-relaxed">
              {selectedMode === 'memory' && 'Observe the flash sequence and reconstruct it in exact order.'}
              {selectedMode === 'focus' && 'Tap only on the designated target. Inhibit response to all distractors.'}
              {selectedMode === 'switch' && 'Follow the shifting rule displayed on screen for each round.'}
            </p>
            <button
              onClick={() => startNewGame(selectedMode)}
              className="px-6 py-2.5 rounded-full bg-amber text-black font-semibold text-xs hover:bg-amber/90 transition-all shadow-[0_0_20px_rgba(212,168,83,0.3)]"
            >
              Start Level 1
            </button>
          </div>
        )}

        {gameState === 'memorizing' && (
          <div className="text-center space-y-2">
            <span className="text-xs font-mono uppercase tracking-widest text-amber animate-pulse">
              Memorizing Signal Stream...
            </span>
            {round?.target_rule && (
              <div className="p-2 rounded-xl bg-amber/10 border border-amber/30 text-xs text-amber font-mono">
                {round.target_rule}
              </div>
            )}
            {round?.active_rule && (
              <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-xs text-blue-300 font-mono">
                Active Rule: {round.active_rule}
              </div>
            )}
            <div className="text-[11px] text-ivory/40">Watch closely</div>
          </div>
        )}

        {gameState === 'input' && (
          <div className="text-center space-y-2">
            <span className="text-xs font-mono uppercase tracking-widest text-emerald-400 animate-pulse">
              Your Turn — Tap the Signal!
            </span>
            {round?.active_rule && (
              <div className="text-xs text-blue-300 font-mono">{round.active_rule}</div>
            )}
            <div className="flex justify-center gap-1.5 pt-1">
              {(round?.expected || round?.sequence || []).map((_, i) => (
                <span
                  key={i}
                  className={`w-2.5 h-2.5 rounded-full ${
                    i < userInputs.length ? 'bg-emerald-400' : 'bg-white/20'
                  }`}
                />
              ))}
            </div>
          </div>
        )}

        {gameState === 'result' && (
          <div className="text-center space-y-4 animate-in zoom-in-95 duration-200">
            <Trophy className="w-12 h-12 text-amber mx-auto" />
            <div>
              <span className="text-xs font-mono text-ivory/40 uppercase">Final Score</span>
              <h2 className="text-3xl font-mono font-bold text-amber">{score.toLocaleString()}</h2>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-ivory/70 pt-1">
              <div className="p-2 rounded-xl bg-white/5">Accuracy: {accuracy}%</div>
              <div className="p-2 rounded-xl bg-white/5">Avg Reaction: {reactionMs}ms</div>
            </div>

            {/* Asynchronous Alisha Challenge Bubble */}
            {alishaChallengeResult && (
              <div className="p-3 rounded-2xl bg-amber/10 border border-amber/30 text-left space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono text-amber">
                  <span>Alisha Bubbzieee Challenge</span>
                  <span>Score: {alishaChallengeResult.alisha_score?.toLocaleString()}</span>
                </div>
                <p className="text-xs text-amber-100 italic">
                  "{alishaChallengeResult.chat_response}"
                </p>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => startNewGame(selectedMode)}
                className="flex-1 py-2.5 rounded-xl bg-emerald-400 text-black font-semibold text-xs hover:bg-emerald-300 transition-all"
              >
                Play Again
              </button>
              <button
                onClick={handleShareChallenge}
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-ivory text-xs font-medium flex items-center gap-1.5 transition-all"
              >
                {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5" />}
                <span>Challenge Friend</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Interactive 4-Pad Signal Grid */}
      <div className="grid grid-cols-2 gap-3 max-w-xs mx-auto">
        {SYMBOLS.map((s, idx) => {
          const isFlashing = flashingIndex === idx;
          return (
            <button
              key={s.id}
              onClick={() => handleSymbolTap(s.id)}
              disabled={gameState !== 'input'}
              className={`h-24 rounded-2xl border flex flex-col items-center justify-center font-mono text-xs font-bold transition-all duration-150 active:scale-95 ${
                s.color
              } ${
                isFlashing
                  ? s.activeGlow + ' scale-105 brightness-125'
                  : 'opacity-90 hover:opacity-100'
              } ${gameState !== 'input' ? 'cursor-default opacity-80' : 'cursor-pointer'}`}
            >
              <span>{s.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
