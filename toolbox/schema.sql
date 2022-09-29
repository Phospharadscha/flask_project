-- Remove the tables if they already exist 
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS paint;
DROP TABLE IF EXISTS calculator;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS wall;
DROP TABLE IF EXISTS obstacle;

-- Create a table to store users
-- A user is defined by a primary key, which is the ID. This id increments with every new user
-- Users also store a username, which is text. And a password, which is also text. 
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  admin INTEGER NOT NULL 
);

CREATE TABLE paint (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  name TEXT UNIQUE NOT NULL,
  price REAL NOT NULL,
  volume REAL NOT NULL,
  coverage REAL NOT NULL
);

CREATE TABLE calculator (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  author_id INTEGER NOT NULL, 
  name TEXT NOT NULL, 
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE room (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  calculator_id INTEGER NOT NULL, 
  name TEXT NOT NULL, 
  FOREIGN KEY (calculator_id) REFERENCES calculator (id)
);

CREATE TABLE wall (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  room_id INTEGER NOT NULL, 
  paint_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  shape TEXT NOT NULL,  
  surface REAL NOT NULL,
  FOREIGN KEY (room_id) REFERENCES room (id),
  FOREIGN KEY (paint_id) REFERENCES paint (id)
);

CREATE TABLE obstacle (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  wall_id INTEGER NOT NULL, 
  name TEXT NOT NULL,
  shape TEXT NOT NULL,  
  surface REAL NOT NULL, 
  FOREIGN KEY (wall_id) REFERENCES wall (id)
);