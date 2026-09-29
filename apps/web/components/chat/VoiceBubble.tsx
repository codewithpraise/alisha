'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause } from 'lucide-react';

interface VoiceBubbleProps {
  audioSrc?: string;
  durationLabel?: string;
  duration?: number | string;
  isKawaii?: boolean;
  caption?: string;
}

const BAR_HEIGHTS = [8, 14, 20, 12, 18, 22, 16, 10, 14, 19, 13, 7, 16, 11, 18, 9];

export default function VoiceBubble({
  audioSrc = '/voice/1247080237633732.wav',
  durationLabel = '0:15',
  duration,
  isKawaii = false,
  caption,
}: VoiceBubbleProps) {
  const initialDuration =
    durationLabel ||
    (typeof duration === 'number'
      ? `0:${duration < 10 ? '0' : ''}${duration}`
      : duration || '0:15');

  const [isPlaying, setIsPlaying] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const [currentDuration, setCurrentDuration] = useState(initialDuration);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Clear timers on unmount
  useEffect(() => {
    return () => {
      if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
      }
    };
  }, []);

  const parseTotalSeconds = () => {
    if (audioRef.current && audioRef.current.duration && !isNaN(audioRef.current.duration)) {
      return Math.ceil(audioRef.current.duration);
    }
    if (typeof duration === 'number' && duration > 0) return duration;
    const parts = (durationLabel || initialDuration).split(':');
    if (parts.length === 2) {
      return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10) || 15;
    }
    return 15;
  };

  const stopPlayback = () => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
      progressTimerRef.current = null;
    }
    if (audioRef.current) {
      try {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      } catch {}
    }
    setIsPlaying(false);
    setActiveIdx(-1);
    setCurrentDuration(initialDuration);
  };

  const startPlayback = () => {
    setIsPlaying(true);
    const totalSec = parseTotalSeconds();
    let elapsedSec = 0;
    const numBars = BAR_HEIGHTS.length;
    const intervalMs = Math.max(150, (totalSec * 1000) / numBars);

    // Immediate initial step
    setActiveIdx(0);

    // Try playing real audio
    if (audioRef.current) {
      try {
        audioRef.current.play().catch(() => {
          // Audio autoplay/playback restriction fallback
        });
      } catch {}
    }

    if (progressTimerRef.current) clearInterval(progressTimerRef.current);

    progressTimerRef.current = setInterval(() => {
      elapsedSec += intervalMs / 1000;
      const progress = Math.min(1, elapsedSec / totalSec);
      const curBar = Math.floor(progress * numBars);
      setActiveIdx(curBar);

      const secDisplay = Math.min(totalSec, Math.floor(elapsedSec));
      const min = Math.floor(secDisplay / 60);
      const remSec = secDisplay % 60;
      setCurrentDuration(`${min}:${remSec < 10 ? '0' : ''}${remSec}`);

      if (progress >= 1) {
        stopPlayback();
      }
    }, intervalMs);
  };

  const handleToggle = () => {
    if (isPlaying) {
      stopPlayback();
    } else {
      startPlayback();
    }
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const dur = audioRef.current.duration;
    const cur = audioRef.current.currentTime;
    if (dur && dur > 0) {
      const progress = Math.min(1, cur / dur);
      const barIdx = Math.floor(progress * BAR_HEIGHTS.length);
      setActiveIdx(barIdx);
      const sec = Math.floor(cur);
      const min = Math.floor(sec / 60);
      const rem = sec % 60;
      setCurrentDuration(`${min}:${rem < 10 ? '0' : ''}${rem}`);
    }
  };

  const formattedSrc = audioSrc.startsWith('http')
    ? audioSrc
    : audioSrc.startsWith('/')
    ? audioSrc
    : `/${audioSrc}`;

  return (
    <div className="flex flex-col gap-1.5 max-w-[85%] self-start">
      <div
        className={`flex items-center gap-3 px-4 py-2.5 rounded-2xl rounded-bl-xs min-w-[240px] transition-all shadow-sm ${
          isKawaii
            ? 'bg-pink-950/30 border border-pink-500/30'
            : 'bg-white/[0.05] border border-white/[0.08]'
        }`}
      >
        <audio
          ref={audioRef}
          src={formattedSrc}
          onTimeUpdate={handleTimeUpdate}
          onEnded={stopPlayback}
          preload="metadata"
        />

        <button
          onClick={handleToggle}
          type="button"
          aria-label={isPlaying ? 'Pause voice message' : 'Play voice message'}
          className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 transition-transform active:scale-95 cursor-pointer shadow-md ${
            isKawaii
              ? 'bg-pink-400 text-black hover:bg-pink-300 shadow-[0_0_12px_#f472b6]'
              : 'bg-amber text-black hover:bg-amber-dark shadow-[0_0_12px_rgba(212,168,83,0.3)]'
          }`}
        >
          {isPlaying ? (
            <Pause className="w-4 h-4 fill-current" />
          ) : (
            <Play className="w-4 h-4 fill-current ml-0.5" />
          )}
        </button>

        <div className="flex-1 flex flex-col gap-1">
          <div className="flex items-center gap-[2.5px] h-[22px]">
            {BAR_HEIGHTS.map((h, i) => (
              <div
                key={i}
                style={{ height: `${h}px` }}
                className={`w-[2.5px] rounded-full transition-all duration-150 ${
                  i <= activeIdx
                    ? isKawaii
                      ? 'bg-pink-400'
                      : 'bg-amber'
                    : 'bg-white/20'
                }`}
              />
            ))}
          </div>
          <div className="flex items-center justify-between text-[10px] font-mono text-muted/70">
            <span>{currentDuration}</span>
            <span className="text-[9px] uppercase tracking-wider opacity-60">Voice Note</span>
          </div>
        </div>
      </div>

      {caption && caption !== 'voice note' && (
        <div className="text-[12px] text-ivory/80 px-2 leading-relaxed font-sans italic">
          "{caption}"
        </div>
      )}
    </div>
  );
}
