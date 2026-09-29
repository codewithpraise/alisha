# Master Product Architecture Report: Alisha AI + Islamic LifeOS

## 1. System Overview
The application unifies two distinct, non-contaminating systems within one coherent, ultra-responsive digital experience:
1. **Alisha AI**: A relationship-grounded conversational system reconstructed from authentic historical WhatsApp corpus (13,653 turns, 100 authentic voice files), powered by Groq Qwen 27B / local GGUF models.
2. **Islamic LifeOS**: A private, zero-cost, offline-first personal-development and Islamic practice engine built around astronomical prayer timing, authentic dhikr tracking, canonical Quran preservation (Tanzil verified), evidence-backed supplications, and mercy-oriented muhasabah.

---

## 2. Core Architectural Pillars

### A. Strict Knowledge Separation & Content Routing
- `IslamicContentRouter` enforces absolute separation between the conversational persona and religious sources.
- Alisha AI does not hallucinate or invent religious rulings (*fatwas*).
- Any query touching religious obligations, prayer times, rulings, or Quranic verses is mapped strictly to the verified LifeOS canonical store.
- LifeOS remains objective, evidence-based, and does not roleplay as Alisha.

### B. Astronomical Salah Calculation Engine (`salah.py`)
- **Mathematical Foundation**: Spherical trigonometry computing solar declination and equation of time with zero external dependencies.
- **Fiqh Compliance**:
  - Configurable Asr juristic calculation: Hanafi ($2\times$ shadow factor) vs. Shafi'i/Standard ($1\times$ shadow factor).
  - High-latitude and standard solar window protections.
  - Calculation of Islamic Midnight (*Nisf al-Layl*) and the Virtuous Last Third of the Night (*Thuluth al-Layl al-Akhir*).
  - Prohibited solar boundary detection (*Awqat Makruha*): Sunrise (*Tulu'*), Zenith (*Istiwa'*), and Sunset yellowing (*Isfirar*).

### C. Canonical Quran Store (`quran.py`)
- **Tanzil-Verified Integrity**: Quranic Arabic text preserved without normalization, alteration, or synthetic modification.
- **Special Virtues Engine**: Clear authenticity classifications differentiating Sahih Sunnah virtues from widely circulated weak (*Da'if*) narrations (e.g., specific wealth narrations for Surah Al-Waqi'ah).
- **Firdaus Path Indexing**: Surah Al-Mu'minun (23:1-11) character traits mapped to actionable daily habits.

### D. Adaptive Dhikr & Progression Engine (`dhikr.py`)
- Authentic daily morning/evening *athkar* with Prophetic source citations.
- Tactile circular progress counter with haptic feedback and optional auditory chime.
- Adaptive goal calibration based on rolling 7-day consistency scores.

### E. Evidence-Backed Duas Database (`duas.py`)
- Fully categorized supplications (Anxiety, Guidance, Knowledge, Health, Rizq, Character).
- Rigorous authenticity grading (Mutawatir, Sahih, Hasan) with specific chapter and hadith numbers.

### F. Mercy-Oriented Muhasabah & Akhlaq Cultivation (`muhasabah.py`)
- Private, guilt-free recovery flow based on Surah Az-Zumar (39:53).
- Focus on immediate mitigation, good replacement deeds, and practical triggers rather than broken-streak shame.
- Daily character cultivation log focusing on foundational akhlaq traits (Anger control, Guarding speech, Sabr, Shukr).

### G. SIGNAL Cognitive Challenge (`game.py`)
- 60-second working memory and response inhibition training.
- Adaptive difficulty progression with distractor filtering.
- Asynchronous "Friend Mode" challenge simulating Alisha's reflexes with personality-authentic chat reactions.

### H. Adaptive Notification Scheduler (`notifications.py`)
- Fiqh-window aware reminders (e.g. Asr makruh window warning, Isha midnight reminder, morning/evening athkar).
- Fatigue dampening algorithm: monitors dismiss/ignore patterns and throttles frequency to prevent notification spam.

---

## 3. Technology Stack & Integration
- **Web App**: Next.js 15, React 19, Tailwind CSS v4, Lucide Icons, PWA Service Worker offline caching.
- **API Server**: Zero-dependency Python standard library HTTP server (`services/api/server.py`) running on port 8000.
- **Mobile / Android**: Native Kotlin architecture (`apps/android/app/src/main/java/com/friendos/alishabubbzieee/core/lifeos/`) with local astronomical computation and boundary routing.
- **Database**: SQLite with FTS5 for local-first storage.

---

## 4. Verification & Quality Gates
- `tests/test_lifeos_all_engines.py`: Complete unit tests covering all 9 engines and modules.
- `tests/test_all_phases.py`: Full end-to-end multi-phase validation including Phase 9 (Islamic LifeOS).
- Zero paid API dependencies; 100% offline-first capable.
