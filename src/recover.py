import smtplib
import ssl
import random

from config import CONFIG
from database import DataBase
from datatypes import User

context = ssl.create_default_context()


def send_email(text: str, to: str):
    try:
        server = smtplib.SMTP(CONFIG.smpt_server, CONFIG.smpt_port)
        server.starttls(context=context)
        server.login(CONFIG.send_mail, CONFIG.send_mail_password)
        server.sendmail(CONFIG.send_mail, to, text)
    except Exception as e:
        print(e)
    finally:
        server.close()


def create_recovery_code(user: User) -> int:
    code = random.randint(100000, 999999)
    DataBase().set_recovery_for_user(user, code)
    return code
