"""
Adaptive Notification & Throttling Engine for LifeOS
Fiqh-aware, fatigue-dampened, respect-oriented reminder scheduler with full customization capabilities.
Zero-spam, zero-guilt, mathematically precise window alignment.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, time, timedelta, date
from typing import Dict, List, Optional, Any
import json
import sqlite3
import os


@dataclass
class NotificationItem:
    id: str
    title: str
    body: str
    category: str  # 'salah', 'dhikr', 'muhasabah', 'quran', 'tafsir', 'fasting', 'health', 'game'
    priority: int  # 1 (Critical), 2 (High), 3 (Medium), 4 (Low)
    scheduled_time: str  # "HH:MM"
    valid_window_minutes: int
    action_url: str
    sound: str = "default"  # 'adhan', 'gentle_bell', 'soft_chime', 'silent'
    icon: str = "bell"
    metadata: Dict[str, Any] = field(default_factory=dict)


DEFAULT_NOTIFICATION_PREFS = {
    "salah_alerts": True,
    "salah_advance_mins": 10,
    "salah_adhan_sound": True,
    "fajr_wake_up": True,
    "tahajjud_reminder": True,
    "tahajjud_mins_before_fajr": 45,
    "morning_athkar": True,
    "morning_athkar_offset_mins": 20,
    "evening_athkar": True,
    "evening_athkar_offset_mins": 30,
    "daily_ayah_hadith": True,
    "daily_ayah_time": "08:30",
    "night_muhasabah": True,
    "night_muhasabah_time": "21:45",
    "sunnah_fasting_reminders": True,
    "friday_kahf_reminder": True,
    "dhikr_nudges": True,
    "hydration_breaks": True,
    "quiet_hours_enabled": True,
    "quiet_hours_start": "23:15",
    "quiet_hours_end": "04:30",
    "sound_enabled": True,
    "vibration_enabled": True,
    "max_daily": 8
}


class AdaptiveNotificationScheduler:
    """
    Computes intelligent, respectful notification schedules based on:
    1. Daily Salah calculation times & Sunnah cycles (Jumu'ah, White Days, Mon/Thu fasting)
    2. User customized preferences and quiet hours
    3. Adaptive fatigue scoring (backs off when user is busy/ignoring)
    4. Essential Islamic practice windows (Adhan, Morning/Evening Athkar, Night Muhasabah)
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        if not self.db_path or not os.path.exists(os.path.dirname(self.db_path)):
            return
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    key TEXT PRIMARY KEY,
                    value_json TEXT,
                    updated_at INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id TEXT PRIMARY KEY,
                    notification_id TEXT,
                    scheduled_time TEXT,
                    sent_at INTEGER,
                    status TEXT, -- 'sent', 'opened', 'dismissed', 'ignored'
                    action_taken TEXT
                )
            """)
            con.commit()
            con.close()
        except Exception as e:
            print(f"[Notification DB Init Error] {e}")

    def get_preferences(self) -> Dict[str, Any]:
        prefs = dict(DEFAULT_NOTIFICATION_PREFS)
        if not self.db_path:
            return prefs
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT value_json FROM notification_preferences WHERE key = 'user_custom'")
            row = cur.fetchone()
            if row and row[0]:
                saved = json.loads(row[0])
                prefs.update(saved)
            con.close()
        except Exception:
            pass
        return prefs

    def save_preferences(self, new_prefs: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_preferences()
        current.update(new_prefs)
        if self.db_path:
            try:
                con = sqlite3.connect(self.db_path)
                cur = con.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO notification_preferences (key, value_json, updated_at) VALUES (?, ?, ?)",
                    ('user_custom', json.dumps(current), int(datetime.now().timestamp() * 1000))
                )
                con.commit()
                con.close()
            except Exception as e:
                print(f"[Save Notification Prefs Error] {e}")
        return current

    def compute_daily_schedule(
        self,
        salah_schedule: Dict[str, str],
        user_prefs: Optional[Dict[str, Any]] = None,
        fatigue_score: float = 0.0,
        target_date: Optional[date] = None
    ) -> List[NotificationItem]:
        """
        Generates a customized, choreographed daily notification schedule.
        """
        prefs = user_prefs or self.get_preferences()
        now_date = target_date or date.today()
        weekday = now_date.weekday()  # Monday is 0, Sunday is 6
        schedule: List[NotificationItem] = []

        # Helper to parse HH:MM
        def parse_hhmm(s: str) -> Optional[datetime]:
            try:
                h, m = map(int, s.split(":"))
                return datetime(now_date.year, now_date.month, now_date.day, h, m)
            except Exception:
                return None

        # 1. Tahajjud & Last Third of Night Alert (Pre-Fajr)
        if prefs.get("tahajjud_reminder") and "fajr" in salah_schedule:
            fajr_dt = parse_hhmm(salah_schedule["fajr"])
            if fajr_dt:
                offset_m = int(prefs.get("tahajjud_mins_before_fajr", 45))
                tahajjud_dt = fajr_dt - timedelta(minutes=offset_m)
                schedule.append(NotificationItem(
                    id="tahajjud_call",
                    title="The Last Third of the Night",
                    body="The gates of acceptance are open. Stand for even 2 rak'ahs of intimate Tahajjud.",
                    category="salah",
                    priority=2,
                    scheduled_time=tahajjud_dt.strftime("%H:%M"),
                    valid_window_minutes=offset_m,
                    action_url="/lifeos/salah",
                    sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                    icon="moon",
                    metadata={"type": "tahajjud", "mins_before_fajr": offset_m}
                ))

        # 2. Salah Adhan & Approaching Expiration Reminders
        if prefs.get("salah_alerts"):
            for prayer in ["fajr", "dhuhr", "asr", "maghrib", "isha"]:
                if prayer in salah_schedule:
                    p_time = salah_schedule[prayer]
                    p_dt = parse_hhmm(p_time)
                    if p_dt:
                        # Advance reminder
                        adv_m = int(prefs.get("salah_advance_mins", 10))
                        if adv_m > 0:
                            adv_dt = p_dt - timedelta(minutes=adv_m)
                            schedule.append(NotificationItem(
                                id=f"salah_advance_{prayer}",
                                title=f"{prayer.title()} in {adv_m} Minutes",
                                body=f"Prepare for {prayer.title()} prayer. Perform wudu and center your mind.",
                                category="salah",
                                priority=2,
                                scheduled_time=adv_dt.strftime("%H:%M"),
                                valid_window_minutes=adv_m,
                                action_url="/lifeos/salah",
                                sound="gentle_bell" if prefs.get("sound_enabled") else "silent",
                                icon="clock",
                                metadata={"prayer": prayer, "type": "advance_reminder"}
                            ))

            # Asr Makruh Warning (25 mins before Maghrib)
            if "maghrib" in salah_schedule:
                mag_dt = parse_hhmm(salah_schedule["maghrib"])
                if mag_dt:
                    asr_warn_dt = mag_dt - timedelta(minutes=25)
                    schedule.append(NotificationItem(
                        id="salah_asr_makruh_warning",
                        title="Asr Window Closing Soon",
                        body="Sun is setting. Safeguard your Asr prayer before the disliked window begins.",
                        category="salah",
                        priority=1,
                        scheduled_time=asr_warn_dt.strftime("%H:%M"),
                        valid_window_minutes=25,
                        action_url="/lifeos/salah",
                        sound="gentle_bell" if prefs.get("sound_enabled") else "silent",
                        icon="alert-circle",
                        metadata={"type": "makruh_warning", "prayer": "asr"}
                    ))

            # Isha Half-Night (Midnight) Boundary
            if "midnight" in salah_schedule:
                schedule.append(NotificationItem(
                    id="salah_isha_midnight_reminder",
                    title="Nisf al-Layl (Islamic Midnight)",
                    body="Preferred Isha window concluding. Complete Isha before midnight.",
                    category="salah",
                    priority=2,
                    scheduled_time=salah_schedule["midnight"],
                    valid_window_minutes=40,
                    action_url="/lifeos/salah",
                    sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                    icon="moon",
                    metadata={"type": "night_boundary", "prayer": "isha"}
                ))

        # 3. Morning Athkar
        if prefs.get("morning_athkar") and "sunrise" in salah_schedule and fatigue_score < 0.75:
            sr_dt = parse_hhmm(salah_schedule["sunrise"])
            if sr_dt:
                off_m = int(prefs.get("morning_athkar_offset_mins", 20))
                athkar_m_dt = sr_dt + timedelta(minutes=off_m)
                schedule.append(NotificationItem(
                    id="athkar_morning",
                    title="Morning Athkar & Protection",
                    body="Begin your day in divine fortress: Ayat al-Kursi and 3 Quls for peace.",
                    category="dhikr",
                    priority=2,
                    scheduled_time=athkar_m_dt.strftime("%H:%M"),
                    valid_window_minutes=90,
                    action_url="/lifeos/dhikr",
                    sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                    icon="sun",
                    metadata={"routine": "morning"}
                ))

        # 4. Daily Ayah & Hadith Reflection
        if prefs.get("daily_ayah_hadith"):
            ayah_time = prefs.get("daily_ayah_time", "08:30")
            schedule.append(NotificationItem(
                id="daily_ayah_hadith_insight",
                title="Daily Qur'an & Sahih Hadith",
                body="Today's divine verse & classical Hanafi wisdom are ready for your reflection.",
                category="tafsir",
                priority=3,
                scheduled_time=ayah_time,
                valid_window_minutes=180,
                action_url="/lifeos/tafsir",
                sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                icon="book-open",
                metadata={"type": "daily_tafsir"}
            ))

        # 5. Friday Surah Al-Kahf Reminder (Fridays only)
        if prefs.get("friday_kahf_reminder") and weekday == 4:  # Friday
            schedule.append(NotificationItem(
                id="friday_surah_kahf",
                title="Jumu'ah Mubarak: Surah Al-Kahf",
                body="Light from this Friday to the next: read Surah Al-Kahf and send Salawat on the Prophet (ﷺ).",
                category="quran",
                priority=2,
                scheduled_time="09:15",
                valid_window_minutes=300,
                action_url="/lifeos/quran?surah=18",
                sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                icon="sparkles",
                metadata={"type": "jumuah_sunnah"}
            ))

        # 6. Sunnah Fasting Reminders (Sunday evening for Monday, Wednesday evening for Thursday)
        if prefs.get("sunnah_fasting_reminders"):
            if weekday in (6, 2):  # Sunday (6) or Wednesday (2)
                fast_day = "Monday" if weekday == 6 else "Thursday"
                schedule.append(NotificationItem(
                    id=f"sunnah_fasting_{fast_day.lower()}_eve",
                    title=f"Sunnah Fast Tomorrow ({fast_day})",
                    body=f"Set your alarm for Suhoor to revive the Sunnah of fasting this {fast_day}.",
                    category="fasting",
                    priority=3,
                    scheduled_time="20:30",
                    valid_window_minutes=150,
                    action_url="/lifeos/salah",
                    sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                    icon="utensils",
                    metadata={"type": "sunnah_fasting", "fast_day": fast_day}
                ))

        # 7. Evening Athkar
        if prefs.get("evening_athkar") and "asr" in salah_schedule and fatigue_score < 0.65:
            asr_dt = parse_hhmm(salah_schedule["asr"])
            if asr_dt:
                off_m = int(prefs.get("evening_athkar_offset_mins", 30))
                athkar_e_dt = asr_dt + timedelta(minutes=off_m)
                schedule.append(NotificationItem(
                    id="athkar_evening",
                    title="Evening Athkar",
                    body="Fortify your evening with remembrance and gratitude before sunset.",
                    category="dhikr",
                    priority=2,
                    scheduled_time=athkar_e_dt.strftime("%H:%M"),
                    valid_window_minutes=90,
                    action_url="/lifeos/dhikr",
                    sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                    icon="sunset",
                    metadata={"routine": "evening"}
                ))

        # 8. Midday Mindful Dhikr & Hydration Nudges
        if prefs.get("dhikr_nudges") and fatigue_score < 0.4:
            schedule.append(NotificationItem(
                id="dhikr_micro_pause_midday",
                title="60-Second Mindful Pause",
                body="Recite 'Astaghfirullah' 10 times and take a sip of water.",
                category="dhikr",
                priority=4,
                scheduled_time="14:15",
                valid_window_minutes=45,
                action_url="/lifeos/dhikr",
                sound="silent",
                icon="heart",
                metadata={"type": "micro_pause"}
            ))

        # 9. Night Muhasabah & Evening Reflection
        if prefs.get("night_muhasabah") and fatigue_score < 0.8:
            muhasabah_time = prefs.get("night_muhasabah_time", "21:45")
            schedule.append(NotificationItem(
                id="muhasabah_night_checkin",
                title="Night Muhasabah & Stillness",
                body="Pause and review today with honesty and hope. Record slips without shame.",
                category="muhasabah",
                priority=3,
                scheduled_time=muhasabah_time,
                valid_window_minutes=120,
                action_url="/lifeos/muhasabah",
                sound="soft_chime" if prefs.get("sound_enabled") else "silent",
                icon="check-square",
                metadata={"type": "daily_reflection"}
            ))

        # Filter out notifications in quiet hours if enabled
        if prefs.get("quiet_hours_enabled"):
            q_start = prefs.get("quiet_hours_start", "23:15")
            q_end = prefs.get("quiet_hours_end", "04:30")
            filtered = []
            for item in schedule:
                # Critical salah or tahajjud alerts bypass quiet hours
                if item.priority == 1 or item.id in ("tahajjud_call", "salah_advance_fajr"):
                    filtered.append(item)
                    continue
                # Check if item falls in quiet window
                t_val = item.scheduled_time
                if q_start > q_end:  # Over midnight (e.g. 23:15 to 04:30)
                    in_quiet = (t_val >= q_start or t_val <= q_end)
                else:
                    in_quiet = (q_start <= t_val <= q_end)
                if not in_quiet:
                    filtered.append(item)
            schedule = filtered

        # Sort chronologically
        schedule.sort(key=lambda x: x.scheduled_time)

        # Apply user cap and fatigue dampening
        max_cap = int(prefs.get("max_daily", 8))
        effective_cap = max(3, int(max_cap * (1.0 - (fatigue_score * 0.4))))
        return schedule[:effective_cap]

    def log_interaction(self, notification_id: str, status: str, action: Optional[str] = None):
        if not self.db_path:
            return
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO notification_logs (id, notification_id, scheduled_time, sent_at, status, action_taken) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    f"log_{int(datetime.now().timestamp() * 1000)}",
                    notification_id,
                    datetime.now().strftime("%H:%M"),
                    int(datetime.now().timestamp() * 1000),
                    status,
                    action or ""
                )
            )
            con.commit()
            con.close()
        except Exception as e:
            print(f"[Notification Log Error] {e}")

    def evaluate_fatigue(self, history: Optional[List[Dict[str, Any]]] = None) -> float:
        if history is not None:
            if not history:
                return 0.0
            ignored = sum(1 for r in history if (r.get("status") if isinstance(r, dict) else r) in ("ignored", "dismissed"))
            return min(1.0, max(0.0, ignored / len(history)))
        if not self.db_path:
            return 0.0
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT status FROM notification_logs ORDER BY sent_at DESC LIMIT 10")
            rows = cur.fetchall()
            con.close()
            if not rows:
                return 0.0
            ignored = sum(1 for r in rows if r[0] in ("ignored", "dismissed"))
            return min(1.0, max(0.0, ignored / len(rows)))
        except Exception:
            return 0.0
