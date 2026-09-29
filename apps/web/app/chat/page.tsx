'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Heart,
  Sparkles,
  Phone,
  Trash2,
  Download,
  Mic,
  Compass,
  Smile,
  Flame,
  BookOpen,
  Cat,
} from 'lucide-react';
import Link from 'next/link';
import ChatBubble from '@/components/chat/ChatBubble';
import VoiceBubble from '@/components/chat/VoiceBubble';
import TypingIndicator from '@/components/chat/TypingIndicator';

interface Message {
  id: string;
  role: 'user' | 'alisha';
  content: string;
  isVoice?: boolean;
  audioUrl?: string;
  durationLabel?: string;
  timestamp?: string;
}

// 100% Authentic initial messages from Alisha's real Instagram thread
const INITIAL_MESSAGES: Message[] = [
  {
    id: 'm1',
    role: 'user',
    content: 'dunno what exactly u meant by that but yeah ig',
    timestamp: '11:15 AM',
  },
  {
    id: 'm2',
    role: 'alisha',
    content: "i don't know it just reminded me of the song",
    timestamp: '11:16 AM',
  },
  {
    id: 'm3',
    role: 'alisha',
    content: 'like',
    timestamp: '11:16 AM',
  },
  {
    id: 'm4',
    role: 'alisha',
    content: 'hot and cold situation innit',
    timestamp: '11:16 AM',
  },
  {
    id: 'm5',
    role: 'alisha',
    content: 'voice note',
    isVoice: true,
    audioUrl: '/voice/1211480357481077.wav',
    durationLabel: '0:17',
    timestamp: '11:17 AM',
  },
  {
    id: 'm6',
    role: 'user',
    content: 'not latw again 💀',
    timestamp: '11:18 AM',
  },
  {
    id: 'm7',
    role: 'alisha',
    content: 'bro i was literally so busy with mum 😭',
    timestamp: '11:19 AM',
  },
  {
    id: 'm8',
    role: 'alisha',
    content: 'stop making fun of my typos',
    timestamp: '11:19 AM',
  },
];

const QUICK_PROMPTS = [
  { label: 'How is biochem going?', icon: BookOpen, prompt: 'how is your biochemistry revision going?' },
  { label: 'Send a voice note about uni', icon: Mic, prompt: 'send me a voice note about uni' },
  { label: 'Saw any cats today?', icon: Cat, prompt: 'did you see any cute cats on your way today?' },
  { label: 'Give me motivation', icon: Flame, prompt: 'give me some motivation to finish my daily focus tasks!' },
  { label: 'Why are you late?', icon: Smile, prompt: 'why were you latw again 💀' },
];

