'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  CheckCircle2, 
  Circle, 
  Plus, 
  Trash2, 
  Target, 
  Zap, 
  Clock, 
  ShieldAlert, 
  Sparkles,
  Layers,
  Flame,
  Check
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  one_liner: string;
  category?: string;
  priority: string;
  completed: boolean;
  est_minutes: number;
}

const DEFAULT_TASKS: Task[] = [
  {
    id: "task_1",
    title: "Organic Chemistry Reaction Mechanisms",
    one_liner: "Open notebook page 28, draw 4 nucleophilic substitution mechanisms once without looking, close tab.",
    priority: "high",
    completed: false,
    est_minutes: 25
  },
  {
    id: "task_2",
    title: "Daily 15-Minute Quran & Tafsir Study",
    one_liner: "Open Surah Al-Mulk, read 10 ayat with classical Hanafi commentary, extract one action rule.",
    priority: "high",
    completed: false,
    est_minutes: 15
  },
  {
    id: "task_3",
    title: "Physical Exercise & Mobility",
    one_liner: "30 pushups, 40 squats, 5 min hamstring stretches before Maghrib without looking at phone.",
    priority: "medium",
    completed: false,
    est_minutes: 20
  }
];

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(DEFAULT_TASKS);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [focusTask, setFocusTask] = useState<Task | null>(null);
  const [focusTimerSeconds, setFocusTimerSeconds] = useState(1500); // 25 min default
  const [isFocusTimerActive, setIsFocusTimerActive] = useState(false);

  // Form State
  const [newTitle, setNewTitle] = useState('');
  const [newOneLiner, setNewOneLiner] = useState('');
  const [newCategory, setNewCategory] = useState('study');
  const [newPriority, setNewPriority] = useState('high');
  const [newEstMins, setNewEstMins] = useState(25);

  const fetchTasks = async () => {
    try {
      const res = await fetch('/api/lifeos/tasks');
      if (res.ok) {
        const data = await res.json();
        if (data && data.tasks) {
          setTasks(data.tasks);
        }
      }
    } catch (e) {
      // Fallback already in place
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // Timer effect for Focus Mode
  useEffect(() => {
    let interval: any = null;
    if (isFocusTimerActive && focusTimerSeconds > 0) {
      interval = setInterval(() => {
        setFocusTimerSeconds((prev) => prev - 1);
      }, 1000);
    } else if (focusTimerSeconds === 0) {
      setIsFocusTimerActive(false);
    }
    return () => clearInterval(interval);
  }, [isFocusTimerActive, focusTimerSeconds]);

  const handleToggle = async (taskId: string) => {
    // Optimistic update
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, completed: !t.completed } : t))
    );

    try {
      await fetch('/api/lifeos/tasks/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId }),
      });
    } catch (e) {
      // Offline fallback
    }
  };

  const handleDelete = async (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    if (focusTask?.id === taskId) {
      setFocusTask(null);
    }

    try {
      await fetch('/api/lifeos/tasks/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId }),
      });
    } catch (e) {
      // Offline fallback
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const oneLinerFinal = newOneLiner.trim() || 'Execute with single-minded focus without tab-switching.';
    const newTask: Task = {
      id: `task_${Date.now()}`,
      title: newTitle.trim(),
      one_liner: oneLinerFinal,
      category: newCategory,
      priority: newPriority,
      completed: false,
      est_minutes: Number(newEstMins) || 15,
    };

    setTasks((prev) => [newTask, ...prev]);
    setIsAddModalOpen(false);
    setNewTitle('');
    setNewOneLiner('');

    try {
      await fetch('/api/lifeos/tasks/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTask.title,
          one_liner: newTask.one_liner,
          category: newCategory,
          priority: newPriority,
          estimated_mins: newTask.est_minutes,
        }),
      });
    } catch (e) {
      // Offline fallback
    }
  };

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.length - completedCount;
  const completionRate = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;
  const totalEstMins = tasks.filter((t) => !t.completed).reduce((acc, t) => acc + (t.est_minutes || 15), 0);

  const filteredTasks = tasks.filter((t) => {
    if (filter === 'pending') return !t.completed;
    if (filter === 'completed') return t.completed;
    return true;
  });

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6 text-ivory select-none pb-28 scrollbar-none">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/lifeos"
          className="w-9 h-9 rounded-full bg-white/[0.05] border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-ivory/80" />
        </Link>
        <div className="text-center">
          <span className="text-[10px] font-mono tracking-widest text-emerald-400 uppercase font-semibold">
            Daily Execution Guard
          </span>
          <h1 className="font-serif text-xl text-ivory">Focus Tasks</h1>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="w-9 h-9 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center hover:bg-emerald-500/30 transition-all shadow-[0_0_12px_rgba(52,211,153,0.2)]"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Hero Metric Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/[0.07] to-white/[0.02] border border-white/10 p-5 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-ivory/60 font-medium">
              <Zap className="w-3.5 h-3.5 text-amber" />
              <span>One-Liner Clarity Rule Active</span>
            </div>
            <div className="text-2xl font-serif text-ivory">
              {completedCount} of {tasks.length} Completed
            </div>
            <p className="text-xs text-ivory/50">
              {totalEstMins > 0 ? `${totalEstMins} mins estimated workload remaining today` : 'All tasks cleared for today!'}
            </p>
          </div>

          {/* Circular Progress Meter */}
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-white/10"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-emerald-400 transition-all duration-700 ease-out"
                strokeDasharray={`${completionRate}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="absolute font-mono text-xs font-bold text-ivory">
              {completionRate}%
            </span>
          </div>
        </div>
      </div>

      {/* Focus Mode Spotlight (Distraction Shield) */}
      {focusTask && (
        <div className="relative rounded-2xl bg-amber/10 border border-amber/30 p-4 space-y-3 shadow-[0_0_24px_rgba(212,168,83,0.15)] animate-in fade-in zoom-in-95 duration-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-amber uppercase tracking-wider">
              <Target className="w-4 h-4 animate-pulse" />
              <span>Distraction-Shield Spotlight</span>
            </div>
            <button
              onClick={() => setFocusTask(null)}
              className="text-xs text-ivory/50 hover:text-ivory px-2 py-0.5 rounded bg-white/5"
            >
              Exit Spotlight
            </button>
          </div>

          <div>
            <h3 className="text-base font-medium text-ivory font-serif">{focusTask.title}</h3>
            <div className="mt-2 p-2.5 rounded-xl bg-black/40 border border-amber/20 text-xs text-amber-200/90 font-mono leading-relaxed">
              <span className="font-bold text-amber block mb-1">Execution One-Liner:</span>
              "{focusTask.one_liner}"
            </div>
          </div>

          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-bold text-ivory tracking-wider">
                {formatTimer(focusTimerSeconds)}
              </span>
              <button
                onClick={() => setIsFocusTimerActive(!isFocusTimerActive)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                  isFocusTimerActive
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}
              >
                {isFocusTimerActive ? 'Pause' : 'Start Focus'}
              </button>
            </div>

            <button
              onClick={() => {
                handleToggle(focusTask.id);
                setFocusTask(null);
              }}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-400 text-black font-semibold hover:bg-emerald-300 transition-all"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Mark Done</span>
            </button>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 bg-white/[0.03] p-1 rounded-xl border border-white/5">
        {(['all', 'pending', 'completed'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
              filter === tab
                ? 'bg-white/10 text-ivory shadow-sm'
                : 'text-ivory/50 hover:text-ivory/80'
            }`}
          >
            {tab} ({tab === 'all' ? tasks.length : tab === 'pending' ? pendingCount : completedCount})
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 space-y-2">
            <p className="text-sm text-ivory/40">No tasks in this view.</p>
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="text-xs text-emerald-400 underline underline-offset-4"
            >
              Add a new task with execution path
            </button>
          </div>
        ) : (
          filteredTasks.map((t) => (
            <div
              key={t.id}
              onClick={() => handleToggle(t.id)}
              className={`group relative overflow-hidden rounded-2xl border p-4 transition-all duration-200 cursor-pointer ${
                t.completed
                  ? 'bg-white/[0.02] border-white/5 opacity-60'
                  : 'bg-white/[0.04] hover:bg-white/[0.07] border-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-start gap-3.5">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleToggle(t.id);
                  }}
                  className="mt-0.5 text-ivory/40 hover:text-emerald-400 transition-colors shrink-0"
                >
                  {t.completed ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                  ) : (
                    <Circle className="w-5 h-5" />
                  )}
                </button>

                <div className="flex-1 min-w-0 space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <h4
                      className={`text-sm font-medium tracking-wide leading-snug ${
                        t.completed ? 'line-through text-ivory/40' : 'text-ivory'
                      }`}
                    >
                      {t.title}
                    </h4>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full border uppercase shrink-0 ${
                        t.priority === 'high'
                          ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                          : 'bg-amber/10 border-amber/30 text-amber'
                      }`}
                    >
                      {t.est_minutes}m
                    </span>
                  </div>

                  {/* Mandatory One-Liner Execution Path */}
                  <div className="p-2 rounded-lg bg-black/30 border border-white/5 text-xs text-ivory/70 font-mono leading-relaxed flex items-start gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-amber shrink-0 mt-0.5" />
                    <span>{t.one_liner}</span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-between pt-1 text-[11px] text-ivory/40">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFocusTask(t);
                        setFocusTimerSeconds(t.est_minutes * 60);
                        setIsFocusTimerActive(true);
                      }}
                      className="text-amber hover:text-amber-300 flex items-center gap-1 transition-colors"
                    >
                      <Target className="w-3 h-3" />
                      <span>Distraction-Shield Mode</span>
                    </button>

                    <button
                      type="button"
                      onClick={(e) => handleDelete(t.id, e)}
                      className="text-rose-400/50 hover:text-rose-400 p-1 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Task Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-sm bg-[#121310] border border-white/10 rounded-3xl p-5 space-y-4 shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-lg text-ivory">Add Focus Task</h3>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-ivory/50 hover:text-ivory text-xs px-2 py-1 rounded bg-white/5"
              >
                Cancel
              </button>
            </div>

            <form onSubmit={handleAddTask} className="space-y-3.5">
              <div>
                <label className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block mb-1">
                  Task Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Study Anatomy Chapter 3"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-ivory placeholder:text-ivory/30 focus:outline-none focus:border-emerald-400"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[11px] font-mono text-amber uppercase tracking-wider font-semibold">
                    One-Liner Execution Path (Required)
                  </label>
                </div>
                <textarea
                  required
                  rows={3}
                  placeholder="Clear exact action: 'Open page 45, review 3 diagrams on heart chambers, close tabs without multitasking.'"
                  value={newOneLiner}
                  onChange={(e) => setNewOneLiner(e.target.value)}
                  className="w-full bg-black/40 border border-amber/30 rounded-xl p-3 text-xs font-mono text-amber-200/90 placeholder:text-ivory/30 focus:outline-none focus:border-amber leading-relaxed"
                />
                <span className="text-[10px] text-ivory/40 block mt-1">
                  Enforces clear execution so you never wander or get distracted.
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block mb-1">
                    Priority
                  </label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-2.5 py-2 text-xs text-ivory focus:outline-none"
                  >
                    <option value="high" className="bg-[#121310]">High Priority</option>
                    <option value="medium" className="bg-[#121310]">Medium Priority</option>
                    <option value="low" className="bg-[#121310]">Low Priority</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-mono text-ivory/60 uppercase tracking-wider block mb-1">
                    Duration (Mins)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="180"
                    value={newEstMins}
                    onChange={(e) => setNewEstMins(Number(e.target.value))}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs text-ivory focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-emerald-400 text-black font-semibold text-sm hover:bg-emerald-300 transition-all shadow-[0_0_15px_rgba(52,211,153,0.3)] mt-2"
              >
                Create Focus Task
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
