package com.friendos.alishabubbzieee.core.diagnostics

/**
 * Local-only diagnostic telemetry.
 * Never uploaded or sent to external servers.
 */
data class ExecutionDiagnostics(
    val modelLoadTimeMs: Long = 0L,
    val promptTokens: Int = 0,
    val generatedTokens: Int = 0,
    val timeToFirstTokenMs: Long = 0L,
    val tokensPerSecond: Float = 0.0f,
    val retrievalCount: Int = 0,
    val retrievalLatencyMs: Long = 0L,
    val contextSizeBytes: Int = 0,
    val ttsFirstAudioLatencyMs: Long = 0L,
    val ttsGenerationTimeMs: Long = 0L,
    val asrLatencyMs: Long = 0L,
    val timestamp: Long = System.currentTimeMillis()
)

interface DiagnosticsCollector {
    fun record(diagnostics: ExecutionDiagnostics)
    fun getLatest(): ExecutionDiagnostics
    fun getRecentHistory(limit: Int = 20): List<ExecutionDiagnostics>
}
