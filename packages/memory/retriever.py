"""
Local Vector, FTS5 & Multi-Signal Memory Retriever for Alisha Bubbzieee.
Implements:
- Deterministic character n-gram dense vectors (128-dim)
- Hybrid score fusion:
    final_score = lexical + semantic + recency + importance + confidence - duplication_penalty
- Duplication suppression
- Stale memory suppression
- Small retrieval depth (3-8 memories)
- Threshold cutoff (retrieves 0 when relevance is weak)
- Real style exemplar retrieval
"""

import math
import re
import time
import zlib
from typing import List, Dict, Any, Optional
from packages.memory.database import MemoryDatabase


def deterministic_text_vector(text: str, dim: int = 128) -> List[float]:
    """
    Computes a deterministic feature vector using CRC32 hash of words and
    character tri-grams, normalized to unit L2 length.
    Ensures identical embeddings across Python and Android/Kotlin.
    """
    vec = [0.0] * dim
    clean = re.sub(r"[^\w\s]", "", text.lower())
    words = clean.split()
    if not words:
        return vec

    for word in words:
        # Word hash
        h_w = zlib.crc32(word.encode("utf-8")) % dim
        vec[h_w] += 2.0
        # Character tri-grams
        for i in range(len(word) - 2):
            tri = word[i : i + 3]
            h_tri = zlib.crc32(tri.encode("utf-8")) % dim
            vec[h_tri] += 1.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-6:
        vec = [x / norm for x in vec]
    return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return max(0.0, min(1.0, sum(a * b for a, b in zip(v1, v2))))


def jaccard_word_similarity(text1: str, text2: str) -> float:
    w1 = set(re.findall(r"\b\w{3,}\b", text1.lower()))
    w2 = set(re.findall(r"\b\w{3,}\b", text2.lower()))
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


class ScoreWeights:
    def __init__(
        self,
        lexical_weight: float = 0.25,
        semantic_weight: float = 0.35,
        recency_weight: float = 0.15,
        importance_weight: float = 0.15,
        confidence_weight: float = 0.10,
        duplication_penalty_weight: float = 0.25,
        min_score_threshold: float = 0.35,
    ):
        self.lexical_weight = lexical_weight
        self.semantic_weight = semantic_weight
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
        self.confidence_weight = confidence_weight
        self.duplication_penalty_weight = duplication_penalty_weight
        self.min_score_threshold = min_score_threshold


