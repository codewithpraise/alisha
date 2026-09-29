package com.friendos.alishabubbzieee.core.engine

import com.friendos.alishabubbzieee.core.diagnostics.ExecutionDiagnostics
import com.friendos.alishabubbzieee.core.voice.AudioChunkCallback

data class EngineTextResponse(
    val messages: List<String>,
    val diagnostics: ExecutionDiagnostics
)

/**
 * Top-level ConversationEngine orchestrating deterministic routing, retrieval,
 * context packing, LLM generation, and optional burst/TTS synthesis.
 */
interface ConversationEngine {
    suspend fun processTextMessage(
        text: String,
        onToken: ((String) -> Unit)? = null
    ): EngineTextResponse

    suspend fun processVoiceAudio(
        audioPcm: ByteArray,
        onAudioChunk: AudioChunkCallback,
        onToken: ((String) -> Unit)? = null
    ): EngineTextResponse

    fun cancelActiveGeneration()
}
