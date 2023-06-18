import PySimpleGUI as psg
import asyncio
from typing import Self
from copy import deepcopy

from database import DataBase, Verifier
from datatypes import User, Post


FONT_NAME = "Arial"


class TemplateForm:
    LAYOUT = [[]]
    BUTTON_FUNCS = {}

    WINDOW_SIZE = (200, 200)
    WINDOW_TIMEOUT = 500

    def __init__(self) -> None:
        self.window = psg.Window("Vacations", deepcopy(self.LAYOUT), grab_anywhere=True, size=self.WINDOW_SIZE)

        self.BUTTON_FUNCS = {}  # should be re-defined in __init__

    def main_loop(self) -> None:
        while True:
            self._loop_step()

    def _start(self) -> None:
        self.main_loop()

    def _loop_step(self) -> None:
        self.event, self.values = self.window.read(timeout=self.WINDOW_TIMEOUT)

        if self.event == psg.WIN_CLOSED or self.event == "-EXIT-":
            exit()

        self.event = self.event.split("::")[-1:][0]  # bruh

        tmp_func = self.BUTTON_FUNCS.get(self.event)
        if tmp_func is not None:
            tmp_func()

    def change_window(self, form: Self):
        self.window.close()
        del self
        form._start()


class StartForm(TemplateForm):
    LAYOUT = [[psg.VPush()],
              [psg.Push(), psg.Button("Вход", key="-LOGIN-", size=(25, 1), font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.Push(), psg.Button("Регистрация", key="-REGISTER-", size=(25, 1), font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.VPush()]]

    WINDOW_SIZE = (225, 175)

    def __init__(self) -> None:
        super().__init__()

        self.BUTTON_FUNCS = {
            "-LOGIN-": lambda: self.login(),
            "-REGISTER-": lambda: self.register(),
        }

    def login(self):
        self.change_window(LoginForm())

    def register(self):
        self.change_window(RegisterForm())


class LoginForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1)), psg.VPush()],
              [psg.Push(), psg.Text("Логин", font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.Push(), psg.Input("", key="-LOGIN-", size=(20, 1)), psg.Push()],
              [psg.Push(), psg.Text("Пароль", font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.Push(), psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*"), psg.Push()],
              [psg.Push(), psg.Button("Вход", key="-LOG_IN-", size=(20, 1), font=(FONT_NAME, 15, "bold")), psg.Push()],
              [psg.VPush()]]

    WINDOW_SIZE = (200, 250)

    def __init__(self) -> None:
        super().__init__()

        self.BUTTON_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-LOG_IN-": lambda: self.login(),
        }

    def login(self) -> None:
        tmp_user = User(login=self.values.get("-LOGIN-"), password=self.values.get("-PASSWORD-"))

        if not (Verifier.username_is_valid(tmp_user.login)) or not (Verifier.password_is_valid(tmp_user.password)):
            psg.popup("Недопустимые данные", title="Ошибка")
            return

        if not DataBase().login_user(tmp_user):
            psg.popup("Неверные данные", title="Ошибка")
            return
        else:
            self.change_window(UserForm(DataBase().get_user(tmp_user)))
            return

    def back(self) -> None:
        self.change_window(StartForm())


class RegisterForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1)), psg.VPush()],
              [psg.Push(), psg.Column([[psg.Text("Фамилия", font=(FONT_NAME, 20, "bold"))], [psg.Input("", key="-FIRST_NAME-", size=(20, 1))]]),
               psg.Push(), psg.Column([[psg.Text("Имя", font=(FONT_NAME, 20, "bold"))], [psg.Input("", key="-SECOND_NAME-", size=(20, 1))]]), psg.Push()],

              [psg.Push(), psg.Column([[psg.Text("Отчество", font=(FONT_NAME, 20, "bold"))], [psg.Input("", key="-SURNAME-", size=(20, 1))]]),
               psg.Push(), psg.Column([[psg.Text("Должность", font=(FONT_NAME, 20, "bold"))], [psg.Combo([post.name.capitalize() for post in DataBase().get_posts()], key="-POST-", size=(18, 1), readonly=True)]]), psg.Push()],

              [psg.Push(), psg.Column([[psg.Text("Логин", font=(FONT_NAME, 20, "bold"))],
                                       [psg.Input("", key="-LOGIN-", size=(20, 1))],
                                       [psg.Text("Пароль", font=(FONT_NAME, 20, "bold"))],
                                       [psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*  ")]]),
               psg.Push(), psg.vbottom(psg.Button("Регистрация", key="-REGISTER-", size=(20, 1), font=(FONT_NAME, 10, "bold"))), psg.Push()],
              [psg.VPush()]]

    WINDOW_SIZE = (400, 400)

    def __init__(self) -> None:
        super().__init__()

        self.BUTTON_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-REGISTER-": lambda: self.register()
        }

    def back(self) -> None:
        self.change_window(StartForm())

    def register(self) -> None:
        tmp_user = User()

        tmp_user.first_name = self.values.get("-FIRST_NAME-")
        tmp_user.second_name = self.values.get("-SECOND_NAME-")
        tmp_user.surname = self.values.get("-SURNAME-")
        tmp_user.post = Post(name=self.values.get("-POST-").lower())
        tmp_user.login = self.values.get("-LOGIN-")
        tmp_user.password = self.values.get("-PASSWORD-")

        if not (tmp_user.first_name != "" and tmp_user.second_name != "" and tmp_user.post.name != "" and tmp_user.login != "" and tmp_user.password != ""):
            psg.Popup("Заполните все необходимые поля", title="Ошибка")
            return

        return_code = DataBase().register_user(tmp_user)

        if return_code == 0:
            self.change_window(UserForm(DataBase().get_user(tmp_user)))

        elif return_code == 1:
            psg.Popup("Такой логин уже существует", title="Ошибка")
            return

        elif return_code == 2:
            psg.Popup("Логин или пароль не верны. Попробуйте использовать другие", title="Ошибка")
            return


class UserForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-RETURN-", size=(2, 1)), psg.VPush()]]

    def __init__(self, user: User) -> None:
        super().__init__()

        self.user = user


if __name__ == "__main__":
    form = StartForm()

    event_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.create_task(form._start())

    event_loop.run_forever()
