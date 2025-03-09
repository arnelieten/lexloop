DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS dictionary;
DROP TABLE IF EXISTS interface;

PRAGMA foreign_keys = ON;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  register_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE dictionary (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  french_word TEXT UNIQUE NOT NULL,
  english_word TEXT NOT NULL
);

CREATE TABLE interface (
  status_word TEXT NOT NULL,
  switch_date TIMESTAMP NOT NULL,
  user_id INTEGER,
  dictionary_id INTEGER,
  PRIMARY KEY (user_id, dictionary_id),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
  FOREIGN KEY (dictionary_id) REFERENCES dictionary(id)
);
