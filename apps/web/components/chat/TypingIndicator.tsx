'use client';

import React from 'react';
import { Mic } from 'lucide-react';

interface TypingIndicatorProps {
  visible?: boolean;
  isKawaii?: boolean;
  isVoice?: boolean;
  label?: string;
}

export default function TypingIndicator({
  visible = true,
  isKawaii = false,
  isVoice = false,
  label,
}: TypingIndicatorProps) {
  if (!visible) return null;

  if (isVoice) {
    return (
      <div className="self-start flex items-center gap-2 bg-white/[0.05] border border-amber/30 px-3.5 py-2.5 rounded-2xl rounded-bl-xs backdrop-blur-md animate-fade-in shadow-[0_0_12px_rgba(212,168,83,0.15)] text-amber">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
        <Mic className="w-3.5 h-3.5 animate-pulse text-amber" />
        <span className="text-[11px] font-mono font-medium tracking-wide">
          {label || 'recording audio… 🎙️'}
        </span>
      </div>
    );
  }

  return (
    <div className="self-start flex items-center gap-2 bg-white/[0.05] border border-white/[0.08] px-3.5 py-2.5 rounded-2xl rounded-bl-xs backdrop-blur-md animate-fade-in shadow-sm">
      <div className="flex items-center gap-1.5">
        <div
          className={`w-1.5 h-1.5 rounded-full animate-typing-bounce ${
            isKawaii ? 'bg-pink-400' : 'bg-amber'
          }`}
          style={{ animationDelay: '-0.32s' }}
        />
        <div
          className={`w-1.5 h-1.5 rounded-full animate-typing-bounce ${
            isKawaii ? 'bg-pink-400' : 'bg-amber'
          }`}
          style={{ animationDelay: '-0.16s' }}
        />
        <div
          className={`w-1.5 h-1.5 rounded-full animate-typing-bounce ${
            isKawaii ? 'bg-pink-400' : 'bg-amber'
          }`}
        />
      </div>
      <span className="text-[10px] font-mono text-muted/70 tracking-wider">
        {label || 'typing…'}
      </span>
    </div>
  );
}
