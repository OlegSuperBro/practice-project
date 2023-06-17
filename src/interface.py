import PySimpleGUI as psg
import asyncio
from typing import Self

from database import DataBase, Verifier
from datatypes import User


FONT_NAME = "Arial"


class TemplateForm:
    LAYOUT = [[]]
    BUTTON_FUNCS = {}

    WINDOW_SIZE = (200, 200)
    WINDOW_TIMEOUT = 500

    def __init__(self) -> None:
        self.window = psg.Window("Vacations", self.LAYOUT, grab_anywhere=True, size=self.WINDOW_SIZE)

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
        pass


class LoginForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-RETURN-", size=(2, 1)), psg.VPush()],
              [psg.Push(), psg.Text("Логин", font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.Push(), psg.Input("", key="-LOGIN-", size=(20, 2)), psg.Push()],
              [psg.Push(), psg.Text("Пароль", font=(FONT_NAME, 20, "bold")), psg.Push()],
              [psg.Push(), psg.Input("", key="-PASSWORD-", size=(20, 2)), psg.Push()],
              [psg.Push(), psg.Button("Вход", key="-LOG_IN-", size=(20, 1), font=(FONT_NAME, 15, "bold")), psg.Push()],
              [psg.VPush()]]

    WINDOW_SIZE = (200, 250)

    def __init__(self) -> None:
        super().__init__()

        self.BUTTON_FUNCS = {
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
