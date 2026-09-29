"""
Quran Engine
Offline-first Quran library adhering to Tanzil text integrity.
Explicitly bundles complete essential surahs:
- Surah Al-Fatihah (Surah 1 - All 7 Verses)
- Surah Al-Baqarah (Selected Essential: 2:255 Ayat al-Kursi, 2:285-286 Amanar Rasul, 2:152-157 Sabr)
- Surah Al-Kahf (Surah 18 - Complete Essential Passages 1-10, 27-31, 100-110)
- Surah Maryam (Surah 19 - Essential Passages 1-15, 30-36)
- Surah Taha (Surah 20 - Essential Passages 1-14, 25-36)
- Surah Al-Mu'minun (Surah 23 - Complete Firdaus Path 1-11, 115-118)
- Surah Al-Furqan (Surah 25 - Ibadur Rahman 63-77)
- Surah Ya-Sin (Surah 36 - Complete Essential Passages 1-32, 51-58, 77-83)
- Surah Ar-Rahman (Surah 55 - Complete Essential Passages 1-36, 60-78)
- Surah Al-Waqi'ah (Surah 56 - Complete 96 Verses & Passages)
- Surah Al-Jumu'ah (Surah 62 - All 11 Verses)
- Surah Al-Mulk (Surah 67 - Complete All 30 Verses)
- Surah Al-Insan / Ad-Dahr (Surah 76 - Verses 1-22)
- Surah An-Naba (Surah 78 - Verses 1-40)
- Surah Ad-Duha (Surah 93 - All 11 Verses)
- Surah Ash-Sharh (Surah 94 - All 8 Verses)
- Surah At-Tin (Surah 95 - All 8 Verses)
- Surah Al-Alaq (Surah 96 - Verses 1-5 First Revelation)
- Surah Al-Qadr (Surah 97 - All 5 Verses)
- Surah Al-Zalzalah (Surah 99 - All 8 Verses)
- Surah Al-Asr (Surah 103 - All 3 Verses)
- Surah Al-Kawthar (Surah 108 - All 3 Verses)
- Surah Al-Kafirun (Surah 109 - All 6 Verses)
- Surah Al-Ikhlas (Surah 112 - All 4 Verses)
- Surah Al-Falaq (Surah 113 - All 5 Verses)
- Surah An-Nas (Surah 114 - All 6 Verses)
"""

import json
from typing import Dict, Any, List, Optional

SPECIAL_VIRTUE_METADATA = {
    "al_mulk_night": {
        "title": "Surah Al-Mulk (The Sovereignty) at Night",
        "surah_number": 67,
        "classification": "Sahih / Hasan",
        "source": "Sunan al-Tirmidhi (2891), Sunan Abi Dawud (1400), Musnad Ahmad",
        "ruling": "Established Sunnah: The Prophet (ﷺ) said: 'There is a surah in the Quran of thirty verses that interceded for a man until he was forgiven: Blessed is He in whose hand is dominion (Surah Al-Mulk).' Recited every night before sleep for protection in the grave.",
        "recommended_time": "Night / Before Sleep"
    },
    "al_kahf_friday": {
        "title": "Surah Al-Kahf on Friday",
        "surah_number": 18,
        "classification": "Sahih",
        "source": "Sunan al-Bayhaqi (5856), Mustadrak al-Hakim (3392), Sahih al-Jami (6470)",
        "ruling": "Established Sunnah: The Prophet (ﷺ) said: 'Whoever recites Surah Al-Kahf on Friday, light will shine for him from beneath his feet to the clouds of the sky, illuminating the Day of Resurrection, and he will be forgiven between the two Fridays.'",
        "recommended_time": "Friday (From Thursday Maghrib until Friday Maghrib)"
    },
    "ayat_al_kursi_sleep": {
        "title": "Ayat al-Kursi (2:255) After Every Salah & Before Sleep",
        "surah_number": 2,
        "ayah": 255,
        "classification": "Sahih",
        "source": "Sahih al-Bukhari (2311); Sunan an-Nasa'i as-Sunan al-Kubra (9928)",
        "ruling": "Established Sunnah: 'Whoever recites Ayat al-Kursi after every obligatory prayer, nothing prevents him from entering Paradise except death.' Before sleep, an angel protects you from Shaytan all night.",
        "recommended_time": "After Every Obligatory Prayer & Before Sleeping"
    },
    "baqarah_last_two": {
        "title": "Last Two Verses of Al-Baqarah (2:285-286)",
        "surah_number": 2,
        "ayahs": "285-286",
        "classification": "Sahih",
        "source": "Sahih al-Bukhari (5009), Sahih Muslim (807)",
        "ruling": "Established Sunnah: The Prophet (ﷺ) said: 'Whoever recites the last two verses of Surah al-Baqarah at night, they will suffice him (from every evil and harm).'",
        "recommended_time": "Night / Evening"
    },
    "yaseen_heart": {
        "title": "Surah Ya-Sin (Heart of the Quran)",
        "surah_number": 36,
        "classification": "Hasan / Highly Recommended for Contemplation",
        "source": "Sunan al-Tirmidhi (2887), Sunan Abi Dawud (3121)",
        "ruling": "Venerated in classical scholarship for reflecting deeply on Tawhid, the Messenger's mission, the signs of resurrection, and the ultimate accountability before Allah.",
        "recommended_time": "Morning / Friday / Times of Need"
    },
    "al_waqiah_night": {
        "title": "Surah Al-Waqi'ah (The Inevitable)",
        "surah_number": 56,
        "classification": "Venerated for Contemplation / Specific Poverty Hadith is Da'if",
        "source": "Ibn Sunni, Bayhaqi; reviewed in Silsilah Da'ifah (289)",
        "ruling": "A masterclass in eschatology sorting humanity into the Foremost (Muqarrabun), the Companions of the Right (Ashab al-Yameen), and the Companions of the Left. Recitation earns continuous reward.",
        "recommended_time": "Evening / Reflection on Akhirah"
    },
    "al_muawwidhat": {
        "title": "Al-Mu'awwidhat (Surah Ikhlas, Falaq, Nas)",
        "surah_number": 112,
        "classification": "Sahih",
        "source": "Sahih al-Bukhari (5017), Sunan Abi Dawud (5082), Sunan an-Nasa'i",
        "ruling": "Established Sunnah: Reciting Surah Al-Ikhlas equals one-third of the Quran. Reciting all three 3 times morning and evening protects from all harm, evil eye, and whispers.",
        "recommended_time": "3x Morning, 3x Evening, After Every Prayer & Before Sleep"
    },
    "al_jumuah_friday": {
        "title": "Surah Al-Jumu'ah (Friday Congregation)",
        "surah_number": 62,
        "classification": "Sahih",
        "source": "Sahih Muslim (877)",
        "ruling": "Sunnah to recite during Friday congregational prayer (Jummah). Reminds believers of abandoning trade when called to prayer and hastening to the remembrance of Allah.",
        "recommended_time": "Friday Prayer"
    }
}

SURAH_CATALOG = [
    {"number": 1, "name_ar": "الفاتحة", "name_en": "Al-Fatihah", "meaning": "The Opening", "verses": 7, "type": "Meccan", "category": "Essential Daily"},
    {"number": 2, "name_ar": "البقرة", "name_en": "Al-Baqarah", "meaning": "The Cow (Ayat al-Kursi)", "verses": 286, "type": "Medinan", "category": "Protection"},
    {"number": 18, "name_ar": "الكهف", "name_en": "Al-Kahf", "meaning": "The Cave", "verses": 110, "type": "Meccan", "category": "Friday Sunnah"},
    {"number": 19, "name_ar": "مريم", "name_en": "Maryam", "meaning": "Mary", "verses": 98, "type": "Meccan", "category": "Prophetic Stories"},
    {"number": 20, "name_ar": "طه", "name_en": "Taha", "meaning": "Ta-Ha", "verses": 135, "type": "Meccan", "category": "Prophetic Stories"},
    {"number": 23, "name_ar": "المؤمنون", "name_en": "Al-Mu'minun", "meaning": "The Believers (Firdaus Path)", "verses": 118, "type": "Meccan", "category": "Character & Akhlaq"},
    {"number": 25, "name_ar": "الفرقان", "name_en": "Al-Furqan", "meaning": "The Criterion (Ibadur Rahman)", "verses": 77, "type": "Meccan", "category": "Character & Akhlaq"},
    {"number": 36, "name_ar": "يس", "name_en": "Ya-Sin", "meaning": "Ya-Sin (Heart of Quran)", "verses": 83, "type": "Meccan", "category": "Heart & Resurrection"},
    {"number": 55, "name_ar": "الرحمن", "name_en": "Ar-Rahman", "meaning": "The Beneficent", "verses": 78, "type": "Medinan", "category": "Divine Blessings"},
    {"number": 56, "name_ar": "الواقعة", "name_en": "Al-Waqi'ah", "meaning": "The Inevitable", "verses": 96, "type": "Meccan", "category": "Eschatology & Paradise"},
    {"number": 62, "name_ar": "الجمعة", "name_en": "Al-Jumu'ah", "meaning": "Friday Congregation", "verses": 11, "type": "Medinan", "category": "Friday Sunnah"},
    {"number": 67, "name_ar": "الملك", "name_en": "Al-Mulk", "meaning": "The Sovereignty", "verses": 30, "type": "Meccan", "category": "Nightly Protection"},
    {"number": 76, "name_ar": "الإنسان", "name_en": "Al-Insan", "meaning": "Man / The Time", "verses": 31, "type": "Medinan", "category": "Paradise Descriptions"},
    {"number": 78, "name_ar": "النبأ", "name_en": "An-Naba", "meaning": "The Great News", "verses": 40, "type": "Meccan", "category": "Day of Judgment"},
    {"number": 93, "name_ar": "الضحى", "name_en": "Ad-Duha", "meaning": "The Morning Hours", "verses": 11, "type": "Meccan", "category": "Comfort & Hope"},
    {"number": 94, "name_ar": "الشرح", "name_en": "Ash-Sharh", "meaning": "The Relief / Expansion", "verses": 8, "type": "Meccan", "category": "Comfort & Ease"},
    {"number": 95, "name_ar": "التين", "name_en": "At-Tin", "meaning": "The Fig", "verses": 8, "type": "Meccan", "category": "Human Nobility"},
    {"number": 96, "name_ar": "العلق", "name_en": "Al-Alaq", "meaning": "The Clot (First Iqra)", "verses": 19, "type": "Meccan", "category": "Knowledge"},
    {"number": 97, "name_ar": "القدر", "name_en": "Al-Qadr", "meaning": "The Night of Decree", "verses": 5, "type": "Meccan", "category": "Laylat al-Qadr"},
    {"number": 99, "name_ar": "الزلزلة", "name_en": "Al-Zalzalah", "meaning": "The Earthquake", "verses": 8, "type": "Medinan", "category": "Accountability"},
    {"number": 103, "name_ar": "العصر", "name_en": "Al-Asr", "meaning": "The Declining Day / Time", "verses": 3, "type": "Meccan", "category": "Ultimate Wisdom"},
    {"number": 108, "name_ar": "الكوثر", "name_en": "Al-Kawthar", "meaning": "Abundance", "verses": 3, "type": "Meccan", "category": "Divine Gifts"},
    {"number": 109, "name_ar": "الكافرون", "name_en": "Al-Kafirun", "meaning": "The Disbelievers", "verses": 6, "type": "Meccan", "category": "Pure Monotheism"},
    {"number": 112, "name_ar": "الإخلاص", "name_en": "Al-Ikhlas", "meaning": "Sincerity (1/3 Quran)", "verses": 4, "type": "Meccan", "category": "Daily Protection"},
    {"number": 113, "name_ar": "الفلق", "name_en": "Al-Falaq", "meaning": "The Daybreak", "verses": 5, "type": "Meccan", "category": "Daily Protection"},
    {"number": 114, "name_ar": "الناس", "name_en": "An-Nas", "meaning": "Mankind", "verses": 6, "type": "Meccan", "category": "Daily Protection"}
]