class MemoryRetriever:
    def __init__(self, db: Any):
        if isinstance(db, str):
            self.db = MemoryDatabase(db)
        else:
            self.db = db

    def get_friend_state(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            try:
                cursor = conn.execute("SELECT * FROM friend_state WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    return dict(row)
            except Exception:
                pass
        return {
            "conversation_state": "idle",
            "current_topic": "general",
            "teasing_level": 0.5,
            "energy": 0.6,
            "verbosity": 0.4,
            "initiation_probability": 0.3,
            "recent_emotional_context": "warm and teasing",
        }

    def get_ongoing_threads(self) -> List[str]:
        episodes = self.db.get_episodes(limit=5)
        return [ep["summary"] for ep in episodes]

    def search_memories(
        self,
        query: str,
        depth: int = 5,
        top_k: Optional[int] = None,
        memory_type: Optional[str] = None,
        min_score: Optional[float] = None,
        weights: Optional[ScoreWeights] = None,
        at_timestamp: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active facts using multi-signal score fusion.
        Suppresses stale memories and duplicates.
        Enforces min_score_threshold (returns empty if relevance is weak).
        """
        effective_depth = top_k if top_k is not None else depth
        w = weights or ScoreWeights()
        if min_score is not None:
            w.min_score_threshold = min_score

        query = query.strip()
        if not query:
            return []

        now_ms = at_timestamp if at_timestamp is not None else int(time.time() * 1000)
        query_vec = deterministic_text_vector(query)
        query_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))

        # 1. Fetch active facts (stale memories already suppressed at DB layer)
        active_facts = self.db.get_active_facts(at_timestamp=now_ms)
        if not active_facts:
            return []

        # 2. Get FTS5 match scores
        fts_matches = self.db.search_facts_fts(query, limit=50)
        fts_ranks = {f["id"]: f.get("bm25_rank", 0.0) for f in fts_matches}

        candidates = []
        for fact in active_facts:
            fact_id = fact["id"]
            fact_text = f"{fact['subject']} {fact['predicate']} {fact['object']}"

            # Vector semantic score
            fact_vec = self.db.get_embedding(fact_id)
            if not fact_vec:
                fact_vec = deterministic_text_vector(fact_text)
                self.db.save_embedding(fact_id, "fact", fact_vec)
            semantic_score = cosine_similarity(query_vec, fact_vec)

            # Lexical score (hybrid FTS5 BM25 + keyword term matches)
            fact_lower = fact_text.lower()
            term_matches = sum(1 for term in query_terms if term in fact_lower)
            lexical_ratio = term_matches / max(1, len(query_terms))
            bm25_boost = 0.3 if fact_id in fts_ranks else 0.0
            lexical_score = min(1.0, lexical_ratio * 0.7 + bm25_boost)

            # Recency score (decay over 60 days)
            days_old = max(0.0, (now_ms - fact.get("last_confirmed", now_ms)) / (1000 * 3600 * 24))
            recency_score = 1.0 / (1.0 + (days_old / 60.0))

            # Importance & Confidence
            importance_score = max(0.0, min(1.0, float(fact.get("importance", 0.5))))
            confidence_score = max(0.0, min(1.0, float(fact.get("confidence", 1.0))))

            # Relevancy gate: recency/importance/confidence only apply if memory is actually relevant to the query
            relevance = max(lexical_score, semantic_score)
            if relevance < 0.28:
                continue

            base_score = (
                w.lexical_weight * lexical_score
                + w.semantic_weight * semantic_score
                + (w.recency_weight * recency_score
                   + w.importance_weight * importance_score
                   + w.confidence_weight * confidence_score) * relevance
            )

            candidates.append({
                "fact": fact,
                "fact_text": fact_text,
                "base_score": base_score,
                "lexical_score": round(lexical_score, 3),
                "semantic_score": round(semantic_score, 3),
                "recency_score": round(recency_score, 3),
                "importance_score": round(importance_score, 3),
                "confidence_score": round(confidence_score, 3),
                "vector": fact_vec,
            })

        if not candidates:
            return []

        # Sort candidate pool by base_score
        candidates.sort(key=lambda x: x["base_score"], reverse=True)

        # 3. Greedy selection with duplication suppression
        selected = []
        target_count = min(max(3, effective_depth), 8)

        for cand in candidates:
            # Calculate duplication penalty against already selected
            max_sim = 0.0
            for sel in selected:
                sim_vec = cosine_similarity(cand["vector"], sel["vector"])
                sim_jac = jaccard_word_similarity(cand["fact_text"], sel["fact_text"])
                max_sim = max(max_sim, sim_vec, sim_jac)

            duplication_penalty = w.duplication_penalty_weight * max_sim
            final_score = cand["base_score"] - duplication_penalty

            if final_score >= w.min_score_threshold:
                selected.append({
                    "id": cand["fact"]["id"],
                    "content": cand["fact_text"],
                    "type": "fact",
                    "source": cand["fact"].get("source_message_id", "local_corpus"),
                    "subject": cand["fact"]["subject"],
                    "predicate": cand["fact"]["predicate"],
                    "object": cand["fact"]["object"],
                    "confidence": cand["fact"]["confidence"],
                    "importance": cand["fact"]["importance"],
                    "source_message_id": cand["fact"]["source_message_id"],
                    "final_score": round(final_score, 3),
                    "lexical_score": cand["lexical_score"],
                    "semantic_score": cand["semantic_score"],
                    "recency_score": cand["recency_score"],
                    "duplication_penalty": round(duplication_penalty, 3),
                    "vector": cand["vector"],
                    "fact_text": cand["fact_text"],
                })

            if len(selected) >= target_count:
                break

        # Remove vector before returning
        for s in selected:
            s.pop("vector", None)
            s.pop("fact_text", None)

        return selected

    def get_style_exemplars(self, mode: str, limit: int = 3, topic_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves real historical message exemplars for the chosen style mode.
        If topic_query is provided, ranks exemplars relevant to that topic.
        """
        all_mode_examples = self.db.get_style_examples(mode=mode, limit=20)
        if not all_mode_examples:
            all_mode_examples = self.db.get_style_examples(limit=20)

        if not all_mode_examples:
            return []

        if not topic_query:
            return all_mode_examples[:limit]

        # Rank exemplars by topic similarity
        q_vec = deterministic_text_vector(topic_query)
        scored = []
        for ex in all_mode_examples:
            ex_vec = deterministic_text_vector(ex["text"])
            sim = cosine_similarity(q_vec, ex_vec)
            scored.append((sim, ex))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def search_corpus_messages(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches all 13,653 classified messages using hybrid FTS5 lexical + category matching.
        """
        if not query or not query.strip():
            return []

        clean_words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
        if not clean_words:
            return []

        with self.db.get_connection() as conn:
            results = []
            try:
                # 1. Try FTS5 match first
                fts_query = " OR ".join([f'"{w}"*' for w in clean_words[:6]])
                sql = """
                    SELECT m.id, m.sender, m.content, m.is_voice, m.category, m.badge, m.ts_ms
                    FROM messages_fts f
                    JOIN messages m ON f.id = m.id
                    WHERE messages_fts MATCH ?
                """
                params: List[Any] = [fts_query]
                if category and category != "all":
                    sql += " AND m.category = ?"
                    params.append(category)

                sql += " ORDER BY rank LIMIT ?"
                params.append(limit)

                cur = conn.execute(sql, params)
                for r in cur.fetchall():
                    results.append(dict(r))
            except Exception:
                pass

            # Fallback to direct LIKE if FTS yielded few results
            if len(results) < limit:
                seen_ids = {r["id"] for r in results}
                like_clauses = " OR ".join(["LOWER(content) LIKE ?" for _ in clean_words[:3]])
                like_params = [f"%{w}%" for w in clean_words[:3]]
                sql_like = f"SELECT id, sender, content, is_voice, category, badge, ts_ms FROM messages WHERE ({like_clauses})"
                if category and category != "all":
                    sql_like += " AND category = ?"
                    like_params.append(category)
                sql_like += " ORDER BY id DESC LIMIT ?"
                like_params.append(limit - len(results))

                try:
                    cur = conn.execute(sql_like, like_params)
                    for r in cur.fetchall():
                        if r["id"] not in seen_ids:
                            results.append(dict(r))
                except Exception:
                    pass

            return results
