-- Remove the tables if they already exist 
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- Create a table to store users
-- A user is defined by a primary key, which is the ID. This id increments with every new user
-- Users also store a username, which is text. And a password, which is also text. 
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  admin INTEGER NOT NULL 
);

-- Create a table to store posts
-- Posts are defined by a primary integer key
-- They have an author id, which will match an id in the user table
-- created, which is a timestamp marking when the post was made
-- title, which stores the title of the post
-- body, which stores the content of the post
-- The foreign key used here links a post to a given user in the user table
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);