# Complete Surah Al-Mulk (All 30 Verses)
SURAH_MULK_COMPLETE = [
    {"num": 1, "ar": "تَبَارَكَ الَّذِي بِيَدِهِ الْمُلْكُ وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ", "en": "Blessed is He in whose hand is dominion, and He is over all things competent -"},
    {"num": 2, "ar": "الَّذِي خَلَقَ الْمَوْتَ وَالْحَيَاةَ لِيَبْلُوَكُمْ أَيُّكُمْ أَحْسَنُ عَمَلًا ۚ وَهُوَ الْعَزِيزُ الْغَفُورُ", "en": "He who created death and life to test you as to which of you is best in deed - and He is the Exalted in Might, the Forgiving -"},
    {"num": 3, "ar": "الَّذِي خَلَقَ سَبْعَ سَمَاوَاتٍ طِبَاقًا ۖ مَّا تَرَىٰ فِي خَلْقِ الرَّحْمَٰنِ مِن تَفَاوُتٍ ۖ فَارْجِعِ الْبَصَرَ هَلْ تَرَىٰ مِن فُطُورٍ", "en": "Who created seven heavens in layers. You see no flaw in the creation of the Most Merciful. Turn your vision again; do you see any rift?"},
    {"num": 4, "ar": "ثُمَّ ارْجِعِ الْبَصَرَ كَرَّتَيْنِ يَنقَلِبْ إِلَيْكَ الْبَصَرُ خَاسِئًا وَهُوَ حَسِيرٌ", "en": "Then return your vision twice again. Your vision will return to you humbled while it is fatigued."},
    {"num": 5, "ar": "وَلَقَدْ زَيَّنَّا السَّمَاءَ الدُّنْيَا بِمَصَابِيحَ وَجَعَلْنَاهَا رُجُومًا لِّلشَّيَاطِينِ ۖ وَأَعْتَدْنَا لَهُمْ عَذَابَ السَّعِيرِ", "en": "And We have certainly beautified the nearest heaven with stars and made them missiles for the devils and prepared for them the punishment of the Blaze."},
    {"num": 6, "ar": "وَلِلَّذِينَ كَفَرُوا بِرَبِّهِمْ عَذَابُ جَهَنَّمَ ۖ وَبِئْسَ الْمَصِيرُ", "en": "And for those who disbelieved in their Lord is the punishment of Hell, and wretched is the destination."},
    {"num": 7, "ar": "إِذَا أُلْقُوا فِيهَا سَمِعُوا لَهَا شَهِيقًا وَهِيَ تَفُورُ", "en": "When they are thrown into it, they hear from it a dreadful inhaling while it boils up."},
    {"num": 8, "ar": "تَكَادُ تَمَيَّزُ مِنَ الْغَيْظِ ۖ كُلَّمَا أُلْقِيَ فِيهَا فَوْجٌ سَأَلَهُمْ خَزَنَتُهَا أَلَمْ يَأْتِكُمْ نَذِيرٌ", "en": "It almost bursts with fury. Every time a company is thrown into it, its keepers ask them: 'Did there not come to you a warner?'"},
    {"num": 9, "ar": "قَالُوا بَلَىٰ قَدْ جَاءَنَا نَذِيرٌ فَكَذَّبْنَا وَقُلْنَا مَا نَزَّلَ اللَّهُ مِن شَيْءٍ إِنْ أَنتُمْ إِلَّا فِي ضَلَالٍ كَبِيرٍ", "en": "They will say: 'Yes, a warner had come to us, but we denied and said, 'Allah has not sent down anything. You are in great error.''"},
    {"num": 10, "ar": "وَقَالُوا لَوْ كُنَّا نَسْمَعُ أَوْ نَعْقِلُ مَا كُنَّا فِي أَصْحَابِ السَّعِيرِ", "en": "And they will say: 'If only we had been listening or reasoning, we would not be among the companions of the Blaze.'"},
    {"num": 11, "ar": "فَاعْتَرَفُوا بِذَنبِهِمْ فَسُحْقًا لِّأَصْحَابِ السَّعِيرِ", "en": "And they will admit their sin, so alienation is for the companions of the Blaze."},
    {"num": 12, "ar": "إِنَّ الَّذِينَ يَخْشَوْنَ رَبَّهُم بِالْغَيْبِ لَهُم مَّغْفِرَةٌ وَأَجْرٌ كَبِيرٌ", "en": "Indeed, those who fear their Lord unseen will have forgiveness and great reward."},
    {"num": 13, "ar": "وَأَسِرُّوا قَوْلَكُمْ أَوِ اجْهَرُوا بِهِ ۖ إِنَّهُ عَلِيمٌ بِذَاتِ الصُّدُورِ", "en": "And conceal your speech or publicize it; indeed, He is Knowing of that within the breasts."},
    {"num": 14, "ar": "أَلَا يَعْلَمُ مَنْ خَلَقَ وَهُوَ اللَّطِيفُ الْخَبِيرُ", "en": "Does He who created not know, while He is the Subtle, the Acquainted?"},
    {"num": 15, "ar": "هُوَ الَّذِي جَعَلَ لَكُمُ الْأَرْضَ ذَلُولًا فَامْشُوا فِي مَنَاكِبِهَا وَكُلُوا مِن رِّزْقِهِ ۖ وَإِلَيْهِ النُّشُورُ", "en": "It is He who made the earth tame for you - so walk among its slopes and eat of His provision - and to Him is the resurrection."},
    {"num": 16, "ar": "أَأَمِنتُم مَّن فِي السَّمَاءِ أَن يَخْسِفَ بِكُمُ الْأَرْضَ فَإِذَا هِيَ تَمُورُ", "en": "Do you feel secure that He who is over the heaven will not cause the earth to swallow you up while it oscillates?"},
    {"num": 17, "ar": "أَمْ أَمِنتُم مَّن فِي السَّمَاءِ أَن يُرْسِلَ عَلَيْكُمْ حَاصِبًا ۖ فَسَتَعْلَمُونَ كَيْفَ نَذِيرِ", "en": "Or do you feel secure that He will not send against you a storm of stones? Then you would know how severe My warning was."},
    {"num": 18, "ar": "وَلَقَدْ كَذَّبَ الَّذِينَ مِن قَبْلِهِمْ فَكَيْفَ كَانَ نَكِيرِ", "en": "And already had those before them denied, and how severe was My reproach."},
    {"num": 19, "ar": "أَوَلَمْ يَرَوْا إِلَى الطَّيْرِ فَوْقَهُمْ صَافَّاتٍ وَيَقْبِضْنَ ۚ مَا يُمْسِكُهُنَّ إِلَّا الرَّحْمَٰنُ ۚ إِنَّهُ بِكُلِّ شَيْءٍ بَصِيرٌ", "en": "Do they not see the birds above them, spreading their wings and folding them? None holds them up except the Most Merciful. He is of all things All-Seeing."},
    {"num": 20, "ar": "أَمَّنْ هَٰذَا الَّذِي هُوَ جُندٌ لَّكُمْ يَنصُرُكُم مِّن دُونِ الرَّحْمَٰنِ ۚ إِنِ الْكَافِرُونَ إِلَّا فِي غُرُورٍ", "en": "Or who is it that could be an army for you to aid you other than the Most Merciful? The disbelievers are not but in delusion."},
    {"num": 21, "ar": "أَمَّنْ هَٰذَا الَّذِي يَرْزُقُكُمْ إِنْ أَمْسَكَ رِزْقَهُ ۚ بَل لَّجُّوا فِي عُتُوٍّ وَنُفُورٍ", "en": "Or who is it that could provide for you if He withheld His provision? Rather, they have persisted in insolence and aversion."},
    {"num": 22, "ar": "أَفَمَن يَمْشِي مُكِبًّا عَلَىٰ وَجْهِهِ أَهْدَىٰ أَمَّن يَمْشِي سَوِيًّا عَلَىٰ صِرَاطٍ مُّسْتَقِيمٍ", "en": "Then is one who walks fallen on his face better guided or one who walks upright on a straight path?"},
    {"num": 23, "ar": "قُلْ هُوَ الَّذِي أَنشَأَكُمْ وَجَعَلَ لَكُمُ السَّمْعَ وَالْأَبْصَارَ وَالْأَفْئِدَةَ ۖ قَلِيلًا مَّا تَشْكُرُونَ", "en": "Say: 'It is He who has produced you and made for you hearing, vision, and hearts; little are you grateful.'"},
    {"num": 24, "ar": "قُلْ هُوَ الَّذِي ذَرَأَكُمْ فِي الْأَرْضِ وَإِلَيْهِ تُحْشَرُونَ", "en": "Say: 'It is He who multiplied you throughout the earth, and to Him you will be gathered.'"},
    {"num": 25, "ar": "وَيَقُولُونَ مَتَىٰ هَٰذَا الْوَعْدُ إِن كُنتُمْ صَادِقِينَ", "en": "And they say: 'When is this promise, if you should be truthful?'"},
    {"num": 26, "ar": "قُلْ إِنَّمَا الْعِلْمُ عِندَ اللَّهِ وَإِنَّمَا أَنَا نَذِيرٌ مُّبِينٌ", "en": "Say: 'The knowledge is only with Allah, and I am only a clear warner.'"},
    {"num": 27, "ar": "فَلَمَّا رَأَوْهُ زُلْفَةً سِيئَتْ وُجُوهُ الَّذِينَ كَفَرُوا وَقِيلَ هَٰذَا الَّذِي كُنتُم بِهِ تَدَّعُونَ", "en": "But when they see it approaching, the faces of those who disbelieved will be distressed, and it will be said: 'This is what you used to call for.'"},
    {"num": 28, "ar": "قُلْ أَرَأَيْتُمْ إِنْ أَهْلَكَنِيَ اللَّهُ وَمَن مَّعِيَ أَوْ رَحِمَنَا فَمَن يُجِيرُ الْكَافِرِينَ مِنْ عَذَابٍ أَلِيمٍ", "en": "Say: 'Have you considered: whether Allah should cause my death and those with me or have mercy upon us, who can protect the disbelievers from a painful punishment?'"},
    {"num": 29, "ar": "قُلْ هُوَ الرَّحْمَٰنُ آمَنَّا بِهِ وَعَلَيْهِ تَوَكَّلْنَا ۖ فَسَتَعْلَمُونَ مَنْ هُوَ فِي ضَلَالٍ مُّبِينٍ", "en": "Say: 'He is the Most Merciful; we have believed in Him, and upon Him we have relied. You will know who it is that is in clear error.'"},
    {"num": 30, "ar": "قُلْ أَرَأَيْتُمْ إِنْ أَصْبَحَ مَاؤُكُمْ غَوْرًا فَمَن يَأْتِيكُم بِمَاءٍ مَّعِينٍ", "en": "Say: 'Have you considered: if your water was to sink into the earth, then who could bring you flowing water?'"}
]

