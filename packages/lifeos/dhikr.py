"""
Dhikr Engine
Manages authentic adhkar, physical counter logic, sessions,
and intelligent weekly adaptive goal progression (consistency over volume).
Includes exhaustive linguistic breakdowns, spiritual significance, and scholar-recommended
adhkar for wealth, well-being, security, health, character, and morals.
"""

import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

DEFAULT_ADHKAR = [
    {
        "id": "istighfar",
        "arabic": "أَسْتَغْفِرُ اللَّهَ وَأَتُوبُ إِلَيْهِ",
        "transliteration": "Astaghfirullaha wa atubu ilayh",
        "translation": "I seek the forgiveness of Allah and I repent unto Him.",
        "target_daily": 100,
        "benefits_category": "Wealth, Well-being & Forgiveness",
        "virtue": "The Prophet (ﷺ) sought forgiveness over 70 to 100 times daily (Sahih al-Bukhari 6307).",
        "category": "istighfar",
        "hadith_reference": "Sahih al-Bukhari (6307); Sahih Muslim (2702)",
        "linguistic_breakdown": [
            {"word": "أَسْتَغْفِرُ (Astaghfiru)", "meaning": "I seek forgiveness / shielding", "root_concept": "From Gh-F-R (غ-ف-ر) meaning the 'Mighfar' (a battle helmet that both conceals and physically protects from lethal blows). It asks Allah to both cover the sin and shield one from its toxic consequences."},
            {"word": "اللَّهَ (Allah)", "meaning": "Allah, the Sole Object of worship and adoration", "root_concept": "The All-Encompassing Divine Name uniting all Majesty and Mercy."},
            {"word": "وَأَتُوبُ (wa atubu)", "meaning": "And I turn / return in active repentance", "root_concept": "From T-W-B (ت-و-ب) meaning to physically turn back from a detour and return home to the Straight Path."},
            {"word": "إِلَيْهِ (ilayh)", "meaning": "Unto Him exclusively", "root_concept": "Total surrender and direct return without intermediary."}
        ],
        "theological_significance": "Istighfar cleanses the spiritual rust (Rayn) from the mirror of the heart. In Surah Nuh (71:10-12) and Surah Hud (11:52), Allah explicitly links continuous Istighfar with economic expansion, rain, sustained wealth, children, gardens, and physical vitality.",
        "psychological_spiritual_effect": "Dissolves subconscious guilt and self-sabotage. Releases mental constriction and replaces anxiety with divine peace and renewed motivation.",
        "khushu_visualization": "With each count, visualize a dark speck of distraction or error dissolving in an ocean of infinite Light, feeling your burden lifted by the Forgiver."
    },
    {
        "id": "subhanallah",
        "arabic": "سُبْحَانَ اللَّهِ",
        "transliteration": "SubhanAllah",
        "translation": "Glory be to Allah (Far removed is He from any imperfection or flaw).",
        "target_daily": 100,
        "benefits_category": "Inner Peace & Divine Awe",
        "virtue": "Whoever says it 100 times, 1,000 good deeds are recorded or 1,000 sins wiped away (Sahih Muslim 2698).",
        "category": "tasbih",
        "hadith_reference": "Sahih Muslim (2698); Sahih al-Bukhari (6405)",
        "linguistic_breakdown": [
            {"word": "سُبْحَانَ (Subhan)", "meaning": "Exalted, flawless, swimming far above defect", "root_concept": "From S-B-H (س-ب-ح) meaning swift, graceful swimming above water. Declares Allah is infinitely elevated above any defect, injustice, tiredness, or human limitation."},
            {"word": "اللَّهِ (Allah)", "meaning": "Allah", "root_concept": "The Absolute Reality."}
        ],
        "theological_significance": "Connects directly with the Divine Names Al-Quddus (The Pure) and As-Salam (The Source of Peace). It removes any lingering grievance or doubt about Allah's decree and timing.",
        "psychological_spiritual_effect": "Frees the mind from bitterness and cynicism. Instills deep awe and tranquility by reminding the soul that everything in the cosmos operates under flawless divine wisdom.",
        "khushu_visualization": "Contemplate the vast galaxies rotating in perfect harmony, recognizing that the Creator of this universe is infinitely beyond any flaw or oversight."
    },
    {
        "id": "alhamdulillah",
        "arabic": "الْحَمْدُ لِلَّهِ",
        "transliteration": "Alhamdulillah",
        "translation": "All praise, adoration, and gratitude belong solely to Allah.",
        "target_daily": 100,
        "benefits_category": "Wealth & Increase in Blessings",
        "virtue": "Fills the cosmic scale of deeds (Mizan) to overflowing (Sahih Muslim 223).",
        "category": "tahmeed",
        "hadith_reference": "Sahih Muslim (223)",
        "linguistic_breakdown": [
            {"word": "الْ (Al)", "meaning": "The (Definite article of universality)", "root_concept": "Indicates that every conceivable form, degree, and category of praise in existence belongs solely to Allah."},
            {"word": "حَمْدُ (Hamd)", "meaning": "Praise joined with profound love and awe", "root_concept": "Deeper than 'Shukr' (gratitude for a specific favor) and 'Madh' (praise of beauty). Hamd is praise for Allah's intrinsic perfection combined with adoration."},
            {"word": "لِلَّهِ (Lillah)", "meaning": "Belongs to Allah alone", "root_concept": "Exclusivity of ownership and origin."}
        ],
        "theological_significance": "Activates the supreme spiritual law of expansion: 'If you are grateful, I will surely increase you' (Surah Ibrahim 14:7). Gratitude anchors existing blessings and invites fresh divine abundance.",
        "psychological_spiritual_effect": "Shifts neurobiology from scarcity, comparison, and fear into abundance, celebration, and contentment. The ultimate antidote to depression and envy.",
        "khushu_visualization": "Reflect on the breath entering your lungs, the safety of your shelter, and the thousands of unearned gifts sustaining your life right now."
    },
    {
        "id": "allahu_akbar",
        "arabic": "اللَّهُ أَكْبَرُ",
        "transliteration": "Allahu Akbar",
        "translation": "Allah is Greater (than anything that exists, was, or will be).",
        "target_daily": 100,
        "benefits_category": "Courage, Security & Perspective",
        "virtue": "Beloved words of remembrance that plant trees in Paradise (Tirmidhi 3465).",
        "category": "takbeer",
        "hadith_reference": "Jami' at-Tirmidhi (3465)",
        "linguistic_breakdown": [
            {"word": "اللَّهُ (Allah)", "meaning": "The Supreme God", "root_concept": "The All-Powerful Creator."},
            {"word": "أَكْبَرُ (Akbar)", "meaning": "Greater (Comparative left open-ended)", "root_concept": "In Arabic grammar, 'Akbar' without 'min' (than X) leaves the comparison open: Allah is greater than whatever problem, king, fear, or worldly obstacle you are facing."}
        ],
        "theological_significance": "Proclaims Allah's absolute supremacy (Kibriya') over the entire creation. Shrinks towering earthly anxieties into minuscule particles in the light of Divine Omnipotence.",
        "psychological_spiritual_effect": "Empowers the heart with unshakable courage and perspective. Eliminates fear of people, fear of future outcomes, and paralyzing anxiety.",
        "khushu_visualization": "See all worldly giants, debts, illnesses, and uncertainties diminishing into tiny specks beneath the infinite Majesty and Power of Allah."
    },
    {
        "id": "la_hawla",
        "arabic": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
        "transliteration": "La hawla wa la quwwata illa billah",
        "translation": "There is no power to avoid harm nor strength to do good except through Allah.",
        "target_daily": 100,
        "benefits_category": "Energy, Burnout Relief & Reliance",
        "virtue": "A treasure from beneath the Throne of the Most Merciful and a gate to Jannah (Sahih al-Bukhari 4205).",
        "category": "reliance",
        "hadith_reference": "Sahih al-Bukhari (4205); Sahih Muslim (2704)",
        "linguistic_breakdown": [
            {"word": "لَا حَوْلَ (La hawla)", "meaning": "No shift, change, or protection from evil", "root_concept": "From H-W-L (ح-و-ل) meaning transformation or moving from one state to another. You cannot turn away from sin or calamity by your own wit."},
            {"word": "وَلَا قُوَّةَ (wa la quwwata)", "meaning": "And no inner strength or capacity", "root_concept": "You possess zero self-generated ability to produce excellence, wealth, or piety without divine enablement."},
            {"word": "إِلَّا بِاللَّهِ (illa billah)", "meaning": "Except by and through Allah", "root_concept": "Absolute dependence upon the Unseen Sustainer."}
        ],
        "theological_significance": "The ultimate surrender of human illusion of control. It transfers all reliance from the weak ego (Nafs) to the infinite Power of Al-Qawiyy Al-Matin.",
        "psychological_spiritual_effect": "Instant relief from chronic fatigue, burnout, overwhelm, and impostor syndrome. Grants superhuman resilience and divine assistance (Tawfiq).",
        "khushu_visualization": "Feel yourself relinquishing all heavy personal control and handing your entire existence into the gentle, all-capable hands of your Creator."
    },
    {
        "id": "subhanallahi_wa_bihamdihi_azeem",
        "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ ، سُبْحَانَ اللَّهِ الْعَظِيمِ",
        "transliteration": "SubhanAllahi wa bihamdihi, SubhanAllahil 'Azeem",
        "translation": "Glory be to Allah and His is the praise; Glory be to Allah, the Tremendous.",
        "target_daily": 100,
        "benefits_category": "Character, Morals & Scales of Goodness",
        "virtue": "Two phrases light on the tongue, beloved to the Most Merciful, heavy on the Scales (Sahih al-Bukhari 6682).",
        "category": "tasbih",
        "hadith_reference": "Sahih al-Bukhari (6682); Sahih Muslim (2694)",
        "linguistic_breakdown": [
            {"word": "سُبْحَانَ اللَّهِ (SubhanAllah)", "meaning": "Flawless is Allah", "root_concept": "Negation of all imperfections."},
            {"word": "وَبِحَمْدِهِ (wa bihamdihi)", "meaning": "And with His praise", "root_concept": "Affirmation of all beauties and perfections."},
            {"word": "الْعَظِيمِ (Al-'Azeem)", "meaning": "The Tremendous, Incomparably Vast", "root_concept": "Derived from 'Azm' (bone / core strength). Allah's greatness is substantial, enduring, and infinitely commanding."}
        ],
        "theological_significance": "Combines Tanzih (transcendence) and Ithbat (affirmation of beauty) with Al-Azamah (majesty). Beloved to Ar-Rahman because it encapsulates the essence of cosmic worship.",
        "psychological_spiritual_effect": "Softens hard hearts, refines speech, cultivates humility, and aligns the personal character with divine nobility.",
        "khushu_visualization": "Feel each word carrying immense golden weight, tipping the balance of your soul toward eternal light and moral refinement."
    },
    {
        "id": "hasbunallah",
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "transliteration": "HasbunAllahu wa ni'mal wakeel",
        "translation": "Allah is sufficient for us, and He is the best Disposer of affairs.",
        "target_daily": 100,
        "benefits_category": "Security, Crisis & Fear Protection",
        "virtue": "The phrase recited by Ibrahim (AS) when thrown into fire, and by Muhammad (ﷺ) when facing overwhelming armies (Sahih al-Bukhari 4563).",
        "category": "protection",
        "hadith_reference": "Surah Ali 'Imran (3:173); Sahih al-Bukhari (4563)",
        "linguistic_breakdown": [
            {"word": "حَسْبُنَا (Hasbuna)", "meaning": "Our complete sufficiency", "root_concept": "From H-S-B (ح-س-ب). Allah is wholly enough; no additional protector or guarantor is needed."},
            {"word": "اللَّهُ (Allah)", "meaning": "Allah", "root_concept": "The All-Sufficient (Al-Hasib)."},
            {"word": "وَنِعْمَ (wa ni'ma)", "meaning": "And how excellent!", "root_concept": "Particle of superlative exclamation and supreme trust."},
            {"word": "الْوَكِيلُ (Al-Wakeel)", "meaning": "The Trustee / Disposer of Affairs", "root_concept": "The One who manages your affairs far better than you could ever manage them yourself."}
        ],
        "theological_significance": "Activates the divine guarantee in Surah At-Talaq (65:3): 'And whoever relies upon Allah—then He is sufficient for him.' Fire turned into cool peace for Ibrahim through this phrase.",
        "psychological_spiritual_effect": "Fortifies the nervous system against panic attacks, legal worries, enemies, and financial instability. Invokes quiet, invincible confidence.",
        "khushu_visualization": "Picture handing the deed of all your worries to the ultimate, infinitely wise Advocate who never loses a case."
    },
    {
        "id": "tahlil",
        "arabic": "لَا إِلٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ",
        "transliteration": "La ilaha illallahu wahdahu la sharika lahu, lahul-mulku wa lahul-hamdu, wa huwa 'ala kulli shay'in qadeer",
        "translation": "None has the right to be worshipped except Allah alone without partner; to Him belongs absolute sovereignty and all praise, and He is over all things Omnipotent.",
        "target_daily": 10,
        "benefits_category": "Security, Fortress & Supreme Freedom",
        "virtue": "Reciting 100 times equals freeing 10 slaves, grants 100 good deeds, erases 100 sins, and serves as an impenetrable shield against Shaytan (Sahih al-Bukhari 3293).",
        "category": "tahlil",
        "hadith_reference": "Sahih al-Bukhari (3293); Sahih Muslim (2691)",
        "linguistic_breakdown": [
            {"word": "لَا إِلٰهَ إِلَّا اللَّهُ (La ilaha illa Allah)", "meaning": "No deity worthy of worship except Allah", "root_concept": "The fundamental negation of false gods, idols of the heart, and earthly tyranny."},
            {"word": "وَحْدَهُ لَا شَرِيكَ لَهُ (wahdahu la sharika lah)", "meaning": "Alone without any partner", "root_concept": "Uncompromising pure Tawhid."},
            {"word": "لَهُ الْمُلْكُ (lahul-mulk)", "meaning": "To Him belongs the Kingdom", "root_concept": "Total cosmic sovereignty over all realms."},
            {"word": "وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ (wa huwa 'ala kulli shay'in qadeer)", "meaning": "And He is over all things Capable", "root_concept": "Zero limitations to His power and intervention."}
        ],
        "theological_significance": "The crowning formula of monotheism. It shatters every illusion of independent earthly power and builds an impenetrable fortress around the believer's soul.",
        "psychological_spiritual_effect": "Dispels existential dread, spiritual oppression, and paranoia. Instills a majestic sense of freedom and dignified peace.",
        "khushu_visualization": "Feel your soul standing entirely liberated from worldly subservience, bowing solely before the Sovereign Monarch of the Heavens and Earth."
    },
    {
        "id": "salawat",
        "arabic": "اللَّهُمَّ صَلِّ عَلَىٰ مُحَمَّدٍ وَعَلَىٰ آلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلَىٰ إِبْرَاهِيمَ وَعَلَىٰ آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ",
        "transliteration": "Allahumma salli 'ala Muhammadin wa 'ala aali Muhammad...",
        "translation": "O Allah, send peace and blessings upon Muhammad and upon the family of Muhammad, as You sent blessings upon Ibrahim...",
        "target_daily": 100,
        "benefits_category": "Well-being, Relief of Anxiety & Rizq",
        "virtue": "When Ubayy asked if he should dedicate all his dua to Salawat, the Prophet (ﷺ) said: 'Then your worries will be sufficient for you and your sins forgiven' (Tirmidhi 2457).",
        "category": "salawat",
        "hadith_reference": "Jami' at-Tirmidhi (2457); Sahih Muslim (408)",
        "linguistic_breakdown": [
            {"word": "اللَّهُمَّ صَلِّ (Allahumma salli)", "meaning": "O Allah, bestow Your praise and exalted mercy", "root_concept": "Salat from Allah onto the Prophet means raising his mention in the highest heavenly assembly and showering him with specialized mercy."},
            {"word": "عَلَىٰ مُحَمَّدٍ (ala Muhammad)", "meaning": "Upon Muhammad", "root_concept": "The Praised One."}
        ],
        "theological_significance": "Participates in the heavenly decree of Surah Al-Ahzab (33:56). Every single Salawat returns 10 direct divine blessings, 10 forgivenesses, and 10 elevated ranks upon the reciter.",
        "psychological_spiritual_effect": "Softens grief, relieves emotional turmoil, cleanses the character of arrogance, and fills the spirit with warm light and prophetic nobility.",
        "khushu_visualization": "Envision sending a radiant beam of love and gratitude toward the Messenger of Allah, and feeling 10 waves of divine mercy showering back over your life."
    },
    {
        "id": "ya_hayyu_ya_qayyum",
        "arabic": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ ، أَصْلِحْ لِي شَأْنِي كُلَّهُ وَلَا تَكِلْنِي إِلَىٰ نَفْسِي طَرْفَةَ عَيْنٍ",
        "transliteration": "Ya Hayyu Ya Qayyumu bi-rahmatika astagheeth, aslih li sha'ni kullahu wa la takilni ila nafsi tarfata 'ayn",
        "translation": "O Ever-Living, O Sustainer of all existence, by Your mercy I seek relief! Rectify for me all of my affairs, and do not leave me to myself even for the blink of an eye.",
        "target_daily": 33,
        "benefits_category": "Health, Well-being & Life Order",
        "virtue": "The supreme prophetic morning and evening supplication for total life rectification (Sunan an-Nasa'i, Sahih by al-Albani).",
        "category": "istighathah",
        "hadith_reference": "Sunan an-Nasa'i (Al-Kubra 10405); Mustadrak al-Hakim (1/545)",
        "linguistic_breakdown": [
            {"word": "يَا حَيُّ (Ya Hayy)", "meaning": "O Ever-Living", "root_concept": "The Life that has neither beginning nor end, giving vitality to all existence."},
            {"word": "يَا قَيُّومُ (Ya Qayyum)", "meaning": "O Self-Sustaining Sustainer", "root_concept": "The One who upholds the heavens, earth, bodily cells, and every atom without exhaustion."},
            {"word": "طَرْفَةَ عَيْنٍ (tarfata 'ayn)", "meaning": "Blink of an eye", "root_concept": "The shortest conceivable fraction of time."}
        ],
        "theological_significance": "Invocates the Greatest Names (Ism Allah al-A'zam) by which if asked, Allah answers. Direct appeal for divine management of health, relationships, and finances.",
        "psychological_spiritual_effect": "Brings total emotional order out of chaos. Replaces scattered thoughts and helplessness with divine alignment and vitality.",
        "khushu_visualization": "Feel every organ, heartbeat, and decision being gently recalibrated into perfect balance by the Ever-Living Sustainer."
    },
    {
        "id": "afiyah_health",
        "arabic": "اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لَا إِلٰهَ إِلَّا أَنْتَ",
        "transliteration": "Allahumma 'afini fi badani, Allahumma 'afini fi sam'i, Allahumma 'afini fi basari, la ilaha illa Anta",
        "translation": "O Allah, grant me vibrant health and well-being in my body; O Allah, preserve health in my hearing; O Allah, preserve health in my sight. None has the right to be worshipped except You.",
        "target_daily": 3,
        "benefits_category": "Health & Vital Protection",
        "virtue": "Repeated 3 times every morning and evening by the Prophet (ﷺ) for holistic bodily preservation (Sunan Abi Dawud 5090).",
        "category": "health",
        "hadith_reference": "Sunan Abi Dawud (5090); Musnad Ahmad (20430)",
        "linguistic_breakdown": [
            {"word": "عَافِنِي ('Afini)", "meaning": "Grant me 'Afiyah (total wellness / immunity / sound health)", "root_concept": "Afiyah is the most comprehensive wellness term in Arabic: shielding from physical illness, mental decay, moral corruption, and spiritual blindness."},
            {"word": "بَدَنِي (Badani)", "meaning": "My physical body / vitality", "root_concept": "Musculoskeletal, cellular, and organ health."},
            {"word": "سَمْعِي وَبَصَرِي (Sam'i wa Basari)", "meaning": "My hearing and my vision", "root_concept": "The gates of perception, cognition, and awareness."}
        ],
        "theological_significance": "Acknowledges that bodily vitality is a sacred trust (Amanah). Direct daily plea to preserve sensory sharpness and physical strength into old age.",
        "psychological_spiritual_effect": "Nurtures deep bodily mindfulness, reduces psychosomatic stress, and protects physical vitality.",
        "khushu_visualization": "Feel a wave of restorative wellness washing through your brain, eyes, ears, and bloodstream, sanctifying your physical vehicle for good deeds."
    },
    {
        "id": "huda_tuqa_ghina",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَىٰ وَالتُّقَىٰ وَالْعَفَافَ وَالْغِنَىٰ",
        "transliteration": "Allahumma inni as'alukal-huda wat-tuqa wal-'afafa wal-ghina",
        "translation": "O Allah, I ask You for Guidance, God-consciousness, Moral Dignity & Chastity, and Self-Sufficient Wealth.",
        "target_daily": 33,
        "benefits_category": "Wealth, Morals, Character & Self-Sufficiency",
        "virtue": "The comprehensive prophetic roadmap for prosperity, noble morals, and independent wealth (Sahih Muslim 2721).",
        "category": "wealth_character",
        "hadith_reference": "Sahih Muslim (2721)",
        "linguistic_breakdown": [
            {"word": "الْهُدَىٰ (Al-Huda)", "meaning": "Clear guidance and insight", "root_concept": "Mental clarity to make optimal choices in career, faith, and relationships."},
            {"word": "التُّقَىٰ (At-Tuqa)", "meaning": "Shield of God-consciousness", "root_concept": "Moral integrity that restrains impulsive destruction."},
            {"word": "الْعَفَافَ (Al-'Afaf)", "meaning": "Chastity, dignity, and restraint", "root_concept": "Noble character that refuses degrading compromises or exploitation."},
            {"word": "الْغِنَىٰ (Al-Ghina)", "meaning": "Richness of soul and financial independence", "root_concept": "Being so self-sufficient through Allah that you are never subservient to people."}
        ],
        "theological_significance": "Combines spiritual illumination with economic sovereignty and moral dignity. The supreme balanced Islamic lifestyle formula.",
        "psychological_spiritual_effect": "Instills regal self-respect, eradicates greed and desperation, and attracts clean, abundant prosperity.",
        "khushu_visualization": "Visualize your soul clothed in noble dignity, your mind filled with divine light, and your hands blessed with honorable abundance."
    }
]

