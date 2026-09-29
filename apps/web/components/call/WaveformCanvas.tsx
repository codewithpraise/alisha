'use client';

import React, { useEffect, useRef } from 'react';

interface WaveformCanvasProps {
  isActive: boolean;
}

export default function WaveformCanvas({ isActive }: WaveformCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let phase = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener('resize', resize);

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const centerY = h / 2;

      ctx.beginPath();
      ctx.strokeStyle = '#D4A853';
      ctx.lineWidth = 2.5;

      for (let x = 0; x < w; x += 3) {
        const energy = isActive
          ? Math.sin(x * 0.03 + phase) * 16 + Math.cos(x * 0.08 - phase) * 8
          : 2;
        const y = centerY + Math.sin((x / w) * Math.PI) * energy;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }

      ctx.stroke();
      phase += 0.05;
      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animId);
    };
  }, [isActive]);

  return <canvas ref={canvasRef} className="w-full h-[70px] my-5" />;
}