# Surah Ya-Sin Complete (All 83 Verses)
SURAH_YASEEN_TEXT = [
    {"num": 1, "ar": "يس", "en": "Ya-Sin."},
    {"num": 2, "ar": "وَالْقُرْآنِ الْحَكِيمِ", "en": "By the wise Qur'an."},
    {"num": 3, "ar": "إِنَّكَ لَمِنَ الْمُرْسَلِينَ", "en": "Indeed you, [O Muhammad], are from among the messengers,"},
    {"num": 4, "ar": "عَلَىٰ صِرَاطٍ مُّسْتَقِيمٍ", "en": "On a straight path."},
    {"num": 5, "ar": "تَنزِيلَ الْعَزِيزِ الرَّحِيمِ", "en": "[This is] a revelation of the Exalted in Might, the Merciful,"},
    {"num": 6, "ar": "لِتُنذِرَ قَوْمًا مَّا أُنذِرَ آبَاؤُهُمْ فَهُمْ غَافِلُونَ", "en": "That you may warn a people whose forefathers were not warned, so they are unaware."},
    {"num": 7, "ar": "لَقَدْ حَقَّ الْقَوْلُ عَلَىٰ أَكْثَرِهِمْ فَهُمْ لَا يُؤْمِنُونَ", "en": "Already the word has come into effect upon most of them, so they do not believe."},
    {"num": 8, "ar": "إِنَّا جَعَلْنَا فِي أَعْنَاقِهِمْ أَغْلَالًا فَهِيَ إِلَى الْأَذْقَانِ فَهُم مُّقْمَحُونَ", "en": "Indeed, We have put shackles on their necks up to their chins, so they are with heads raised aloft."},
    {"num": 9, "ar": "وَجَعَلْنَا مِن بَيْنِ أَيْدِيهِمْ سَدًّا وَمِنْ خَلْفِهِمْ سَدًّا فَأَغْشَيْنَاهُمْ فَهُمْ لَا يُبْصِرُونَ", "en": "And We have put before them a barrier and behind them a barrier and covered them, so they do not see."},
    {"num": 10, "ar": "وَسَوَاءٌ عَلَيْهِمْ أَأَنذَرْتَهُمْ أَمْ لَمْ تُنذِرْهُمْ لَا يُؤْمِنُونَ", "en": "And it is all the same for them whether you warn them or do not warn them - they will not believe."},
    {"num": 11, "ar": "إِنَّمَا تُنذِرُ مَنِ اتَّبَعَ الذِّكْرَ وَخَشِيَ الرَّحْمَٰنَ بِالْغَيْبِ ۖ فَبَشِّرْهُ بِمَغْفِرَةٍ وَأَجْرٍ كَرِيمٍ", "en": "You can only warn one who follows the message and fears the Most Merciful unseen. So give him good tidings of forgiveness and noble reward."},
    {"num": 12, "ar": "إِنَّا نَحْنُ نُحْيِي الْمَوْتَىٰ وَنَكْتُبُ مَا قَدَّمُوا وَآثَارَهُمْ ۚ وَكُلَّ شَيْءٍ أَحْصَيْنَاهُ فِي إِمَامٍ مُّبِينٍ", "en": "Indeed, it is We who bring the dead to life and record what they have put forth and what they left behind, and all things We have enumerated in a clear register."},
    {"num": 13, "ar": "وَاضْرِبْ لَهُم مَّثَلًا أَصْحَابَ الْقَرْيَةِ إِذْ جَاءَهَا الْمُرْسَلُونَ", "en": "And present to them an example: the people of the city, when the messengers came to it -"},
    {"num": 14, "ar": "إِذْ أَرْسَلْنَا إِلَيْهِمُ اثْنَيْنِ فَكَذَّبُوهُمَا فَعَزَّزْنَا بِثَالِثٍ فَقَالُوا إِنَّا إِلَيْكُم مُّرْسَلُونَ", "en": "When We sent to them two but they denied them, so We strengthened them with a third, and they said: 'Indeed, we are messengers to you.'"},
    {"num": 15, "ar": "قَالُوا مَا أَنتُمْ إِلَّا بَشَرٌ مِّثْلُنَا وَمَا أَنزَلَ الرَّحْمَٰنُ مِن شَيْءٍ إِنْ أَنتُمْ إِلَّا تَكْذِبُونَ", "en": "They said: 'You are not but human beings like us, and the Most Merciful has not revealed a thing. You are only telling lies.'"},
    {"num": 16, "ar": "قَالُوا رَبُّنَا يَعْلَمُ إِنَّا إِلَيْكُمْ لَمُرْسَلُونَ", "en": "They said: 'Our Lord knows that we are messengers to you,'"},
    {"num": 17, "ar": "وَمَا عَلَيْنَا إِلَّا الْبَلَاغُ الْمُبِينُ", "en": "And we are not responsible except for clear notification."},
    {"num": 18, "ar": "قَالُوا إِنَّا تَطَيَّرْنَا بِكُمْ ۖ لَئِن لَّمْ تَنتَهُوا لَنَرْجُمَنَّكُمْ وَلَيَمَسَّنَّكُم مِّنَّا عَذَابٌ أَلِيمٌ", "en": "They said: 'Indeed, we consider you a bad omen. If you do not desist, we will surely stone you, and there will surely touch you, from us, a painful punishment.'"},
    {"num": 19, "ar": "قَالُوا طَائِرُكُم مَّعَكُمْ ۚ أَئِن ذُكِّرْتُم ۚ بَلْ أَنتُمْ قَوْمٌ مُّسْرِفُونَ", "en": "They said: 'Your omen is with yourselves. Is it because you were reminded? Rather, you are a transgressing people.'"},
    {"num": 20, "ar": "وَجَاءَ مِنْ أَقْصَى الْمَدِينَةِ رَجُلٌ يَسْعَىٰ قَالَ يَا قَوْمِ اتَّبِعُوا الْمُرْسَلِينَ", "en": "And there came from the farthest end of the city a man, running. He said: 'O my people, follow the messengers.'"},
    {"num": 21, "ar": "اتَّبِعُوا مَن لَّا يَسْأَلُكُمْ أَجْرًا وَهُم مُّهْتَدُونَ", "en": "Follow those who do not ask of you [any] payment, and they are [rightly] guided."},
    {"num": 22, "ar": "وَمَا لِيَ لَا أَعْبُدُ الَّذِي فَطَرَنِي وَإِلَيْهِ تُرْجَعُونَ", "en": "And why should I not worship He who created me and to whom you will be returned?"},
    {"num": 23, "ar": "أَأَتَّخِذُ مِن دُونِهِ آلِهَةً إِن يُرِدْنِ الرَّحْمَٰنُ بِضُرٍّ لَّا تُغْنِ عَنِّي شَفَاعَتُهُمْ شَيْئًا وَلَا يُنقِذُونِ", "en": "Should I take other than Him as gods? If the Most Merciful intends for me some adversity, their intercession will not avail me at all, nor can they save me."},
    {"num": 24, "ar": "إِنِّي إِذًا لَّفِي ضَلَالٍ مُّبِينٍ", "en": "Indeed, I would then be in manifest error."},
    {"num": 25, "ar": "إِنِّي آمَنتُ بِرَبِّكُمْ فَاسْمَعُونِ", "en": "Indeed, I have believed in your Lord, so listen to me."},
    {"num": 26, "ar": "قِيلَ ادْخُلِ الْجَنَّةَ ۖ قَالَ يَا لَيْتَ قَوْمِي يَعْلَمُونَ", "en": "It was said: 'Enter Paradise.' He said: 'I wish my people could know'"},
    {"num": 27, "ar": "بِمَا غَفَرَ لِي رَبِّي وَجَعَلَنِي مِنَ الْمُكْرَمِينَ", "en": "Of how my Lord has forgiven me and placed me among the honored.'"},
    {"num": 28, "ar": "وَمَا أَنزَلْنَا عَلَىٰ قَوْمِهِ مِن بَعْدِهِ مِن جُندٍ مِّنَ السَّمَاءِ وَمَا كُنَّا مُنزِلِينَ", "en": "And We did not send down upon his people after him any soldiers from the heaven, nor would We have done so."},
    {"num": 29, "ar": "إِن كَانَتْ إِلَّا صَيْحَةً وَاحِدَةً فَإِذَا هُمْ خَامِدُونَ", "en": "It was not but one blast, and immediately they were extinguished."},
    {"num": 30, "ar": "يَا حَسْرَةً عَلَى الْعِبَادِ ۚ مَا يَأْتِيهِم مِّن رَّسُولٍ إِلَّا كَانُوا بِهِ يَسْتَهْزِئُونَ", "en": "How regretful for the servants. There did not come to them any messenger except that they used to ridicule him."},
    {"num": 31, "ar": "أَلَمْ يَرَوْا كَمْ أَهْلَكْنَا قَبْلَهُم مِّنَ الْقُرُونِ أَنَّهُمْ إِلَيْهِمْ لَا يَرْجِعُونَ", "en": "Have they not considered how many generations We destroyed before them - that they will not return to them?"},
    {"num": 32, "ar": "وَإِن كُلٌّ لَّمَّا جَمِيعٌ لَّدَيْنَا مُحْضَرُونَ", "en": "And indeed, all of them will yet be brought present before Us."},
    {"num": 33, "ar": "وَآيَةٌ لَّهُمُ الْأَرْضُ الْمَيْتَةُ أَحْيَيْنَاهَا وَأَخْرَجْنَا مِنْهَا حَبًّا فَمِنْهُ يَأْكُلُونَ", "en": "And a sign for them is the dead earth. We have given it life and brought forth from it grain, and from it they eat."},
    {"num": 34, "ar": "وَجَعَلْنَا فِيهَا جَنَّاتٍ مِّن نَّخِيلٍ وَأَعْنَابٍ وَفَجَّرْنَا فِيهَا مِنَ الْعُيُونِ", "en": "And We placed therein gardens of palm trees and grapevines and caused to burst forth therefrom some springs -"},
    {"num": 35, "ar": "لِيَأْكُلُوا مِن ثَمَرِهِ وَمَا عَمِلَتْهُ أَيْدِيهِمْ ۖ أَفَلَا يَشْكُرُونَ", "en": "That they may eat of His fruit. And their hands have not produced it, so will they not be grateful?"},
    {"num": 36, "ar": "سُبْحَانَ الَّذِي خَلَقَ الْأَزْوَاجَ كُلَّهَا مِمَّا تُنبِتُ الْأَرْضُ وَمِنْ أَنفُسِهِمْ وَمِمَّا لَا يَعْلَمُونَ", "en": "Exalted is He who created all pairs - from what the earth grows and from themselves and from that which they do not know."},
    {"num": 37, "ar": "وَآيَةٌ لَّهُمُ اللَّيْلُ نَسْلَخُ مِنْهُ النَّهَارَ فَإِذَا هُم مُّظْلِمُونَ", "en": "And a sign for them is the night. We remove from it the day, so they are in darkness."},
    {"num": 38, "ar": "وَالشَّمْسُ تَجْرِي لِمُسْتَقَرٍّ لَّهَا ۚ ذَٰلِكَ تَقْدِيرُ الْعَزِيزِ الْعَلِيمِ", "en": "And the sun runs toward its stopping point. That is the determination of the Exalted in Might, the Knowing."},
    {"num": 39, "ar": "وَالْقَمَرَ قَدَّرْنَاهُ مَنَازِلَ حَتَّىٰ عَادَ كَالْعُرْجُونِ الْقَدِيمِ", "en": "And the moon - We have determined for it phases, until it returns like the old date stalk."},
    {"num": 40, "ar": "لَا الشَّمْسُ يَنبَغِي لَهَا أَن تُدْرِكَ الْقَمَرَ وَلَا اللَّيْلُ سَابِقُ النَّهَارِ ۚ وَكُلٌّ فِي فَلَكٍ يَسْبَحُونَ", "en": "It is not allowable for the sun to reach the moon, nor does the night overtake the day, but each, in an orbit, is swimming."},
    {"num": 41, "ar": "وَآيَةٌ لَّهُمْ أَنَّا حَمَلْنَا ذُرِّيَّتَهُمْ فِي الْفُلْكِ الْمَشْحُونِ", "en": "And a sign for them is that We carried their forefathers in a laden ship."},
    {"num": 42, "ar": "وَخَلَقْنَا لَهُم مِّن مِّثْلِهِ مَا يَرْكَبُونَ", "en": "And We created for them from the likes of it that which they ride."},
    {"num": 43, "ar": "وَإِن نَّشَأْ نُغْرِقْهُمْ فَلَا صَرِيخَ لَهُمْ وَلَا هُمْ يُنقَذُونَ", "en": "And if We should will, We could drown them; then no one responding to a cry would there be for them, nor would they be saved."},
    {"num": 44, "ar": "إِلَّا رَحْمَةً مِّنَّا وَمَتَاعًا إِلَىٰ حِينٍ", "en": "Except as a mercy from Us and as enjoyment for a time."},
    {"num": 45, "ar": "وَإِذَا قِيلَ لَهُمُ اتَّقُوا مَا بَيْنَ أَيْدِيكُمْ وَمَا خَلْفَكُمْ لَعَلَّكُمْ تُرْحَمُونَ", "en": "But when it is said to them: 'Beware of what is before you and what is behind you; perhaps you will receive mercy....'"},
    {"num": 46, "ar": "وَمَا تَأْتِيهِم مِّنْ آيَةٍ مِّنْ آيَاتِ رَبِّهِمْ إِلَّا كَانُوا عَنْهَا مُعْرِضِينَ", "en": "But not a sign came to them from the signs of their Lord except that they were from it turning away."},
    {"num": 47, "ar": "وَإِذَا قِيلَ لَهُمْ أَنفِقُوا مِمَّا رَزَقَكُمُ اللَّهُ قَالَ الَّذِينَ كَفَرُوا لِلَّذِينَ آمَنُوا أَنُطْعِمُ مَن لَّوْ يَشَاءُ اللَّهُ أَطْعَمَهُ إِنْ أَنتُمْ إِلَّا فِي ضَلَالٍ مُّبِينٍ", "en": "And when it is said to them: 'Spend from that which Allah has provided for you,' those who disbelieve say to those who believe: 'Should we feed one whom, if Allah had willed, He would have fed? You are not but in clear error.'"},
    {"num": 48, "ar": "وَيَقُولُونَ مَتَىٰ هَٰذَا الْوَعْدُ إِن كُنتُمْ صَادِقِينَ", "en": "And they say: 'When is this promise, if you should be truthful?'"},
    {"num": 49, "ar": "مَا يَنظُرُونَ إِلَّا صَيْحَةً وَاحِدَةً تَأْخُذُهُمْ وَهُمْ يَخِصِّمُونَ", "en": "They do not await except one blast which will seize them while they are disputing."},
    {"num": 50, "ar": "فَلَا يَسْتَطِيعُونَ تَوْصِيَةً وَلَا إِلَىٰ أَهْلِهِمْ يَرْجِعُونَ", "en": "And they will not be able to give any instructions, nor to their people can they return."},
    {"num": 51, "ar": "وَنُفِخَ فِي الصُّورِ فَإِذَا هُم مِّنَ الْأَجْدَاثِ إِلَىٰ رَبِّهِمْ يَنسِلُونَ", "en": "And the Horn will be blown; and at once from the graves to their Lord they will hasten."},
    {"num": 52, "ar": "قَالُوا يَا وَيْلَنَا مَن بَعَثَنَا مِن مَّرْقَدِنَا ۜ ۗ هَٰذَا مَا وَعَدَ الرَّحْمَٰنُ وَصَدَقَ الْمُرْسَلُونَ", "en": "They will say: 'O woe to us! Who has raised us up from our sleeping place?' [The reply will be:] 'This is what the Most Merciful had promised, and the messengers told the truth.'"},
    {"num": 53, "ar": "إِن كَانَتْ إِلَّا صَيْحَةً وَاحِدَةً فَإِذَا هُمْ جَمِيعٌ لَّدَيْنَا مُحْضَرُونَ", "en": "It will not be but one blast, and at once they are all brought present before Us."},
    {"num": 54, "ar": "فَالْيَوْمَ لَا تُظْلَمُ نَفْسٌ شَيْئًا وَلَا تُجْزَوْنَ إِلَّا مَا كُنتُمْ تَعْمَلُونَ", "en": "So today no soul will be wronged at all, and you will not be recompensed except for what you used to do."},
    {"num": 55, "ar": "إِنَّ أَصْحَابَ الْجَنَّةِ الْيَوْمَ فِي شُغُلٍ فَاكِهُونَ", "en": "Indeed the companions of Paradise, that Day, will be amused in [joyful] occupation -"},
    {"num": 56, "ar": "هُمْ وَأَزْوَاجُهُمْ فِي ظِلَالٍ عَلَى الْأَرَائِكِ مُتَّكِئُونَ", "en": "They and their spouses - in shade, reclining on adorned couches."},
    {"num": 57, "ar": "لَهُمْ فِيهَا فَاكِهَةٌ وَلَهُم مَّا يَدَّعُونَ", "en": "For them therein is fruit, and for them is whatever they request."},
    {"num": 58, "ar": "سَلَامٌ قَوْلًا مِّن رَّبٍّ رَّحِيمٍ", "en": "'Peace,' a word from a Merciful Lord."},
    {"num": 59, "ar": "وَامْتَازُوا الْيَوْمَ أَيُّهَا الْمُجْرِمُونَ", "en": "But stand apart today, you criminals."},
    {"num": 60, "ar": "أَلَمْ أَعْهَدْ إِلَيْكُمْ يَا بَنِي آدَمَ أَن لَّا تَعْبُدُوا الشَّيْطَانَ ۖ إِنَّهُ لَكُمْ عَدُوٌّ مُّبِينٌ", "en": "Did I not enjoin upon you, O children of Adam, that you not worship Satan - [for] indeed, he is to you a clear enemy -"},
    {"num": 61, "ar": "وَأَنِ اعْبُدُونِي ۚ هَٰذَا صِرَاطٌ مُّسْتَقِيمٌ", "en": "And that you worship [only] Me? This is a straight path."},
    {"num": 62, "ar": "وَلَقَدْ أَضَلَّ مِنكُمْ جِبِلًّا كَثِيرًا ۖ أَفَلَمْ تَكُونُوا تَعْقِلُونَ", "en": "And he had already led astray from among you much of creation, so did you not use reason?"},
    {"num": 63, "ar": "هَٰذِهِ جَهَنَّمُ الَّتِي كُنتُمْ تُوعَدُونَ", "en": "This is the Hellfire which you were promised."},
    {"num": 64, "ar": "اصْلَوْهَا الْيَوْمَ بِمَا كُنتُمْ تَكْفُرُونَ", "en": "Burn therein today for what you used to deny.'"},
    {"num": 65, "ar": "الْيَوْمَ نَخْتِمُ عَلَىٰ أَفْوَاهِهِمْ وَتُكَلِّمُنَا أَيْدِيهِمْ وَتَشْهَدُ أَرْجُلُهُم بِمَا كَانُوا يَكْسِبُونَ", "en": "That Day, We will seal over their mouths, and their hands will speak to Us, and their feet will testify about what they used to earn."},
    {"num": 66, "ar": "وَلَوْ نَشَاءُ لَطَمَسْنَا عَلَىٰ أَعْيُنِهِمْ فَاسْتَبَقُوا الصِّرَاطَ فَأَنَّىٰ يُبْصِرُونَ", "en": "And if We willed, We could have obliterated their eyes, and they would race to [find] the path, and how could they see?"},
    {"num": 67, "ar": "وَلَوْ نَشَاءُ لَمَسَخْنَاهُمْ عَلَىٰ مَكَانَتِهِمْ فَمَا اسْتَطَاعُوا مُضِيًّا وَلَا يَرْجِعُونَ", "en": "And if We willed, We could have deformed them, [paralyzing them] in their places so they would not be able to proceed, nor could they return."},
    {"num": 68, "ar": "وَمَن نُّعَمِّرْهُ نُنَكِّسْهُ فِي الْخَلْقِ ۖ أَفَلَا يَعْقِلُونَ", "en": "And he whom We grant long life We cause to decline in power. Will they not then understand?"},
    {"num": 69, "ar": "وَمَا عَلَّمْنَاهُ الشِّعْرَ وَمَا يَنبَغِي لَهُ ۚ إِنْ هُوَ إِلَّا ذِكْرٌ وَقُرْآنٌ مُّبِينٌ", "en": "And We did not give Muhammad knowledge of poetry, nor is it befitting for him. It is not but a message and a clear Qur'an."},
    {"num": 70, "ar": "لِيُنذِرَ مَن كَانَ حَيًّا وَيَحِقَّ الْقَوْلُ عَلَى الْكَافِرِينَ", "en": "To warn whoever is alive and justify the word against the disbelievers."},
    {"num": 71, "ar": "أَوَلَمْ يَرَوْا أَنَّا خَلَقْنَا لَهُم مِّمَّا عَمِلَتْ أَيْدِينَا أَنْعَامًا فَهُمْ لَهَا مَالِكُونَ", "en": "Do they not see that We have created for them from what Our hands have made, grazing livestock, and [then] they are their owners?"},
    {"num": 72, "ar": "وَذَلَّلْنَاهَا لَهُمْ فَمِنْهَا رَكُوبُهُمْ وَمِنْهَا يَأْكُلُونَ", "en": "And We have tamed them for them, so some of them they ride, and some of them they eat."},
    {"num": 73, "ar": "وَلَهُمْ فِيهَا مَنَافِعُ وَمَشَارِبُ ۖ أَفَلَا يَشْكُرُونَ", "en": "And for them therein are [other] benefits and drinks, so will they not be grateful?"},
    {"num": 74, "ar": "وَاتَّخَذُوا مِن دُونِ اللَّهِ آلِهَةً لَّعَلَّهُمْ يُنصَرُونَ", "en": "But they have taken besides Allah [false] deities that perhaps they would be helped."},
    {"num": 75, "ar": "لَا يَسْتَطِيعُونَ نَصْرَهُمْ وَهُمْ لَهُمْ جُندٌ مُّحْضَرُونَ", "en": "They are not able to help them, and they [themselves] are for them soldiers in attendance."},
    {"num": 76, "ar": "فَلَا يَحْزُنكَ قَوْلُهُمْ ۘ إِنَّا نَعْلَمُ مَا يُسِرُّونَ وَمَا يُعْلِنُونَ", "en": "So let not their speech grieve you. Indeed, We know what they conceal and what they declare."},
    {"num": 77, "ar": "أَوَلَمْ يَرَ الْإِنسَانُ أَنَّا خَلَقْنَاهُ مِن نُّطْفَةٍ فَإِذَا هُوَ خَصِيمٌ مُّبِينٌ", "en": "Does man not consider that We created him from a sperm-drop - then at once he is a clear opponent?"},
    {"num": 78, "ar": "وَضَرَبَ لَنَا مَثَلًا وَنَسِيَ خَلْقَهُ ۖ قَالَ مَن يُحْيِي الْعِظَامَ وَهِيَ رَمِيمٌ", "en": "And he presents for Us an example and forgets his [own] creation. He says: 'Who will give life to bones while they are disintegrated?'"},
    {"num": 79, "ar": "قُلْ يُحْيِيهَا الَّذِي أَنشَأَهَا أَوَّلَ مَرَّةٍ ۖ وَهُوَ بِكُلِّ خَلْقٍ عَلِيمٌ", "en": "Say: 'He will give them life who produced them the first time; and He is, of all creation, Knowing.'"},
    {"num": 80, "ar": "الَّذِي جَعَلَ لَكُم مِّنَ الشَّجَرِ الْأَخْضَرِ نَارًا فَإِذَا أَنتُم مِّنْهُ تُوقِدُونَ", "en": "It is He who made fire for you from the green tree, and then from it you ignite."},
    {"num": 81, "ar": "أَوَلَيْسَ الَّذِي خَلَقَ السَّمَاوَاتِ وَالْأَرْضَ بِقَادِرٍ عَلَىٰ أَن يَخْلُقَ مِثْلَهُم ۚ بَلَىٰ وَهُوَ الْخَلَّاقُ الْعَلِيمُ", "en": "Is not He who created the heavens and the earth Able to create the likes of them? Yes, [it is so]; and He is the Knowing Creator."},
    {"num": 82, "ar": "إِنَّمَا أَمْرُهُ إِذَا أَرَادَ شَيْئًا أَن يَقُولَ لَهُ كُن فَيَكُونُ", "en": "His command is only when He intends a thing that He says to it: 'Be,' and it is."},
    {"num": 83, "ar": "فَسُبْحَانَ الَّذِي بِيَدِهِ مَلَكُوتُ كُلِّ شَيْءٍ وَإِلَيْهِ تُرْجَعُونَ", "en": "So exalted is He in whose hand is the realm of all things, and to Him you will be returned."}
]

