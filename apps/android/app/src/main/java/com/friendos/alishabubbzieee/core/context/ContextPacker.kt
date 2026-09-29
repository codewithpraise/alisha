package com.friendos.alishabubbzieee.core.context

import com.friendos.alishabubbzieee.core.memory.EpisodeEntity
import com.friendos.alishabubbzieee.core.memory.FactEntity
import com.friendos.alishabubbzieee.core.memory.MessageEntity
import com.friendos.alishabubbzieee.core.memory.StyleExampleEntity

data class PackedContext(
    val prompt: String,
    val promptTokensEstimate: Int,
    val injectedFactCount: Int,
    val injectedExemplarCount: Int
)

interface ContextPacker {
    fun pack(
        systemIdentity: String,
        recentMessages: List<MessageEntity>,
        relevantFacts: List<FactEntity>,
        episodeMemory: EpisodeEntity?,
        styleExemplars: List<StyleExampleEntity>,
        currentUserInput: String,
        maxContextBudgetTokens: Int = 1024
    ): PackedContext
}
