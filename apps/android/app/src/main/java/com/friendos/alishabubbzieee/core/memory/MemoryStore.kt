package com.friendos.alishabubbzieee.core.memory

/**
 * Local SQLite memory store abstraction.
 * Enforces provenance, temporal memory updates, and local-only queries.
 */
interface MemoryStore {
    suspend fun insertMessage(message: MessageEntity)
    suspend fun getRecentMessages(limit: Int = 10): List<MessageEntity>

    suspend fun insertFact(fact: FactEntity)
    suspend fun updateFactTemporally(factId: String, newFact: FactEntity)
    suspend fun getActiveFacts(): List<FactEntity>

    suspend fun insertEpisode(episode: EpisodeEntity)
    suspend fun getRecentEpisodes(limit: Int = 5): List<EpisodeEntity>

    suspend fun insertRelationship(relationship: RelationshipEntity)
    suspend fun getRelationshipsForSubject(subject: String): List<RelationshipEntity>

    suspend fun insertStyleExample(example: StyleExampleEntity)
    suspend fun getStyleExamplesForMode(mode: StyleMode, limit: Int = 4): List<StyleExampleEntity>

    suspend fun searchFts(query: String, limit: Int = 10): List<FactEntity>
}