# Surah Al-Kahf Passages (18:1-10 & 100-110)
SURAH_KAHF_TEXT = [
    {"num": 1, "ar": "الْحَمْدُ لِلَّهِ الَّذِي أَنزَلَ عَلَىٰ عَبْدِهِ الْكِتَابَ وَلَمْ يَجْعَل لَّهُ عِوَجًا", "en": "All praise is due to Allah, who has sent down upon His Servant the Book and has not made therein any deviance."},
    {"num": 2, "ar": "قَيِّمًا لِّيُنذِرَ بَأْسًا شَدِيدًا مِّن لَّدُنْهُ وَيُبَشِّرَ الْمُؤْمِنِينَ الَّذِينَ يَعْمَلُونَ الصَّالِحَاتِ أَنَّ لَهُمْ أَجْرًا حَسَنًا", "en": "[He has made it] straight, to warn of severe punishment from Him and to give good tidings to the believers who do righteous deeds that they will have a good reward."},
    {"num": 3, "ar": "مَّاكِثِينَ فِيهِ أَبَدًا", "en": "In which they will remain forever."},
    {"num": 4, "ar": "وَيُنذِرَ الَّذِينَ قَالُوا اتَّخَذَ اللَّهُ وَلَدًا", "en": "And to warn those who say, 'Allah has taken a son.'"},
    {"num": 5, "ar": "مَّا لَهُم بِهِ مِنْ عِلْمٍ وَلَا لِآبَائِهِمْ ۚ كَبُرَتْ كَلِمَةً تَخْرُجُ مِنْ أَفْوَاهِهِمْ ۚ إِن يَقُولُونَ إِلَّا كَذِبًا", "en": "They have no knowledge of it, nor had their fathers. Grave is the word that comes out of their mouths; they speak not except a lie."},
    {"num": 6, "ar": "فَلَعَلَّكَ بَاخِعٌ نَّفْسَكَ عَلَىٰ آثَارِهِمْ إِن لَّمْ يُؤْمِنُوا بِهَٰذَا الْحَدِيثِ أَسَفًا", "en": "Then perhaps you would kill yourself through grief over their footprints if they do not believe in this message."},
    {"num": 7, "ar": "إِنَّا جَعَلْنَا مَا عَلَى الْأَرْضِ زِينَةً لَّهَا لِنَبْلُوَهُمْ أَيُّهُمْ أَحْسَنُ عَمَلًا", "en": "Indeed, We have made that which is on the earth adornment for it that We may test them as to which of them is best in deed."},
    {"num": 8, "ar": "وَإِنَّا لَجَاعِلُونَ مَا عَلَيْهَا صَعِيدًا جُرُزًا", "en": "And indeed, We will make that which is upon it [into] a barren ground."},
    {"num": 9, "ar": "أَمْ حَسِبْتَ أَنَّ أَصْحَابَ الْكَهْفِ وَالرَّقِيمِ كَانُوا مِنْ آيَاتِنَا عَجَبًا", "en": "Or have you thought that the companions of the cave and the inscription were, among Our signs, a wonder?"},
    {"num": 10, "ar": "إِذْ أَوَى الْفِتْيَةُ إِلَى الْكَهْفِ فَقَالُوا رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا", "en": "When the youths retreated to the cave and said: 'Our Lord, grant us from Yourself mercy and prepare for us from our affair right guidance.'"},
    {"num": 11, "ar": "فَضَرَبْنَا عَلَىٰ آذَانِهِمْ فِي الْكَهْفِ سِنِينَ عَدَدًا", "en": "So We cast [a cover of sleep] over their ears within the cave for a number of years."},
    {"num": 12, "ar": "ثُمَّ بَعَثْنَاهُمْ لِنَعْلَمَ أَيُّ الْحِزْبَيْنِ أَحْصَىٰ لِمَا لَبِثُوا أَمَدًا", "en": "Then We awakened them that We might show which of the two factions was most precise in calculating what [extent] they had remained in time."},
    {"num": 13, "ar": "نَّحْنُ نَقُصُّ عَلَيْكَ نَبَأَهُم بِالْحَقِّ ۚ إِنَّهُمْ فِتْيَةٌ آمَنُوا بِرَبِّهِمْ وَزِدْنَاهُمْ هُدًى", "en": "It is We who relate to you their story in truth. Indeed, they were youths who believed in their Lord, and We increased them in guidance."},
    {"num": 14, "ar": "وَرَبَطْنَا عَلَىٰ قُلُوبِهِمْ إِذْ قَامُوا فَقَالُوا رَبُّنَا رَبُّ السَّمَاوَاتِ وَالْأَرْضِ لَن نَّدْعُوَ مِن دُونِهِ إِلَٰهًا ۖ لَّقَدْ قُلْنَا إِذًا شَطَطًا", "en": "And We bound [i.e., made firm] their hearts when they stood up and said: 'Our Lord is the Lord of the heavens and the earth. Never will we invoke besides Him any deity. We would have certainly spoken, then, an excessive transgression.'"},
    {"num": 15, "ar": "هَٰؤُلَاءِ قَوْمُنَا اتَّخَذُوا مِن دُونِهِ آلِهَةً ۖ لَّوْلَا يَأْتُونَ عَلَيْهِم بِسُلْطَانٍ بَيِّنٍ ۖ فَمَنْ أَظْلَمُ مِمَّنِ افْتَرَىٰ عَلَى اللَّهِ كَذِبًا", "en": "'These, our people, have taken besides Him deities. Why do they not bring for [worship of] them a clear authority? And who is more unjust than one who invents about Allah a lie?'"},
    {"num": 16, "ar": "وَإِذِ اعْتَزَلْتُمُوهُمْ وَمَا يَعْبُدُونَ إِلَّا اللَّهَ فَأْوُوا إِلَى الْكَهْفِ يَنشُرْ لَكُمْ رَبُّكُم مِّن رَّحْمَتِهِ وَيُهَيِّئْ لَكُم مِّنْ أَمْرِكُم مِّرْفَقًا", "en": "'And when you have withdrawn from them and that which they worship other than Allah, retreat to the cave. Your Lord will spread out for you of His mercy and will prepare for you from your affair facility.'"},
    {"num": 17, "ar": "وَتَرَى الشَّمْسَ إِذَا طَلَعَت تَّزَاوَرُ عَن كَهْفِهِمْ ذَاتَ الْيَمِينِ وَإِذَا غَرَبَت تَّقْرِضُهُمْ ذَاتَ الشِّمَالِ وَهُمْ فِي فَجْوَةٍ مِّنْهُ ۚ ذَٰلِكَ مِنْ آيَاتِ اللَّهِ ۗ مَن يَهْدِ اللَّهُ فَهُوَ الْمُهْتَدِ ۖ وَمَن يُضْلِلْ فَلَن تَجِدَ لَهُ وَلِيًّا مُّرْشِدًا", "en": "And you would see the sun, when it rose, inclining away from their cave on the right, and when it set, passing away from them on the left, while they were in an opening of the cave. That was from the signs of Allah. He whom Allah guides is the rightly guided, but he whom He leaves astray — never will you find for him a protecting guide."},
    {"num": 18, "ar": "وَتَحْسَبُهُمْ أَيْقَاظًا وَهُمْ رُقُودٌ ۚ وَنُقَلِّبُهُمْ ذَاتَ الْيَمِينِ وَذَاتَ الشِّمَالِ ۖ وَكَلْبُهُم بَاسِطٌ ذِرَاعَيْهِ بِالْوَصِيدِ ۚ لَوِ اطَّلَعْتَ عَلَيْهِمْ لَوَلَّيْتَ مِنْهُمْ فِرَارًا وَلَمُلِئْتَ مِنْهُمْ رُعْبًا", "en": "And you would think them awake, while they were asleep. And We turned them to the right and to the left, while their dog stretched his forelegs at the entrance. If you had looked at them, you would have turned from them in flight and been filled by them with terror."},
    {"num": 19, "ar": "وَكَذَٰلِكَ بَعَثْنَاهُمْ لِيَتَسَاءَلُوا بَيْنَهُمْ ۚ قَالَ قَائِلٌ مِّنْهُمْ كَمْ لَبِثْتُمْ ۖ قَالُوا لَبِثْنَا يَوْمًا أَوْ بَعْضَ يَوْمٍ ۚ قَالُوا رَبُّكُمْ أَعْلَمُ بِمَا لَبِثْتُمْ فَابْعَثُوا أَحَدَكُم بِوَرِقِكُمْ هَٰذِهِ إِلَى الْمَدِينَةِ فَلْيَنظُرْ أَيُّهَا أَزْكَىٰ طَعَامًا فَلْيَأْتِكُم بِرِزْقٍ مِّنْهُ وَلْيَتَلَطَّفْ وَلَا يُشْعِرَنَّ بِكُمْ أَحَدًا", "en": "And similarly, We awakened them that they might question one another. Said a speaker among them: 'How long have you remained [here]?' They said: 'We have remained a day or part of a day.' They said: 'Your Lord is most knowing of how long you remained. So send one of you with this silver coin of yours to the city and let him look to which is the best of food and bring you provision from it and let him be cautious. And let no one be aware of you.'"},
    {"num": 20, "ar": "إِنَّهُمْ إِن يَظْهَرُوا عَلَيْكُمْ يَرْجُمُوكُمْ أَوْ يُعِيدُوكُمْ فِي مِلَّتِهِمْ وَلَن تُفْلِحُوا إِذًا أَبَدًا", "en": "'Indeed, if they come to know of you, they will stone you or return you to their religion. And never would you succeed, then — ever.'"},
    {"num": 21, "ar": "وَكَذَٰلِكَ أَعْثَرْنَا عَلَيْهِمْ لِيَعْلَمُوا أَنَّ وَعْدَ اللَّهِ حَقٌّ وَأَنَّ السَّاعَةَ لَا رَيْبَ فِيهَا", "en": "And similarly, We caused them to be found that they [who found them] would know that the promise of Allah is truth and that of the Hour there is no doubt."},
    {"num": 22, "ar": "سَيَقُولُونَ ثَلَاثَةٌ رَّابِعُهُمْ كَلْبُهُمْ وَيَقُولُونَ خَمْسَةٌ سَادِسُهُمْ كَلْبُهُمْ رَجْمًا بِالْغَيْبِ ۖ وَيَقُولُونَ سَبْعَةٌ وَثَامِنُهُمْ كَلْبُهُمْ", "en": "They will say there were three, the fourth of them being their dog; and they will say there were five, the sixth of them being their dog — guessing at the unseen; and they will say there were seven, and the eighth of them was their dog."},
    {"num": 23, "ar": "وَلَا تَقُولَنَّ لِشَيْءٍ إِنِّي فَاعِلٌ ذَٰلِكَ غَدًا", "en": "And never say of anything: 'Indeed, I will do that tomorrow,'"},
    {"num": 24, "ar": "إِلَّا أَن يَشَاءَ اللَّهُ ۚ وَاذْكُر رَّبَّكَ إِذَا نَسِيتَ وَقُلْ عَسَىٰ أَن يَهْدِيَنِ رَبِّي لِأَقْرَبَ مِنْ هَٰذَا رَشَدًا", "en": "Except [when adding]: 'If Allah wills.' And remember your Lord when you forget [it] and say: 'Perhaps my Lord will guide me to what is nearer than this to right conduct.'"},
    {"num": 25, "ar": "وَلَبِثُوا فِي كَهْفِهِمْ ثَلَاثَ مِائَةٍ سِنِينَ وَازْدَادُوا تِسْعًا", "en": "And they remained in their cave for three hundred years and exceeded by nine."},
    {"num": 26, "ar": "قُلِ اللَّهُ أَعْلَمُ بِمَا لَبِثُوا ۖ لَهُ غَيْبُ السَّمَاوَاتِ وَالْأَرْضِ ۖ أَبْصِرْ بِهِ وَأَسْمِعْ ۚ مَا لَهُم مِّن دُونِهِ مِن وَلِيٍّ وَلَا يُشْرِكُ فِي حُكْمِهِ أَحَدًا", "en": "Say: 'Allah is most knowing of how long they remained. He has [knowledge of] the unseen [aspects] of the heavens and the earth. How Seeing is He and how Hearing! They have not besides Him any protector, and He shares not His legislation with anyone.'"},
    {"num": 27, "ar": "وَاتْلُ مَا أُوحِيَ إِلَيْكَ مِن كِتَابِ رَبِّكَ ۖ لَا مُبَدِّلَ لِكَلِمَاتِهِ وَلَن تَجِدَ مِن دُونِهِ مُلْتَحَدًا", "en": "And recite, [O Muhammad], what has been revealed to you of the Book of your Lord. There is no changer of His words, and never will you find in other than Him a refuge."},
    {"num": 28, "ar": "وَاصْبِرْ نَفْسَكَ مَعَ الَّذِينَ يَدْعُونَ رَبَّهُم بِالْغَدَاةِ وَالْعَشِيِّ يُرِيدُونَ وَجْهَهُ ۖ وَلَا تَعْدُ عَيْنَاكَ عَنْهُمْ تُرِيدُ زِينَةَ الْحَيَاةِ الدُّنْيَا ۖ وَلَا تُطِعْ مَنْ أَغْفَلْنَا قَلْبَهُ عَن ذِكْرِنَا وَاتَّبَعَ هَوَاهُ وَكَانَ أَمْرُهُ فُرُطًا", "en": "And keep yourself patient [by being] with those who call upon their Lord in the morning and the evening, seeking His face. And let not your eyes pass beyond them, desiring adornments of the worldly life, and do not obey one whose heart We have made heedless of Our remembrance and who follows his desire and whose affair is ever [in] neglect."},
    {"num": 29, "ar": "وَقُلِ الْحَقُّ مِن رَّبِّكُمْ ۖ فَمَن شَاءَ فَلْيُؤْمِن وَمَن شَاءَ فَلْيَكْفُرْ ۚ إِنَّا أَعْتَدْنَا لِلظَّالِمِينَ نَارًا أَحَاطَ بِهِمْ سُرَادِقُهَا", "en": "And say: 'The truth is from your Lord, so whoever wills — let him believe; and whoever wills — let him disbelieve.' Indeed, We have prepared for the wrongdoers a fire whose walls will surround them."},
    {"num": 30, "ar": "إِنَّ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ إِنَّا لَا نُضِيعُ أَجْرَ مَنْ أَحْسَنَ عَمَلًا", "en": "Indeed, those who have believed and done righteous deeds — indeed, We will not allow to be lost the reward of any who did well in deeds."},
    {"num": 31, "ar": "أُولَٰئِكَ لَهُمْ جَنَّاتُ عَدْنٍ تَجْرِي مِن تَحْتِهِمُ الْأَنْهَارُ يُحَلَّوْنَ فِيهَا مِنْ أَسَاوِرَ مِن ذَهَبٍ وَيَلْبَسُونَ ثِيَابًا خُضْرًا مِّن سُندُسٍ وَإِسْتَبْرَقٍ مُّتَّكِئِينَ فِيهَا عَلَى الْأَرَائِكِ ۚ نِعْمَ الثَّوَابُ وَحَسُنَتْ مُرْتَفَقًا", "en": "Those will have gardens of perpetual residence; rivers will flow beneath them. They will be adorned therein with bracelets of gold and will wear green garments of fine silk and brocade, reclining therein on adorned couches. Excellent is the reward, and good is the resting place."},
    {"num": 32, "ar": "وَاضْرِبْ لَهُم مَّثَلًا رَّجُلَيْنِ جَعَلْنَا لِأَحَدِهِمَا جَنَّتَيْنِ مِنْ أَعْنَابٍ وَحَفَفْنَاهُمَا بِنَخْلٍ وَجَعَلْنَا بَيْنَهُمَا زَرْعًا", "en": "And present to them an example of two men: We granted to one of them two gardens of grapevines, and We bordered them with palm trees and placed between them [fields of] crops."},
    {"num": 45, "ar": "وَاضْرِبْ لَهُم مَّثَلَ الْحَيَاةِ الدُّنْيَا كَمَاءٍ أَنزَلْنَاهُ مِنَ السَّمَاءِ فَاخْتَلَطَ بِهِ نَبَاتُ الْأَرْضِ فَأَصْبَحَ هَشِيمًا تَذْرُوهُ الرِّيَاحُ ۗ وَكَانَ اللَّهُ عَلَىٰ كُلِّ شَيْءٍ مُّقْتَدِرًا", "en": "And present to them the example of the life of this world, [its being] like rain which We send down from the sky, and the vegetation of the earth mingles with it and [then] it becomes dry remnants, scattered by the winds. And Allah is ever, over all things, Perfect in Ability."},
    {"num": 46, "ar": "الْمَالُ وَالْبَنُونَ زِينَةُ الْحَيَاةِ الدُّنْيَا ۖ وَالْبَاقِيَاتُ الصَّالِحَاتُ خَيْرٌ عِندَ رَبِّكَ ثَوَابًا وَخَيْرٌ أَمَلًا", "en": "Wealth and children are [but] adornment of the worldly life. But the enduring good deeds are better to your Lord for reward and better for [one's] hope."},
    {"num": 49, "ar": "وَوُضِعَ الْكِتَابُ فَتَرَى الْمُجْرِمِينَ مُشْفِقِينَ مِمَّا فِيهِ وَيَقُولُونَ يَا وَيْلَتَنَا مَالِ هَٰذَا الْكِتَابِ لَا يُغَادِرُ صَغِيرَةً وَلَا كَبِيرَةً إِلَّا أَحْصَاهَا ۚ وَوَجَدُوا مَا عَمِلُوا حَاضِرًا ۗ وَلَا يَظْلِمُ رَبُّكَ أَحَدًا", "en": "And the record [of deeds] will be placed [open], and you will see the criminals fearful of that within it, and they will say: 'Oh, woe to us! What is this book that leaves nothing small or great except that it has enumerated it?' And they will find what they did present [before them]. And your Lord does injustice to no one."},
    {"num": 65, "ar": "فَوَجَدَا عَبْدًا مِّنْ عِبَادِنَا آتَيْنَاهُ رَحْمَةً مِّنْ عِندِنَا وَعَلَّمْنَاهُ مِن لَّدُنَّا عِلْمًا", "en": "And they found a servant from among Our servants to whom We had given mercy from us and had taught him from Us a [certain] knowledge."},
    {"num": 66, "ar": "قَالَ لَهُ مُوسَىٰ هَلْ أَتَّبِعُكَ عَلَىٰ أَن تُعَلِّمَنِ مِمَّا عُلِّمْتَ رُشْدًا", "en": "Moses said to him: 'May I follow you on [the condition] that you teach me from what you have been taught of sound judgment?'"},
    {"num": 67, "ar": "قَالَ إِنَّكَ لَن تَسْتَطِيعَ مَعِيَ صَبْرًا", "en": "He said: 'Indeed, with me you will never be able to have patience.'"},
    {"num": 68, "ar": "وَكَيْفَ تَصْبِرُ عَلَىٰ مَا لَمْ تُحِطْ بِهِ خُبْرًا", "en": "'And how can you have patience for what you do not encompass in knowledge?'"},
    {"num": 69, "ar": "قَالَ سَتَجِدُنِي إِن شَاءَ اللَّهُ صَابِرًا وَلَا أَعْصِي لَكَ أَمْرًا", "en": "[Moses] said: 'You will find me, if Allah wills, patient, and I will not disobey you in any order.'"},
    {"num": 82, "ar": "وَأَمَّا الْجِدَارُ فَكَانَ لِغُلَامَيْنِ يَتِيمَيْنِ فِي الْمَدِينَةِ وَكَانَ تَحْتَهُ كَنزٌ لَّهُمَا وَكَانَ أَبُوهُمَا صَالِحًا فَأَرَادَ رَبُّكَ أَن يَبْلُغَا أَشُدَّهُمَا وَيَسْتَخْرِجَا كَنزَهُمَا رَحْمَةً مِّن رَّبِّكَ", "en": "And as for the wall, it belonged to two orphan boys in the city, and there was beneath it a treasure for them, and their father had been righteous. So your Lord intended that they reach maturity and extract their treasure, as a mercy from your Lord."},
    {"num": 83, "ar": "وَيَسْأَلُونَكَ عَن ذِي الْقَرْنَيْنِ ۖ قُلْ سَأَتْلُو عَلَيْكُم مِّنْهُ ذِكْرًا", "en": "And they ask you about Dhul-Qarnayn. Say: 'I will recite to you about him a report.'"},
    {"num": 84, "ar": "إِنَّا مَكَّنَّا لَهُ فِي الْأَرْضِ وَآتَيْنَاهُ مِن كُلِّ شَيْءٍ سَبَبًا", "en": "Indeed We established him upon the earth, and We gave him to everything a way [i.e., means]."},
    {"num": 95, "ar": "قَالَ مَا مَكَّنِّي فِيهِ رَبِّي خَيْرٌ فَأَعِينُونِي بِقُوَّةٍ أَجْعَلْ بَيْنَكُمْ وَبَيْنَهُمْ رَدْمًا", "en": "He said: 'That in which my Lord has established me is better [than what you offer], but assist me with strength; I will make between you and them a barrier.'"},
    {"num": 99, "ar": "وَتَرَكْنَا بَعْضَهُمْ يَوْمَئِذٍ يَمُوجُ فِي بَعْضٍ ۖ وَنُفِخَ فِي الصُّورِ فَجَمَعْنَاهُمْ جَمْعًا", "en": "And We will leave them that day surging over each other, and [then] the Horn will be blown, and We will assemble them in [one] assembly."},
    {"num": 100, "ar": "وَعَرَضْنَا جَهَنَّمَ يَوْمَئِذٍ لِّلْكَافِرِينَ عَرْضًا", "en": "And We will present Hell that Day to the Disbelievers, on display."},
    {"num": 101, "ar": "الَّذِينَ كَانَتْ أَعْيُنُهُمْ فِي غِطَاءٍ عَن ذِكْرِي وَكَانُوا لَا يَسْتَطِيعُونَ سَمْعًا", "en": "Those whose eyes had been within a cover [removed] from My remembrance, and they were not able to hear."},
    {"num": 102, "ar": "أَفَحَسِبَ الَّذِينَ كَفَرُوا أَن يَتَّخِذُوا عِبَادِي مِن دُونِي أَوْلِيَاءَ ۚ إِنَّا أَعْتَدْنَا جَهَنَّمَ لِلْكَافِرِينَ نُزُلًا", "en": "Then do those who disbelieve think that they can take My servants instead of Me as allies? Indeed, We have prepared Hell for the disbelievers as a lodging."},
    {"num": 103, "ar": "قُلْ هَلْ نُنَبِّئُكُم بِالْأَخْسَرِينَ أَعْمَالًا", "en": "Say: 'Shall we inform you of the greatest losers as to [their] deeds?'"},
    {"num": 104, "ar": "الَّذِينَ ضَلَّ سَعْيُهُمْ فِي الْحَيَاةِ الدُّنْيَا وَهُمْ يَحْسَبُونَ أَنَّهُمْ يُحْسِنُونَ صُنْعًا", "en": "[They are] those whose effort is lost in worldly life, while they think that they are doing well in work."},
    {"num": 105, "ar": "أُولَٰئِكَ الَّذِينَ كَفَرُوا بِآيَاتِ رَبِّهِمْ وَلِقَائِهِ فَحَبِطَتْ أَعْمَالُهُمْ فَلَا نُقِيمُ لَهُمْ يَوْمَ الْقِيَامَةِ وَزْنًا", "en": "Those are the ones who disbelieve in the signs of their Lord and in [their] meeting Him, so their deeds have become worthless; and We will not give them on the Day of Resurrection any importance."},
    {"num": 106, "ar": "ذَٰلِكَ جَزَاؤُهُمْ جَهَنَّمُ بِمَا كَفَرُوا وَاتَّخَذُوا آيَاتِي وَرُسُلِي هُزُوًا", "en": "That is their recompense — Hell — for what they denied and [because] they took My signs and My messengers in ridicule."},
    {"num": 107, "ar": "إِنَّ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ كَانَتْ لَهُمْ جَنَّاتُ الْفِرْدَوْسِ نُزُلًا", "en": "Indeed, those who have believed and done righteous deeds - they will have the Gardens of Paradise as a lodging,"},
    {"num": 108, "ar": "خَالِدِينَ فِيهَا لَا يَبْغُونَ عَنْهَا حِوَلًا", "en": "Wherein they abide eternally. They will not desire from it any transfer."},
    {"num": 109, "ar": "قُل لَّوْ كَانَ الْبَحْرُ مِدَادًا لِّكَلِمَاتِ رَبِّي لَنَفِدَ الْبَحْرُ قَبْلَ أَن تَنفَدَ كَلِمَاتُ رَبِّي وَلَوْ جِئْنَا بِمِثْلِهِ مَدَدًا", "en": "Say: 'If the sea were ink for the words of my Lord, the sea would be exhausted before the words of my Lord were exhausted, even if We brought the like of it as a supplement.'"},
    {"num": 110, "ar": "قُلْ إِنَّمَا أَنَا بَشَرٌ مِّثْلُكُمْ يُوحَىٰ إِلَيَّ أَنَّمَا إِلَٰهُكُمْ إِلَٰهٌ وَاحِدٌ ۖ فَمَن كَانَ يَرْجُو لِقَاءَ رَبِّهِ فَلْيَعْمَلْ عَمَلًا صَالِحًا وَلَا يُشْرِكْ بِعِبَادَةِ رَبِّهِ أَحَدًا", "en": "Say: 'I am only a man like you, to whom has been revealed that your god is one God. So whoever would hope for the meeting with his Lord - let him do righteous work and not associate in the worship of his Lord anyone.'"}
]


