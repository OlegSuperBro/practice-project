import PySimpleGUI as psg
import datetime
import sys
from typing import Self
from copy import deepcopy

from database import DataBase, Verifier, ping_connection, export_to_excel
from datatypes import User, Post, Vacation
from recover import send_recovery_email, create_recovery_code, create_recovery_text


FONT_NAME = "Arial"


# 27374D
# 526D82
# 9DB2BF
# DDE6ED
class Theme:
    background_color = "#27374D"
    push_background = "#27374D"
    text_background = "#27374D"
    button_color = "#526D82"
    column_color = "#27374D"
    unactive_tab_color = "#27374D"
    unactive_tab_text_color = "#FFFFFF"
    active_tab_color = "#DDE6ED"
    active_tab_text_color = "#000000"


class TemplateForm:
    LAYOUT = [[]]
    EVENT_FUNCS = {}

    WINDOW_SIZE = (200, 200)
    WINDOW_TIMEOUT = 500

    def __init__(self) -> None:
        self.window = psg.Window("Vacations", deepcopy(self.LAYOUT), grab_anywhere=True, size=self.WINDOW_SIZE, finalize=True, background_color=Theme.background_color)

        self.EVENT_FUNCS = {}  # should be re-defined in __init__

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

        tmp_func = self.EVENT_FUNCS.get(self.event)
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
              [psg.Push(background_color=Theme.push_background), psg.Button("Экспортировать все отпуски", key="-EXPORT_VACATIONS-", size=(25, 1), font=(FONT_NAME, 9, "bold")), psg.Push(background_color=Theme.push_background)],
              [psg.VPush(background_color=Theme.push_background)]]

    WINDOW_SIZE = (225, 175)

    def __init__(self) -> None:
        if not ping_connection():
            psg.popup("База данных не доступна. Возможно она в данный момент оффлайн.", title="Ошибка")
            sys.exit(0)

        super().__init__()

        self.EVENT_FUNCS = {
            "-LOGIN-": lambda: self.login(),
            "-REGISTER-": lambda: self.register(),
            "-EXPORT_VACATIONS-": lambda: self.export_vacations()
        }

    def login(self):
        self.change_window(LoginForm())

    def register(self):
        self.change_window(RegisterForm())

    def export_vacations(self):
        file_path = psg.PopupGetFile("Сохранить как", "Сохранить как...", save_as=True, no_window=True, file_types=[("Excel 2010 files", "*.xlsx")])

        if file_path == "":
            return

        workbook = export_to_excel()

        try:
            workbook.save(file_path)
            psg.popup("Экспортировано успешно")
        except PermissionError:
            psg.popup("Не удалось открыть файл, возможно он занят другой программой или процессом", title="Ошибка")


class RecoveryForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color)],
              [psg.Text("Если вы забыли пароль, то можете отправить запрос на востановление. (старый код перестанет действовать)", background_color=Theme.text_background)],
              [psg.Text("Логин", background_color=Theme.text_background), psg.Input(size=(20, 1), key="-REQUEST_LOGIN-")],
              [psg.Text("Добавить дополнительную информацию (например почту для контакта)", background_color=Theme.text_background)],
              [psg.Multiline(size=(40, 5), key="-ADDITIONAL_INFO-")],
              [psg.Push(background_color=Theme.push_background), psg.Button("Отправить запрос", key="-SEND_REQUEST-", button_color=Theme.button_color)],
              [psg.Text("Если у вас уже есть код введите его", background_color=Theme.text_background)],
              [psg.Text("Логин", background_color=Theme.text_background), psg.Input(size=(20, 1), key="-CODE_LOGIN-"), psg.Text("Код", background_color=Theme.text_background), psg.Input(size=(10, 1), key="-CODE-")],
              [psg.Text("Новый пароль", background_color=Theme.text_background), psg.Input(size=(20, 1), key="-CODE_PASSWORD-", password_char="*"), psg.Button("Изменить пароль", key="-CHANGE_PASSWORD-", button_color=Theme.button_color)]]

    WINDOW_SIZE = (500, 350)

    def __init__(self) -> None:
        super().__init__()

        self.EVENT_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-SEND_REQUEST-": lambda: self.send_request(),
            "-CHANGE_PASSWORD-": lambda: self.change_password(),
        }

    def back(self) -> None:
        self.change_window(LoginForm())

    def send_request(self):
        login = self.values["-REQUEST_LOGIN-"]
        if not Verifier.username_is_valid(login):
            psg.Popup("Данный логин не допустим")
            return
        if not DataBase().user_exist(login):
            psg.Popup("Данного пользователя не существует")
            return

        create_recovery_code(DataBase().get_user(login))
        send_recovery_email(create_recovery_text(DataBase().get_user(login), additional_info=self.values["-ADDITIONAL_INFO-"]))
        psg.popup("Запрос отправлен успешно")

    def change_password(self):
        login = self.values["-CODE_LOGIN-"]
        password = self.values["-CODE_PASSWORD-"]
        code = self.values["-CODE-"]

        if not (Verifier.username_is_valid(login) and Verifier.password_is_valid(password)):
            psg.Popup("Данные не допустимы")
            return

        if not DataBase().user_exist(login):
            psg.Popup("Данного пользователя не существует")
            return

        if code == "" or not DataBase().check_recovery_for_user(user=DataBase().get_user(login), code=int(code)):
            psg.Popup("Неверный код для востановления")
            return

        DataBase().set_password_for_user(DataBase().get_user(login), password)
        DataBase().delete_recovery_for_user(DataBase().get_user(login))
        self.change_window(UserForm(DataBase().get_user(login)))


class LoginForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.VPush(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Text("Логин", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Input("", key="-LOGIN-", size=(20, 1)), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Text("Пароль", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*"), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Button("Вход", key="-LOG_IN-", size=(20, 1), font=(FONT_NAME, 15, "bold"), button_color=Theme.button_color), psg.Push(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Button("Забыли пароль", key="-FORGET_PASSWORD-", size=(15, 1), font=(FONT_NAME, 10, "bold"), button_color=Theme.button_color), psg.VPush(background_color=Theme.push_background)]]

    WINDOW_SIZE = (200, 250)

    def __init__(self) -> None:
        super().__init__()

        self.EVENT_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-LOG_IN-": lambda: self.login(),
            "-FORGET_PASSWORD-": lambda: self.forget_password(),
        }

    def login(self) -> None:
        tmp_user = User(login=self.values.get("-LOGIN-"), password=self.values.get("-PASSWORD-"))

        if not DataBase().login_user(tmp_user):
            psg.popup("Неверные данные", title="Ошибка")
            return
        else:
            user = DataBase().get_user(tmp_user)
            if user.role == "admin":
                self.change_window(AdminForm(user))
            elif user.role == "user":
                self.change_window(UserForm(user))
            return

    def forget_password(self):
        self.change_window(RecoveryForm())

    def back(self) -> None:
        self.change_window(StartForm())


class RegisterForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.VPush(background_color=Theme.push_background)],
              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Фамилия", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-FIRST_NAME-", size=(20, 1))]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Имя", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-SECOND_NAME-", size=(20, 1))]], background_color=Theme.column_color), psg.Push(background_color=Theme.push_background)],

              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Отчество", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Input("", key="-SURNAME-", size=(20, 1))]], background_color=Theme.column_color),
               psg.Push(background_color=Theme.push_background), psg.Column([[psg.Text("Должность", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)], [psg.Combo([post.name.capitalize() for post in DataBase().get_posts()], key="-POST-", size=(18, 1), readonly=True)]], background_color=Theme.column_color), psg.Push(background_color=Theme.push_background)],

              [psg.Push(background_color=Theme.push_background), psg.Column([[psg.Column([[psg.Text("Логин", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)],
                                                                                          [psg.Input("", key="-LOGIN-", size=(20, 1))]], background_color=Theme.column_color)],
                                                                             [psg.Column([[psg.Text("Пароль", font=(FONT_NAME, 20, "bold"), background_color=Theme.text_background)],
                                                                                          [psg.Input("", key="-PASSWORD-", size=(20, 1), password_char="*"), psg.Push(background_color=Theme.push_background),  psg.Button("Регистрация", key="-REGISTER-", size=(20, 1), font=(FONT_NAME, 10, "bold"), button_color=Theme.button_color)]], background_color=Theme.column_color)]],
                                                                            background_color=Theme.column_color), psg.Push(background_color=Theme.push_background)]]

    WINDOW_SIZE = (400, 400)

    def __init__(self) -> None:
        super().__init__()

        self.EVENT_FUNCS = {
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

        if DataBase().user_exist(tmp_user):
            psg.Popup("Такой логин уже существует", title="Ошибка")
            return

        if not (Verifier.username_is_valid(tmp_user.login)) or not (Verifier.password_is_valid(tmp_user.password)):
            psg.Popup("Логин или пароль не верны. Попробуйте использовать другие", title="Ошибка")
            return

        DataBase().register_user(tmp_user)

        self.change_window(UserForm(DataBase().get_user(tmp_user)))


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

    WINDOW_SIZE = (375, 250)

    WINDOW_TIMEOUT = 100

    def __init__(self, user: User) -> None:
        super().__init__()

        self.EVENT_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-ADD-": lambda: self.add(),
            "-DELETE-": lambda: self.delete(),
            "-SAVE-": lambda: self.save(),
        }

        self.user = user

        self.vacations = user.vacations
        self.vacation_id = 100

        self.window["-LOGINED_AS-"].update(f"Вы вошли как {self.user.login}")
        self.window["-FIRST_DATE-"].update(datetime.date.today().strftime("%d/%m/%Y"))
        self.window["-SECOND_DATE-"].update(datetime.date.today().strftime("%d/%m/%Y"))

        self.update_vacations_list()

    def update_vacations_list(self) -> None:
        self.window["-VACATIONS_LIST-"].update([f"{index + 1}. {vacation.start_date.strftime('%d-%m-%Y')} - {vacation.end_date.strftime('%d-%m-%Y')}" for index, vacation in enumerate(self.vacations)])

    def _loop_step(self) -> None:
        super()._loop_step()

        if self.values["-FIRST_DATE-"] != "":
            self.window["-FIRST_DATE-"].update(self.values["-FIRST_DATE-"].replace("-", "/"))
        if self.values["-SECOND_DATE-"] != "":
            self.window["-SECOND_DATE-"].update(self.values["-SECOND_DATE-"].replace("-", "/"))

    def back(self) -> None:
        self.change_window(LoginForm())

    def add(self) -> None:
        if self.values["-FIRST_DATE-"] == "":
            self.values["-FIRST_DATE-"] = datetime.datetime.now().strftime("%d-%m-%Y")

        if self.values["-SECOND_DATE-"] == "":
            self.values["-SECOND_DATE-"] = datetime.datetime.now().strftime("%d-%m-%Y")
        self.vacations.append(Vacation(_id=self.vacation_id, start_date=datetime.datetime.strptime(self.values["-FIRST_DATE-"], "%d-%m-%Y").date(),
                                       end_date=datetime.datetime.strptime(self.values["-SECOND_DATE-"], "%d-%m-%Y").date()))
        self.vacation_id += 1
        self.update_vacations_list()

    def save(self) -> None:
        if len(self.vacations) > len(self.user.post.max_vacations_length):
            psg.popup(f"Превышено максимум отпусков ({len(self.user.post.max_vacations_length)})", title="Ошибка")
            return

        for index1, vacation in enumerate(self.vacations):
            for index2, tmp_vacation in enumerate(self.vacations):
                if vacation._id != tmp_vacation._id and (vacation.start_date <= tmp_vacation.end_date and vacation.end_date >= tmp_vacation.start_date):
                    psg.popup(f"Отпуски не могут пересекаться ({index1 + 1} и {index2 + 1})", title="Ошибка")
                    return

            if (vacation.end_date - vacation.start_date).days > self.user.post.max_vacations_length[index1]:
                psg.popup(f"Отпуск превышает масимальную длительность ({index1 + 1} max:{self.user.post.max_vacations_length[index1]})", title="Ошибка")
                return

            if len(DataBase().execute_sql(f"SELECT * FROM vacations WHERE start_date <= '{vacation.end_date}' AND end_date >= '{vacation.start_date}' AND user_id != {self.user._id}")) > 0:
                psg.popup(f"Ваш отпуск пересекается с чужим ({index1 + 1})", title="Ошибка")
                return

            if not Verifier.vacation_is_valid(vacation):
                psg.popup(f"Дата начала отпуска не может быть меньше даты окончания ({index1 + 1})", title="Ошибка")
                return

        DataBase().delete_vacations_for_user(self.user, commit=False)
        for vacation in self.vacations:
            DataBase().add_vacation(self.user, vacation)
        psg.Popup("Успешно сохранено")
        return

    def delete(self) -> None:
        for selected_vacation in self.values["-VACATIONS_LIST-"]:
            self.vacations.pop(int(selected_vacation.split(".")[0]) - 1)
        self.update_vacations_list()


