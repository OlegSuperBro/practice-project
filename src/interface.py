import PySimpleGUI as psg
import asyncio
import datetime
import sys
from typing import Self
from copy import deepcopy

from database import DataBase, Verifier
from datatypes import User, Post, Vacation


FONT_NAME = "Arial"


class Theme:
    background = "#27374D"
    push_background = "#27374D"
    text_background = "#27374D"
    button_color = "#526D82"
    column_color = "#27374D"


class TemplateForm:
    LAYOUT = [[]]
    BUTTON_FUNCS = {}

    WINDOW_SIZE = (200, 200)
    WINDOW_TIMEOUT = 500

    def __init__(self) -> None:
        self.window = psg.Window("Vacations", deepcopy(self.LAYOUT), grab_anywhere=True, size=self.WINDOW_SIZE, finalize=True, background_color=Theme.background)

        self.BUTTON_FUNCS = {}  # should be re-defined in __init__

    def main_loop(self) -> None:
        while True:
            self._loop_step()

    def _start(self) -> None:
        self.main_loop()

    def _loop_step(self) -> None:
        self.event, self.values = self.window.read(timeout=self.WINDOW_TIMEOUT)

        if self.event == psg.WIN_CLOSED or self.event == "-EXIT-":
            sys.exit(0)

        self.event = self.event.split("::")[-1:][0]  # bruh

        tmp_func = self.BUTTON_FUNCS.get(self.event)
        if tmp_func is not None:
            tmp_func()

    def change_window(self, form: Self):
        self.window.close()
        del self
        form._start()


class StartForm(TemplateForm):
    LAYOUT = [[psg.VPush(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Button("Вход", key="-LOGIN-", size=(25, 1), font=(FONT_NAME, 20, "bold")), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Button("Регистрация", key="-REGISTER-", size=(25, 1), font=(FONT_NAME, 20, "bold")), psg.Push(background_color=Theme.push_background)],
              [psg.VPush(background_color=Theme.push_background)]]

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
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.VPush(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Text("Логин", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Input("", key="-LOGIN-", size=(20, 1)), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Text("Пароль", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*"), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Button("Вход", key="-LOG_IN-", size=(20, 1), font=(FONT_NAME, 15, "bold"), button_color=Theme.button_color), psg.Push(background_color=Theme.push_background)],
              [psg.VPush(background_color=Theme.push_background)]]

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
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.VPush(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Фамилия", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-FIRST_NAME-", size=(20, 1))]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Имя", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-SECOND_NAME-", size=(20, 1))]], background_color=Theme.column_color), psg.Push(background_color=Theme.push_background)],

              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Отчество", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-SURNAME-", size=(20, 1))]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Должность", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Combo([post.name.capitalize() for post in DataBase().get_posts()], key="-POST-", size=(18, 1), readonly=True)]], background_color=Theme.column_color), psg.Push(background_color=Theme.push_background)],

              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Логин", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)],
                                                                             [psg.Input("", key="-LOGIN-", size=(20, 1))],
                                                                             [psg.Text("Пароль", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)],
                                                                             [psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*")]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background), psg.vbottom(psg.Button("Регистрация", key="-REGISTER-", size=(20, 1), font=(FONT_NAME, 10, "bold"), button_color=Theme.button_color)), psg.Push(background_color=Theme.push_background)],
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
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.Text("", key="-LOGINED_AS-", font=(FONT_NAME, 10, "bold"), background_color=Theme.text_background)],

              [psg.Column([[psg.CalendarButton("", key="-FIRST_DATE-", format="%d-%m-%Y", target=(psg.ThisRow, 0), close_when_date_chosen=False, button_color=Theme.button_color),
                            psg.Text("-", font=(FONT_NAME, 10, "bold"), background_color=Theme.text_background),
                            psg.CalendarButton("", key="-SECOND_DATE-", format="%d-%m-%Y", target=(psg.ThisRow, 2), close_when_date_chosen=False, button_color=Theme.button_color)],
                           [psg.Push(background_color=Theme.column_color), psg.Button("Добавить", key="-ADD-", button_color=Theme.button_color)]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background),
               psg.Button("Удалить выделенное", key="-DELETE-", button_color=Theme.button_color)],

              [psg.Listbox([], key="-VACATIONS_LIST-", no_scrollbar=True, expand_x=True, expand_y=True)],
              [psg.Push(background_color=Theme.column_color), psg.Button("Сохранить", key="-SAVE-", button_color=Theme.button_color)]]

    WINDOW_SIZE = (350, 250)

    def __init__(self, user: User) -> None:
        super().__init__()

        self.BUTTON_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-ADD-": lambda: self.add(),
            "-DELETE-": lambda: self.delete(),
            "-SAVE-": lambda: self.save(),
        }

        self.user = user

        self.vacations = user.vacations

        self.window["-LOGINED_AS-"].update(f"Вы вошли как {self.user.login}")
        self.window["-FIRST_DATE-"].update(f"{datetime.date.today().day}/{datetime.date.today().month}/{datetime.date.today().year}")
        self.window["-SECOND_DATE-"].update(f"{datetime.date.today().day}/{datetime.date.today().month}/{datetime.date.today().year}")

        self._update_vacations_list()

    def _update_vacations_list(self) -> None:
        self.window["-VACATIONS_LIST-"].update([f"{vacation.start_date.strftime('%d-%m-%Y')} - {vacation.end_date.strftime('%d-%m-%Y')}" for vacation in self.vacations])

    def back(self) -> None:
        self.change_window(LoginForm())

    def add(self) -> None:
        self.vacations.append(Vacation(start_date=datetime.datetime.strptime(self.values["-FIRST_DATE-"], "%d-%m-%Y").date(),
                                       end_date=datetime.datetime.strptime(self.values["-SECOND_DATE-"], "%d-%m-%Y").date()))
        self._update_vacations_list()

    def save(self) -> None:
        tmp = DataBase()
        tmp.delete_vacations_for_user(self.user)
        for vacation in self.vacations:
            tmp.add_vacation(self.user, vacation)

    def delete(self) -> None:
        for selected_vacation in self.values["-VACATIONS_LIST-"]:
            tmp_vacation = Vacation(start_date=datetime.datetime.strptime(selected_vacation.split(" - ")[0], "%d-%m-%Y").date(),
                                    end_date=datetime.datetime.strptime(selected_vacation.split(" - ")[1], "%d-%m-%Y").date())
            for vacation in self.vacations:
                if vacation == tmp_vacation:
                    self.vacations.remove(vacation)
        self._update_vacations_list()


class AdminForm(TemplateForm):
    pass


if __name__ == "__main__":
    form = UserForm(DataBase().get_user("root"))
    # form = StartForm()

    event_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.create_task(form._start())

    event_loop.run_forever()