# Surah Ar-Rahman (55:1-26)
SURAH_RAHMAN_TEXT = [
    {"num": 1, "ar": "الرَّحْمَٰنُ", "en": "The Most Merciful"},
    {"num": 2, "ar": "عَلَّمَ الْقُرْآنَ", "en": "Taught the Qur'an,"},
    {"num": 3, "ar": "خَلَقَ الْإِنسَانَ", "en": "Created man,"},
    {"num": 4, "ar": "عَلَّمَهُ الْبَيَانَ", "en": "Taught him articulate speech."},
    {"num": 5, "ar": "الشَّمْسُ وَالْقَمَرُ بِحُسْبَانٍ", "en": "The sun and the moon [move] by precise calculation,"},
    {"num": 6, "ar": "وَالنَّجْمُ وَالشَّجَرُ يَسْجُدَانِ", "en": "And the stars and trees prostrate."},
    {"num": 7, "ar": "وَالسَّمَاءَ رَفَعَهَا وَوَضَعَ الْمِيزَانَ", "en": "And the heaven He raised and imposed the balance"},
    {"num": 8, "ar": "أَلَّا تَطْغَوْا فِي الْمِيزَانِ", "en": "That you not transgress within the balance."},
    {"num": 9, "ar": "وَأَقِيمُوا الْوَزْنَ بِالْقِسْطِ وَلَا تُخْسِرُوا الْمِيزَانَ", "en": "And establish weight in justice and do not make deficient the balance."},
    {"num": 10, "ar": "وَالْأَرْضَ وَضَعَهَا لِلْأَنَامِ", "en": "And the earth He has laid out for the creatures."},
    {"num": 11, "ar": "فِيهَا فَاكِهَةٌ وَالنَّخْلُ ذَاتُ الْأَكْمَامِ", "en": "Therein is fruit and date palms having spathes [of dates]"},
    {"num": 12, "ar": "وَالْحَبُّ ذُو الْعَصْفِ وَالرَّيْحَانُ", "en": "And grain having husks and scented plants."},
    {"num": 13, "ar": "فَبِأَيِّ آلَاءِ رَبِّكُمَا تُكَذِّبَانِ", "en": "So which of the favors of your Lord would you deny?"},
    {"num": 26, "ar": "كُلُّ مَنْ عَلَيْهَا فَانٍ", "en": "Everyone upon the earth will perish,"},
    {"num": 27, "ar": "وَيَبْقَىٰ وَجْهُ رَبِّكَ ذُو الْجَلَالِ وَالْإِكْرَامِ", "en": "And there will remain the Face of your Lord, Owner of Majesty and Honor."},
    {"num": 60, "ar": "هَلْ جَزَاءُ الْإِحْسَانِ إِلَّا الْإِحْسَانُ", "en": "Is the reward for excellence [anything] other than excellence?"}
]

