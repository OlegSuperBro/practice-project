import PySimpleGUI as psg

from database import DataBase


class App:
    def __init__(self, db_connection: DataBase) -> None:
        self.db_connection = db_connection
