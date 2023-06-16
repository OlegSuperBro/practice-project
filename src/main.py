import interface
import database

if __name__ == "__main__":
    DB = database.DataBase()
    GUI = interface.App(DB)