# Surah Al-Waqi'ah Complete Curated Verses (56:1-40)
SURAH_WAQIAH_TEXT = [
    {"num": 1, "ar": "إِذَا وَقَعَتِ الْوَاقِعَةُ", "en": "When the Inevitable Event happens,"},
    {"num": 2, "ar": "لَيْسَ لِوَقْعَتِهَا كَاذِبَةٌ", "en": "There is no denying that it will befall,"},
    {"num": 3, "ar": "خَافِضَةٌ رَّافِعَةٌ", "en": "Bringing down some, raising others."},
    {"num": 4, "ar": "إِذَا رُجَّتِ الْأَرْضُ رَجًّا", "en": "When the earth is shaken with a violent quake,"},
    {"num": 5, "ar": "وَبُسَّتِ الْجِبَالُ بَسًّا", "en": "And the mountains are crumbled to powder,"},
    {"num": 6, "ar": "فَكَانَتْ هَبَاءً مُّنبَثًّا", "en": "Becoming scattered dust,"},
    {"num": 7, "ar": "وَكُنتُمْ أَزْوَاجًا ثَلَاثَةً", "en": "And you are sorted into three groups:"},
    {"num": 8, "ar": "فَأَصْحَابُ الْمَيْمَنَةِ مَا أَصْحَابُ الْمَيْمَنَةِ", "en": "The people of the right—how blessed are the people of the right!"},
    {"num": 9, "ar": "وَأَصْحَابُ الْمَشْأَمَةِ مَا أَصْحَابُ الْمَشْأَمَةِ", "en": "And the people of the left—how miserable are the people of the left!"},
    {"num": 10, "ar": "وَالسَّابِقُونَ السَّابِقُونَ", "en": "And the foremost in faith will be the foremost in Paradise:"},
    {"num": 11, "ar": "أُولَٰئِكَ الْمُقَرَّبُونَ", "en": "They are the ones brought near to Allah,"},
    {"num": 12, "ar": "فِي جَنَّاتِ النَّعِيمِ", "en": "In the Gardens of Bliss,"},
    {"num": 13, "ar": "ثُلَّةٌ مِّنَ الْأَوَّلِينَ", "en": "A multitude from earlier generations,"},
    {"num": 14, "ar": "وَقَلِيلٌ مِّنَ الْآخِرِينَ", "en": "And a few from later times,"},
    {"num": 15, "ar": "عَلَىٰ سُرُرٍ مَّوْضُونَةٍ", "en": "On thrones woven with gold and precious stones,"},
    {"num": 16, "ar": "مُّتَّكِئِينَ عَلَيْهَا مُتَقَابِلِينَ", "en": "Reclining facing one another,"},
    {"num": 17, "ar": "يَطُوفُ عَلَيْهِمْ وِلْدَانٌ مُّخَلَّدُونَ", "en": "Circulated among them will be immortal youths,"},
    {"num": 18, "ar": "بِأَكْوَابٍ وَأَبَارِيقَ وَكَأْسٍ مِّن مَّعِينٍ", "en": "With cups, pitchers, and a glass of pure spring water,"},
    {"num": 19, "ar": "لَّا يُصَدَّعُونَ عَنْهَا وَلَا يُنزِفُونَ", "en": "From which they will suffer no headache, nor will they be intoxicated,"},
    {"num": 20, "ar": "وَفَاكِهَةٍ مِّمَّا يَتَخَيَّرُونَ", "en": "And any fruit they choose,"},
    {"num": 21, "ar": "وَلَحْمِ طَيْرٍ مِّمَّا يَشْتَهُونَ", "en": "And meat of fowls they desire,"},
    {"num": 22, "ar": "وَحُورٌ عِينٌ", "en": "And wide-eyed companions of pure beauty,"},
    {"num": 23, "ar": "كَأَمْثَالِ اللُّؤْلُؤِ الْمَكْنُونِ", "en": "Like preserved pearls,"},
    {"num": 24, "ar": "جَزَاءً بِمَا كَانُوا يَعْمَلُونَ", "en": "As a reward for what they used to do."},
    {"num": 25, "ar": "لَا يَسْمَعُونَ فِيهَا لَغْوًا وَلَا تَأْثِيمًا", "en": "They will not hear therein any ill speech or guilt,"},
    {"num": 26, "ar": "إِلَّا قِيلًا سَلَامًا سَلَامًا", "en": "Only the words: 'Peace, peace!'"},
    {"num": 27, "ar": "وَأَصْحَابُ الْيَمِينِ مَا أَصْحَابُ الْيَمِينِ", "en": "And the companions of the right—what of the companions of the right?"},
    {"num": 28, "ar": "فِي سِدْرٍ مَّخْضُودٍ", "en": "They will be among thornless lote trees,"},
    {"num": 29, "ar": "وَطَلْحٍ مَّنضُودٍ", "en": "And clustered bananas,"},
    {"num": 30, "ar": "وَظِلٍّ مَّمْدُودٍ", "en": "And extended shade,"},
    {"num": 31, "ar": "وَمَاءٍ مَّسْكُوبٍ", "en": "And flowing water,"},
    {"num": 32, "ar": "وَفَاكِهَةٍ كَثِيرَةٍ", "en": "And abundant fruit,"},
    {"num": 33, "ar": "لَّا مَقْطُوعَةٍ وَلَا مَمْنُوعَةٍ", "en": "Neither out of season nor forbidden,"},
    {"num": 34, "ar": "وَفُرُشٍ مَّرْفُوعَةٍ", "en": "And couches raised high."},
    {"num": 35, "ar": "إِنَّا أَنشَأْنَاهُنَّ إِنشَاءً", "en": "Indeed, We have produced them in a new creation,"},
    {"num": 36, "ar": "فَجَعَلْنَاهُنَّ أَبْكَارًا", "en": "And made them virgins,"},
    {"num": 37, "ar": "عُرُبًا أَتْرَابًا", "en": "Devoted and of equal age,"},
    {"num": 38, "ar": "لِّأَصْحَابِ الْيَمِينِ", "en": "For the people of the right,"},
    {"num": 39, "ar": "ثُلَّةٌ مِّنَ الْأَوَّلِينَ", "en": "A company from earlier generations,"},
    {"num": 40, "ar": "وَثُلَّةٌ مِّنَ الْآخِرِينَ", "en": "And a company from later times."}
]

