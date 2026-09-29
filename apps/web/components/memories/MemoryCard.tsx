'use client';

import React from 'react';
import { CheckCircle2, Sparkles, BookOpen, Heart, Users, Smile, Shield } from 'lucide-react';

interface MemoryCardProps {
  badge: string;
  confidence: string | number;
  content: string;
  status?: string;
  evidence_count?: number;
  category?: string;
}

const CATEGORY_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  education: BookOpen,
  study: BookOpen,
  faith: Sparkles,
  personal: Shield,
  preference: Heart,
  cats: Heart,
  family: Users,
  personality: Smile,
  behavior: Sparkles,
};

export default function MemoryCard({
  badge,
  confidence,
  content,
  status = 'verified',
  evidence_count = 12,
  category = 'personal',
}: MemoryCardProps) {
  const Icon = CATEGORY_ICONS[category.toLowerCase()] || Sparkles;

  return (
    <div className="glass-card rounded-2xl p-4 flex flex-col gap-2.5 transition-all hover:scale-[1.01] hover:border-amber/30 animate-slide-up shadow-sm">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-1.5">
          <div className="w-5 h-5 rounded-full bg-amber/10 border border-amber/20 flex items-center justify-center text-amber">
            <Icon className="w-3 h-3" />
          </div>
          <span className="text-[11px] font-semibold text-amber uppercase tracking-wider">
            {badge}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {status === 'verified' && (
            <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-mono bg-emerald-950/30 border border-emerald-500/20 px-1.5 py-0.5 rounded-full">
              <CheckCircle2 className="w-2.5 h-2.5" />
              <span>Verified</span>
            </span>
          )}
          <span className="text-[10px] font-mono text-muted/70">
            {Math.round(Number(confidence) * 100)}% Match
          </span>
        </div>
      </div>

      <p className="text-[14px] text-ivory/95 leading-relaxed font-sans">{content}</p>

      <div className="flex items-center justify-between pt-1 border-t border-white/[0.04] text-[10px] font-mono text-muted/60">
        <span>{evidence_count} corpus interactions</span>
        <span className="capitalize">{category}</span>
      </div>
    </div>
  );
}
