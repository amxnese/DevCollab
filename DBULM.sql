CREATE TABLE Users (
  username VARCHAR PRIMARY KEY,
  password VARCHAR
);

CREATE TABLE Projects (
  project_id INTEGER PRIMARY KEY,
  username VARCHAR,
  name VARCHAR,
  FOREIGN KEY (username) REFERENCES Users(username)
);

CREATE TABLE Tasks (
  task_id INTEGER PRIMARY KEY,
  project_id INTEGER,
  username VARCHAR,
  likes INTEGER,
  dislikes INTEGER,
  status VARCHAR,
  FOREIGN KEY (project_id) REFERENCES Projects(project_id),
  FOREIGN KEY (username) REFERENCES Users(username)
);

CREATE TABLE Interactions (
  interaction_id INTEGER PRIMARY KEY,
  task_id INTEGER,
  username VARCHAR,
  type VARCHAR,
  FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
  FOREIGN KEY (username) REFERENCES Users(username)
);
