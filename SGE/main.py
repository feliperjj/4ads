from gui.main_window import MainWindow
from database import Database

if __name__ == "__main__":
    db = Database()
    app = MainWindow(db)
    app.mainloop()
