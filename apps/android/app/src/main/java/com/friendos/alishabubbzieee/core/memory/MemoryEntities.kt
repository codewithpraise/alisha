package com.friendos.alishabubbzieee.core.memory

data class MessageEntity(
    val id: String,
    val conversationId: String,
    val timestamp: Long,
    val sender: String,
    val text: String,
    val sourceIndex: Int
)

data class FactEntity(
    val id: String,
    val subject: String,
    val predicate: String,
    val obj: String,
    val confidence: Float = 1.0f,
    val importance: Float = 0.5f,
    val firstSeen: Long,
    val lastConfirmed: Long,
    val validFrom: Long,
    val validUntil: Long? = null,
    val sourceMessageId: String? = null
)

data class EpisodeEntity(
    val id: String,
    val startTimestamp: Long,
    val endTimestamp: Long,
    val summary: String,
    val importance: Float = 0.5f,
    val confidence: Float = 1.0f,
    val sourceStartMessageId: String? = null,
    val sourceEndMessageId: String? = null
)

data class RelationshipEntity(
    val id: String,
    val subject: String,
    val relation: String,
    val obj: String,
    val confidence: Float = 1.0f,
    val firstSeen: Long,
    val lastConfirmed: Long,
    val sourceMessageId: String? = null
)

enum class StyleMode {
    NEUTRAL,
    PLAYFUL,
    TEASING,
    AFFECTIONATE,
    SERIOUS,
    COMFORTING,
    EXPLANATORY,
    ANNOYED
}

data class StyleExampleEntity(
    val id: String,
    val mode: StyleMode,
    val text: String,
    val sourceMessageId: String? = null,
    val confidence: Float = 1.0f,
    val importance: Float = 0.5f
)
