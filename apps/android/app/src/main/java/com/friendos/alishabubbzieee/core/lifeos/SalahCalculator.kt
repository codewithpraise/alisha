package com.friendos.alishabubbzieee.core.lifeos

import java.util.Calendar
import java.util.Date
import java.util.TimeZone
import kotlin.math.*

/**
 * Astronomical Prayer Window Calculator for Android.
 * Pure mathematical spherical trigonometry; zero external dependencies.
 * Fiqh-compliant for Hanafi and Shafi'i Asr calculation.
 */
data class PrayerSchedule(
    val fajr: String,
    val sunrise: String,
    val dhuhr: String,
    val asr: String,
    val maghrib: String,
    val isha: String,
    val midnight: String,
    val lastThird: String
)

data class PrayerStatus(
    val currentPrayer: String,
    val state: String,
    val remainingFormatted: String,
    val nextPrayer: String,
    val nextInFormatted: String,
    val schedule: PrayerSchedule
)

class AndroidSalahCalculator(
    private val lat: Double = 24.8607,
    private val lng: Double = 67.0011,
    private val timezoneOffset: Double = 5.0,
    private val madhhab: String = "hanafi",
    private val fajrAngle: Double = 18.0,
    private val ishaAngle: Double = 18.0
) {
    fun calculatePrayerTimes(calendar: Calendar = Calendar.getInstance()): PrayerSchedule {
        val dayOfYear = calendar.get(Calendar.DAY_OF_YEAR)
        val d = dayOfYear.toDouble()

        // Solar Declination & Equation of Time
        val gamma = 2.0 * Math.PI / 365.0 * (d - 1.0)
        val eqTime = 229.18 * (0.000075 + 0.001868 * cos(gamma) - 0.032077 * sin(gamma) -
                0.014615 * cos(2.0 * gamma) - 0.040849 * sin(2.0 * gamma))

        val decl = 0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma) -
                0.006758 * cos(2.0 * gamma) + 0.000907 * sin(2.0 * gamma)

        val latRad = Math.toRadians(lat)

        // Solar noon (Dhuhr)
        val noonUtc = 12.0 - (lng / 15.0) - (eqTime / 60.0)
        val dhuhrDec = noonUtc + timezoneOffset

        // Sunrise & Sunset (center at -0.833 degrees for refraction)
        val sunRad = Math.toRadians(-0.833)
        val cosHaSun = (sin(sunRad) - sin(latRad) * sin(decl)) / (cos(latRad) * cos(decl))
        val haSun = Math.toDegrees(acos(cosHaSun.coerceIn(-1.0, 1.0))) / 15.0

        val sunriseDec = dhuhrDec - haSun
        val sunsetDec = dhuhrDec + haSun

        // Fajr
        val fajrRad = Math.toRadians(-fajrAngle)
        val cosHaFajr = (sin(fajrRad) - sin(latRad) * sin(decl)) / (cos(latRad) * cos(decl))
        val haFajr = Math.toDegrees(acos(cosHaFajr.coerceIn(-1.0, 1.0))) / 15.0
        val fajrDec = dhuhrDec - haFajr

        // Isha
        val ishaRad = Math.toRadians(-ishaAngle)
        val cosHaIsha = (sin(ishaRad) - sin(latRad) * sin(decl)) / (cos(latRad) * cos(decl))
        val haIsha = Math.toDegrees(acos(cosHaIsha.coerceIn(-1.0, 1.0))) / 15.0
        val ishaDec = dhuhrDec + haIsha

        // Asr (shadow factor: 2.0 for Hanafi, 1.0 for Shafi'i)
        val shadowFactor = if (madhhab.lowercase() == "hanafi") 2.0 else 1.0
        val zenithDiff = abs(latRad - decl)
        val asrAlt = atan(1.0 / (shadowFactor + tan(zenithDiff)))
        val cosHaAsr = (sin(asrAlt) - sin(latRad) * sin(decl)) / (cos(latRad) * cos(decl))
        val haAsr = Math.toDegrees(acos(cosHaAsr.coerceIn(-1.0, 1.0))) / 15.0
        val asrDec = dhuhrDec + haAsr

        // Night calculations
        val nightDuration = ((fajrDec + 24.0) - sunsetDec) % 24.0
        val midnightDec = (sunsetDec + nightDuration / 2.0) % 24.0
        val lastThirdDec = (sunsetDec + nightDuration * (2.0 / 3.0)) % 24.0

        return PrayerSchedule(
            fajr = formatDecimalTime(fajrDec),
            sunrise = formatDecimalTime(sunriseDec),
            dhuhr = formatDecimalTime(dhuhrDec),
            asr = formatDecimalTime(asrDec),
            maghrib = formatDecimalTime(sunsetDec),
            isha = formatDecimalTime(ishaDec),
            midnight = formatDecimalTime(midnightDec),
            lastThird = formatDecimalTime(lastThirdDec)
        )
    }

    private fun formatDecimalTime(dec: Double): String {
        val totalMinutes = (dec * 60.0).roundToInt().let { (it % 1440 + 1440) % 1440 }
        val hours = totalMinutes / 60
        val minutes = totalMinutes % 60
        return String.format("%02d:%02d", hours, minutes)
    }
}
