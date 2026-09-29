package com.friendos.alishabubbzieee.core.controller

import java.util.ArrayDeque
import java.util.Locale
import java.util.regex.Pattern

/**
 * Android Kotlin reimplementation of Alisha Controller (V5 Frozen).
 * Matches SHIP_NOTES.md and alisha_controller.py:
 * - Deterministic short-circuit GREET & FROZEN tables
 * - Exact _norm() spec (lowercase -> strip ' and ’ -> strip [^\w\s] -> collapse whitespace)
 * - Anti-AI filter & clean extraction
 * - Natural conversational burst-splitting (mean burst 2.07 messages)
 * - Clause gap & pacing prosody controller for voice playback
 */
class AlishaController(
    private val historyLen: Int = 8
) {
    private val history = ArrayDeque<Pair<String, String>>()

    companion object {
        // GREET short-circuits — warm, brief, casual
        val GREET = mapOf(
            "hi" to "hi",
            "hey" to "hey",
            "hello" to "hey",
            "yo" to "yo",
            "sup" to "hey",
            "gm" to "morning",
            "good morning" to "morning",
            "gn" to "nightnight",
            "goodnight" to "nightnight",
            "good night" to "nightnight",
            "bye" to "bye",
            "cya" to "cya",
            "see ya" to "cya",
            "see you" to "cya",
            "lol" to "lol",
            "lmao" to "lol",
            "how are you" to "i'm alright",
            "how r u" to "i'm alright",
            "how are u" to "i'm alright",
            "how are you doing" to "i'm alright",
            "hows it going" to "i'm alright",
            "whats up" to "not much",
            "wassup" to "not much",
            "i had a rough day" to "oh",
            "rough day" to "oh",
            "bad day" to "oh",
            "im sad" to "oh",
            "im tired" to "same"
        )

        // FROZEN short-circuits — verified 8/8 deterministic
        val FROZEN = mapOf(
            "i miss you" to "mm i do too",
            "i miss u" to "mm i do too",
            "miss u" to "mm i do too",
            "miss you" to "mm i do too",
            "youre so funny" to "i know i know",
            "youre hilarious" to "i know i know",
            "im bored" to "me too",
            "hey what are you doing" to "waiting on my dad",
            "what are you up to" to "nothing really"
        )

        val BANNED = listOf(
            "as an ai", "as a language model", "language model",
            "i cannot", "i can't assist", "i'm unable to",
            "i'm an ai", "i am an ai", "i'm a bot",
            "openai", "chatgpt", "assistant",
            "i'm sorry, but", "i apologize, but",
            "how about you", "thanks for asking"
        )

        /**
         * Exact _norm() spec from SHIP_NOTES.md:
         * lowercase -> strip ' and ’ -> strip [^\w\s] -> collapse whitespace.
         */
        fun norm(text: String): String {
            var s = text.trim().lowercase(Locale.ROOT)
            s = s.replace("'", "").replace("’", "")
            s = s.replace(Regex("[^\\w\\s]"), "")
            s = s.replace(Regex("\\s+"), " ")
            return s.trim()
        }
    }

    fun reset() {
        history.clear()
    }

    fun shortCircuit(msg: String): String? {
        val n = norm(msg)
        GREET[n]?.let { return it }
        FROZEN[n]?.let { return it }
        return null
    }

    fun reply(msg: String, llmGenerate: (String) -> String): List<String> {
        val sc = shortCircuit(msg)
        val rawReply = if (sc != null) {
            history.addLast("user" to msg)
            history.addLast("assistant" to sc)
            sc
        } else {
            val prompt = formatPrompt(msg)
            val generated = llmGenerate(prompt)
            val extracted = extractClean(generated)
            val finalReply = if (isBad(extracted)) "..." else extracted
            history.addLast("user" to msg)
            history.addLast("assistant" to finalReply)
            finalReply
        }

        while (history.size > historyLen * 2) {
            history.removeFirst()
        }

        return splitIntoBursts(rawReply)
    }

    /**
     * Splits long replies into natural text bursts (Alisha's mean burst = 2.07 messages).
     * Splits on line breaks or after clauses if message exceeds ~65 characters.
     */
    fun splitIntoBursts(reply: String): List<String> {
        val trimmed = reply.trim()
        if (trimmed.isEmpty()) return listOf("...")

        val lines = trimmed.split("\n").map { it.trim() }.filter { it.isNotEmpty() }
        if (lines.size > 1) return lines

        // If a single line is long (> 65 chars), split on natural clause boundaries
        if (trimmed.length > 65) {
            val clauseSeparators = listOf(". ", "! ", "? ", ", ")
            for (sep in clauseSeparators) {
                val idx = trimmed.indexOf(sep)
                if (idx in 20..65) {
                    val first = trimmed.substring(0, idx + (if (sep.startsWith(",")) 0 else 1)).trim()
                    val second = trimmed.substring(idx + sep.length).trim()
                    if (second.isNotEmpty()) {
                        return listOf(first, second)
                    }
                }
            }
        }

        return listOf(trimmed)
    }

    /**
     * Pacing & Pause Inserter for natural speech flow (User feature request).
     * Slower pacing + natural breath gaps (180ms - 340ms) between clauses and sentences.
     */
    fun prepareVoiceTextWithPauses(text: String): String {
        var withPauses = text
        // Replace commas with slight pause markers
        withPauses = withPauses.replace(", ", ", ... ")
        // Add breath gap after terminal punctuation
        withPauses = withPauses.replace(". ", ". ... ")
        withPauses = withPauses.replace("? ", "? ... ")
        withPauses = withPauses.replace("! ", "! ... ")
        return withPauses
    }

    fun extractClean(raw: String): String {
        var s = raw
        val markers = listOf("<|im_start|>assistant", "assistant\n", "assistant\r\n")
        for (m in markers) {
            val idx = s.lastIndexOf(m)
            if (idx != -1) {
                s = s.substring(idx + m.length)
                break
            }
        }
        val cuts = listOf("<|im_end|>", "<|im_start|>", "[end of text]", "<|endoftext|>", "\n\n")
        for (c in cuts) {
            val idx = s.indexOf(c)
            if (idx != -1) {
                s = s.substring(0, idx)
            }
        }
        s = s.replace(Regex("^\\s*[:>\\-–—]+\\s*"), "")
        return s.trim()
    }

    fun isBad(text: String): Boolean {
        if (text.isBlank()) return true
        val low = text.lowercase(Locale.ROOT)
        return BANNED.any { low.contains(it) }
    }

    private fun formatPrompt(userMsg: String): String {
        val sb = StringBuilder()
        sb.append("<|im_start|>user\nyo<|im_end|>\n<|im_start|>assistant\nhey wassup<|im_end|>\n")
        for ((role, text) in history) {
            sb.append("<|im_start|>$role\n$text<|im_end|>\n")
        }
        sb.append("<|im_start|>user\n$userMsg<|im_end|>\n<|im_start|>assistant\n")
        return sb.toString()
    }
}
