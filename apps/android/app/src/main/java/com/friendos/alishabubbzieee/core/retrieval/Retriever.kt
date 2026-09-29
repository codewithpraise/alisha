package com.friendos.alishabubbzieee.core.retrieval

import com.friendos.alishabubbzieee.core.memory.FactEntity
import com.friendos.alishabubbzieee.core.memory.StyleExampleEntity
import com.friendos.alishabubbzieee.core.memory.StyleMode

data class ScoreWeights(
    val lexicalWeight: Float = 0.25f,
    val semanticWeight: Float = 0.35f,
    val recencyWeight: Float = 0.15f,
    val importanceWeight: Float = 0.15f,
    val confidenceWeight: Float = 0.10f,
    val duplicationPenaltyWeight: Float = 0.20f,
    val minScoreThreshold: Float = 0.35f
)

data class ScoredMemory(
    val fact: FactEntity,
    val finalScore: Float,
    val lexicalScore: Float,
    val semanticScore: Float,
    val recencyScore: Float,
    val importanceScore: Float,
    val confidenceScore: Float,
    val duplicatePenalty: Float
)

data class RetrievalResult(
    val memories: List<ScoredMemory>,
    val styleExemplars: List<StyleExampleEntity>,
    val retrievalLatencyMs: Long
)

interface MemoryRetriever {
    suspend fun retrieve(
        query: String,
        styleMode: StyleMode,
        depth: Int = 5,
        weights: ScoreWeights = ScoreWeights()
    ): RetrievalResult
}
