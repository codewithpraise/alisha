'use client';

import React, { useState } from 'react';
import { Copy, Check, Sparkles, Heart } from 'lucide-react';

interface ChatBubbleProps {
  content: string;
  role: 'user' | 'alisha';
  timestamp?: string;
  isKawaii?: boolean;
}

// Simple Rich Text / Markdown Formatter
function renderFormattedContent(text: string) {
  if (!text) return null;

  // Split by line
  const lines = text.split('\n');

  return (
    <div className="space-y-1">
      {lines.map((line, lineIdx) => {
        if (!line.trim()) {
          return <div key={lineIdx} className="h-1.5" />;
        }

        // Parse bold, italic, code
        const parts = [];
        let current = line;
        let pIdx = 0;

        // Regex for bold **text** or *text* or `code`
        const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
        let lastIndex = 0;
        let match;

        while ((match = regex.exec(current)) !== null) {
          if (match.index > lastIndex) {
            parts.push(<span key={pIdx++}>{current.substring(lastIndex, match.index)}</span>);
          }
          const m = match[0];
          if (m.startsWith('**') && m.endsWith('**')) {
            parts.push(<strong key={pIdx++} className="font-semibold text-ivory">{m.slice(2, -2)}</strong>);
          } else if (m.startsWith('*') && m.endsWith('*')) {
            parts.push(<em key={pIdx++} className="italic text-ivory/90">{m.slice(1, -1)}</em>);
          } else if (m.startsWith('`') && m.endsWith('`')) {
            parts.push(
              <code key={pIdx++} className="font-mono text-xs bg-white/10 px-1 py-0.5 rounded text-amber">
                {m.slice(1, -1)}
              </code>
            );
          }
          lastIndex = regex.lastIndex;
        }

        if (lastIndex < current.length) {
          parts.push(<span key={pIdx++}>{current.substring(lastIndex)}</span>);
        }

        // Bullet point support
        if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
          return (
            <div key={lineIdx} className="flex items-start gap-1.5 pl-1">
              <span className="text-amber">•</span>
              <div>{parts.length > 0 ? parts : line.slice(2)}</div>
            </div>
          );
        }

        return <div key={lineIdx}>{parts.length > 0 ? parts : line}</div>;
      })}
    </div>
  );
}

export default function ChatBubble({
  content,
  role,
  timestamp,
  isKawaii = false,
}: ChatBubbleProps) {
  const isUser = role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const timeString = timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (isUser) {
    return (
      <div className="self-end max-w-[85%] sm:max-w-[75%] flex flex-col items-end group animate-slide-up">
        <div
          className={`px-4 py-2.5 rounded-2xl rounded-br-xs text-[14.5px] leading-relaxed break-words shadow-md transition-all ${
            isKawaii
              ? 'bg-gradient-to-br from-pink-500/25 to-purple-600/20 text-pink-50 border border-pink-500/30 shadow-[0_4px_20px_rgba(244,114,182,0.15)]'
              : 'bg-gradient-to-br from-amber/25 to-amber/10 text-ivory border border-amber/30 shadow-[0_4px_20px_rgba(212,168,83,0.12)]'
          }`}
        >
          {renderFormattedContent(content)}
        </div>
        <div className="flex items-center gap-1 mt-1 px-1 text-[10px] text-muted/60 font-mono">
          <span>{timeString}</span>
          <span className={isKawaii ? 'text-pink-400' : 'text-amber'}>✓✓</span>
        </div>
      </div>
    );
  }

  return (
    <div className="self-start max-w-[85%] sm:max-w-[75%] flex items-start gap-2.5 group animate-slide-up">
      {/* Alisha Avatar Badge */}
      <div
        className={`w-7 h-7 rounded-full shrink-0 flex items-center justify-center border mt-0.5 shadow-sm ${
          isKawaii
            ? 'bg-gradient-to-br from-pink-500/30 to-purple-500/20 border-pink-400/40 text-pink-300'
            : 'bg-gradient-to-br from-amber/20 to-emerald-500/10 border-amber/30 text-amber'
        }`}
      >
        {isKawaii ? (
          <Heart className="w-3.5 h-3.5 fill-pink-400/60" />
        ) : (
          <Sparkles className="w-3.5 h-3.5" />
        )}
      </div>

      <div className="flex flex-col items-start">
        <div
          className={`relative px-4 py-2.5 rounded-2xl rounded-bl-xs text-[14.5px] leading-relaxed break-words backdrop-blur-md transition-all shadow-sm ${
            isKawaii
              ? 'bg-pink-950/20 text-ivory border border-pink-500/20 hover:border-pink-500/35'
              : 'bg-white/[0.05] text-ivory border border-white/[0.08] hover:border-white/20'
          }`}
        >
          {renderFormattedContent(content)}

          {/* Quick Copy Button */}
          <button
            onClick={handleCopy}
            title="Copy message"
            className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-surface border border-hairline flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:scale-110 text-muted hover:text-ivory cursor-pointer"
          >
            {copied ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
          </button>
        </div>

        <div className="flex items-center gap-2 mt-1 px-1 text-[10px] text-muted/60 font-mono">
          <span className="font-sans font-medium text-muted/80">
            {isKawaii ? 'Alisha-Chan' : 'alisha bubbzieee'}
          </span>
          <span>•</span>
          <span>{timeString}</span>
        </div>
      </div>
    </div>
  );
}