class AdminForm(TemplateForm):
    LAYOUT = [[psg.Button("<", key="-BACK-", size=(2, 1), button_color=Theme.button_color), psg.Text("", key="-LOGINED_AS-", font=(FONT_NAME, 10, "bold"), background_color=Theme.text_background)],

              [psg.TabGroup([
                    [psg.Tab("Отпуски", [[psg.Column([[psg.CalendarButton("", key="-FIRST_DATE-", format="%d-%m-%Y", target=(psg.ThisRow, 0), close_when_date_chosen=False, button_color=Theme.button_color),
                                                       psg.Text("-", font=(FONT_NAME, 10, "bold"), background_color=Theme.text_background),
                                                       psg.CalendarButton("", key="-SECOND_DATE-", format="%d-%m-%Y", target=(psg.ThisRow, 2), close_when_date_chosen=False, button_color=Theme.button_color)],
                                                      [psg.Push(background_color=Theme.column_color), psg.Button("Добавить", key="-ADD-", button_color=Theme.button_color)]], background_color=Theme.column_color),
                                          psg.Push(background_color=Theme.push_background),
                                          psg.Button("Удалить выделенный отпуск", key="-DELETE_VACATION-", button_color=Theme.button_color)],
                                         [psg.Column([[psg.Listbox([], key="-USER_LIST-", size=(30), expand_y=True, enable_events=True), psg.Listbox([], key="-VACATIONS_LIST-", no_scrollbar=True, size=(50, 18))]],
                                                     background_color=Theme.column_color)],
                                         [psg.Push(background_color=Theme.column_color), psg.Button("Сохранить", key="-SAVE_VACATIONS-", button_color=Theme.button_color)]],
                             background_color=Theme.background_color),

                     psg.Tab("Пользователи", [[psg.Column([[psg.Button("Удалить", key="-DELETE_USER-", button_color=Theme.button_color)]], background_color=Theme.column_color)],
                                              [psg.Table([[]], headings=["Логин", "ФИО", "Должность"], key="-FULL_USER_TABLE-", expand_x=True,  expand_y=True)]],
                             background_color=Theme.background_color)
                     ]
                            ],
                            expand_x=True,
                            expand_y=True,
                            background_color=Theme.background_color,
                            tab_background_color=Theme.unactive_tab_color,
                            selected_background_color=Theme.active_tab_color,
                            title_color=Theme.unactive_tab_text_color,
                            selected_title_color=Theme.active_tab_text_color)
               ]]

    WINDOW_SIZE = (600, 500)

    WINDOW_TIMEOUT = 100

    def __init__(self, user: User) -> None:
        super().__init__()

        self.EVENT_FUNCS = {
            "-BACK-": lambda: self.back(),
            "-ADD-": lambda: self.vacations_add(),
            "-DELETE_VACATION-": lambda: self.vacations_delete(),
            "-SAVE_VACATIONS-": lambda: self.vacations_save(),
            "-USER_LIST-": lambda: self.vacations_change_user(),
            "-DELETE_USER-": lambda: self.users_delete_user(),
        }

        self.user = user

        self.vacations = user.vacations
        self.vacation_id = 100

        self.window["-LOGINED_AS-"].update(f"Вы вошли как {self.user.login}")
        self.window["-FIRST_DATE-"].update(datetime.date.today().strftime("%d/%m/%Y"))
        self.window["-SECOND_DATE-"].update(datetime.date.today().strftime("%d/%m/%Y"))

        self.vacations_update_list()
        self.vacations_update_users_list()
        self.users_update_table()

    def vacations_update_list(self) -> None:
        self.window["-VACATIONS_LIST-"].update([f"{index + 1}. {vacation.start_date.strftime('%d-%m-%Y')} - {vacation.end_date.strftime('%d-%m-%Y')}" for index, vacation in enumerate(self.vacations)])

    def vacations_update_users_list(self) -> None:
        self.window["-USER_LIST-"].update([f"{user.login}" for user in DataBase().get_users()])

    def vacations_change_user(self) -> None:
        self.user = DataBase().get_user(self.values["-USER_LIST-"][0])
        self.vacations = self.user.vacations
        self.vacations_update_list()

    def vacations_add(self) -> None:
        if self.values["-FIRST_DATE-"] == "":
            self.values["-FIRST_DATE-"] = datetime.datetime.now().strftime("%d-%m-%Y")

        if self.values["-SECOND_DATE-"] == "":
            self.values["-SECOND_DATE-"] = datetime.datetime.now().strftime("%d-%m-%Y")
        self.vacations.append(Vacation(_id=self.vacation_id, start_date=datetime.datetime.strptime(self.values["-FIRST_DATE-"], "%d-%m-%Y").date(),
                                       end_date=datetime.datetime.strptime(self.values["-SECOND_DATE-"], "%d-%m-%Y").date()))
        self.vacation_id += 1
        self.vacations_update_list()

    def vacations_save(self) -> None:
        if len(self.vacations) > len(self.user.post.max_vacations_length):
            psg.popup(f"Превышено максимум отпусков ({len(self.user.post.max_vacations_length)})", title="Ошибка")
            return

        for index1, vacation in enumerate(self.vacations):
            for index2, tmp_vacation in enumerate(self.vacations):
                if vacation._id != tmp_vacation._id and (vacation.start_date <= tmp_vacation.end_date and vacation.end_date >= tmp_vacation.start_date):
                    psg.popup(f"Отпуски не могут пересекаться ({index1 + 1} и {index2 + 1})", title="Ошибка")
                    return

            if (vacation.end_date - vacation.start_date).days > self.user.post.max_vacations_length[index1]:
                psg.popup(f"Отпуск превышает масимальную длительность ({index1 + 1} max:{self.user.post.max_vacations_length[index1]})", title="Ошибка")
                return

            if len(DataBase().execute_sql(f"SELECT * FROM vacations WHERE start_date <= '{vacation.end_date}' AND end_date >= '{vacation.start_date}' AND user_id != {self.user._id}")) > 0:
                psg.popup(f"Ваш отпуск пересекается с чужим ({index1 + 1})", title="Ошибка")
                return

            if not Verifier.vacation_is_valid(vacation):
                psg.popup(f"Дата начала отпуска не может быть меньше даты окончания ({index1 + 1})", title="Ошибка")
                return

        DataBase().delete_vacations_for_user(self.user)
        for vacation in self.vacations:
            DataBase().add_vacation(self.user, vacation)
        psg.Popup("Успешно сохранено")
        return

    def vacations_delete(self) -> None:
        for selected_vacation in self.values["-VACATIONS_LIST-"]:
            self.vacations.pop(int(selected_vacation.split(".")[0]) - 1)
        self.vacations_update_list()

    def users_update_table(self) -> None:
        self.window["-FULL_USER_TABLE-"].update([[f"{user.login}",
                                                  f"{user.first_name if user.first_name is not None else ''} {user.second_name if user.second_name is not None else ''} {user.surname if user.second_name is not None else ''}",
                                                  f"{user.post.name.capitalize() if user.post is not None else ''}"]
                                                 for user in DataBase().get_users()])

    def _users_get_selected_user(self) -> User:
        if self.values["-FULL_USER_TABLE-"] == []:
            return None
        return DataBase().get_user(self.window["-FULL_USER_TABLE-"].Values[self.values["-FULL_USER_TABLE-"][0]][0])

    def users_generate_recovery_code(self) -> None:
        pass

    def users_delete_user(self) -> None:
        user = self._users_get_selected_user()
        if user is None:
            return
        if user.role == "admin":
            psg.popup("Невозможно удалить администратора", title="Ошибка")
            return
        DataBase().delete_user(user)
        self.users_update_table()

    def _loop_step(self) -> None:
        super()._loop_step()

        if self.values["-FIRST_DATE-"] != "":
            self.window["-FIRST_DATE-"].update(self.values["-FIRST_DATE-"].replace("-", "/"))
        if self.values["-SECOND_DATE-"] != "":
            self.window["-SECOND_DATE-"].update(self.values["-SECOND_DATE-"].replace("-", "/"))

    def back(self) -> None:
        self.change_window(LoginForm())


if __name__ == "__main__":
    # form = UserForm(DataBase().get_user("root"))
    form = AdminForm(DataBase().get_user("root"))
    # form = StartForm()
    # form = RecoveryForm()

    form.main_loop()