class DhikrEngine:
    """Handles dhikr counters, persistence, and adaptive goal progression."""

    def __init__(self, db_path: str = "alisha_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dhikr_counts (
                        dhikr_id TEXT,
                        log_date TEXT,
                        count INTEGER DEFAULT 0,
                        target INTEGER DEFAULT 100,
                        updated_at TEXT,
                        PRIMARY KEY (dhikr_id, log_date)
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dhikr_adaptive_goals (
                        dhikr_id TEXT PRIMARY KEY,
                        current_daily_target INTEGER,
                        recommended_target INTEGER,
                        consistency_score REAL,
                        last_reviewed_week TEXT
                    )
                """)
                conn.commit()
        except Exception:
            pass

    def get_available_adhkar(self) -> List[Dict[str, Any]]:
        return DEFAULT_ADHKAR

    def get_adhkar(self) -> List[Dict[str, Any]]:
        return DEFAULT_ADHKAR

    def get_today_progress(self, log_date: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.get_daily_adhkar(log_date)


    def get_dhikr_by_id(self, dhikr_id: str) -> Optional[Dict[str, Any]]:
        for d in DEFAULT_ADHKAR:
            if d["id"] == dhikr_id:
                return d
        return None

    def get_daily_adhkar(self, log_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns today's adhkar list merged with active persisted counts."""
        target_date = log_date or date.today().isoformat()
        counts_map = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT dhikr_id, count, target FROM dhikr_counts WHERE log_date = ?", (target_date,))
                for row in cur.fetchall():
                    counts_map[row[0]] = {"count": row[1], "target": row[2]}
        except Exception:
            pass

        results = []
        for item in DEFAULT_ADHKAR:
            c = counts_map.get(item["id"], {"count": 0, "target": item["target_daily"]})
            count = c["count"]
            target = c["target"]
            pct = min(100, int((count / target) * 100)) if target > 0 else 0
            results.append({
                **item,
                "count": count,
                "target": target,
                "percentage": pct,
                "completed": count >= target
            })
        return results

    def increment_count(self, dhikr_id: str, delta: int = 1, log_date: Optional[str] = None) -> Dict[str, Any]:
        """Increments today's counter atomically and returns updated state."""
        target_date = log_date or date.today().isoformat()
        now_str = datetime.now().isoformat()

        target_item = self.get_dhikr_by_id(dhikr_id)
        default_target = target_item["target_daily"] if target_item else 100

        new_count = delta
        target = default_target

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT count, target FROM dhikr_counts WHERE dhikr_id = ? AND log_date = ?",
                    (dhikr_id, target_date)
                )
                row = cur.fetchone()
                if row:
                    new_count = row[0] + delta
                    target = row[1]
                    cur.execute(
                        "UPDATE dhikr_counts SET count = ?, updated_at = ? WHERE dhikr_id = ? AND log_date = ?",
                        (new_count, now_str, dhikr_id, target_date)
                    )
                else:
                    cur.execute(
                        "INSERT INTO dhikr_counts (dhikr_id, log_date, count, target, updated_at) VALUES (?, ?, ?, ?, ?)",
                        (dhikr_id, target_date, new_count, default_target, now_str)
                    )
                conn.commit()
        except Exception:
            pass

        completed = new_count >= target
        pct = min(100, int((new_count / target) * 100)) if target > 0 else 0

        return {
            "dhikr_id": dhikr_id,
            "new_count": new_count,
            "target": target,
            "percentage": pct,
            "completed": completed
        }

    def increment(self, dhikr_id: str, delta: int = 1, log_date: Optional[str] = None) -> Dict[str, Any]:
        return self.increment_count(dhikr_id, delta, log_date)

    def get_adaptive_recommendation(self, dhikr_id: str) -> Dict[str, Any]:
        """Calculates consistency score and recommends gentle progressive target adjustment."""
        today = date.today()
        seven_days_ago = (today - timedelta(days=7)).isoformat()
        days_completed = 0

        target_item = self.get_dhikr_by_id(dhikr_id)
        default_target = target_item["target_daily"] if target_item else 100

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT count, target FROM dhikr_counts
                    WHERE dhikr_id = ? AND log_date >= ?
                """, (dhikr_id, seven_days_ago))
                rows = cur.fetchall()
                for r in rows:
                    if r[0] >= r[1]:
                        days_completed += 1
        except Exception:
            pass

        consistency_score = days_completed / 7.0

        if consistency_score >= 0.85:
            rec_target = int(default_target * 1.2)
            action = "stretch"
            rationale = "Exceptional 7-day consistency! Ready for a light progressive increase."
        elif consistency_score <= 0.30:
            rec_target = max(33, int(default_target * 0.7))
            action = "ease"
            rationale = "Consistency is better than volume. Lowering target slightly to preserve daily rhythm."
        else:
            rec_target = default_target
            action = "maintain"
            rationale = "Solid sustainable cadence. Maintain current focus."

        return {
            "dhikr_id": dhikr_id,
            "current_target": default_target,
            "recommended_target": rec_target,
            "consistency_score": consistency_score,
            "action": action,
            "rationale": rationale
        }

    def compute_adaptive_goals(self, dhikr_id: str) -> Dict[str, Any]:
        return self.get_adaptive_recommendation(dhikr_id)
