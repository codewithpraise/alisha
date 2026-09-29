-- FriendOS / Alisha Bubbzieee Memory Database Schema

CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  type TEXT CHECK(type IN ('episodic', 'semantic', 'relational', 'behavioral', 'ongoing')),
  source TEXT CHECK(source IN ('real_conversation', 'inference', 'user_input')),
  confidence REAL DEFAULT 1.0,
  created_at INTEGER,
  last_accessed INTEGER,
  access_count INTEGER DEFAULT 0,
  keywords TEXT,        -- comma-separated tags
  embedding TEXT        -- JSON array of float values for zero-cost local vector cosine search
);

CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  started_at INTEGER,
  ended_at INTEGER,
  turn_count INTEGER,
  unresolved_threads TEXT  -- JSON array
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT REFERENCES conversations(id),
  role TEXT CHECK(role IN ('user', 'alisha')),
  content TEXT NOT NULL,
  timestamp INTEGER,
  message_type TEXT CHECK(message_type IN ('text', 'voice', 'reaction'))
);

CREATE TABLE IF NOT EXISTS friend_state (
  id INTEGER PRIMARY KEY DEFAULT 1,
  conversation_state TEXT,
  current_topic TEXT,
  unfinished_threads TEXT,
  recent_emotional_context TEXT,
  initiation_probability REAL DEFAULT 0.3,
  teasing_level REAL DEFAULT 0.5,
  energy REAL DEFAULT 0.5,
  verbosity REAL DEFAULT 0.4,
  last_updated INTEGER
);

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