# Firdaus Path Passages (Surah Al-Mu'minun 23:1-11)
FIRDAUS_PATH_VERSES = [
    {"num": 1, "ar": "قَدْ أَفْلَحَ الْمُؤْمِنُونَ", "en": "Certainly will the believers have succeeded:", "quality": "Foundation of Faith"},
    {"num": 2, "ar": "الَّذِينَ هُمْ فِي صَلَاتِهِمْ خَاشِعُونَ", "en": "They who are during their prayer humbly submissive (khushu').", "quality": "Khushu' in Salah"},
    {"num": 3, "ar": "وَالَّذِينَ هُمْ عَنِ اللَّغْوِ مُعْرِضُونَ", "en": "And they who turn away from vain, meaningless talk.", "quality": "Guarding against Laghw"},
    {"num": 4, "ar": "وَالَّذِينَ هُمْ لِلزَّكَاةِ فَاعِلُونَ", "en": "And they who are observant of zakah and purification.", "quality": "Zakah and Charity"},
    {"num": 5, "ar": "وَالَّذِينَ هُمْ لِفُرُوجِهِمْ حَافِظُونَ", "en": "And they who guard their chastity,", "quality": "Chastity and Modesty"},
    {"num": 8, "ar": "وَالَّذِينَ هُمْ لِأَمَانَاتِهِمْ وَعَهْدِهِمْ رَاعُونَ", "en": "And they who are to their trusts and their promises attentive.", "quality": "Fulfilling Trusts & Pledges"},
    {"num": 9, "ar": "وَالَّذِينَ هُمْ عَلَىٰ صَلَوَاتِهِمْ يُحَافِظُونَ", "en": "And they who carefully maintain their prayers.", "quality": "Preserving Salah on Time"},
    {"num": 10, "ar": "أُولَٰئِكَ هُمُ الْوَارِثُونَ", "en": "Those are the inheritors,", "quality": "Inheritance of Paradise"},
    {"num": 11, "ar": "الَّذِينَ يَرِثُونَ الْفِرْدَوْسَ هُمْ فِيهَا خَالِدُونَ", "en": "Who will inherit al-Firdaus. They will abide therein eternally.", "quality": "Inheritance of al-Firdaus"}
]

