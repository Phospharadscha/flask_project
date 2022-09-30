-- Remove the tables if they already exist 
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cryptid;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  about TEXT NOT NULL, 
  favourite_crpytid TEXT NOT NULL,
  cryptid_id INTEGER NOT NULL,
  FOREIGN KEY (cryptid_id) REFERENCES cryptid (id)
);

CREATE TABLE cryptid (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL, 
  first_sighted TIMESTAMP NOT NULL,
  last_sighted TIMESTAMP NOT NULL, 
  wikipedia_url TEXT NOT NULL,
  alternative_url TEXT
);