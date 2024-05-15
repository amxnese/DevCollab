Table Users {
  username varchar [pk]
  password varchar
}

Table Projects {
  project_id int [pk]
  username varchar [ref: > Users.username]
  name varchar
}

Table Tasks {
  task_id int [pk]
  project_id int [ref: > Projects.project_id]
  username varchar [ref: > Users.username]
  likes int
  dislikes int
  status varchar
}

Table Interactions {
  interaction_id int [pk]
  task_id int [ref: > Tasks.task_id]
  username varchar [ref: > Users.username]
  type varchar
}
