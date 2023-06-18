DROP TABLE IF EXISTS vacations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
  id serial,
  name text,
  max_vacations text,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE users (
  id serial,
  login text NOT NULL,
  password text NOT NULL,
  first_name text,
  second_name text,
  surname text,
  post text REFERENCES posts (name) ON DELETE SET NULL,
  role text DEFAULT 'user',
  recovery_code integer,
  UNIQUE (login),
  PRIMARY KEY (id)
);


CREATE TABLE vacations (
  id serial,
  user_id integer NOT NULL REFERENCES users ON DELETE CASCADE,
  start_date date NOT NULL,
  end_date date NOT NULL,
  PRIMARY KEY (id)
);
