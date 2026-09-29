package com.friendos.alishabubbzieee.core.llm

/**
 * Generation request for local LLM inference.
 */
data class GenerationRequest(
    val prompt: String,
    val maxTokens: Int = 128,
    val temperature: Float = 0.75f,
    val topP: Float = 0.90f,
    val stopTokens: List<String> = listOf("\nUser:", "\nFriend:", "<|im_end|>", "<|endoftext|>"),
    val deterministicTestMode: Boolean = false,
    val seed: Long? = null
)

/**
 * Diagnostics and result metrics from LLM generation.
 */
data class GenerationResult(
    val text: String,
    val promptTokens: Int = 0,
    val generatedTokens: Int = 0,
    val timeToFirstTokenMs: Long = 0L,
    val totalTimeMs: Long = 0L,
    val tokensPerSecond: Float = 0.0f,
    val isCancelled: Boolean = false
)

/**
 * Configuration options for the LLM subsystem.
 */
data class LlmConfig(
    val modelPath: String,
    val contextWindowTokens: Int = 1024,
    val threadCount: Int = 4,
    val repeatPenalty: Float = 1.15f
)

/**
 * Abstraction for local LLM inference (llama.cpp GGUF compatible).
 * Neither ConversationEngine, Memory, UI, nor TTS depend on specific llama.cpp classes.
 */
interface LlmEngine {
    suspend fun generate(
        request: GenerationRequest,
        onToken: (String) -> Unit
    ): GenerationResult

    fun cancel()
}
