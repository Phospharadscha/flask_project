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

-- Create a table to store paints
-- Each paint has a primary key, which increments automatically,
-- a name, which must be unique. So you cannot have two paints with the same name,
-- a price, which is a float. This will be in pounds,
-- a volume, which is a float. This will be in litres,
-- a coverate. This is the area (m2) which can be covered per litre.
CREATE TABLE paint (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  name TEXT UNIQUE NOT NULL,
  price REAL NOT NULL,
  volume REAL NOT NULL,
  coverage REAL NOT NULL
);

-- Create a table to store calculators. 
-- A calculator consists of a primary key, which is an int,
-- an author id, which is a foreign key linking to a user id,
-- a name. 
CREATE TABLE calculator (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  author_id INTEGER NOT NULL, 
  name TEXT NOT NULL, 
  FOREIGN KEY (author_id) REFERENCES user (id)
);

-- Create a table to store rooms.
-- A room consists of a primary key which is an int,
-- a calculator id. This is a foreign key linking to the id of a calculator,
-- a name,
CREATE TABLE room (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  calculator_id INTEGER NOT NULL, 
  name TEXT NOT NULL, 
  FOREIGN KEY (calculator_id) REFERENCES calculator (id)
);

-- Create a table to store walls. #
-- A wall consists of a primary key which is an int, 
-- a room id. This is a foreign key linking to the id of a room,
-- a paint id. This is a foreign key linking to the id of a paint,
-- a name, 
-- the shape of the wall
-- the surface area, in m2. 
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
