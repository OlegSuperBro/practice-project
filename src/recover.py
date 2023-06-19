import smtplib
import ssl
import random
from email.message import EmailMessage

from config import CONFIG
from database import DataBase
from datatypes import User

context = ssl.create_default_context()


def send_recovery_email(text: str):
    try:
        tmp_mail = EmailMessage()
        tmp_mail["Subject"] = "Запрос на востановление пароля в базе данных отпусков"
        tmp_mail["From"] = CONFIG.send_mail
        tmp_mail["To"] = CONFIG.recovery_mail

        tmp_mail.set_content(text)

        server = smtplib.SMTP(CONFIG.smtp_server, CONFIG.smtp_port)
        server.starttls(context=context)
        server.login(CONFIG.send_mail, CONFIG.send_mail_password)
        server.send_message(tmp_mail)
    except Exception as e:
        print(e)
    finally:
        server.close()


def create_recovery_text(username: str, additional_info: str = ""):
    user = DataBase().get_user(username)
    return f"Пользователь {user.login} ({user.post.name.capitalize() if user.post != None else ''} {user.first_name if user.first_name != None else ''} {user.second_name if user.second_name != None else ''} {user.surname if user.surname != None else ''}) запросил востановление пароля.\n" +\
           f"Код востановления для этого пользователя {DataBase().get_recovery_for_user(user)}\n" +\
           f"Дополнительная информация:\n{additional_info}"


def create_recovery_code(user: User) -> int:
    code = random.randint(100000, 999999)
    DataBase().set_recovery_for_user(user, code)
    return code


if __name__ == "__main__":
    # print(create_recovery_code(DataBase().get_user("root")))
    print(create_recovery_text("root").encode("cp1251", "ignore").decode("cp1251"))
    send_recovery_email(create_recovery_text("root"), "olegrakovic323@gmail.com")
