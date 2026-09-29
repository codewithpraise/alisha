package com.friendos.alishabubbzieee.core.voice

fun interface AudioChunkCallback {
    fun onAudioChunk(chunk: ByteArray, isFinal: Boolean)
}

/**
 * Replaceable local TTS abstraction (e.g. Qwen3-TTS, Pocket TTS).
 */
interface TtsEngine {
    fun synthesize(
        text: String,
        callback: AudioChunkCallback
    )
    fun cancel()
}

/**
 * Replaceable local ASR abstraction (e.g. Whisper-family local inference).
 */
interface AsrEngine {
    suspend fun transcribe(
        audioPcm: ByteArray,
        sampleRate: Int = 16000
    ): String
}

/**
 * Voice Activity Detection abstraction (e.g. Silero VAD).
 */
interface VadEngine {
    fun processFrame(audioPcm: ByteArray): Boolean
    fun reset()
}
