package com.friendos.alishabubbzieee.core.lifeos

/**
 * Android Islamic Content Router.
 * Ensures absolute separation of boundaries between Alisha AI's persona
 * and the verified Islamic LifeOS canonical sources.
 */
class AndroidIslamicContentRouter {
    private val religiousKeywords = listOf(
        "salah", "namaz", "prayer time", "fajr", "dhuhr", "asr", "maghrib", "isha",
        "quran", "surah", "ayat", "ayah", "dhikr", "tasbih", "dua", "hadith",
        "fatwa", "halal", "haram", "muhasabah", "firdaus", "waqiah", "mulk", "kahf"
    )

    fun isReligiousQuery(query: String): Boolean {
        val lower = query.lowercase().trim()
        return religiousKeywords.any { kw -> lower.contains(kw) }
    }

    fun getRoutingNotice(): String {
        return "Islamic practice & rulings are routed through verified LifeOS canonical sources. Alisha does not generate synthetic religious fatwas."
    }
}
