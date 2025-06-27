from database import Database
from SGE.gui.main_window import MainWindow
from SGE.gui.login import LoginWindow  # Importa a janela de login
import tkinter as tk

if __name__ == "__main__":
    db = Database()

    # Inicia a janela de login
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal temporariamente
    login_window = LoginWindow(root, db)
    root.wait_window(login_window)  # Espera a janela de login ser fechada

    if login_window.usuario_logado:
        # Se o login foi bem-sucedido, inicializa a MainWindow
        app = MainWindow(db, login_window.usuario_logado)
        root.destroy()  # Destrói a janela root que escondeu
        app.mainloop()
    else:
        # Se o login falhou ou foi cancelado, fecha o aplicativo
        root.destroy()
        print("Login cancelado ou falhou. Encerrando o sistema.")