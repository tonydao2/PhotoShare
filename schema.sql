CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id INT NOT NULL  AUTO_INCREMENT,
    gender VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    birthday DATE NOT NULL,
    hometown VARCHAR(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Photos
(
  photo_id INT AUTO_INCREMENT,
  user_id INT,
  imgdata longblob,
  caption VARCHAR(255),
  album_id INT NOT NULL,
  CONSTRAINT photos_pk PRIMARY KEY (photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Albums
(
  album_id INT AUTO_INCREMENT,
  user_id int4 NOT NULL,
  album_name VARCHAR(255) NOT NULL,
  date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX upid_idx (user_id),
  CONSTRAINT albums_pk PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Comments
(
  comment_id INT NOT NULL AUTO_INCREMENT,
  text TEXT NOT NULL,
  user_id INT NOT NULL,
  picture_id INT NOT NULL,
  date_of_comment DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (comment_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
);

CREATE TABLE Likes
(
  user_id INT NOT NULL,
  picture_id INT NOT NULL,
  PRIMARY KEY (photo_id, user_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
);

CREATE TABLE Tags
(
  tag_id INT,
  name VARCHAR(100),
  PRIMARY KEY(tag_id)
);

CREATE TABLE Tagged
(
  photo_id INT,
  tag_id INT,
  PRIMARY KEY(photo_id, tag_id),
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id),
  FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);

CREATE TABLE Friends
(
  UID1 INT NOT NULL,
  UID2 INT NOT NULL,
  CHECK (UID1 != UID2),
  PRIMARY KEY (UID1, UID2),
  FOREIGN KEY (UID1) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (UID2) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
