"""
Islamic Content Router & Knowledge Boundary Guard
Enforces strict separation between conversational AI and verified Islamic jurisprudence / sources.
Prevents hallucination of religious rulings, hadiths, or Quranic texts.
Routes queries to verified repositories with explicit citation levels.
"""

from typing import Dict, Any, Optional
from .salah import SalahCalculator
from .quran import QuranEngine, SPECIAL_VIRTUE_METADATA
from .duas import DuasDatabase

class IslamicContentRouter:
    """Routes queries to verified Islamic sources and preserves strict knowledge boundaries."""

    def __init__(self):
        self.quran = QuranEngine()
        self.duas = DuasDatabase()
        self.salah = SalahCalculator()

    def route_query(self, user_query: str) -> Dict[str, Any]:
        """
        Classifies query intent and retrieves canonical, source-grounded answers.
        """
        q = user_query.lower()

        # Fiqh ruling boundaries (LifeOS does not issue fatwas)
        if any(term in q for term in ["fast valid", "valid by mistake", "fatwa", "halal or haram", "is eating during fast"]):
            return {
                "type": "fiqh_boundary",
                "domain": "fiqh_boundary",
                "authority": "Scholarly Boundary",
                "source_type": "LifeOS Advisory",
                "message": "LifeOS provides authentic sources and structure, not independent fatwas. Consult qualified scholars for fiqh rulings.",
                "ruling_notice": "For religious rulings, always refer to qualified scholarly consensus."
            }

        # Fiqh & Salah timing
        if any(term in q for term in ["salah", "prayer", "fajr", "dhuhr", "asr", "maghrib", "isha", "prohibited", "makruh", "zawal", "zenith"]):
            status = self.salah.get_current_status()
            return {
                "domain": "fiqh_salah",
                "authority": "Astronomical calculation & Hanafi/Standard Fiqh rules",
                "source_type": "Fiqh Engine",
                "content": status,
                "ruling_notice": "Salah times calculated via local spherical geometry. Boundary rules derived from classical Hanafi / Shafi'i fiqh."
            }

        # Surah Al-Waqi'ah or specific special virtues
        if "waqiah" in q or "waqi'ah" in q or "surah 56" in q:
            waqiah_data = self.quran.get_surah(56)
            special_meta = SPECIAL_VIRTUE_METADATA.get("al_waqiah_night")
            return {
                "domain": "quran_surah",
                "authority": "Tanzil Verified Quran",
                "source_type": "Qur'an / Hadith Evaluation",
                "content": waqiah_data,
                "virtue_ruling": special_meta,
                "ruling_notice": "Quranic text is preserved verbatim from Tanzil. Hadith claims on wealth prevention are documented as weak."
            }

        # Surah Al-Mulk
        if "mulk" in q or "surah 67" in q:
            mulk_data = self.quran.get_surah(67)
            special_meta = SPECIAL_VIRTUE_METADATA.get("al_mulk_night")
            return {
                "domain": "quran_surah",
                "authority": "Tanzil Verified Quran",
                "source_type": "Qur'an / Sahih Hadith",
                "content": mulk_data,
                "virtue_ruling": special_meta,
                "ruling_notice": "Established Sunnah for evening recitation before sleep (Tirmidhi 2891)."
            }

        # Duas & Supplications
        if any(term in q for term in ["dua", "supplication", "rizq", "anxiety", "knowledge", "forgiveness"]):
            results = self.duas.search(user_query)
            if not results:
                results = self.duas.get_all()[:3]
            return {
                "domain": "duas",
                "authority": "Sahih/Hasan Hadith & Qur'anic Duas",
                "source_type": "Curated Authentic Database",
                "content": results,
                "ruling_notice": "Authentic citations provided for every dua. Authenticity grades are verified."
            }

        # General / Reflection
        return {
            "domain": "general_reflection",
            "authority": "Personal Reflection & Growth",
            "source_type": "LifeOS Growth Engine",
            "content": {"message": "Cultivate consistency in fard obligations, dhikr, and virtuous character."},
            "ruling_notice": "For religious rulings, always refer to qualified scholarly consensus."
        }

    def is_religious_query(self, user_query: str) -> bool:
        """Determines if a query pertains to Islamic practices, Quran, Hadith, Salah, or Duas."""
        import re
        q = user_query.lower()
        religious_terms = [
            "salah", "prayer", "fajr", "dhuhr", "asr", "maghrib", "isha", "namaz",
            "prohibited", "makruh", "zawal", "zenith", "qibla",
            "quran", "surah", "ayah", "ayat", "tafsir", "hadith", "sunnah",
            "dua", "duas", "supplication", "dhikr", "zikr", "tasbih", "istighfar",
            "allah", "prophet", "islam", "halal", "haram", "hanafi", "shafii",
            "fasting", "ramadan", "zakat", "hajj", "umrah", "wudu", "ghusl"
        ]
        return any(re.search(r'\b' + re.escape(term) + r'\b', q) for term in religious_terms)
