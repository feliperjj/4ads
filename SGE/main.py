from database import Database
from SGE.gui.main_window import MainWindow


if __name__ == "__main__":
    db = Database()
    app = MainWindow(db)
    app.mainloop()
