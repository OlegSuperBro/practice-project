DROP TABLE IF EXISTS vacations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
  id integer,
  name text,
  max_vacations text,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE users (
  id integer,
  login text NOT NULL,
  password text NOT NULL,
  first_name text NOT NULL,
  second_name text NOT NULL,
  surname text DEFAULT '',
  post text NOT NULL REFERENCES posts (name) ON DELETE SET NULL,
  role text DEFAULT 'user',
  UNIQUE (login),
  PRIMARY KEY (id)
);


CREATE TABLE vacations (
  id integer,
  user_id integer NOT NULL REFERENCES users ON DELETE CASCADE,
  start_date date NOT NULL,
  end_date date NOT NULL,
  PRIMARY KEY (id)
);
