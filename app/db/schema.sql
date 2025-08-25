PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS movies(
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  title    TEXT NOT NULL,
  year     TEXT,
  file_id  TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_movies_title_year ON movies(title, year);

CREATE TABLE IF NOT EXISTS settings(
  key   TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS junk_words(
  word TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS pending_actions(
  user_id INTEGER NOT NULL,
  chat_id INTEGER NOT NULL,
  action  TEXT NOT NULL,
  context TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(user_id, chat_id)
);
