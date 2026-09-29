"""
Duas Database — Curated Comprehensive Authentic Islamic Supplications
100% verified Qur'anic supplications and canonical Sunnah duas.
Features full vocalized Arabic with tashkeel, standard English transliteration,
eloquent English translation, exact Hadith & Qur'an citations, authenticity grading,
recommended contextual timings, repetition targets, and scholarly virtues.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

CATEGORIES_META = [
    {
        "id": "all",
        "name": "All Duas",
        "name_ar": "جميع الأدعية",
        "icon": "sparkles"
    },
    {
        "id": "morning_evening",
        "name": "Morning & Evening",
        "name_ar": "أذكار الصباح والمساء",
        "icon": "sun"
    },
    {
        "id": "anxiety_distress",
        "name": "Anxiety & Distress",
        "name_ar": "الهم والحزن والكرب",
        "icon": "heart-handshake"
    },
    {
        "id": "forgiveness_repentance",
        "name": "Forgiveness & Repentance",
        "name_ar": "الاستغفار والتوبة",
        "icon": "shield-check"
    },
    {
        "id": "sleep_waking",
        "name": "Sleep & Waking",
        "name_ar": "النوم والاستيقاظ",
        "icon": "moon"
    },
    {
        "id": "guidance_istikhara",
        "name": "Guidance & Istikhara",
        "name_ar": "الهداية والاستخارة",
        "icon": "compass"
    },
    {
        "id": "rizq_debt",
        "name": "Rizq & Debt Relief",
        "name_ar": "الرزق وسداد الدين",
        "icon": "coins"
    },
    {
        "id": "health_ruqyah",
        "name": "Health & Healing",
        "name_ar": "الشفاء والعافية والرقية",
        "icon": "activity"
    },
    {
        "id": "knowledge_exams",
        "name": "Knowledge & Exams",
        "name_ar": "العلم والامتحانات",
        "icon": "book-open"
    },
    {
        "id": "family_parents",
        "name": "Family & Parents",
        "name_ar": "الوالدين والأسرة",
        "icon": "users"
    },
    {
        "id": "daily_travel_food",
        "name": "Daily Life & Travel",
        "name_ar": "الحياة اليومية والسفر",
        "icon": "navigation"
    },
    {
        "id": "patience_protection",
        "name": "Patience & Protection",
        "name_ar": "الصبر والوقاية من الفتن",
        "icon": "shield"
    },
    {
        "id": "gratitude_praise",
        "name": "Gratitude & Praise",
        "name_ar": "الشكر والحمد والثناء",
        "icon": "heart"
    }
]

CURATED_DUAS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. MORNING & EVENING (أذكار الصباح والمساء)
    # -------------------------------------------------------------
    {
        "id": "dua_sayyidul_istighfar",
        "title": "Sayyidul Istighfar (Master Supplication for Forgiveness)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ",
        "transliteration": "Allahumma Anta Rabbi la ilaha illa Anta, khalaqtani wa ana 'abduka, wa ana 'ala 'ahdika wa wa'dika mastata'tu, a'udhu bika min sharri ma sana'tu, abu'u laka bini'matika 'alayya, wa abu'u bidhanbi faghfir li, fa-innahu la yaghfirudh-dhunuba illa Anta.",
        "translation": "O Allah, You are my Lord, there is no deity worthy of worship except You. You created me and I am Your servant, and I abide by Your covenant and promise as best I can. I seek refuge in You from the evil of what I have done. I acknowledge before You Your blessings upon me, and I confess to You my sin. So forgive me, for none forgives sins except You.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6306)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite every morning after Fajr and every evening after Asr/Maghrib.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) said: 'Whoever recites this with firm conviction during the day and dies before evening will be among the people of Paradise; and whoever recites it at night and dies before morning will be among the people of Paradise.'"
    },
    {
        "id": "dua_ayat_al_kursi",
        "title": "Ayat al-Kursi (The Throne Verse - Supreme Protection)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ",
        "transliteration": "Allahu la ilaha illa Huwa, Al-Hayyul-Qayyum. La ta'khudhuhu sinatuw-wa la nawm. Lahu ma fis-samawati wa ma fil-ard. Man dhal-ladhi yashfa'u 'indahu illa bi-idhnih. Ya'lamu ma bayna aydihim wa ma khalfahum, wa la yuhitoona bishay'im-min 'ilmihi illa bima sha'a. Wasi'a kursiyyuhus-samawati wal-ard, wa la ya'uduhu hifzuhuma, wa Huwal-'Aliyyul-'Adheem.",
        "translation": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of all existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that can intercede with Him except by His permission? He knows what is before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most High, the Most Great.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Baqarah (2:255); Sahih al-Bukhari (2311); Sahih Muslim (810)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Morning, evening, after every obligatory prayer, and immediately before sleeping.",
        "repeat_count": 1,
        "notes": "The greatest verse in the Qur'an. Protects against all demonic interference and ensures divine guardianship until morning."
    },
    {
        "id": "dua_bismillah_la_yadurru",
        "title": "Protection from All Earthly & Heavenly Harm (3x)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
        "transliteration": "Bismillahil-ladhi la yadurru ma'as-mihi shay'un fil-ardi wa la fis-sama'i wa Huwas-Sami'ul-'Aleem.",
        "translation": "In the name of Allah, with whose name nothing on earth or in heaven can cause harm, and He is the All-Hearing, the All-Knowing.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (5088); Jami' at-Tirmidhi (3388)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite 3 times in the morning and 3 times in the evening.",
        "repeat_count": 3,
        "notes": "The Prophet (ﷺ) declared that whoever recites this three times morning and evening will not be afflicted by any sudden calamity or poison."
    },
    {
        "id": "dua_raditu_billah",
        "title": "Pleasure with Allah, Islam, and Muhammad (ﷺ) (3x)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "رَضِيتُ بِاللَّهِ رَبًّا، وَبِالْإِسْلَامِ دِينًا، وَبِمُحَمَّدٍ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ نَبِيًّا",
        "transliteration": "Raditu billahi Rabba, wa bil-Islami dina, wa bi-Muhammadin sallallahu 'alayhi wa sallama Nabiyya.",
        "translation": "I am pleased with Allah as my Lord, with Islam as my religion, and with Muhammad (peace and blessings of Allah be upon him) as my Prophet.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (5072); Jami' at-Tirmidhi (3389)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite 3 times in the morning and 3 times in the evening.",
        "repeat_count": 3,
        "notes": "The Prophet (ﷺ) stated that whoever recites this 3 times, Allah takes upon Himself the duty to satisfy and please him on the Day of Resurrection."
    },
    {
        "id": "dua_health_afiyah",
        "title": "Supplication for Bodily, Hearing & Sight Wellness (3x)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لَا إِلٰهَ إِلَّا أَنْتَ. اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ، وَأَعُوذُ بِكَ مِنْ عَذَابِ الْقَبْرِ، لَا إِلٰهَ إِلَّا أَنْتَ",
        "transliteration": "Allahumma 'afini fi badani, Allahumma 'afini fi sam'i, Allahumma 'afini fi basari, la ilaha illa Anta. Allahumma inni a'udhu bika minal-kufri wal-faqr, wa a'udhu bika min 'adhabal-qabr, la ilaha illa Anta.",
        "translation": "O Allah, grant me health in my body; O Allah, grant me health in my hearing; O Allah, grant me health in my sight. There is no deity worthy of worship except You. O Allah, I seek refuge in You from disbelief and poverty, and I seek refuge in You from the punishment of the grave. There is no deity worthy of worship except You.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (5090); Musnad Ahmad (20430)",
        "authenticity_grade": "Hasan",
        "recommended_context": "Recite 3 times in the morning and 3 times in the evening.",
        "repeat_count": 3,
        "notes": "Abu Bakrah reported that the Prophet (ﷺ) never neglected this three-fold supplication for physical preservation."
    },
    {
        "id": "dua_ya_hayyu_ya_qayyoom",
        "title": "Invocation of the Ever-Living, Sustainer for Complete Rectification",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ، أَصْلِحْ لِي شَأْنِي كُلَّهُ، وَلَا تَكِلْنِي إِلَى نَفْسِي طَرْفَةَ عَيْنٍ",
        "transliteration": "Ya Hayyu Ya Qayyumu bi-rahmatika astagheeth, aslih li sha'ni kullahu wa la takilni ila nafsi tarfata 'ayn.",
        "translation": "O Ever-Living, O Sustainer of all existence, by Your mercy I seek assistance; rectify for me all of my affairs and do not leave me to myself even for the blink of an eye.",
        "source_type": "Hadith",
        "source_reference": "Sunan an-Nasa'i (al-Kubra 10330); Mustadrak al-Hakim (1/545)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Morning and evening, and whenever initiating significant work.",
        "repeat_count": 1,
        "notes": "Anas ibn Malik reported that the Prophet (ﷺ) advised Fatimah (may Allah be pleased with her) to never leave off reciting this every morning and evening."
    },
    {
        "id": "dua_hasbiyallahu_7x",
        "title": "Sufficiency of Allah for All Worldly & Spiritual Concerns (7x)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "حَسْبِيَ اللَّهُ لَا إِلٰهَ إِلَّا هُوَ ۖ عَلَيْهِ تَوَكَّلْتُ ۖ وَهُوَ رَبُّ الْعَرْشِ الْعَظِيمِ",
        "transliteration": "Hasbiyallahu la ilaha illa Huwa, 'alayhi tawakkaltu wa Huwa Rabbul-'Arshil-'Adheem.",
        "translation": "Allah is sufficient for me; there is no deity except Him. Upon Him I have relied, and He is the Lord of the Great Throne.",
        "source_type": "Qur'an & Hadith",
        "source_reference": "Surah At-Tawbah (9:129); Sunan Abi Dawud (5081)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite 7 times in the morning and 7 times in the evening.",
        "repeat_count": 7,
        "notes": "Abu ad-Darda' reported: 'Whoever says this 7 times in the morning and evening, Allah will suffice him for whatever worries him in this world and the next.'"
    },
    {
        "id": "dua_juwayriyah_tasbih",
        "title": "Juwayriyah's Weighty Tasbih of Immense Reward (3x)",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، عَدَدَ خَلْقِهِ، وَرِضَا نَفْسِهِ، وَزِنَةَ عَرْشِهِ، وَمِدَادَ كَلِمَاتِهِ",
        "transliteration": "Subhanallahi wa bihamdihi, 'adada khalqihi, wa rida nafsihi, wa zinata 'arshihi, wa midada kalimatih.",
        "translation": "Glory be to Allah and His is the praise, equal to the number of His creation, to the satisfaction of His Self, to the weight of His Throne, and to the ink of His words.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (2726)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite 3 times after Fajr prayer.",
        "repeat_count": 3,
        "notes": "The Prophet (ﷺ) returned to Juwayriyah after dawn and told her that reciting these words 3 times outweighs hours of continuous devotion."
    },
    {
        "id": "dua_asbahna_wa_asbahal_mulk",
        "title": "Morning Proclamation of Divine Dominion & Universal Good",
        "category": "morning_evening",
        "category_name": "Morning & Evening",
        "category_ar": "أذكار الصباح والمساء",
        "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، رَبِّ أَسْأَلُكَ خَيْرَ مَا فِي هَذَا الْيَوْمِ وَخَيْرَ مَا بَعْدَهُ، وَأَعُوذُ بِكَ مِنْ شَرِّ مَا فِي هَذَا الْيَوْمِ وَشَرِّ مَا بَعْدَهُ",
        "transliteration": "Asbahna wa asbahal-mulku lillah, wal-hamdu lillah, la ilaha illallahu wahdahu la sharika lah, lahul-mulku wa lahul-hamdu wa Huwa 'ala kulli shay'in Qadeer. Rabbi as'aluka khayra ma fi hadhal-yawmi wa khayra ma ba'dah, wa a'udhu bika min sharri ma fi hadhal-yawmi wa sharri ma ba'dah.",
        "translation": "We have entered the morning and the kingdom belongs to Allah, and all praise is for Allah. There is no deity except Allah alone, without partner. To Him belongs all sovereignty and praise, and He is over all things omnipotent. My Lord, I ask You for the good of this day and the good of what comes after it, and I seek refuge in You from the evil of this day and the evil of what comes after it.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (2723)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At sunrise and early morning.",
        "repeat_count": 1,
        "notes": "Comprehensive prophetic start to the day, framing the morning with sovereignty, reliance, and petition for goodness."
    },

    # -------------------------------------------------------------
    # 2. ANXIETY, DISTRESS & HARDSHIP (الهم والحزن والكرب)
    # -------------------------------------------------------------
    {
        "id": "dua_distress_yunus",
        "title": "Supplication of Prophet Yunus (Deliverance from the Depths)",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "لَّا إِلٰهَ إِلَّا أَنتَ سُبْحَانَكَ إِنِّي كُنتُ مِنَ الظَّالِمِينَ",
        "transliteration": "La ilaha illa Anta subhanaka inni kuntu minaz-zalimin.",
        "translation": "There is no deity except You; exalted are You. Indeed, I have been of the wrongdoers.",
        "source_type": "Qur'an & Hadith",
        "source_reference": "Surah Al-Anbiya (21:87); Jami' at-Tirmidhi (3505)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "During overwhelming anxiety, distress, panic, grief, or feeling cornered.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) said: 'No Muslim suppliant ever prays with these words for anything, but Allah responds to him.'"
    },
    {
        "id": "dua_anxiety_hamm_hazan",
        "title": "Prophetic Shield Against Anxiety, Grief, Inability & Debt",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ، وَالْعَجْزِ وَالْكَسَلِ، وَالْجُبْنِ وَالْبُخْلِ، وَضَلَعِ الدَّيْنِ، وَغَلَبَةِ الرِّجَالِ",
        "transliteration": "Allahumma inni a'udhu bika minal-hammi wal-hazan, wal-'ajzi wal-kasal, wal-jubni wal-bukhl, wa dala'id-dayni wa ghalabatir-rijal.",
        "translation": "O Allah, I seek refuge in You from anxiety (about the future) and sorrow (over the past), from incapacity and laziness, from cowardice and miserliness, from the heavy burden of debt and from being overpowered by people.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (2893)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite daily in the morning, evening, and during times of mental fatigue or financial stress.",
        "repeat_count": 1,
        "notes": "Anas reported that the Prophet (ﷺ) used to say this supplication more than almost any other."
    },
    {
        "id": "dua_karb_severe_distress",
        "title": "Du'a al-Karb (The Supreme Prayer for Severe Distress)",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "لَا إِلَهَ إِلَّا اللَّهُ الْعَظِيمُ الْحَلِيمُ، لَا إِلَهَ إِلَّا اللَّهُ رَبُّ الْعَرْشِ الْعَظِيمِ، لَا إِلَهَ إِلَّا اللَّهُ رَبُّ السَّمَاوَاتِ وَرَبُّ الْأَرْضِ وَرَبُّ الْعَرْشِ الْكَرِيمِ",
        "transliteration": "La ilaha illallahul-'Adheemul-Haleem, la ilaha illallahu Rabbul-'Arshil-'Adheem, la ilaha illallahu Rabbus-samawati wa Rabbul-ardi wa Rabbul-'Arshil-Kareem.",
        "translation": "There is no deity worthy of worship except Allah, the Magnificent, the Forbearing. There is no deity except Allah, Lord of the Magnificent Throne. There is no deity except Allah, Lord of the heavens, Lord of the earth, and Lord of the Noble Throne.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6345); Sahih Muslim (2730)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At moments of sudden shock, acute agony, bad news, or immense crises.",
        "repeat_count": 1,
        "notes": "Ibn Abbas narrated that whenever the Messenger of Allah (ﷺ) faced grave distress, he repeatedly uttered this."
    },
    {
        "id": "dua_ease_in_difficulty",
        "title": "Dua for Making Difficulty Easy",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "اللَّهُمَّ لَا سَهْلَ إِلَّا مَا جَعَلْتَهُ سَهْلًا، وَأَنْتَ تَجْعَلُ الْحَزْنَ إِذَا شِئْتَ سَهْلًا",
        "transliteration": "Allahumma la sahla illa ma ja'altahu sahla, wa Anta taj'alul-hazna idha shi'ta sahla.",
        "translation": "O Allah, there is no ease except in that which You have made easy, and You make difficulty, when You will, easy.",
        "source_type": "Hadith",
        "source_reference": "Sahih Ibn Hibban (972); Al-Adhkar by Imam al-Nawawi",
        "authenticity_grade": "Sahih",
        "recommended_context": "Before beginning hard tasks, complex exams, surgery, or confronting complicated problems.",
        "repeat_count": 1,
        "notes": "A classic sunnah supplication to eliminate mental bottlenecks and induce cognitive and logistical ease."
    },
    {
        "id": "dua_ayyub_affliction",
        "title": "Supplication of Prophet Ayyub in Severe Sickness & Hardship",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "أَنِّي مَسَّنِيَ الضُّرُّ وَأَنتَ أَرْحَمُ الرَّاحِمِينَ",
        "transliteration": "Anni massaniyad-durru wa Anta Arhamur-Rahimin.",
        "translation": "Indeed, adversity has touched me, and You are the Most Merciful of the merciful.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Anbiya (21:83)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Chronic illness, bodily exhaustion, or lengthy trials.",
        "repeat_count": 1,
        "notes": "The epitome of dignified patience (Sabr Jameel), presenting one's state to Allah without complaint."
    },
    {
        "id": "dua_hasbunallah",
        "title": "Hasbunallahu wa Ni'mal Wakeel (Ultimate Divine Sufficiency)",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "transliteration": "Hasbunallahu wa ni'mal-Wakeel.",
        "translation": "Allah is sufficient for us, and He is the best Disposer of affairs.",
        "source_type": "Qur'an & Hadith",
        "source_reference": "Surah Ali 'Imran (3:173); Sahih al-Bukhari (4563)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "When feeling powerless, facing slander, intimidation, or overwhelming odds.",
        "repeat_count": 7,
        "notes": "Uttered by Ibrahim when cast into the blaze, and by Muhammad (ﷺ) when told that the enemy had gathered against them."
    },
    {
        "id": "dua_quran_spring_of_heart",
        "title": "Healing Sorrow & Expanding the Chest through the Qur'an",
        "category": "anxiety_distress",
        "category_name": "Anxiety & Distress",
        "category_ar": "الهم والحزن والكرب",
        "arabic": "اللَّهُمَّ إِنِّي عَبْدُكَ، وَابْنُ عَبْدِكَ، وَابْنُ أَمَتِكَ، نَاصِيَتِي بِيَدِكَ، مَاضٍ فِيَّ حُكْمُكَ، عَدْلٌ فِيَّ قَضَاؤُكَ، أَسْأَلُكَ بِكُلِّ اسْمٍ هُوَ لَكَ، سَمَّيْتَ بِهِ نَفْسَكَ، أَوْ أَنْزَلْتَهُ فِي كِتَابِكَ، أَوْ عَلَّمْتَهُ أَحَدًا مِنْ خَلْقِكَ، أَوِ اسْتَأْثَرْتَ بِهِ فِي عِلْمِ الْغَيْبِ عِنْدَكَ، أَنْ تَجْعَلَ الْقُرْآنَ رَبِيعَ قَلْبِي، وَنُورَ صَدْرِي، وَجَلَاءَ حُزْنِي، وَذَهَابَ هَمِّي",
        "transliteration": "Allahumma inni 'abduka, wabnu 'abdika, wabnu amatika, nasiyati biyadika, madin fiyya hukmuka, 'adlun fiyya qada'uka, as'aluka bikulli ismin huwa laka sammayta bihi nafsaka, aw anzaltahu fi kitabika, aw 'allamtahu ahadan min khalqika, awis-ta'tharta bihi fi 'ilmil-ghaybi 'indaka, an taj'alal-Qur'ana rabi'a qalbi, wa nura sadri, wa jala'a huzni, wa dhahaba hammi.",
        "translation": "O Allah, I am Your servant, son of Your servant, son of Your maidservant, my forelock is in Your hand, Your command over me is forever executed and Your decree over me is just. I ask You by every name belonging to You which You have named Yourself with, or revealed in Your Book, or taught to any of Your creation, or preserved in the knowledge of the unseen with You, that You make the Qur'an the spring of my heart, the light of my chest, the banisher of my grief, and the reliever of my anxiety.",
        "source_type": "Hadith",
        "source_reference": "Musnad Ahmad (3712); Sahih Ibn Hibban (972)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Times of emotional numbness, depression, and spiritual burnout.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) said: 'Whoever says this in distress, Allah will remove his sorrow and replace it with joy.'"
    },

    # -------------------------------------------------------------
    # 3. FORGIVENESS & REPENTANCE (الاستغفار والتوبة)
    # -------------------------------------------------------------
    {
        "id": "dua_adam_hawwa_tawbah",
        "title": "Supplication of Adam & Hawwa for Sincere Repentance",
        "category": "forgiveness_repentance",
        "category_name": "Forgiveness & Repentance",
        "category_ar": "الاستغفار والتوبة",
        "arabic": "رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ",
        "transliteration": "Rabbana zalamna anfusana wa il-lam taghfir lana wa tarhamna lanakoonanna minal-khasireen.",
        "translation": "Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-A'raf (7:23)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "After falling into a mistake, in private prayer, and in Sajdah.",
        "repeat_count": 1,
        "notes": "The very words revealed by Allah to Adam when turning to Him in repentance."
    },
    {
        "id": "dua_astaghfirullah_al_adheem",
        "title": "Comprehensive Istighfar with the Ever-Living, Sustainer (3x)",
        "category": "forgiveness_repentance",
        "category_name": "Forgiveness & Repentance",
        "category_ar": "الاستغفار والتوبة",
        "arabic": "أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ الَّذِي لَا إِلٰهَ إِلَّا هُوَ الْحَيَّ الْقَيُّومَ وَأَتُوبُ إِلَيْهِ",
        "transliteration": "Astaghfirullahal-'Adheemal-ladhi la ilaha illa Huwal-Hayyul-Qayyumu wa atubu ilayh.",
        "translation": "I seek the forgiveness of Allah the Magnificent, besides whom there is no deity, the Ever-Living, the Sustainer of all existence, and I repent unto Him.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (1517); Jami' at-Tirmidhi (3577)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite 3 times daily or 100 times for complete purification of heart.",
        "repeat_count": 3,
        "notes": "The Prophet (ﷺ) said: 'Whoever says this, his sins will be forgiven even if he had fled from battle.'"
    },
    {
        "id": "dua_abu_bakr_tashahhud",
        "title": "Abu Bakr's Prayer for Forgiveness in Tashahhud",
        "category": "forgiveness_repentance",
        "category_name": "Forgiveness & Repentance",
        "category_ar": "الاستغفار والتوبة",
        "arabic": "اللَّهُمَّ إِنِّي ظَلَمْتُ نَفْسِي ظُلْمًا كَثِيرًا، وَلَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ، فَاغْفِرْ لِي مَغْفِرَةً مِنْ عِنْدِكَ، وَارْحَمْنِي إِنَّكَ أَنْتَ الْغَفُورُ الرَّحِيمُ",
        "transliteration": "Allahumma inni zalamtu nafsi zulman katheeran, wa la yaghfirudh-dhunuba illa Anta, faghfir li maghfiratan min 'indika warhamni, innaka Antal-Ghafurur-Raheem.",
        "translation": "O Allah, I have wronged myself greatly, and none forgives sins except You, so grant me forgiveness from Yourself and have mercy on me. Truly You are the Oft-Forgiving, Most Merciful.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (834); Sahih Muslim (2705)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At the end of every Salah before the final Tasleem.",
        "repeat_count": 1,
        "notes": "Taught personally by the Prophet (ﷺ) to his closest companion Abu Bakr as-Siddiq."
    },
    {
        "id": "dua_rabbighfir_warham",
        "title": "Dua for Forgiveness and Supreme Mercy",
        "category": "forgiveness_repentance",
        "category_name": "Forgiveness & Repentance",
        "category_ar": "الاستغفار والتوبة",
        "arabic": "رَّبِّ اغْفِرْ وَارْحَمْ وَأَنتَ خَيْرُ الرَّاحِمِينَ",
        "transliteration": "Rabbigh-fir warham wa Anta Khayrur-Rahimin.",
        "translation": "My Lord, forgive and have mercy, and You are the best of the merciful.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Mu'minun (23:118)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Between the two prostrations in Salah and during quiet reflection.",
        "repeat_count": 1,
        "notes": "The concluding verse of Surah Al-Mu'minun, encapsulating the entire believer's plea."
    },

    # -------------------------------------------------------------
    # 4. SLEEP, DREAMS & WAKING (النوم والاستيقاظ)
    # -------------------------------------------------------------
    {
        "id": "dua_before_sleep_bismika_rabbi",
        "title": "Before Sleeping (Placing Side Down with Soul Entrustment)",
        "category": "sleep_waking",
        "category_name": "Sleep & Waking",
        "category_ar": "النوم والاستيقاظ",
        "arabic": "بِاسْمِكَ رَبِّي وَضَعْتُ جَنْبِي وَبِكَ أَرْفَعُهُ، إِنْ أَمْسَكْتَ نَفْسِي فَارْحَمْهَا، وَإِنْ أَرْسَلْتَهَا فَاحْفَظْهَا بِمَا تَحْفَظُ بِهِ عِبَادَكَ الصَّالِحِينَ",
        "transliteration": "Bismika Rabbi wada'tu janbi wa bika arfa'uh, in amsakta nafsi farhamha, wa in arsaltaha fahfazha bima tahfazu bihi 'ibadakas-salihin.",
        "translation": "In Your name, my Lord, I lay down my side, and in Your name I raise it up. If You hold back my soul, then have mercy upon it, and if You release it, then protect it with that which You protect Your righteous servants.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6320); Sahih Muslim (2714)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Right before closing eyes on the right side of the bed.",
        "repeat_count": 1,
        "notes": "Sunnah to dust the bed thrice with the inside of one's garment before reciting."
    },
    {
        "id": "dua_before_sleep_short",
        "title": "Before Sleeping (Short Form of Living & Dying)",
        "category": "sleep_waking",
        "category_name": "Sleep & Waking",
        "category_ar": "النوم والاستيقاظ",
        "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "transliteration": "Bismika Allahumma amutu wa ahya.",
        "translation": "In Your name, O Allah, I die and I live.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6312); Sahih Muslim (2711)",
        "authenticity_grade": "Sahih",
        "recommended_context": "As the final spoken phrase before sleep.",
        "repeat_count": 1,
        "notes": "Re-centers the heart on the reality that sleep is the minor death."
    },
    {
        "id": "dua_waking_up",
        "title": "Upon Waking Up (Gratitude for Restored Life)",
        "category": "sleep_waking",
        "category_name": "Sleep & Waking",
        "category_ar": "النوم والاستيقاظ",
        "arabic": "الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ",
        "transliteration": "Alhamdu lillahil-ladhi ahyana ba'da ma amatana wa ilayhin-nushoor.",
        "translation": "Praise be to Allah Who gave us life after having caused us to die, and unto Him is the resurrection.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6312); Sahih Muslim (2711)",
        "authenticity_grade": "Sahih",
        "recommended_context": "First conscious utterance upon opening eyes in the morning.",
        "repeat_count": 1,
        "notes": "Establishes gratitude as the primary operating frequency of the newly opened day."
    },
    {
        "id": "dua_waking_at_night_tahajjud",
        "title": "Waking Up at Night (Ubadah ibn as-Samit Guaranteed Answer)",
        "category": "sleep_waking",
        "category_name": "Sleep & Waking",
        "category_ar": "النوم والاستيقاظ",
        "arabic": "لَا إِلٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، الْحَمْدُ لِلَّهِ، وَسُبْحَانَ اللَّهِ، وَلَا إِلٰهَ إِلَّا اللَّهُ، وَاللَّهُ أَكْبَرُ، وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ، رَبِّ اغْفِرْ لِي",
        "transliteration": "La ilaha illallahu wahdahu la sharika lah, lahul-mulku wa lahul-hamd, wa Huwa 'ala kulli shay'in Qadeer. Alhamdu lillah, wa Subhanallah, wa la ilaha illallah, wallahu Akbar, wa la hawla wa la quwwata illa billah. Rabbigh-fir li.",
        "translation": "There is no deity except Allah alone, without partner. To Him belongs sovereignty and all praise, and He is over all things omnipotent. Praise be to Allah, glory be to Allah, there is no deity except Allah, Allah is the Greatest, and there is no power nor might except with Allah. My Lord, forgive me.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (1154)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Whenever stirring or waking during the night.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) said: 'Whoever wakes at night and says this, then asks Allah for forgiveness or makes any dua, it will be accepted; and if he performs wudu and prays, his salah will be accepted.'"
    },

    # -------------------------------------------------------------
    # 5. GUIDANCE, STEADFASTNESS & ISTIKHARA (الهداية والاستخارة)
    # -------------------------------------------------------------
    {
        "id": "dua_muqallibal_quloob",
        "title": "Dua for Steadfastness of the Heart upon the Deen",
        "category": "guidance_istikhara",
        "category_name": "Guidance & Istikhara",
        "category_ar": "الهداية والاستخارة",
        "arabic": "يَا مُقَلِّبَ الْقُلُوبِ ثَبِّتْ قَلْبِي عَلَى دِينِكَ",
        "transliteration": "Ya Muqallibal-quloob, thabbit qalbi 'ala deenik.",
        "translation": "O Turner of the hearts, keep my heart steadfast upon Your religion.",
        "source_type": "Hadith",
        "source_reference": "Jami' at-Tirmidhi (2140); Musnad Ahmad (12107)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Daily supplication during Sujood and after prayer.",
        "repeat_count": 1,
        "notes": "Umm Salamah noted that this was the single most frequent supplication of the Prophet (ﷺ)."
    },
    {
        "id": "dua_rabbana_la_tuzigh",
        "title": "Dua of the Deeply Rooted in Knowledge Against Deviation",
        "category": "guidance_istikhara",
        "category_name": "Guidance & Istikhara",
        "category_ar": "الهداية والاستخارة",
        "arabic": "رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً ۚ إِنَّكَ أَنتَ الْوَهَّابُ",
        "transliteration": "Rabbana la tuzigh quloobana ba'da idh hadaytana wa hab lana mil-ladunka rahmah, innaka Antal-Wahhab.",
        "translation": "Our Lord, let not our hearts deviate after You have guided us and grant us from Yourself mercy. Indeed, You are the Bestower.",
        "source_type": "Qur'an",
        "source_reference": "Surah Ali 'Imran (3:8)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "When facing spiritual doubts, ideological challenges, or new life crossroads.",
        "repeat_count": 1,
        "notes": "The signature supplication of those firmly grounded in wisdom ('Ar-Rasikhoona fil-'Ilm')."
    },
    {
        "id": "dua_istikhara_complete",
        "title": "Salat al-Istikhara (The Complete Decision-Making Prayer)",
        "category": "guidance_istikhara",
        "category_name": "Guidance & Istikhara",
        "category_ar": "الهداية والاستخارة",
        "arabic": "اللَّهُمَّ إِنِّي أَسْتَخِيرُكَ بِعِلْمِكَ، وَأَسْتَقْدِرُكَ بِقُدْرَتِكَ، وَأَسْأَلُكَ مِنْ فَضْلِكَ الْعَظِيمِ، فَإِنَّكَ تَقْدِرُ وَلَا أَقْدِرُ، وَتَعْلَمُ وَلَا أَعْلَمُ، وَأَنْتَ عَلَّامُ الْغُيُوبِ. اللَّهُمَّ إِنْ كُنْتَ تَعْلَمُ أَنَّ هَذَا الْأَمْرَ خَيْرٌ لِي فِي دِينِي وَمَعَاشِي وَعَاقِبَةِ أَمْرِي فَاقْدُرْهُ لِي وَيَسِّرْهُ لِي ثُمَّ بَارِكْ لِي فِيهِ، وَإِنْ كُنْتَ تَعْلَمُ أَنَّ هَذَا الْأَمْرَ شَرٌّ لِي فِي دِينِي وَمَعَاشِي وَعَاقِبَةِ أَمْرِي فَاصْرِفْهُ عَنِّي وَاصْرِفْنِي عَنْهُ، وَاقْدُرْ لِيَ الْخَيْرَ حَيْثُ كَانَ ثُمَّ أَرْضِنِي بِهِ",
        "transliteration": "Allahumma inni astakhiruka bi'ilmika, wa astaqdiruka biqudratika, wa as'aluka min fadlikal-'adheem, fa-innaka taqdiru wa la aqdir, wa ta'lamu wa la a'lam, wa Anta 'Allamul-ghuyoob. Allahumma in kunta ta'lamu anna hadhal-amra khayrun li fi deeni wa ma'ashi wa 'aqibati amri faqdurhu li wa yassirhu li thumma barik li feeh. Wa in kunta ta'lamu anna hadhal-amra sharrun li fi deeni wa ma'ashi wa 'aqibati amri fasrifhu 'anni wasrifni 'anhu, waqdur liyal-khayra haythu kana thumma ardini bih.",
        "translation": "O Allah, I seek Your counsel by Your knowledge, and I seek ability by Your power, and I ask You from Your great bounty. For surely You have power and I have none, and You know and I know not, and You are the Knower of the unseen. O Allah, if You know that this matter is good for me in my religion, my livelihood and the outcome of my affair, then decree it for me, facilitate it for me, and then bless it for me. And if You know that this matter is harmful for me in my religion, my livelihood and the outcome of my affair, then turn it away from me and turn me away from it, and decree for me the good wherever it may be, and then make me pleased with it.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (1162)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Pray 2 rak'ahs of non-obligatory prayer, then recite this supplication specifying the decision.",
        "repeat_count": 1,
        "notes": "Jabir reported: 'The Messenger of Allah (ﷺ) used to teach us the Istikhara in all matters just as he taught us a Surah from the Qur'an.'"
    },
    {
        "id": "dua_huda_tuqa_ghina",
        "title": "Supplication for Guidance, Piety, Chastity & Inner Wealth",
        "category": "guidance_istikhara",
        "category_name": "Guidance & Istikhara",
        "category_ar": "الهداية والاستخارة",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى وَالتُّقَى وَالْعَفَافَ وَالْغِنَى",
        "transliteration": "Allahumma inni as'alukal-huda wat-tuqa wal-'afafa wal-ghina.",
        "translation": "O Allah, I ask You for guidance, piety, modesty/chastity, and self-sufficiency/contentment.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (2721)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Daily morning and evening contemplation.",
        "repeat_count": 1,
        "notes": "Four words that summarize the entire well-being of the human soul in this life and the next."
    },

    # -------------------------------------------------------------
    # 6. RIZQ & DEBT RELIEF (الرزق وسداد الدين)
    # -------------------------------------------------------------
    {
        "id": "dua_debt_relief_thabir",
        "title": "Supplication for Complete Relief from Overwhelming Debt",
        "category": "rizq_debt",
        "category_name": "Rizq & Debt Relief",
        "category_ar": "الرزق وسداد الدين",
        "arabic": "اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ، وَأَغْنِنِي بِفَضْلِكَ عَمَّنْ سِوَاكَ",
        "transliteration": "Allahummak-fini bi-halalika 'an haramik, wa aghnini bi-fadlika 'amman siwak.",
        "translation": "O Allah, suffice me with what is lawful against what is prohibited, and enrich me with Your bounty so that I am independent of all besides You.",
        "source_type": "Hadith",
        "source_reference": "Jami' at-Tirmidhi (3563); Musnad Ahmad (1318)",
        "authenticity_grade": "Hasan",
        "recommended_context": "Recite frequently after obligatory prayers when dealing with financial burdens.",
        "repeat_count": 1,
        "notes": "Ali (may Allah be pleased with him) stated: 'Even if your debt were the size of Mount Thabir, Allah would discharge it on your behalf.'"
    },
    {
        "id": "dua_musa_faqir_rizq",
        "title": "Supplication of Musa in Utter Need (Provision & Shelter)",
        "category": "rizq_debt",
        "category_name": "Rizq & Debt Relief",
        "category_ar": "الرزق وسداد الدين",
        "arabic": "رَبِّ إِنِّي لِمَا أَنزَلْتَ إِلَيَّ مِنْ خَيْرٍ فَقِيرٌ",
        "transliteration": "Rabbi inni lima anzalta ilayya min khayrin faqir.",
        "translation": "My Lord, truly I am in dire need of whatever good You bestow upon me.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Qasas (28:24)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Seeking employment, housing, marriage, or when feeling financially depleted.",
        "repeat_count": 1,
        "notes": "Recited by Musa under the shade in Madyan; immediately followed by marriage, honest work, and security."
    },
    {
        "id": "dua_fajr_ilm_rizq_amal",
        "title": "Morning Supplication for Beneficial Knowledge & Pure Sustenance",
        "category": "rizq_debt",
        "category_name": "Rizq & Debt Relief",
        "category_ar": "الرزق وسداد الدين",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا، وَرِزْقًا طَيِّبًا، وَعَمَلًا مُتَقَبَّلًا",
        "transliteration": "Allahumma inni as'aluka 'ilman nafi'a, wa rizqan tayyiba, wa 'amalan mutaqabbala.",
        "translation": "O Allah, I ask You for beneficial knowledge, pure and lawful sustenance, and deeds that are accepted.",
        "source_type": "Hadith",
        "source_reference": "Sunan Ibn Majah (925); Musnad Ahmad (26521)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Immediately after the final Tasleem of Fajr prayer.",
        "repeat_count": 1,
        "notes": "Umm Salamah reported that the Prophet (ﷺ) said this after every Fajr prayer without fail."
    },

    # -------------------------------------------------------------
    # 7. HEALTH, HEALING & RUQYAH (الشفاء والعافية والرقية)
    # -------------------------------------------------------------
    {
        "id": "dua_ruqyah_prophetic_healing",
        "title": "The Prophetic Ruqyah for Healing & Affliction Removal",
        "category": "health_ruqyah",
        "category_name": "Health & Healing",
        "category_ar": "الشفاء والعافية والرقية",
        "arabic": "اللَّهُمَّ رَبَّ النَّاسِ، أَذْهِبِ الْبَأْسَ، اشْفِ وَأَنْتَ الشَّافِي، لَا شِفَاءَ إِلَّا شِفَاؤُكَ، شِفَاءً لَا يُغَادِرُ سَقَمًا",
        "transliteration": "Allahumma Rabban-nas, adhhibil-ba's, ishfi wa Antash-Shafi, la shifa'a illa shifa'uk, shifa'an la yughadiru saqama.",
        "translation": "O Allah, Lord of mankind, remove the affliction. Grant healing, for You are the Healer. There is no healing except Your healing — a healing that leaves behind no disease or ailment.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (5743); Sahih Muslim (2191)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recited while placing the right hand on the location of pain or over the sick.",
        "repeat_count": 1,
        "notes": "A'isha reported that the Prophet (ﷺ) used to treat his family with this supplication."
    },
    {
        "id": "dua_pain_bismillah_3x_audhu_7x",
        "title": "Relief from Localized Bodily Pain (3x Bismillah + 7x A'udhu)",
        "category": "health_ruqyah",
        "category_name": "Health & Healing",
        "category_ar": "الشفاء والعافية والرقية",
        "arabic": "بِسْمِ اللَّهِ (3 مرات) ، أَعُوذُ بِاللَّهِ وَقُدْرَتِهِ مِنْ شَرِّ مَا أَجِدُ وَأُحَاذِرُ (7 مرات)",
        "transliteration": "Bismillah (3x), A'udhu billahi wa qudratihi min sharri ma ajidu wa uhadhir (7x).",
        "translation": "In the name of Allah (3 times). I seek refuge in Allah and His power from the evil of what I feel and fear (7 times).",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (2202)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Place hand on the painful area: say Bismillah 3 times, then the formula 7 times.",
        "repeat_count": 7,
        "notes": "Taught by the Prophet (ﷺ) to Uthman ibn Abi al-As for severe chronic physical pain."
    },
    {
        "id": "dua_protection_evil_eye_children",
        "title": "Protection of Loved Ones & Children from Evil Eye & Poison",
        "category": "health_ruqyah",
        "category_name": "Health & Healing",
        "category_ar": "الشفاء والعافية والرقية",
        "arabic": "أُعِيذُكَ بِكَلِمَاتِ اللَّهِ التَّامَّةِ، مِنْ كُلِّ شَيْطَانٍ وَهَامَّةٍ، وَمِنْ كُلِّ عَيْنٍ لَامَّةٍ",
        "transliteration": "U'idhuka bi-kalimatillahit-tammah, min kulli shaytanin wa hammah, wa min kulli 'aynin lammah.",
        "translation": "I seek refuge for you in the perfect words of Allah, from every devil and poisonous reptile, and from every envious, harmful evil eye.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (3371)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Recite over children, family members, or oneself daily.",
        "repeat_count": 1,
        "notes": "Ibrahim recited this over Ismail and Ishaq, and Muhammad (ﷺ) recited it over Hasan and Husayn."
    },
    {
        "id": "dua_protection_dreadful_diseases",
        "title": "Protection from Debilitating Diseases & Mental Illnesses",
        "category": "health_ruqyah",
        "category_name": "Health & Healing",
        "category_ar": "الشفاء والعافية والرقية",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْبَرَصِ، وَالْجُنُونِ، وَالْجُذَامِ، وَمِنْ سَيِّئِ الْأَسْقَامِ",
        "transliteration": "Allahumma inni a'udhu bika minal-barasi, wal-junooni, wal-judhami, wa min sayyi'il-asqam.",
        "translation": "O Allah, I seek refuge in You from vitiligo/leprosy, insanity, debilitating chronic disease, and from all dreadful ailments.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (1554); Sunan an-Nasa'i (5493)",
        "authenticity_grade": "Sahih",
        "recommended_context": "During epidemics, health anxieties, and in regular morning dhikr.",
        "repeat_count": 1,
        "notes": "Anas reported that the Prophet (ﷺ) invoked this consistently against cognitive and physical degradation."
    },

    # -------------------------------------------------------------
    # 8. KNOWLEDGE, EXAMS & ELOQUENCE (العلم والامتحانات)
    # -------------------------------------------------------------
    {
        "id": "dua_knowledge",
        "title": "The Direct Command to Seek Increase in Knowledge",
        "category": "knowledge",
        "category_name": "Knowledge & Exams",
        "category_ar": "العلم والامتحانات",
        "arabic": "رَبِّ زِدْنِي عِلْمًا",
        "transliteration": "Rabbi zidni 'ilma",
        "translation": "My Lord, increase me in knowledge.",
        "source_type": "Qur'an",
        "source_reference": "Surah Taha (20:114)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Before study sessions, research, lectures, and exams.",
        "repeat_count": 1,
        "notes": "The only entity in creation that Allah explicitly commanded the Prophet (ﷺ) to ask an increase of."
    },
    {
        "id": "dua_musa_eloquence_speech",
        "title": "Supplication of Musa for Expansion of Chest & Fluent Speech",
        "category": "knowledge",
        "category_name": "Knowledge & Exams",
        "category_ar": "العلم والامتحانات",
        "arabic": "رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي وَاحْلُلْ عُقْدَةً مِّن لِّسَانِي يَفْقَهُوا قَوْلِي",
        "transliteration": "Rabbish-rah li sadri, wa yassir li amri, wahlul 'uqdatam-mil-lisani yafqahu qawli.",
        "translation": "My Lord, expand for me my breast, and ease for me my task, and untie the knot from my tongue that they may understand my speech.",
        "source_type": "Qur'an",
        "source_reference": "Surah Taha (20:25-28)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Before oral examinations, presentations, tough conversations, and public speaking.",
        "repeat_count": 1,
        "notes": "Musa's prayer before confronting Pharaoh, removing stage fright and clarifying expression."
    },
    {
        "id": "dua_beneficial_knowledge_tirmidhi",
        "title": "Dua for Applying Knowledge and Perpetual Increase",
        "category": "knowledge",
        "category_name": "Knowledge & Exams",
        "category_ar": "العلم والامتحانات",
        "arabic": "اللَّهُمَّ انْفَعْنِي بِمَا عَلَّمْتَنِي، وَعَلِّمْنِي مَا يَنْفَعُنِي، وَزِدْنِي عِلْمًا، وَالْحَمْدُ لِلَّهِ عَلَى كُلِّ حَالٍ",
        "transliteration": "Allahumman-fa'ni bima 'allamtani, wa 'allimni ma yanfa'uni, wa zidni 'ilma, wal-hamdu lillahi 'ala kulli hal.",
        "translation": "O Allah, benefit me through that which You have taught me, and teach me that which will benefit me, and increase me in knowledge; and praise be to Allah under all circumstances.",
        "source_type": "Hadith",
        "source_reference": "Jami' at-Tirmidhi (3599); Sunan Ibn Majah (251)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At the start or conclusion of academic revision.",
        "repeat_count": 1,
        "notes": "Combines learning with practical fruit and protection from sterile academic pride."
    },

    # -------------------------------------------------------------
    # 9. FAMILY & PARENTS (الوالدين والأسرة)
    # -------------------------------------------------------------
    {
        "id": "dua_parents_mercy_isra",
        "title": "Dua of Mercy for Parents",
        "category": "family_parents",
        "category_name": "Family & Parents",
        "category_ar": "الوالدين والأسرة",
        "arabic": "رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا",
        "transliteration": "Rabbir-hamhuma kama rabbayani saghira.",
        "translation": "My Lord, have mercy upon them both as they brought me up when I was small.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Isra (17:24)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "After every single prayer and during regular daily contemplation.",
        "repeat_count": 1,
        "notes": "Direct Qur'anic instruction on filial devotion, honoring parental sacrifice."
    },
    {
        "id": "dua_parents_believers_hisab",
        "title": "Supplication for Parents & Believers on the Day of Reckoning",
        "category": "family_parents",
        "category_name": "Family & Parents",
        "category_ar": "الوالدين والأسرة",
        "arabic": "رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ",
        "transliteration": "Rabbanagh-fir li wa li-walidayya wa lil-mu'minina yawma yaqoomul-hisab.",
        "translation": "Our Lord, forgive me and my parents and the believers the Day the account is established.",
        "source_type": "Qur'an",
        "source_reference": "Surah Ibrahim (14:41)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "During the final Tashahhud sitting or during Qiyam al-Layl.",
        "repeat_count": 1,
        "notes": "The prayer of Ibrahim encompassing himself, his parents, and the universal ummah."
    },
    {
        "id": "dua_family_qurrata_ayun",
        "title": "Dua for Joy in Spouses & Children ('Ibadur-Rahman)",
        "category": "family_parents",
        "category_name": "Family & Parents",
        "category_ar": "الوالدين والأسرة",
        "arabic": "رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا",
        "transliteration": "Rabbana hab lana min azwajina wa dhurriyyatina qurrata a'yunin waj'alna lil-muttaqina imama.",
        "translation": "Our Lord, grant us from among our spouses and offspring comfort to our eyes and make us an example for the righteous.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Furqan (25:74)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "For marital harmony, righteous descendants, and exemplary leadership.",
        "repeat_count": 1,
        "notes": "The signature quality of the Servants of the Most Merciful."
    },
    {
        "id": "dua_ibrahim_muqimas_salah",
        "title": "Supplication for Establishing Prayer Across Generations",
        "category": "family_parents",
        "category_name": "Family & Parents",
        "category_ar": "الوالدين والأسرة",
        "arabic": "رَبِّ اجْعَلْنِي مُقِيمَ الصَّلَاةِ وَمِن ذُرِّيَّتِي ۚ رَبَّنَا وَتَقَبَّلْ دُعَاءِ",
        "transliteration": "Rabbij-'alni muqimas-salati wa min dhurriyyati, Rabbana wa taqabbal du'a.",
        "translation": "My Lord, make me an establisher of prayer, and from my descendants. Our Lord, and accept my supplication.",
        "source_type": "Qur'an",
        "source_reference": "Surah Ibrahim (14:40)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Recite in Sujood and when praying for family righteousness.",
        "repeat_count": 1,
        "notes": "Safeguards family members from negligence toward Salah."
    },

    # -------------------------------------------------------------
    # 10. DAILY LIFE, TRAVEL & FOOD (الحياة اليومية والسفر)
    # -------------------------------------------------------------
    {
        "id": "dua_leaving_house",
        "title": "Leaving the House (Total Protection & Guidance)",
        "category": "daily_travel_food",
        "category_name": "Daily Life & Travel",
        "category_ar": "الحياة اليومية والسفر",
        "arabic": "بِسْمِ اللَّهِ، تَوَكَّلْتُ عَلَى اللَّهِ، وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
        "transliteration": "Bismillahi tawakkaltu 'alallahi, wa la hawla wa la quwwata illa billah.",
        "translation": "In the name of Allah, I place my trust in Allah; there is no might and no power except in Allah.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (5095); Jami' at-Tirmidhi (3426)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Upon stepping outside the front door.",
        "repeat_count": 1,
        "notes": "Angels reply: 'You are guided, defended, and protected,' and shaytan withdraws."
    },
    {
        "id": "dua_entering_house",
        "title": "Entering the House (Divine Blessing & Peace)",
        "category": "daily_travel_food",
        "category_name": "Daily Life & Travel",
        "category_ar": "الحياة اليومية والسفر",
        "arabic": "بِسْمِ اللَّهِ وَلَجْنَا، وَبِسْمِ اللَّهِ خَرَجْنَا، وَعَلَى رَبِّنَا تَوَكَّلْنَا",
        "transliteration": "Bismillahi walajna, wa bismillahi kharajna, wa 'ala Rabbina tawakkalna.",
        "translation": "In the name of Allah we enter, and in the name of Allah we leave, and upon our Lord we place our trust.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (5096)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Upon crossing the threshold into the home.",
        "repeat_count": 1,
        "notes": "Followed by giving Salam to the occupants to bring barakah to the house."
    },
    {
        "id": "dua_travel_safar",
        "title": "Supplication for Travel (Dua as-Safar)",
        "category": "daily_travel_food",
        "category_name": "Daily Life & Travel",
        "category_ar": "الحياة اليومية والسفر",
        "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ وَإِنَّا إِلَىٰ رَبِّنَا لَمُنقَلِبُونَ. اللَّهُمَّ إِنَّا نَسْأَلُكَ فِي سَفَرِنَا هَٰذَا الْبِرَّ وَالتَّقْوَى، وَمِنَ الْعَمَلِ مَا تَرْضَى، اللَّهُمَّ هَوِّنْ عَلَيْنَا سَفَرَنَا هَٰذَا وَاطْوِ عَنَّا بُعْدَهُ",
        "transliteration": "Subhanal-ladhi sakh-khara lana hadha wa ma kunna lahu muqrinin, wa inna ila Rabbina lamunqaliboon. Allahumma inna nas'aluka fi safarina hadhal-birra wat-taqwa, wa minal-'amali ma tarda. Allahumma hawwin 'alayna safarana hadha watwi 'anna bu'dah.",
        "translation": "Glory be to Him Who has subjected this to us, and we could never have done it by ourselves. And indeed, to our Lord we will return. O Allah, we ask You on this journey of ours for righteousness and piety, and for deeds that please You. O Allah, ease this journey for us and shorten its distance.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (1342)",
        "authenticity_grade": "Sahih",
        "recommended_context": "When getting into a car, bus, train, plane, or setting off on any journey.",
        "repeat_count": 1,
        "notes": "Brings peace, safety, and divine accompaniment on journeys."
    },
    {
        "id": "dua_after_wudu",
        "title": "After Completing Ablution (8 Gates of Jannah Opened)",
        "category": "daily_travel_food",
        "category_name": "Daily Life & Travel",
        "category_ar": "الحياة اليومية والسفر",
        "arabic": "أَشْهَدُ أَنْ لَا إِلٰهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ. اللَّهُمَّ اجْعَلْنِي مِنَ التَّوَّابِينَ وَاجْعَلْنِي مِنَ الْمُتَطَهِّرِينَ",
        "transliteration": "Ashhadu alla ilaha illallahu wahdahu la sharika lah, wa ashhadu anna Muhammadan 'abduhu wa Rasuluh. Allahummaj-'alni minat-tawwabina waj-'alni minal-mutatahhireen.",
        "translation": "I testify that there is no deity except Allah alone, without partner, and I testify that Muhammad is His servant and messenger. O Allah, make me of those who constantly repent, and make me of those who purify themselves.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (234); Jami' at-Tirmidhi (55)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Immediately upon drying or finishing Wudu.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) said: 'Whoever says this, all eight gates of Paradise are opened for him to enter from whichever he wills.'"
    },
    {
        "id": "dua_after_eating",
        "title": "Gratitude After Eating Food & Drink",
        "category": "daily_travel_food",
        "category_name": "Daily Life & Travel",
        "category_ar": "الحياة اليومية والسفر",
        "arabic": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ",
        "transliteration": "Alhamdu lillahil-ladhi at'amana wa saqana wa ja'alana Muslimeen.",
        "translation": "Praise be to Allah Who has fed us, given us drink, and made us Muslims.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (3850); Jami' at-Tirmidhi (3457)",
        "authenticity_grade": "Hasan",
        "recommended_context": "Immediately upon finishing a meal or drink.",
        "repeat_count": 1,
        "notes": "Connects physical sustenance with gratitude for faith."
    },

    # -------------------------------------------------------------
    # 11. PATIENCE & PROTECTION (الصبر والوقاية من الفتن)
    # -------------------------------------------------------------
    {
        "id": "dua_talut_patience_firmness",
        "title": "Dua for Pouring Out Patience & Steadfast Victory",
        "category": "patience_protection",
        "category_name": "Patience & Protection",
        "category_ar": "الصبر والوقاية من الفتن",
        "arabic": "رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ",
        "transliteration": "Rabbana afrigh 'alayna sabraw-wa thabbit aqdamana wansurna 'alal-qawmil-kafirin.",
        "translation": "Our Lord, pour down upon us patience and plant firmly our feet and give us victory over the disbelieving people.",
        "source_type": "Qur'an",
        "source_reference": "Surah Al-Baqarah (2:250)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "When facing intense opposition, high pressure, or severe competition.",
        "repeat_count": 1,
        "notes": "Supplication of Talut's steadfast companions against Goliath (Jalut)."
    },
    {
        "id": "dua_protection_dajjal_grave",
        "title": "Protection from Hellfire, Grave Punishment & the False Messiah",
        "category": "patience_protection",
        "category_name": "Patience & Protection",
        "category_ar": "الصبر والوقاية من الفتن",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ عَذَابِ جَهَنَّمَ، وَمِنْ عَذَابِ الْقَبْرِ، وَمِنْ فِتْنَةِ الْمَحْيَا وَالْمَمَاتِ، وَمِنْ شَرِّ فِتْنَةِ الْمَسِيحِ الدَّجَّالِ",
        "transliteration": "Allahumma inni a'udhu bika min 'adhabi jahannam, wa min 'adhabal-qabr, wa min fitnatil-mahya wal-mamat, wa min sharri fitnatil-Maseehid-Dajjal.",
        "translation": "O Allah, I seek refuge in You from the punishment of Hell, from the punishment of the grave, from the trials of life and death, and from the evil trial of the False Messiah (Dajjal).",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (588); Sahih al-Bukhari (1377)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At the conclusion of every Tashahhud before ending Salah.",
        "repeat_count": 1,
        "notes": "Sunnah Mu'akkadah in prayer to guard against existential trials."
    },
    {
        "id": "dua_anger_istiazah",
        "title": "Extinguishing Anger & Emotional Turbulence",
        "category": "patience_protection",
        "category_name": "Patience & Protection",
        "category_ar": "الصبر والوقاية من الفتن",
        "arabic": "أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ",
        "transliteration": "A'udhu billahi minash-shaytanir-rajeem.",
        "translation": "I seek refuge in Allah from Satan, the accursed.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (6115); Sahih Muslim (2610)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Immediately when feeling anger, agitation, or losing temper.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) stated that saying this causes rage to dissipate immediately."
    },

    # -------------------------------------------------------------
    # 12. GRATITUDE & PRAISE (الشكر والحمد والثناء)
    # -------------------------------------------------------------
    {
        "id": "dua_sulayman_shukr",
        "title": "Supplication of Prophet Sulayman for Lifelong Gratitude",
        "category": "gratitude_praise",
        "category_name": "Gratitude & Praise",
        "category_ar": "الشكر والحمد والثناء",
        "arabic": "رَبِّ أَوْزِعْنِي أَنْ أَشْكُرَ نِعْمَتَكَ الَّتِي أَنْعَمْتَ عَلَيَّ وَعَلَىٰ وَالِدَيَّ وَأَنْ أَعْمَلَ صَالِحًا تَرْضَاهُ وَأَدْخِلْنِي بِرَحْمَتِكَ فِي عِبَادِكَ الصَّالِحِينَ",
        "transliteration": "Rabbi awzi'ni an ashkura ni'matakal-lati an'amta 'alayya wa 'ala walidayya wa an a'mala salihan tardahu wa adkhilni bi-rahmatika fi 'ibadikas-salihin.",
        "translation": "My Lord, enable me to be grateful for Your favor which You have bestowed upon me and upon my parents and to do righteous deeds of which You will approve and admit me by Your mercy into the ranks of Your righteous servants.",
        "source_type": "Qur'an",
        "source_reference": "Surah An-Naml (27:19); Surah Al-Ahqaf (46:15)",
        "authenticity_grade": "Mutawatir (Qur'an)",
        "recommended_context": "Upon receiving good news, milestones, promotions, or accomplishments.",
        "repeat_count": 1,
        "notes": "The prayer of Sulayman recognizing that success requires deeper humility."
    },
    {
        "id": "dua_muadh_shukr_ibadah",
        "title": "Prophetic Pledge for Perpetual Remembrance, Gratitude & Beautiful Worship",
        "category": "gratitude_praise",
        "category_name": "Gratitude & Praise",
        "category_ar": "الشكر والحمد والثناء",
        "arabic": "اللَّهُمَّ أَعِنِّي عَلَى ذِكْرِكَ، وَشُكْرِكَ، وَحُسْنِ عِبَادَتِكَ",
        "transliteration": "Allahumma a'inni 'ala dhikrika, wa shukrika, wa husni 'ibadatik.",
        "translation": "O Allah, assist me in remembering You, expressing gratitude to You, and worshiping You in the most beautiful manner.",
        "source_type": "Hadith",
        "source_reference": "Sunan Abi Dawud (1522); Sunan an-Nasa'i (1303)",
        "authenticity_grade": "Sahih",
        "recommended_context": "At the conclusion of every single Salah.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) held Mu'adh's hand and advised him never to leave this after any prayer."
    },
    {
        "id": "dua_praise_30_angels",
        "title": "Magnificent Praise That Raced Thirty Angels to Record",
        "category": "gratitude_praise",
        "category_name": "Gratitude & Praise",
        "category_ar": "الشكر والحمد والثناء",
        "arabic": "رَبَّنَا وَلَكَ الْحَمْدُ، حَمْدًا كَثِيرًا طَيِّبًا مُبَارَكًا فِيهِ",
        "transliteration": "Rabbana wa lakal-hamd, hamdan katheeran tayyiban mubarakan feeh.",
        "translation": "Our Lord, and to You belongs all praise — an abundant, beautiful, blessed praise.",
        "source_type": "Hadith",
        "source_reference": "Sahih al-Bukhari (799)",
        "authenticity_grade": "Sahih",
        "recommended_context": "After rising from Ruku' in Salah and during moments of gratitude.",
        "repeat_count": 1,
        "notes": "The Prophet (ﷺ) saw over thirty angels competing to be the first to record its reward."
    },
    {
        "id": "dua_akhlaq_character",
        "title": "Supplication for Noble Character & Eliminating Impulses",
        "category": "guidance_istikhara",
        "category_name": "Guidance & Istikhara",
        "category_ar": "الهداية والاستخارة",
        "arabic": "اللَّهُمَّ اهْدِنِي لِأَحْسَنِ الْأَخْلَاقِ لَا يَهْدِي لِأَحْسَنِهَا إِلَّا أَنْتَ، وَاصْرِفْ عَنِّي سَيِّئَهَا لَا يَصْرِفُ عَنِّي سَيِّئَهَا إِلَّا أَنْتَ",
        "transliteration": "Allahummah-dini li-ahsani al-akhlaq, la yahdi li-ahsaniha illa Anta, wasrif 'anni sayyi'aha la yasrifu 'anni sayyi'aha illa Anta.",
        "translation": "O Allah, guide me to the best of character, none can guide to the best of it except You; and turn away from me bad character, none can turn it away except You.",
        "source_type": "Hadith",
        "source_reference": "Sahih Muslim (771)",
        "authenticity_grade": "Sahih",
        "recommended_context": "Opening of night prayer (Qiyam) and daily self-cultivation.",
        "repeat_count": 1,
        "notes": "Foundational prayer for akhlaq and conquering impulsive reactions."
    }
]


class DuasDatabase:
    """
    Manages curated authentic Islamic supplications, category filtering,
    instant text search, featured daily recommendations, and category metadata.
    """

    def __init__(self):
        self.duas = CURATED_DUAS

    def get_all(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all duas, optionally filtered by category slug."""
        if not category or category.lower() in ("all", ""):
            return self.duas
        cat_lower = category.lower().strip()
        
        # 1. Exact match priority
        exact = [d for d in self.duas if d["category"].lower() == cat_lower]
        if exact:
            return exact
            
        # 2. Substring or category name match
        return [
            d for d in self.duas
            if cat_lower in d["category"].lower()
            or cat_lower in d.get("category_name", "").lower()
        ]

    def get_by_id(self, dua_id: str) -> Optional[Dict[str, Any]]:
        """Look up single dua by id."""
        return next((d for d in self.duas if d["id"] == dua_id), None)

    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fast full-text search across Arabic, transliteration, English, notes, and references,
        ranked by relevancy score.
        """
        q = query.lower().strip()
        base_list = self.get_all(category)
        if not q:
            return base_list

        scored_results = []
        for d in base_list:
            score = 0
            d_id = d["id"].lower()
            d_title = d.get("title", "").lower()
            d_trans = d.get("translation", "").lower()
            d_lat = d.get("transliteration", "").lower()
            d_cat = d.get("category", "").lower()
            d_cat_name = d.get("category_name", "").lower()
            d_ar = d.get("arabic", "")
            d_notes = d.get("notes", "").lower()
            d_ref = d.get("source_reference", "").lower()
            d_ctx = d.get("recommended_context", "").lower()

            if q == d_id or d_id == f"dua_{q}":
                score += 1000
            elif q in d_id:
                score += 300

            if q in d_title:
                score += 500
            if q in d_trans:
                score += 250
            if q in d_cat or q in d_cat_name:
                score += 150
            if q in d_lat or q in d_ar:
                score += 120
            if q in d_ref:
                score += 80
            if q in d_ctx:
                score += 60
            if q in d_notes:
                score += 30

            if score > 0:
                scored_results.append((score, d))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [d for score, d in scored_results]

    def get_categories(self) -> List[str]:
        """Returns distinct legacy list of category string identifiers."""
        cats = []
        for d in self.duas:
            if d["category"] not in cats:
                cats.append(d["category"])
        return sorted(cats)

    def get_categories_detailed(self) -> List[Dict[str, Any]]:
        """Returns rich category objects with Arabic labels and count of duas."""
        detailed = []
        for cat in CATEGORIES_META:
            if cat["id"] == "all":
                count = len(self.duas)
            else:
                count = sum(
                    1 for d in self.duas 
                    if d["category"] == cat["id"] 
                    or cat["id"] in d["category"]
                    or (cat["id"] == "morning_evening" and d["category"] in ("morning_evening", "morning"))
                    or (cat["id"] == "anxiety_distress" and d["category"] in ("anxiety_distress", "anxiety"))
                    or (cat["id"] == "forgiveness_repentance" and d["category"] in ("forgiveness_repentance", "forgiveness"))
                    or (cat["id"] == "sleep_waking" and d["category"] in ("sleep_waking", "sleep"))
                    or (cat["id"] == "guidance_istikhara" and d["category"] in ("guidance_istikhara", "guidance"))
                    or (cat["id"] == "rizq_debt" and d["category"] in ("rizq_debt", "rizq"))
                    or (cat["id"] == "health_ruqyah" and d["category"] in ("health_ruqyah", "health"))
                    or (cat["id"] == "knowledge_exams" and d["category"] in ("knowledge_exams", "knowledge"))
                    or (cat["id"] == "family_parents" and d["category"] in ("family_parents", "family"))
                    or (cat["id"] == "daily_travel_food" and d["category"] in ("daily_travel_food", "travel", "daily"))
                    or (cat["id"] == "patience_protection" and d["category"] in ("patience_protection", "patience", "protection"))
                    or (cat["id"] == "gratitude_praise" and d["category"] in ("gratitude_praise", "gratitude"))
                )
            detailed.append({
                **cat,
                "count": count
            })
        return detailed

    def get_daily_featured(self, hour: Optional[int] = None) -> Dict[str, Any]:
        """
        Selects a contextually appropriate featured Dua based on the current hour:
        - 04:00 - 11:00: Morning Adhkar / Sayyidul Istighfar / Juwayriyah
        - 11:00 - 16:00: Guidance / Knowledge / Rizq
        - 16:00 - 21:00: Evening Adhkar / Anxiety & Ease / Gratitude
        - 21:00 - 04:00: Sleep & Night Wakefulness / Tahajjud
        """
        if hour is None:
            hour = datetime.now().hour

        if 4 <= hour < 11:
            featured_ids = ["dua_sayyidul_istighfar", "dua_bismillah_la_yadurru", "dua_juwayriyah_tasbih", "dua_fajr_ilm_rizq_amal"]
        elif 11 <= hour < 16:
            featured_ids = ["dua_knowledge", "dua_musa_faqir_rizq", "dua_ease_in_difficulty", "dua_huda_tuqa_ghina"]
        elif 16 <= hour < 21:
            featured_ids = ["dua_raditu_billah", "dua_anxiety_hamm_hazan", "dua_sulayman_shukr", "dua_distress_yunus"]
        else:
            featured_ids = ["dua_before_sleep_bismika_rabbi", "dua_waking_at_night_tahajjud", "dua_ayat_al_kursi", "dua_abu_bakr_tashahhud"]

        # Pick based on day of month to rotate
        day = datetime.now().day
        chosen_id = featured_ids[day % len(featured_ids)]
        found = self.get_by_id(chosen_id)
        return found or self.duas[0]
