'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, MicOff, PhoneOff, Volume2 } from 'lucide-react';
import WaveformCanvas from '@/components/call/WaveformCanvas';

export default function CallPage() {
  const router = useRouter();
  const [seconds, setSeconds] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [status, setStatus] = useState('Listening...');

  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTimer = (totalSec: number) => {
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleEndCall = () => {
    router.push('/chat');
  };

  const handleInterrupt = () => {
    setStatus('Interrupted!');
    setTimeout(() => {
      setStatus('Listening...');
    }, 1200);
  };

  return (
    <div
      onClick={handleInterrupt}
      className="flex-1 flex flex-col items-center justify-between p-8 pb-10 bg-[radial-gradient(circle_at_50%_35%,#1F201C_0%,#111210_70%)]"
    >
      {/* Header Info */}
      <div className="text-center">
        <h2 className="font-serif text-4xl text-ivory mb-1 font-normal">Alisha</h2>
        <div className="inline-flex items-center gap-1.5 text-xs text-amber bg-amber-dim border border-amber/25 px-3 py-0.5 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-amber shadow-[0_0_6px_#D4A853] animate-pulse-amber" />
          <span>{status}</span>
        </div>
        <div className="font-mono text-sm text-muted mt-2">{formatTimer(seconds)}</div>
      </div>

      {/* Center Breathing Visual */}
      <div className="relative w-[220px] h-[220px] flex items-center justify-center">
        <div className="absolute inset-0 rounded-full border border-amber/20 shadow-[0_0_35px_rgba(212,168,83,0.15)] animate-breath-ring" />
        <div className="w-[120px] h-[120px] rounded-full bg-[#171815] border-2 border-amber flex items-center justify-center font-serif text-5xl italic text-ivory z-10 shadow-2xl">
          A
        </div>
      </div>

      {/* Dynamic Waveform Visualizer */}
      <div className="w-full">
        <WaveformCanvas isActive={true} />
        <p className="text-xs text-tertiary text-center">
          Tap anywhere to speak &middot; Alisha supports instant barge-in
        </p>
      </div>

      {/* Call Controls */}
      <div className="flex items-center gap-5" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => setIsMuted(!isMuted)}
          className={`w-[54px] h-[54px] rounded-full border flex items-center justify-center transition-colors cursor-pointer ${
            isMuted
              ? 'bg-rose border-rose text-white'
              : 'bg-raised border-hairline text-ivory hover:bg-[#2D2E2B]'
          }`}
          title="Mute"
        >
          {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>

        <button
          onClick={handleEndCall}
          className="w-[54px] h-[54px] rounded-full bg-rose hover:bg-[#A9554C] text-white flex items-center justify-center shadow-[0_4px_18px_rgba(196,112,103,0.25)] transition-transform active:scale-95 cursor-pointer"
          title="End Call"
        >
          <PhoneOff className="w-5 h-5" />
        </button>

        <button
          onClick={() => setIsSpeakerOn(!isSpeakerOn)}
          className={`w-[54px] h-[54px] rounded-full bg-raised border border-hairline flex items-center justify-center transition-colors cursor-pointer ${
            isSpeakerOn ? 'text-amber' : 'text-muted'
          }`}
          title="Speaker"
        >
          <Volume2 className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
