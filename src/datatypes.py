import datetime
from typing import List
from dataclasses import dataclass, field


@dataclass
class Vacation:
    _id: int = 0
    start_date: datetime.date = datetime.date.today()
    end_date: datetime.date = datetime.date.today()

    @staticmethod
    def from_sql(**kwargs):
        tmp_vacation = Vacation()
        tmp_vacation._id = kwargs.get("id")
        tmp_vacation.start_date = kwargs.get("start_date")
        tmp_vacation.end_date = kwargs.get("end_date")
        return tmp_vacation

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Vacation):
            return False

        if self.start_date == __value.start_date and self.end_date == __value.end_date:
            return True

        return False


@dataclass
class Post:
    _id: int = 0
    name: str = ""
    max_vacations_length: List[int] = field(default_factory=list)  # for each new holiday add new number. For example (1, 5, 3) will allow for this post 3 holidays with length 1, 5 ,3

    @staticmethod
    def from_sql(**kwargs):
        tmp_post = Post()
        tmp_post._id = kwargs.get("id")
        tmp_post.name = kwargs.get("name")
        tmp_post.max_vacations_length = list(map(lambda x: int(x), kwargs.get("max_vacations").lstrip("(").rstrip(")").split(",")))

        return tmp_post


@dataclass
class User:
    _id: int = 0
    login: str = ""
    password: str = ""
    first_name: str = ""
    second_name: str = ""
    surname: str = ""
    post: Post = field(default_factory=Post)
    role: str = "user"
    vacations: List[Vacation] = field(default_factory=list)

    @staticmethod
    def from_sql(**kwargs):
        tmp_user = User()
        tmp_user._id = kwargs.get("id")
        tmp_user.login = kwargs.get("login")
        tmp_user.password = kwargs.get("password")
        tmp_user.first_name = kwargs.get("first_name")
        tmp_user.second_name = kwargs.get("second_name")
        tmp_user.surname = kwargs.get("surname")
        tmp_user.post = kwargs.get("post")
        tmp_user.role = kwargs.get("role")
        tmp_user.vacations = kwargs.get("vacations")
        return tmp_user