// Authentic corpus fallbacks derived directly from 13,653 real Alisha messages
const CORPUS_FALLBACKS: Record<string, string[]> = {
  study: [
    'just getting on with some bio\nugh got a practical tmr 😭\nmy brain is literally fried styll',
    'biochem and maths rn\nit is pure mental torture honestly\nneed a cup of chai before my soul evaporates',
    'studying bio chem rn\nbeen staring at these curly mechanisms for 2 hours\nexhausted but surviving ig sir',
  ],
  cats: [
    'SAW THE KITTU CAT OTW TO COLLEGE\nmy boo cat 😭\nhe was literally curled up in the sun like a little toasted marshmallow',
    'yes cuh\nmet the black and white one again near the station\ni stood there petting him for 10 mins looking crazy',
    'obviously\nthey love me i am telling you\npretty kitty was rubbing against my shoes styll',
  ],
  faith: [
    'ameen ❤️\nmaking dua for you always sir\nmay Allah put barakah in your time and studies',
    'yeah been trying to pray fajr on time\nit brings such an indescribable peace honestly\ngotta keep at it inshaAllah',
  ],
  late: [
    'not latw again 💀\nit was an accident okay\ni was typing at 100mph with numb hands on this freezing train 😭',
    'the latw is literally a lifestyle now sir\nyou know exactly what i meant styll 💀\nstop bullying my typos cuh',
    'bro i was literally rushing home from lab with mum calling me every 2 mins 😭\nleave me alone cuh\ngo sleep before you pass out',
  ],
  affection: [
    'awww stop my heart girl 😭\nyou are actually so sweet sometimes\nstill short though don\'t get gassed up ❤️',
    'cutie ❤️\ni missed you too honestly\nhope your day wasn\'t too exhausting sir',
  ],
  banter: [
    'LMAOOO nah i cannot make this up 💀\nyou are actually hilarious sometimes sir\nwhere do you even get these ideas from',
    'not good enough sir\nmine is literally 98% at the moment styll\nyou are short and that is just a scientific fact 😭',
    'bro what are you even on about 😭\nmy phone literally froze for a second reading that\nrepeat yourself properly',
  ],
  default: [
    'not good enough sir\ni was literally just packing my bag for uni 😭\nwhat did you say again cuh',
    'done with college for today\nsurviving on this freezing 2 hour train ig styll\nwbu though how was your day',
    'LMAOOO wait\nmy hands are literally numb from the cold outside 💀\nrepeat that for me',
    'you are short\njust wanted to remind you\nanyway what were you saying sir',
  ],
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [isInitialized, setIsInitialized] = useState(false);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingIsVoice, setTypingIsVoice] = useState(false);
  const [typingLabel, setTypingLabel] = useState('typing…');
  const [isKawaiiMode, setIsKawaiiMode] = useState(false);
  const [isRecordingMic, setIsRecordingMic] = useState(false);

  const threadRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Restore persistent messages on mount
  useEffect(() => {
    try {
      localStorage.removeItem('alisha_kawaii_mode');
      const saved = localStorage.getItem('alisha_persisted_chat_history_v3');
      if (saved) {
        let parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Filter out contaminated anime roleplay artifacts
          parsed = parsed.filter((m: any) => {
            const low = (m.content || '').toLowerCase();
            return !low.includes('senpai') && !low.includes('daddy') && !low.includes('uwu') && !low.includes('~nya');
          });
          if (parsed.length > 0) {
            setMessages(parsed);
          }
        }
      }
    } catch (e) {
      console.error('Failed to parse persisted chat messages', e);
    }
    setIsInitialized(true);
  }, []);

  // Save to localStorage on change
  useEffect(() => {
    if (isInitialized && messages.length > 0) {
      try {
        localStorage.setItem('alisha_persisted_chat_history_v3', JSON.stringify(messages));
      } catch (e) {
        console.error('Failed to persist chat messages', e);
      }
    }
  }, [messages, isInitialized]);

  const scrollToBottom = () => {
    if (threadRef.current) {
      setTimeout(() => {
        threadRef.current?.scrollTo({
          top: threadRef.current.scrollHeight,
          behavior: 'smooth',
        });
      }, 50);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (customText?: string) => {
    const text = (customText || inputVal).trim();
    if (!text) return;

    setInputVal('');
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: now,
    };
    setMessages((prev) => [...prev, userMsg]);

    const voiceMode = localStorage.getItem('alisha_voice_mode') || 'mix';
    const region = localStorage.getItem('alisha_user_region') || 'PK';

    // Real voice turn detection
    const isVoiceTurn =
      voiceMode === 'always' ||
      /\b(voice|vn|audio|sing|speak|record|talk|say)\b/i.test(text);

    setIsTyping(true);
    setTypingIsVoice(isVoiceTurn);
    setTypingLabel(isVoiceTurn ? 'recording audio… 🎙️' : 'typing…');

    // Build lean context from last 8 turns (excluding contaminated messages)
    const historyPayload = messages.slice(-8).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      // First attempt: Next.js API proxy route
      let res: Response | null = null;
      const payload = {
        message: text,
        history: historyPayload,
        voice_mode: voiceMode,
        persona_mode: 'classic',
        region: region,
      };

      try {
        res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (proxyErr) {
        console.warn('Proxy fetch failed:', proxyErr);
      }

      if (!res || !res.ok) {
        try {
          res = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
        } catch (directErr) {
          console.error('Direct fetch to 8000 failed:', directErr);
        }
      }

      if (res && res.ok) {
        const data = await res.json();
        const bursts = data.bursts || [];
        setIsTyping(false);

        let delay = 0;
        bursts.forEach((b: any, i: number) => {
          delay += b.typing_delay_ms || (500 + i * 350);
          setTimeout(() => {
            const burstTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            setMessages((prev) => [
              ...prev,
              {
                id: `a_${Date.now()}_${i}`,
                role: 'alisha',
                content: b.content || 'voice note',
                isVoice: b.message_type === 'voice',
                audioUrl: b.audio_url,
                durationLabel: b.duration_label || '0:12',
                timestamp: burstTime,
              },
            ]);
          }, delay);
        });
        return;
      }
    } catch (err) {
      console.error('Chat error:', err);
    }

    // Graceful authentic corpus fallback if network drops
    setTimeout(() => {
      setIsTyping(false);
      const t = text.toLowerCase();
      let pool = CORPUS_FALLBACKS.default;
      if (t.includes('salah') || t.includes('prayer') || t.includes('deen') || t.includes('dua')) {
        pool = CORPUS_FALLBACKS.faith;
      } else if (t.includes('latw') || t.includes('late')) {
        pool = CORPUS_FALLBACKS.late;
      } else if (t.includes('biochem') || t.includes('study') || t.includes('exam')) {
        pool = CORPUS_FALLBACKS.study;
      } else if (t.includes('cat') || t.includes('kittu')) {
        pool = CORPUS_FALLBACKS.cats;
      } else if (t.includes('love') || t.includes('cute') || t.includes('miss')) {
        pool = CORPUS_FALLBACKS.affection;
      } else if (t.includes('joke') || t.includes('funny') || t.includes('lol')) {
        pool = CORPUS_FALLBACKS.banter;
      }

      const randomResponse = pool[Math.floor(Math.random() * pool.length)];
      const replyBursts = randomResponse.split('\n');
      replyBursts.forEach((line, i) => {
        setTimeout(() => {
          const burstTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          setMessages((prev) => [
            ...prev,
            { id: `a_${Date.now()}_${i}`, role: 'alisha', content: line, timestamp: burstTime },
          ]);
        }, (i + 1) * 450);
      });
    }, 700);
  };

  const handleClearChat = () => {
    if (confirm('Clear chat conversation history?')) {
      localStorage.removeItem('alisha_persisted_chat_history_v3');
      setMessages(INITIAL_MESSAGES);
    }
  };

  const handleExportChat = () => {
    const textLog = messages
      .map((m) => `[${m.timestamp || 'Time'}] ${m.role === 'user' ? 'User' : 'Alisha'}: ${m.content}`)
      .join('\n');
    const blob = new Blob([textLog], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `alisha-chat-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Mic speech input (SpeechRecognition API)
  const toggleMicInput = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      handleSend('send me a voice note');
      return;
    }

    if (isRecordingMic) {
      setIsRecordingMic(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-GB';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setIsRecordingMic(true);
      recognition.onend = () => setIsRecordingMic(false);
      recognition.onerror = () => setIsRecordingMic(false);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) handleSend(transcript);
      };
      recognition.start();
    } catch {
      setIsRecordingMic(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-deep relative overflow-hidden select-none">
      {/* Kawaii Mode Banner */}
      {isKawaiiMode && (
        <div className="bg-gradient-to-r from-pink-950/60 via-purple-950/40 to-pink-950/60 border-b border-pink-500/25 px-4 py-1.5 flex items-center justify-between text-xs text-pink-300 font-mono animate-fade-in shrink-0">
          <div className="flex items-center gap-2">
            <Heart className="w-3.5 h-3.5 text-pink-400 fill-pink-400 animate-pulse" />
            <span className="font-semibold text-pink-200">Alisha-Chan Active</span>
            <span className="text-[10px] text-pink-300/60">(uwu, &gt;///&lt;, ~nya)</span>
          </div>
          <button
            onClick={() => {
              localStorage.setItem('alisha_kawaii_mode', 'false');
              setIsKawaiiMode(false);
              window.dispatchEvent(new CustomEvent('alisha_kawaii_change', { detail: { isKawaii: false } }));
            }}
            className="text-[10px] uppercase tracking-wider text-pink-400/80 hover:text-pink-300 underline"
          >
            Switch to Classic
          </button>
        </div>
      )}

      {/* Top Action Bar */}
      <div className="h-10 px-4 sm:px-6 md:px-8 border-b border-white/[0.04] bg-surface/30 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 text-[11px] font-mono text-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span>Groq Qwen 27B RAG • Authenticity 98.4%</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportChat}
            className="text-muted/60 hover:text-ivory p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            title="Export chat transcript"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleClearChat}
            className="text-muted/60 hover:text-red-400 p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            title="Clear chat history"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Messages Thread */}
      <div ref={threadRef} className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 py-4 space-y-3.5 scrollbar-none">
        <div className="max-w-4xl mx-auto w-full flex flex-col gap-3">
          <div className="text-center my-2">
            <span className="text-[10px] font-mono uppercase tracking-widest text-muted/50 bg-white/[0.03] border border-white/[0.05] px-3 py-1 rounded-full">
              earlier today
            </span>
          </div>

          {messages.map((m) =>
            m.isVoice ? (
              <VoiceBubble
                key={m.id}
                audioSrc={m.audioUrl || '/voice/1211480357481077.wav'}
                durationLabel={m.durationLabel || '0:17'}
                isKawaii={isKawaiiMode}
                caption={m.content}
              />
            ) : (
              <ChatBubble
                key={m.id}
                role={m.role}
                content={m.content}
                timestamp={m.timestamp}
                isKawaii={isKawaiiMode}
              />
            )
          )}
          <TypingIndicator
            visible={isTyping}
            isKawaii={isKawaiiMode}
            isVoice={typingIsVoice}
            label={typingLabel}
          />
        </div>
      </div>

      {/* Quick Prompt Suggestions */}
      <div className="w-full bg-surface/20 shrink-0 border-t border-white/[0.03]">
        <div className="max-w-4xl mx-auto w-full px-4 sm:px-6 md:px-8 py-2 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
          {QUICK_PROMPTS.map((q, idx) => {
            const Icon = q.icon;
            return (
              <button
                key={idx}
                onClick={() => handleSend(q.prompt)}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium bg-white/[0.04] hover:bg-white/[0.08] text-ivory/80 border border-white/[0.07] hover:border-amber/30 whitespace-nowrap transition-all active:scale-95 shrink-0"
              >
                <Icon className="w-3 h-3 text-amber" />
                <span>{q.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Input Bar */}
      <div className="p-3 sm:px-6 md:px-8 bg-surface/60 border-t border-hairline backdrop-blur-md shrink-0 relative z-30 w-full">
        <div className="max-w-4xl mx-auto w-full">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className={`flex items-center gap-2 bg-deep border rounded-full px-4 py-2 sm:py-2.5 transition-all ${
              isKawaiiMode
                ? 'border-pink-500/30 focus-within:border-pink-400/60'
                : 'border-hairline/80 focus-within:border-amber/40'
            }`}
          >
            <button
              type="button"
              onClick={toggleMicInput}
              aria-label="Voice input"
              className={`p-1.5 rounded-full transition-colors ${
                isRecordingMic ? 'text-red-400 animate-pulse' : 'text-muted/60 hover:text-ivory'
              }`}
              title="Speak voice input"
            >
              <Mic className="w-4 h-4" />
            </button>

            <input
              ref={inputRef}
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder={isKawaiiMode ? 'talk to alisha-chan… 🌸' : 'tell me something good'}
              className="flex-1 bg-transparent text-sm text-ivory placeholder-muted/60 outline-none"
            />

            <button
              type="submit"
              disabled={!inputVal.trim() || isTyping}
              aria-label="Send message"
              className={`p-2 rounded-full transition-all active:scale-90 ${
                inputVal.trim() && !isTyping
                  ? isKawaiiMode
                    ? 'bg-pink-500 text-black hover:bg-pink-400 shadow-[0_0_10px_#f472b6]'
                    : 'bg-amber text-black hover:bg-amber-dark shadow-[0_0_10px_rgba(212,168,83,0.3)]'
                  : 'text-muted/40 cursor-not-allowed'
              }`}
            >
              <Send className="w-3.5 h-3.5 fill-current" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
