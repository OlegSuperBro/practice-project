import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Union

from datatypes import User, Vacation, Post
from config import CONFIG


class Verifier:
    @staticmethod
    def password_is_valid(password: str):
        if len(password) < CONFIG.min_passwords_length:
            return False
        if password in CONFIG.banned_passwords:
            return False

        return True

    @staticmethod
    def username_is_valid(username: str):
        if len(username) < CONFIG.min_username_length:
            return False
        if username in CONFIG.banned_usernames:
            return False

        return True


def get_connection():
    """
    Returns connection to database

    Returns
    ----
    psycopg2.connection - connection to database
    None - No connection :(  (error accured, possibly database is offline)
    """
    try:
        return psycopg2.connect(dbname="vacations", user="postgres", password="root")
    except psycopg2.DatabaseError:
        return None


class DataBase:
    def __init__(self, connection=get_connection()) -> None:
        self.connection = connection

    def user_exist(self, user: User):
        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM users WHERE login={user.login}")
            return len(cur.fetchall()) != 0

    def register_user(self, user: User) -> int:
        if self.user_exist(user):
            return 1

        if Verifier.username_is_valid(user.login):
            return 2

        if Verifier.password_is_valid(user.password):
            return 3

        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("INSERT INTO users (login, password, first_name, second_name, surname, post, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (user.login, user.password, user.first_name, user.second_name, user.surname, user.post.name, user.role))

        return 0

    def login_user(self, user: User) -> bool:
        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM users WHERE login={user.login} AND pasword={user.password}")
            return len(cur.fetchall()) != 0

    def get_vacations_for_user(self, user: User) -> List[Vacation]:
        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM vacations WHERE user_id={user._id}")
            if cur.fetchall() == []:
                return None
            return [Vacation.from_sql(vacation) for vacation in cur.fetchall()]

    def get_post(self, name: str) -> Union[Post, None]:
        """
        Get post from it name

        Args
        ----
        name: str
            name of post

        Returns
        ----
        Post
            post representation
        """
        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM posts WHERE name={name}")
            if cur.fetchall() == []:
                return None
            return Post(**cur.fetchone())

    def get_user(self, login) -> Union[User, None]:
        with self.connection.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"SELECT * FROM users WHERE login={login}")
            if cur.fetchall() == []:
                return None
            result = cur.fetchone()
            result["vacations"] = self.get_vacations_for_user(User(_id=result.get("id")))
            return User.from_sql(result)

    def __delete__(self, instance):
        self.connection.close()
