"""
Salah Calculator (Astronomical & Fiqh Engine)
Calculates Islamic prayer times locally using standard spherical trigonometry.
Zero paid APIs. Supports Hanafi / Standard madhhab, prohibited solar windows,
Makruh windows, dynamic solar arc graphs, and precise countdown calculations.
Default: Islamabad, Pakistan (Lat 33.6844, Lng 73.0479, PKT UTC+5).
"""

import math
from datetime import datetime, date, time, timedelta
from typing import Dict, Any, Optional, Tuple, List

# Standard Calculation Conventions: (Fajr angle, Isha angle or minutes)
METHODS = {
    "karachi": {"name": "University of Islamic Sciences, Karachi", "fajr_angle": 18.0, "isha_angle": 18.0},
    "mwl": {"name": "Muslim World League", "fajr_angle": 18.0, "isha_angle": 17.0},
    "isna": {"name": "Islamic Society of North America (ISNA)", "fajr_angle": 15.0, "isha_angle": 15.0},
    "umm_al_qura": {"name": "Umm Al-Qura University, Makkah", "fajr_angle": 18.5, "isha_interval_min": 90},
}

class PrayerWindow:
    VALID = "valid"
    PREFERRED = "preferred"
    MAKRUH_LATE = "makruh_late"
    PROHIBITED = "prohibited"
    EXPIRED = "expired"

