'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  MessageCircle,
  Phone,
  Clock,
  Compass,
  BookOpen,
  Sparkles,
  Gamepad2,
  Wind,
  BarChart3,
  CheckSquare,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  highlight?: boolean;
}

const ALISHA_NAV: NavItem[] = [
  { label: 'Home', href: '/', icon: Home },
  { label: 'Chat', href: '/chat', icon: MessageCircle },
  { label: 'Call', href: '/call', icon: Phone },
  { label: 'Memories', href: '/memories', icon: Clock },
  { label: 'LifeOS', href: '/lifeos', icon: Compass, highlight: true },
];

const LIFEOS_NAV: NavItem[] = [
  { label: 'Today', href: '/lifeos', icon: Compass },
  { label: 'Salah', href: '/lifeos/salah', icon: Clock },
  { label: 'Tasks', href: '/lifeos/tasks', icon: CheckSquare },
  { label: 'Dhikr', href: '/lifeos/dhikr', icon: Sparkles },
  { label: 'Quran', href: '/lifeos/quran', icon: BookOpen },
  { label: 'Reports', href: '/lifeos/history', icon: BarChart3 },
  { label: 'Games', href: '/lifeos/game', icon: Gamepad2 },
];

export default function BottomNav() {
  const pathname = usePathname();
  const isLifeOS = pathname.startsWith('/lifeos');
  const items = isLifeOS ? LIFEOS_NAV : ALISHA_NAV;

  return (
    <nav className="h-[64px] w-full bg-deep/95 backdrop-blur-lg border-t border-white/[0.06] shrink-0 z-40 select-none">
      <div className="max-w-4xl mx-auto h-full flex items-center justify-around px-2 sm:px-6">
        {items.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-1 py-1.5 px-3 rounded-xl text-[10px] transition-all relative group ${
                isActive
                  ? isLifeOS
                    ? 'text-emerald-400 font-semibold'
                    : 'text-amber font-semibold'
                  : item.highlight
                  ? 'text-emerald-400/80 hover:text-emerald-300'
                  : 'text-muted/70 hover:text-ivory'
              }`}
            >
              {isActive && (
                <span
                  className={`absolute -top-1 w-6 h-0.5 rounded-full ${
                    isLifeOS ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-amber shadow-[0_0_8px_#D4A853]'
                  }`}
                />
              )}
              <Icon
                className={`w-4 h-4 transition-transform group-hover:scale-110 ${
                  item.highlight && !isActive ? 'animate-pulse' : ''
                }`}
              />
              <span className="truncate max-w-[56px]">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