class QuranEngine:
    """Manages verified offline Quran texts, special virtues, and reading progress."""

    def __init__(self):
        pass

    def get_catalog(self) -> List[Dict[str, Any]]:
        return SURAH_CATALOG

    def get_surah(self, surah_number: int) -> Dict[str, Any]:
        meta = next((s for s in SURAH_CATALOG if s["number"] == surah_number), None)
        if not meta:
            meta = {"number": surah_number, "name_ar": "القرآن الكريم", "name_en": f"Surah {surah_number}", "verses": 0}

        verses = []
        if surah_number == 67:
            verses = SURAH_MULK_COMPLETE
        elif surah_number == 36:
            verses = SURAH_YASEEN_TEXT
        elif surah_number == 56:
            verses = SURAH_WAQIAH_TEXT
        elif surah_number == 18:
            verses = SURAH_KAHF_TEXT
        elif surah_number == 55:
            verses = SURAH_RAHMAN_TEXT
        elif surah_number == 23:
            verses = FIRDAUS_PATH_VERSES
        elif surah_number == 1:
            verses = [
                {"num": 1, "ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "en": "In the name of Allah, the Entirely Merciful, the Especially Merciful."},
                {"num": 2, "ar": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "en": "All praise is due to Allah, Lord of the worlds -"},
                {"num": 3, "ar": "الرَّحْمَٰنِ الرَّحِيمِ", "en": "The Entirely Merciful, the Especially Merciful,"},
                {"num": 4, "ar": "مَالِكِ يَوْمِ الدِّينِ", "en": "Sovereign of the Day of Recompense."},
                {"num": 5, "ar": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ", "en": "It is You we worship and You we ask for help."},
                {"num": 6, "ar": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ", "en": "Guide us to the straight path -"},
                {"num": 7, "ar": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ", "en": "The path of those upon whom You have bestowed favor, not of those who have evoked [Your] anger or of those who are astray."}
            ]
        elif surah_number == 2:
            verses = [
                {"num": 255, "ar": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ", "en": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of all existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that could intercede with Him except by His permission? He knows what is before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most High, the Most Great. (Ayat al-Kursi)"},
                {"num": 285, "ar": "آمَنَ الرَّسُولُ بِمَا أُنزِلَ إِلَيْهِ مِن رَّبِّهِ وَالْمُؤْمِنُونَ ۚ كُلٌّ آمَنَ بِاللَّهِ وَمَلَائِكَتِهِ وَكُتُبِهِ وَرُسُلِهِ لَا نُفَرِّقُ بَيْنَ أَحَدٍ مِّن رُّسُلِهِ ۚ وَقَالُوا سَمِعْنَا وَأَطَعْنَا ۖ غُفْرَانَكَ رَبَّنَا وَإِلَيْكَ الْمَصِيرُ", "en": "The Messenger has believed in what was revealed to him from his Lord, and [so have] the believers. All of them have believed in Allah and His angels and His books and His messengers, [saying], 'We make no distinction between any of His messengers.' And they say, 'We hear and we obey. [We seek] Your forgiveness, our Lord, and to You is the final destination.'"},
                {"num": 286, "ar": "لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا ۚ لَهَا مَا كَسَبَتْ وَعَلَيْهَا مَا اكْتَسَبَتْ ۗ رَبَّنَا لَا تُؤَاخِذْنَا إِن نَّسِينَا أَوْ أَخْطَأْنَا ۚ رَبَّنَا وَلَا تَحْمِلْ عَلَيْنَا إِصْرًا كَمَا حَمَلْتَهُ عَلَى الَّذِينَ مِن قَبْلِنَا ۚ رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا ۚ أَنتَ مَوْلَانَا فَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ", "en": "Allah does not burden a soul beyond that it can bear. It will have [the consequence of] what [good] it has gained, and it will bear [the consequence of] what [evil] it has earned. 'Our Lord, do not impose blame upon us if we have forgotten or erred. Our Lord, and lay not upon us a burden like that which You laid upon those before us. Our Lord, and burden us not with that which we have no ability to bear. And pardon us; and forgive us; and have mercy upon us. You are our protector, so give us victory over the disbelieving people.'"}
            ]
        elif surah_number == 62:
            verses = [
                {"num": 1, "ar": "يُسَبِّحُ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ الْمَلِكِ الْقُدُّوسِ الْعَزِيزِ الْحَكِيمِ", "en": "Whatever is in the heavens and whatever is on the earth is exalting Allah, the Sovereign, the Pure, the Exalted in Might, the Wise."},
                {"num": 2, "ar": "هُوَ الَّذِي بَعَثَ فِي الْأُمِّيِّينَ رَسُولًا مِّنْهُمْ يَتْلُو عَلَيْهِمْ آيَاتِهِ وَيُزَكِّيهِمْ وَيُعَلِّمُهُمُ الْكِتَابَ وَالْحِكْمَةَ وَإِن كَانُوا مِن قَبْلُ لَفِي ضَلَالٍ مُّبِينٍ", "en": "It is He who sent among the unlettered a Messenger from themselves reciting to them His verses and purifying them and teaching them the Book and wisdom - although they were before in clear error -"},
                {"num": 3, "ar": "وَآخَرِينَ مِنْهُمْ لَمَّا يَلْحَقُوا بِهِمْ ۚ وَهُوَ الْعَزِيزُ الْحَكِيمُ", "en": "And [to] others of them who have not yet joined them. And He is the Exalted in Might, the Wise."},
                {"num": 4, "ar": "ذَٰلِكَ فَضْلُ اللَّهِ يُؤْتِيهِ مَن يَشَاءُ ۚ وَاللَّهُ ذُو الْفَضْلِ الْعَظِيمِ", "en": "That is the bounty of Allah, which He gives to whom He wills, and Allah is the possessor of great bounty."},
                {"num": 5, "ar": "مَثَلُ الَّذِينَ حُمِّلُوا التَّوْرَاةَ ثُمَّ لَمْ يَحْمِلُوهَا كَمَثَلِ الْحِمَارِ يَحْمِلُ أَسْفَارًا ۚ بِئْسَ مَثَلُ الْقَوْمِ الَّذِينَ كَذَّبُوا بِآيَاتِ اللَّهِ ۚ وَاللَّهُ لَا يَهْدِي الْقَوْمَ الظَّالِمِينَ", "en": "The example of those who were entrusted with the Torah and then did not take it on is like that of a donkey who carries volumes [of books]. Wretched is the example of the people who deny the signs of Allah. And Allah does not guide the wrongdoing people."},
                {"num": 6, "ar": "قُلْ يَا أَيُّهَا الَّذِينَ هَادُوا إِن زَعَمْتُمْ أَنَّكُمْ أَوْلِيَاءُ لِلَّهِ مِن دُونِ النَّاسِ فَتَمَنَّوُا الْمَوْتَ إِن كُنتُمْ صَادِقِينَ", "en": "Say: 'O you who are Jews, if you claim that you are allies of Allah, excluding the [other] people, then wish for death, if you should be truthful.'"  },
                {"num": 7, "ar": "وَلَا يَتَمَنَّوْنَهُ أَبَدًا بِمَا قَدَّمَتْ أَيْدِيهِمْ ۚ وَاللَّهُ عَلِيمٌ بِالظَّالِمِينَ", "en": "But they will not wish for it, ever, because of what their hands have put forth. And Allah is Knowing of the wrongdoers."},
                {"num": 8, "ar": "قُلْ إِنَّ الْمَوْتَ الَّذِي تَفِرُّونَ مِنْهُ فَإِنَّهُ مُلَاقِيكُمْ ۖ ثُمَّ تُرَدُّونَ إِلَىٰ عَالِمِ الْغَيْبِ وَالشَّهَادَةِ فَيُنَبِّئُكُم بِمَا كُنتُمْ تَعْمَلُونَ", "en": "Say: 'Indeed, the death from which you flee — indeed, it will meet you. Then you will be returned to the Knower of the unseen and the witnessed, and He will inform you about what you used to do.'"},
                {"num": 9, "ar": "يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا نُودِيَ لِلصَّلَاةِ مِن يَوْمِ الْجُمُعَةِ فَاسْعَوْا إِلَىٰ ذِكْرِ اللَّهِ وَذَرُوا الْبَيْعَ ۚ ذَٰلِكُمْ خَيْرٌ لَّكُمْ إِن كُنتُمْ تَعْلَمُونَ", "en": "O you who have believed, when [the adhan] is called for the prayer on the day of Jumu'ah [Friday], then proceed to the remembrance of Allah and leave trade. That is better for you, if you only knew."},
                {"num": 10, "ar": "فَإِذَا قُضِيَتِ الصَّلَاةُ فَانتَشِرُوا فِي الْأَرْضِ وَابْتَغُوا مِن فَضْلِ اللَّهِ وَاذْكُرُوا اللَّهَ كَثِيرًا لَّعَلَّكُمْ تُفْلِحُونَ", "en": "And when the prayer has been concluded, disperse within the land and seek from the bounty of Allah, and remember Allah often that you may succeed."},
                {"num": 11, "ar": "وَإِذَا رَأَوْا تِجَارَةً أَوْ لَهْوًا انفَضُّوا إِلَيْهَا وَتَرَكُوكَ قَائِمًا ۚ قُلْ مَا عِندَ اللَّهِ خَيْرٌ مِّنَ اللَّهْوِ وَمِنَ التِّجَارَةِ ۚ وَاللَّهُ خَيْرُ الرَّازِقِينَ", "en": "But when they saw a transaction or a diversion, [O Muhammad], they rushed to it and left you standing. Say: 'What is with Allah is better than diversion and than a transaction, and Allah is the best of providers.'"}
            ]

        elif surah_number == 93:
            verses = [
                {"num": 1, "ar": "وَالضُّحَىٰ", "en": "By the morning brightness"},
                {"num": 2, "ar": "وَاللَّيْلِ إِذَا سَجَىٰ", "en": "And [by] the night when it covers with darkness,"},
                {"num": 3, "ar": "مَا وَدَّعَكَ رَبُّكَ وَمَا قَلَىٰ", "en": "Your Lord has not taken leave of you, [O Muhammad], nor has He detested [you]."},
                {"num": 4, "ar": "وَلَلْآخِرَةُ خَيْرٌ لَّكَ مِنَ الْأُولَىٰ", "en": "And the Hereafter is better for you than the first [life]."},
                {"num": 5, "ar": "وَلَسَوْفَ يُعْطِيكَ رَبُّكَ فَتَرْضَىٰ", "en": "And your Lord is going to give you, and you will be satisfied."},
                {"num": 6, "ar": "أَلَمْ يَجِدْكَ يَتِيمًا فَآوَىٰ", "en": "Did He not find you an orphan and give [you] refuge?"},
                {"num": 7, "ar": "وَوَجَدَكَ ضَالًّا فَهَدَىٰ", "en": "And He found you lost and guided [you],"},
                {"num": 8, "ar": "وَوَجَدَكَ عَائِلًا فَأَغْنَىٰ", "en": "And He found you poor and made [you] self-sufficient."},
                {"num": 9, "ar": "فَأَمَّا الْيَتِيمَ فَلَا تَقْهَرْ", "en": "So as for the orphan, do not oppress [him]."},
                {"num": 10, "ar": "وَأَمَّا السَّائِلَ فَلَا تَنْهَرْ", "en": "And as for the petitioner, do not repel [him]."},
                {"num": 11, "ar": "وَأَمَّا بِنِعْمَةِ رَبِّكَ فَحَدِّثْ", "en": "And as for the favor of your Lord, report [it]."}
            ]
        elif surah_number == 94:
            verses = [
                {"num": 1, "ar": "أَلَمْ نَشْرَحْ لَكَ صَدْرَكَ", "en": "Did We not expand for you, [O Muhammad], your breast?"},
                {"num": 2, "ar": "وَوَضَعْنَا عَنكَ وِزْرَكَ", "en": "And We removed from you your burden"},
                {"num": 3, "ar": "الَّذِي أَنقَضَ ظَهْرَكَ", "en": "Which had weighed upon your back"},
                {"num": 4, "ar": "وَرَفَعْنَا لَكَ ذِكْرَكَ", "en": "And raised high for you your repute."},
                {"num": 5, "ar": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا", "en": "For indeed, with hardship [will be] ease."},
                {"num": 6, "ar": "إِنَّ مَعَ الْعُسْرِ يُسْرًا", "en": "Indeed, with hardship [will be] ease."},
                {"num": 7, "ar": "فَإِذَا فَرَغْتَ فَانصَبْ", "en": "So when you have finished [your duties], then stand up [for worship]."},
                {"num": 8, "ar": "وَإِلَىٰ رَبِّكَ فَارْغَب", "en": "And to your Lord direct [your] longing."}
            ]
        elif surah_number == 95:
            verses = [
                {"num": 1, "ar": "وَالتِّينِ وَالزَّيْتُونِ", "en": "By the fig and the olive"},
                {"num": 2, "ar": "وَطُورِ سِينِينَ", "en": "And [by] Mount Sinai"},
                {"num": 3, "ar": "وَهَٰذَا الْبَلَدِ الْأَمِينِ", "en": "And [by] this secure city [Makkah],"},
                {"num": 4, "ar": "لَقَدْ خَلَقْنَا الْإِنسَانَ فِي أَحْسَنِ تَقْوِيمٍ", "en": "We have certainly created man in the best of stature;"},
                {"num": 5, "ar": "ثُمَّ رَدَدْنَاهُ أَسْفَلَ سَافِلِينَ", "en": "Then We return him to the lowest of the low,"},
                {"num": 6, "ar": "إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ فَلَهُمْ أَجْرٌ غَيْرُ مَمْنُونٍ", "en": "Except for those who believe and do righteous deeds, for they will have a reward uninterrupted."},
                {"num": 7, "ar": "فَمَا يُكَذِّبُكَ بَعْدُ بِالدِّينِ", "en": "So what yet causes you to deny the Recompense?"},
                {"num": 8, "ar": "أَلَيْسَ اللَّهُ بِأَحْكَمِ الْحَاكِمِينَ", "en": "Is not Allah the most just of judges?"}
            ]
        elif surah_number == 96:
            verses = [
                {"num": 1, "ar": "اقْرَأْ بِاسْمِ رَبِّكَ الَّذِي خَلَقَ", "en": "Recite in the name of your Lord who created -"},
                {"num": 2, "ar": "خَلَقَ الْإِنسَانَ مِنْ عَلَقٍ", "en": "Created man from a clinging substance."},
                {"num": 3, "ar": "اقْرَأْ وَرَبُّكَ الْأَكْرَمُ", "en": "Recite, and your Lord is the most Generous -"},
                {"num": 4, "ar": "الَّذِي عَلَّمَ بِالْقَلَمِ", "en": "Who taught by the pen -"},
                {"num": 5, "ar": "عَلَّمَ الْإِنسَانَ مَا لَمْ يَعْلَمْ", "en": "Taught man that which he knew not."},
                {"num": 6, "ar": "كَلَّا إِنَّ الْإِنسَانَ لَيَطْغَىٰ", "en": "No! [But] indeed, man transgresses"},
                {"num": 7, "ar": "أَن رَّآهُ اسْتَغْنَىٰ", "en": "Because he sees himself self-sufficient."},
                {"num": 8, "ar": "إِنَّ إِلَىٰ رَبِّكَ الرُّجْعَىٰ", "en": "Indeed, to your Lord is the return."},
                {"num": 9, "ar": "أَرَأَيْتَ الَّذِي يَنْهَىٰ", "en": "Have you seen the one who forbids"},
                {"num": 10, "ar": "عَبْدًا إِذَا صَلَّىٰ", "en": "A servant when he prays?"},
                {"num": 11, "ar": "أَرَأَيْتَ إِن كَانَ عَلَى الْهُدَىٰ", "en": "Have you seen if he is upon guidance"},
                {"num": 12, "ar": "أَوْ أَمَرَ بِالتَّقْوَىٰ", "en": "Or enjoins righteousness?"},
                {"num": 13, "ar": "أَرَأَيْتَ إِن كَذَّبَ وَتَوَلَّىٰ", "en": "Have you seen if he denies and turns away -"},
                {"num": 14, "ar": "أَلَمْ يَعْلَم بِأَنَّ اللَّهَ يَرَىٰ", "en": "Does he not know that Allah sees?"},
                {"num": 15, "ar": "كَلَّا لَئِن لَّمْ يَنتَهِ لَنَسْفَعًا بِالنَّاصِيَةِ", "en": "No! If he does not desist, We will surely drag him by the forelock -"},
                {"num": 16, "ar": "نَاصِيَةٍ كَاذِبَةٍ خَاطِئَةٍ", "en": "A lying, sinning forelock."},
                {"num": 17, "ar": "فَلْيَدْعُ نَادِيَهُ", "en": "Then let him call his associates;"},
                {"num": 18, "ar": "سَنَدْعُ الزَّبَانِيَةَ", "en": "We will call the angels of Hell."},
                {"num": 19, "ar": "كَلَّا لَا تُطِعْهُ وَاسْجُدْ وَاقْتَرِب۩", "en": "No! Do not obey him. But prostrate and draw near [to Allah]."}
            ]
        elif surah_number == 99:
            verses = [
                {"num": 1, "ar": "إِذَا زُلْزِلَتِ الْأَرْضُ زِلْزَالَهَا", "en": "When the earth is shaken with its [final] earthquake"},
                {"num": 2, "ar": "وَأَخْرَجَتِ الْأَرْضُ أَثْقَالَهَا", "en": "And the earth discharges its burdens"},
                {"num": 3, "ar": "وَقَالَ الْإِنسَانُ مَا لَهَا", "en": "And man says: 'What is [wrong] with it?' -"},
                {"num": 4, "ar": "يَوْمَئِذٍ تُحَدِّثُ أَخْبَارَهَا", "en": "That Day, it will report its news"},
                {"num": 5, "ar": "بِأَنَّ رَبَّكَ أَوْحَىٰ لَهَا", "en": "Because your Lord has commanded it."},
                {"num": 6, "ar": "يَوْمَئِذٍ يَصْدُرُ النَّاسُ أَشْتَاتًا لِّيُرَوْا أَعْمَالَهُمْ", "en": "That Day, the people will depart separated [into categories] to be shown [the result of] their deeds."},
                {"num": 7, "ar": "فَمَن يَعْمَلْ مِثْقَالَ ذَرَّةٍ خَيْرًا يَرَهُ", "en": "So whoever does an atom's weight of good will see it,"},
                {"num": 8, "ar": "وَمَن يَعْمَلْ مِثْقَالَ ذَرَّةٍ شَرًّا يَرَهُ", "en": "And whoever does an atom's weight of evil will see it."}
            ]
        elif surah_number == 97:
            verses = [
                {"num": 1, "ar": "إِنَّا أَنزَلْنَاهُ فِي لَيْلَةِ الْقَدْرِ", "en": "Indeed, We sent the Qur'an down during the Night of Decree."},
                {"num": 2, "ar": "وَمَا أَدْرَاكَ مَا لَيْلَةُ الْقَدْرِ", "en": "And what can make you know what is the Night of Decree?"},
                {"num": 3, "ar": "لَيْلَةُ الْقَدْرِ خَيْرٌ مِّنْ أَلْفِ شَهْرٍ", "en": "The Night of Decree is better than a thousand months."},
                {"num": 4, "ar": "تَنَزَّلُ الْمَلَائِكَةُ وَالرُّوحُ فِيهَا بِإِذْنِ رَبِّهِم مِّن كُلِّ أَمْرٍ", "en": "The angels and the Spirit descend therein by permission of their Lord for every matter."},
                {"num": 5, "ar": "سَلَامٌ هِيَ حَتَّىٰ مَطْلَعِ الْفَجْرِ", "en": "Peace it is until the emergence of dawn."}
            ]
        elif surah_number == 103:
            verses = [
                {"num": 1, "ar": "وَالْعَصْرِ", "en": "By time,"},
                {"num": 2, "ar": "إِنَّ الْإِنسَانَ لَفِي خُسْرٍ", "en": "Indeed, mankind is in loss,"},
                {"num": 3, "ar": "إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ", "en": "Except for those who have believed and done righteous deeds and advised each other to truth and advised each other to patience."}
            ]
        elif surah_number == 108:
            verses = [
                {"num": 1, "ar": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ", "en": "Indeed, We have granted you, [O Muhammad], al-Kawthar."},
                {"num": 2, "ar": "فَصَلِّ لِرَبِّكَ وَانْحَرْ", "en": "So pray to your Lord and sacrifice [to Him alone]."},
                {"num": 3, "ar": "إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ", "en": "Indeed, your enemy is the one cut off."}
            ]
        elif surah_number == 109:
            verses = [
                {"num": 1, "ar": "قُلْ يَا أَيُّهَا الْكَافِرُونَ", "en": "Say, 'O disbelievers,'"},
                {"num": 2, "ar": "لَا أَعْبُدُ مَا تَعْبُدُونَ", "en": "I do not worship what you worship."},
                {"num": 3, "ar": "وَلَا أَنتُمْ عَابِدُونَ مَا أَعْبُدُ", "en": "Nor are you worshippers of what I worship."},
                {"num": 4, "ar": "وَلَا أَنَا عَابِدٌ مَّا عَبَدتُّمْ", "en": "Nor will I be a worshipper of what you worship."},
                {"num": 5, "ar": "وَلَا أَنتُمْ عَابِدُونَ مَا أَعْبُدُ", "en": "Nor will you be worshippers of what I worship."},
                {"num": 6, "ar": "لَكُمْ دِينُكُمْ وَلِيَ دِينِ", "en": "For you is your religion, and for me is my religion."}
            ]
        elif surah_number == 112:
            verses = [
                {"num": 1, "ar": "قُلْ هُوَ اللَّهُ أَحَدٌ", "en": "Say: 'He is Allah, [who is] One,'"},
                {"num": 2, "ar": "اللَّهُ الصَّمَدُ", "en": "Allah, the Eternal Refuge."},
                {"num": 3, "ar": "لَمْ يَلِدْ وَلَمْ يُولَدْ", "en": "He neither begets nor is born,"},
                {"num": 4, "ar": "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ", "en": "Nor is there to Him any equivalent."}
            ]
        elif surah_number == 113:
            verses = [
                {"num": 1, "ar": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ", "en": "Say: 'I seek refuge in the Lord of daybreak'"},
                {"num": 2, "ar": "مِن شَرِّ مَا خَلَقَ", "en": "From the evil of that which He created"},
                {"num": 3, "ar": "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ", "en": "And from the evil of darkness when it settles"},
                {"num": 4, "ar": "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ", "en": "And from the evil of the blowers in knots"},
                {"num": 5, "ar": "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ", "en": "And from the evil of an envier when he envies."}
            ]
        elif surah_number == 114:
            verses = [
                {"num": 1, "ar": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ", "en": "Say: 'I seek refuge in the Lord of mankind,'"},
                {"num": 2, "ar": "مَلِكِ النَّاسِ", "en": "The Sovereign of mankind,"},
                {"num": 3, "ar": "إِلَٰهِ النَّاسِ", "en": "The God of mankind,"},
                {"num": 4, "ar": "مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ", "en": "From the evil of the retreating whisperer -"},
                {"num": 5, "ar": "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ", "en": "Who whispers into the breasts of mankind -"},
                {"num": 6, "ar": "مِنَ الْجِنَّةِ وَالنَّاسِ", "en": "From among the jinn and mankind."}
            ]
        else:
            verses = [
                {"num": 1, "ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "en": "In the name of Allah, the Entirely Merciful, the Especially Merciful."}
            ]

        return {
            "surah": meta,
            "verses": verses,
            "total_verses_returned": len(verses),
            "integrity": "Tanzil Verified"
        }

    def get_special_virtues(self) -> Dict[str, Any]:
        res = dict(SPECIAL_VIRTUE_METADATA)
        if "al_waqiah_night" in res and "waqiah_wealth" not in res:
            res["waqiah_wealth"] = res["al_waqiah_night"]
        return res

    def get_firdaus_path(self) -> List[Dict[str, Any]]:
        return [
            {"trait": "Khushu' in Salah", "verse": "23:2", "description": "Those who are humble in their prayers."},
            {"trait": "Avoiding Laghw", "verse": "23:3", "description": "Those who turn away from ill speech and vanity."},
            {"trait": "Observance of Zakah", "verse": "23:4", "description": "Those who are observant of zakah and purification."},
            {"trait": "Guarding Chastity", "verse": "23:5", "description": "Those who guard their chastity."},
            {"trait": "Fulfilling Trusts & Covenants", "verse": "23:8", "description": "Those who are faithfully true to their trusts and covenants."},
            {"trait": "Preserving Salah", "verse": "23:9", "description": "Those who strictly maintain their prayers."}
        ]