class SalahCalculator:
    """Astronomical prayer calculation engine without external API dependency."""

    def __init__(self, lat: float = 33.6844, lng: float = 73.0479, timezone_offset: float = 5.0,
                 madhhab: str = "hanafi", method: str = "karachi"):
        self.lat = lat
        self.lng = lng
        self.tz_offset = timezone_offset
        self.madhhab = madhhab.lower()  # "hanafi" or "shafii"
        self.method = method.lower() if method.lower() in METHODS else "karachi"

    def _julian_date(self, year: int, month: int, day: int) -> float:
        if month <= 2:
            year -= 1
            month += 12
        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)
        return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5

    def _sun_coordinates(self, jd: float) -> Tuple[float, float, float]:
        """Calculates solar declination and equation of time (in minutes)."""
        d = jd - 2451545.0
        g = (357.529 + 0.98560028 * d) % 360.0
        q = (280.459 + 0.98564736 * d) % 360.0
        l = (q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))) % 360.0
        e = 23.439 - 0.00000036 * d

        ra = (math.degrees(math.atan2(math.cos(math.radians(e)) * math.sin(math.radians(l)), math.cos(math.radians(l)))) / 15.0) % 24.0

        decl = math.degrees(math.asin(math.sin(math.radians(e)) * math.sin(math.radians(l))))
        eqt = (q / 15.0) - ra
        eqt = ((eqt + 12.0) % 24.0) - 12.0
        return decl, eqt * 60.0, l

    def _time_diff_for_angle(self, angle: float, decl: float) -> Optional[float]:
        """Calculates hour angle difference in hours for a given sun depression/elevation angle."""
        lat_r = math.radians(self.lat)
        dec_r = math.radians(decl)
        ang_r = math.radians(angle)
        cos_ha = (math.sin(ang_r) - math.sin(lat_r) * math.sin(dec_r)) / (math.cos(lat_r) * math.cos(dec_r))
        if cos_ha < -1.0 or cos_ha > 1.0:
            return None
        return math.degrees(math.acos(cos_ha)) / 15.0

    def _asr_shadow_factor(self) -> float:
        return 2.0 if self.madhhab == "hanafi" else 1.0

    def calculate_times(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Calculates exact prayer times and solar boundaries for target date."""
        if target_date is None:
            target_date = date.today()

        jd = self._julian_date(target_date.year, target_date.month, target_date.day)
        decl, eqt_min, _ = self._sun_coordinates(jd)

        # Midday (Solar Transit / Istiwa/Zawal center) in UTC+tz hours
        transit = 12.0 + (self.tz_offset - self.lng / 15.0) - (eqt_min / 60.0)

        # Sunrise & Sunset (center of sun 0.833 degrees below horizon due to refraction)
        ha_sunrise = self._time_diff_for_angle(-0.833, decl)
        if ha_sunrise is None:
            ha_sunrise = 6.0

        sunrise_h = transit - ha_sunrise
        sunset_h = transit + ha_sunrise

        # Fajr (true dawn)
        m_params = METHODS[self.method]
        fajr_angle = m_params["fajr_angle"]
        ha_fajr = self._time_diff_for_angle(-fajr_angle, decl) or (ha_sunrise + 1.5)
        fajr_h = transit - ha_fajr

        # Dhuhr (technically slightly past zenith, typically +1 to +2 minutes)
        dhuhr_h = transit + (2.0 / 60.0)

        # Asr
        lat_r = math.radians(self.lat)
        dec_r = math.radians(decl)
        noon_angle = math.pi / 2 - abs(lat_r - dec_r)
        noon_shadow = 1.0 / math.tan(noon_angle) if noon_angle > 0 else 0.0
        asr_factor = self._asr_shadow_factor()
        asr_angle_rad = math.atan(1.0 / (asr_factor + noon_shadow))
        ha_asr = self._time_diff_for_angle(math.degrees(asr_angle_rad), decl) or 3.0
        asr_h = transit + ha_asr

        # Maghrib (sunset)
        maghrib_h = sunset_h

        # Isha
        if "isha_angle" in m_params:
            ha_isha = self._time_diff_for_angle(-m_params["isha_angle"], decl) or (ha_sunrise + 1.5)
            isha_h = transit + ha_isha
        else:
            isha_h = maghrib_h + (m_params.get("isha_interval_min", 90) / 60.0)

        # Night markers
        night_duration = (fajr_h + 24.0) - sunset_h
        midnight_h = sunset_h + (night_duration / 2.0)
        last_third_h = sunset_h + (night_duration * 2.0 / 3.0)

        def _fmt(val_h: float) -> str:
            norm = (val_h + 24) % 24
            hours = int(norm)
            minutes = int((norm - hours) * 60)
            return f"{hours:02d}:{minutes:02d}"

        # Prohibited Windows:
        tulu_end_h = sunrise_h + (15.0 / 60.0)      # Tulu' ends ~15m post sunrise
        istiwa_start_h = transit - (10.0 / 60.0)    # Istiwa begins ~10m before transit
        ghurub_start_h = sunset_h - (20.0 / 60.0)   # Isfirar begins ~20m before sunset

        return {
            "date": target_date.isoformat(),
            "method": m_params["name"],
            "madhhab": self.madhhab,
            "city": "Islamabad, Pakistan",
            "coordinates": {"lat": self.lat, "lng": self.lng, "tz": self.tz_offset},
            "schedule": {
                "fajr": _fmt(fajr_h),
                "sunrise": _fmt(sunrise_h),
                "ishraq_duha": _fmt(tulu_end_h),
                "dhuhr": _fmt(dhuhr_h),
                "asr": _fmt(asr_h),
                "maghrib": _fmt(maghrib_h),
                "isha": _fmt(isha_h),
                "midnight": _fmt(midnight_h),
                "last_third": _fmt(last_third_h)
            },
            "prohibited_windows": {
                "sunrise_prohibited": f"{_fmt(sunrise_h)} - {_fmt(tulu_end_h)}",
                "zenith_prohibited": f"{_fmt(istiwa_start_h)} - {_fmt(transit)}",
                "sunset_prohibited": f"{_fmt(ghurub_start_h)} - {_fmt(sunset_h)}"
            },
            "makruh_notes": {
                "asr_delay": f"Delaying Asr past {_fmt(ghurub_start_h)} (Isfirar) is Makruh Tahrimi.",
                "isha_delay": f"Delaying Isha past Midnight ({_fmt(midnight_h)}) is Makruh Tanzihi."
            },
            "raw_hours": {
                "fajr": fajr_h,
                "sunrise": sunrise_h,
                "tulu_end": tulu_end_h,
                "istiwa_start": istiwa_start_h,
                "transit": transit,
                "dhuhr": dhuhr_h,
                "asr": asr_h,
                "ghurub_start": ghurub_start_h,
                "sunset": sunset_h,
                "maghrib": maghrib_h,
                "isha": isha_h,
                "midnight": midnight_h,
                "last_third": last_third_h
            }
        }

    def calculate_prayer_times(self, target_date: Optional[date] = None) -> Dict[str, str]:
        """Returns the prayer time schedule mapping (fajr, sunrise, dhuhr, asr, etc.)."""
        full = self.calculate_times(target_date)
        return full.get("schedule", {})

    def get_current_status(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        """Returns the current prayer state, remaining time, window category, and next prayer."""
        if now is None:
            now = datetime.now()

        times = self.calculate_times(now.date())
        raw = times["raw_hours"]
        now_h = now.hour + now.minute / 60.0 + now.second / 3600.0

        fajr_h = raw["fajr"]
        sunrise_h = raw["sunrise"]
        tulu_end_h = raw["tulu_end"]
        istiwa_start_h = raw["istiwa_start"]
        transit_h = raw["transit"]
        dhuhr_h = raw["dhuhr"]
        asr_h = raw["asr"]
        ghurub_start_h = raw["ghurub_start"]
        sunset_h = raw["sunset"]
        maghrib_h = raw["maghrib"]
        isha_h = raw["isha"]
        midnight_h = raw["midnight"]
        last_third_h = raw["last_third"]

        def _fmt_dur(h: float) -> str:
            total_sec = max(0, int(h * 3600))
            hrs = total_sec // 3600
            mins = (total_sec % 3600) // 60
            secs = total_sec % 60
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"

        def _fmt_friendly(h: float) -> str:
            total_sec = max(0, int(h * 3600))
            hrs = total_sec // 3600
            mins = (total_sec % 3600) // 60
            if hrs > 0:
                return f"{hrs} hr {mins} min"
            return f"{mins} min"

        current_prayer = "Duha / Ishraq"
        state = PrayerWindow.PREFERRED
        window_total_h = 4.0
        elapsed_h = 1.0
        remaining_h = 2.0
        next_prayer = "Dhuhr"
        next_in_h = 2.0
        status_message = "Duha (Chasht) time is active."
        sun_phase = "Morning Sun"

        # 1. FAJR (Dawn until Sunrise)
        if fajr_h <= now_h < sunrise_h:
            current_prayer = "Fajr"
            window_total_h = max(0.1, sunrise_h - fajr_h)
            elapsed_h = now_h - fajr_h
            remaining_h = max(0.0, sunrise_h - now_h)
            next_prayer = "Sunrise / Ishraq"
            next_in_h = remaining_h
            state = PrayerWindow.MAKRUH_LATE if remaining_h < 0.25 else PrayerWindow.VALID
            status_message = f"Fajr time is active. Valid for {_fmt_friendly(remaining_h)} until Sunrise."
            sun_phase = "Dawn Twilight"

        # 2. SUNRISE / TULU' (Prohibited: Sunrise until ~15m post sunrise)
        elif sunrise_h <= now_h < tulu_end_h:
            current_prayer = "Sunrise (Tulu')"
            state = PrayerWindow.PROHIBITED
            window_total_h = max(0.1, tulu_end_h - sunrise_h)
            elapsed_h = now_h - sunrise_h
            remaining_h = max(0.0, tulu_end_h - now_h)
            next_prayer = "Ishraq / Duha"
            next_in_h = remaining_h
            status_message = f"Prohibited solar window (Sunrise). Voluntary salah begins in {_fmt_friendly(remaining_h)}."
            sun_phase = "Sunrise"

        # 3. DUHA / ISHRAQ / CHASHT (Morning: ~15m post sunrise until Istiwa)
        elif tulu_end_h <= now_h < istiwa_start_h:
            current_prayer = "Duha / Ishraq (Chasht)"
            state = PrayerWindow.PREFERRED
            window_total_h = max(0.1, istiwa_start_h - tulu_end_h)
            elapsed_h = now_h - tulu_end_h
            remaining_h = max(0.0, istiwa_start_h - now_h)
            next_prayer = "Dhuhr"
            next_in_h = max(0.0, dhuhr_h - now_h)
            status_message = f"Duha & Ishraq (Chasht) window active. Highly meritorious voluntary prayer. Next Fard (Dhuhr) in {_fmt_friendly(next_in_h)}."
            sun_phase = "Morning Sun"

        # 4. ZENITH / ISTIWA (Prohibited: ~10m before transit until Zawal)
        elif istiwa_start_h <= now_h < transit_h:
            current_prayer = "Zenith (Istiwa / Zawal)"
            state = PrayerWindow.PROHIBITED
            window_total_h = max(0.1, transit_h - istiwa_start_h)
            elapsed_h = now_h - istiwa_start_h
            remaining_h = max(0.0, transit_h - now_h)
            next_prayer = "Dhuhr"
            next_in_h = max(0.0, dhuhr_h - now_h)
            status_message = f"Prohibited solar zenith window. Voluntary salah forbidden. Dhuhr begins in {_fmt_friendly(next_in_h)}."
            sun_phase = "Solar Zenith"

        # 5. DHUHR (Zawal until Asr)
        elif dhuhr_h <= now_h < asr_h:
            current_prayer = "Dhuhr"
            state = PrayerWindow.VALID
            window_total_h = max(0.1, asr_h - dhuhr_h)
            elapsed_h = now_h - dhuhr_h
            remaining_h = max(0.0, asr_h - now_h)
            next_prayer = "Asr"
            next_in_h = remaining_h
            status_message = f"Dhuhr time is active. Valid for {_fmt_friendly(remaining_h)} until Asr."
            sun_phase = "Afternoon Sun"

        # 6. ASR (Asr until Isfirar)
        elif asr_h <= now_h < ghurub_start_h:
            current_prayer = "Asr"
            state = PrayerWindow.VALID
            window_total_h = max(0.1, sunset_h - asr_h)
            elapsed_h = now_h - asr_h
            remaining_h = max(0.0, sunset_h - now_h)
            next_prayer = "Maghrib"
            next_in_h = remaining_h
            status_message = f"Asr time is active. Preferred performance before Isfirar ({times['schedule']['asr']} - {times['prohibited_windows']['sunset_prohibited'].split(' - ')[0]})."
            sun_phase = "Late Afternoon"

        # 7. ASR ISFIRAR (Makruh late window before sunset)
        elif ghurub_start_h <= now_h < sunset_h:
            current_prayer = "Asr (Isfirar)"
            state = PrayerWindow.MAKRUH_LATE
            window_total_h = max(0.1, sunset_h - ghurub_start_h)
            elapsed_h = now_h - ghurub_start_h
            remaining_h = max(0.0, sunset_h - now_h)
            next_prayer = "Maghrib"
            next_in_h = remaining_h
            status_message = f"Makruh late window for Asr. Sunset in {_fmt_friendly(remaining_h)}. Pray immediately."
            sun_phase = "Sunset Glow"

        # 8. MAGHRIB (Sunset until Isha)
        elif maghrib_h <= now_h < isha_h:
            current_prayer = "Maghrib"
            state = PrayerWindow.VALID
            window_total_h = max(0.1, isha_h - maghrib_h)
            elapsed_h = now_h - maghrib_h
            remaining_h = max(0.0, isha_h - now_h)
            next_prayer = "Isha"
            next_in_h = remaining_h
            status_message = f"Maghrib time is active. Valid for {_fmt_friendly(remaining_h)} until Isha."
            sun_phase = "Dusk Twilight"

        # 9. ISHA & NIGHT / TAHAJJUD
        else:
            if now_h >= isha_h:
                window_total_h = max(0.1, (fajr_h + 24.0) - isha_h)
                elapsed_h = now_h - isha_h
                remaining_h = max(0.0, (fajr_h + 24.0) - now_h)
                next_in_h = remaining_h
            else:
                window_total_h = max(0.1, (fajr_h + 24.0) - isha_h)
                elapsed_h = (now_h + 24.0) - isha_h
                remaining_h = max(0.0, fajr_h - now_h)
                next_in_h = remaining_h

            next_prayer = "Fajr"
            current_prayer = "Isha"
            sun_phase = "Night Sky"

            # Check Tahajjud / Last Third of the Night
            is_last_third = (now_h >= last_third_h and now_h < 24.0) or (last_third_h > 24.0 and (now_h + 24.0) >= last_third_h) or (now_h < fajr_h and now_h >= (last_third_h - 24.0))
            is_past_midnight = (now_h >= midnight_h and now_h < 24.0) or (midnight_h > 24.0 and (now_h + 24.0) >= midnight_h) or (now_h < fajr_h and now_h >= (midnight_h - 24.0))

            if is_last_third:
                current_prayer = "Tahajjud / Qiyam al-Layl"
                state = PrayerWindow.PREFERRED
                status_message = f"Last Third of the Night (Tahajjud) active! Divine descent of mercy. Fajr in {_fmt_friendly(next_in_h)}."
                sun_phase = "Pre-Dawn Tahajjud"
            elif is_past_midnight:
                state = PrayerWindow.MAKRUH_LATE
                status_message = f"Isha delayed past midnight (Makruh Tanzihi). Fajr in {_fmt_friendly(next_in_h)}."
            else:
                state = PrayerWindow.VALID
                status_message = f"Isha time is active. Valid for {_fmt_friendly(remaining_h)} until Fajr."

        progress_pct = min(100.0, max(0.0, (elapsed_h / window_total_h) * 100.0)) if window_total_h > 0 else 0.0

        is_past_midnight_val = bool((now_h >= midnight_h and now_h < 24.0) or (midnight_h > 24.0 and (now_h + 24.0) >= midnight_h) or (now_h < fajr_h and now_h >= (midnight_h - 24.0)))
        is_last_third_val = bool((now_h >= last_third_h and now_h < 24.0) or (last_third_h > 24.0 and (now_h + 24.0) >= last_third_h) or (now_h < fajr_h and now_h >= (last_third_h - 24.0)))

        # Timeline items for Visual Timeline Graph
        timeline = [
            {"id": "fajr", "name": "Fajr", "time": times["schedule"]["fajr"], "status": "passed" if now_h >= sunrise_h else ("active" if fajr_h <= now_h < sunrise_h else "upcoming")},
            {"id": "sunrise", "name": "Sunrise", "time": times["schedule"]["sunrise"], "status": "passed" if now_h >= tulu_end_h else ("active" if sunrise_h <= now_h < tulu_end_h else "upcoming")},
            {"id": "duha", "name": "Duha (Chasht)", "time": times["schedule"]["ishraq_duha"], "status": "passed" if now_h >= istiwa_start_h else ("active" if tulu_end_h <= now_h < istiwa_start_h else "upcoming")},
            {"id": "dhuhr", "name": "Dhuhr", "time": times["schedule"]["dhuhr"], "status": "passed" if now_h >= asr_h else ("active" if dhuhr_h <= now_h < asr_h else "upcoming")},
            {"id": "asr", "name": "Asr", "time": times["schedule"]["asr"], "status": "passed" if now_h >= sunset_h else ("active" if asr_h <= now_h < sunset_h else "upcoming")},
            {"id": "maghrib", "name": "Maghrib", "time": times["schedule"]["maghrib"], "status": "passed" if now_h >= isha_h else ("active" if maghrib_h <= now_h < isha_h else "upcoming")},
            {"id": "isha", "name": "Isha", "time": times["schedule"]["isha"], "status": "active" if (now_h >= isha_h or now_h < fajr_h) else "upcoming"},
            {"id": "midnight", "name": "Midnight", "time": times["schedule"]["midnight"], "status": "passed" if is_past_midnight_val else "upcoming"},
            {"id": "last_third", "name": "Tahajjud", "time": times["schedule"]["last_third"], "status": "active" if is_last_third_val else "upcoming"},
        ]

        return {
            "current_prayer": current_prayer,
            "state": state,
            "status_message": status_message,
            "sun_phase": sun_phase,
            "valid_duration_formatted": _fmt_friendly(window_total_h),
            "valid_duration_seconds": int(window_total_h * 3600),
            "elapsed_formatted": _fmt_friendly(elapsed_h),
            "elapsed_seconds": int(elapsed_h * 3600),
            "remaining_formatted": _fmt_dur(remaining_h),
            "remaining_friendly": _fmt_friendly(remaining_h),
            "remaining_seconds": max(0, int(remaining_h * 3600)),
            "progress_pct": round(progress_pct, 1),
            "next_prayer": next_prayer,
            "next_in_formatted": _fmt_dur(next_in_h),
            "next_in_friendly": _fmt_friendly(next_in_h),
            "next_in_seconds": max(0, int(next_in_h * 3600)),
            "schedule": times["schedule"],
            "prohibited_windows": times["prohibited_windows"],
            "makruh_notes": times["makruh_notes"],
            "city": times["city"],
            "madhhab": self.madhhab,
            "method": times["method"],
            "timeline": timeline
        }
