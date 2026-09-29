package com.friendos.alishabubbzieee.core.policy

import com.friendos.alishabubbzieee.core.memory.StyleMode

data class PolicyDecision(
    val isExplicitMemoryRequest: Boolean,
    val retrievalDepth: Int,
    val styleMode: StyleMode,
    val maxResponseTokens: Int,
    val isVoiceRequested: Boolean,
    val permitSecondMessageBurst: Boolean
)

/**
 * Deterministic routing controller.
 * Directs memory depth, style mode, response length, and burst allowance without LLM overhead.
 */
interface DeterministicPolicy {
    fun evaluate(
        userInput: String,
        recentTurnCount: Int,
        isVoiceInput: Boolean
    ): PolicyDecision
}
