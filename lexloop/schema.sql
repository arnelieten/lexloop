DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS dictionary;
DROP TABLE IF EXISTS dashboard;
DROP TABLE IF EXISTS password_reset;

PRAGMA foreign_keys = ON;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  register_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dictionary (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  french_word TEXT UNIQUE NOT NULL,
  english_word TEXT NOT NULL
);

CREATE TABLE dashboard (
  status_word TEXT NOT NUll,
  switch_date TIMESTAMP,
  user_id INTEGER,
  dictionary_id INTEGER,
  PRIMARY KEY (user_id, dictionary_id),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (dictionary_id) REFERENCES dictionary(id)
);

CREATE TABLE password_reset (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);