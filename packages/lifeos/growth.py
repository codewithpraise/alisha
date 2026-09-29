"""
Personal Growth Engine
Manages Daily Mode plans, adaptive daily load (minimum viable vs stretch),
habit tracking, varied daily reflection prompts, and weekly synthesis.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional

REFLECTION_PROMPTS = [
    "What did I delay today that I knew mattered most?",
    "Where did I choose comfort over discipline today?",
    "What moment today made me lose presence or composure?",
    "Where was I unexpectedly granted ease or blessing today?",
    "What habit is quietly costing me the most clarity or time?",
    "Did my speech today uplift someone or did it involve vanity/criticism?",
    "What is the single most important task for tomorrow that cannot wait?"
]

DEFAULT_HABITS = [
    {"id": "deep_work", "name": "Deep Work Block", "category": "learning", "target": "45 min focus without phone"},
    {"id": "exercise", "name": "Physical Movement", "category": "health", "target": "20-30 min brisk walk, mobility, or workout"},
    {"id": "quran_daily", "name": "Daily Quran Engagement", "category": "worship", "target": "10 min focused reading with meaning"},
    {"id": "sleep_hygiene", "name": "Digital Sunset", "category": "health", "target": "Screens away 45 min before sleep"}
]

class PersonalGrowthEngine:
    """Coordinates daily planning, reflections, habits, and weekly reviews."""

    def __init__(self):
        pass

    def get_today_reflection_prompt(self, day_seed: Optional[int] = None) -> str:
        if day_seed is None:
            day_seed = date.today().timetuple().tm_yday
        return REFLECTION_PROMPTS[day_seed % len(REFLECTION_PROMPTS)]

    def generate_daily_plan(self, energy_level: str = "normal") -> Dict[str, Any]:
        """
        Adaptive load generator:
        - 'low' / difficult day: Minimum Viable Routine (protects continuity, zero overwhelm)
        - 'normal': Balanced routine
        - 'high' / strong day: Stretch goals
        """
        prompt = self.get_today_reflection_prompt()

        if energy_level == "low":
            return {
                "energy_level": "low",
                "energy_tier": "low (Minimum Viable Routine)",
                "quote": "The most beloved deeds to Allah are those that are consistent, even if small.",
                "worship": {
                    "salah": "5/5 Fard on time (pray immediately upon entry)",
                    "dhikr": "33x SubhanAllah, Alhamdulillah, Allahu Akbar after each prayer",
                    "quran": "5 minutes reading (e.g. Surah Al-Mulk or Ayat al-Kursi)"
                },
                "health": "Stay hydrated, 10 min gentle walk, sleep on time",
                "focus": "1 essential priority task; disengage from low-priority noise",
                "reflection": prompt,
                "character": "Patience with oneself and avoiding harsh speech"
            }
        elif energy_level == "high":
            return {
                "energy_level": "high",
                "energy_tier": "high (Stretch Day)",
                "quote": "Seize five before five: your youth before old age, your health before sickness...",
                "worship": {
                    "salah": "5/5 Fard in first half of window + Sunnah prayers + Tahajjud/Witr",
                    "dhikr": "Full morning & evening adhkar + 100x Istighfar + 100x Salawat",
                    "quran": "Read 1 Hizb or Surah Al-Waqi'ah / Surah Al-Kahf with commentary"
                },
                "health": "45 min vigorous strength or cardio session",
                "focus": "Two 90-minute Deep Work blocks",
                "reflection": prompt,
                "character": "Actively initiate acts of kindness and guard every conversation"
            }
        else:
            return {
                "energy_level": "normal",
                "energy_tier": "normal (Steady Cadence)",
                "quote": "Take up deeds according to your capacity.",
                "worship": {
                    "salah": "5/5 Fard preserved on time",
                    "dhikr": "Daily dhikr targets (100 Tasbih, 70 Istighfar)",
                    "quran": "10-15 minutes reading"
                },
                "health": "25 minutes mobility / walk, wholesome meals",
                "focus": "One 60-minute Deep Work block on highest value task",
                "reflection": prompt,
                "character": "Lower ego during discussions and guard against laghw"
            }

    def generate_weekly_review(self, salah_ratio: float = 0.9, dhikr_ratio: float = 0.8) -> Dict[str, Any]:
        """Produces concise 4-pillar review: preserve, improve, remove, next focus."""
        return {
            "title": "Weekly Muhasabah & LifeOS Synthesis",
            "framework": "4-Pillar Muhasabah (Preserve, Improve, Remove, Next Focus)",
            "questions": [
                "What salah/dhikr consistency did you preserve?",
                "Where did spiritual or mental friction occur?",
                "What distraction should be permanently removed?",
                "What is the single core focal point for next week?"
            ],
            "one_to_preserve": "Morning Fajr consistency and prompt prayer entry.",
            "one_to_improve": "Eliminate social media friction right before Isha and bed.",
            "one_to_remove": "Late night multi-tasking and idle browser tab hoarding.",
            "one_focus_next_week": "Cultivate khushu' during Dhuhr & Asr transitions."
        }
