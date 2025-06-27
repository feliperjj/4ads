import tkinter as tk
from tkinter import ttk, messagebox
import hashlib # Para hash de senhas

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("SGE - Login")
        self.geometry("350x200")
        self.resizable(False, False)
        self.grab_set() # Torna a janela modal
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Captura o fechamento da janela

        self.usuario_logado = None # Armazenará o ID e nível do usuário logado

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        self._criar_interface()

    def _criar_interface(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Usuário:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.username_entry.focus_set() # Foco inicial

        ttk.Label(main_frame, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(main_frame, show="*") # Esconde a senha
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.password_entry.bind('<Return>', lambda event: self._tentar_login()) # Login ao apertar Enter

        login_button = ttk.Button(main_frame, text="Login", command=self._tentar_login)
        login_button.grid(row=2, columnspan=2, pady=15)

        main_frame.grid_columnconfigure(1, weight=1)

    def _tentar_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Erro de Login", "Por favor, insira usuário e senha.")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            user = self.db.executar("SELECT id, nivel_acesso FROM usuarios WHERE username = ? AND password_hash = ?", (username, password_hash)).fetchone()
            if user:
                self.usuario_logado = {'id': user[0], 'nivel_acesso': user[1], 'username': username}
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                self.destroy() # Fecha a janela de login
            else:
                messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao tentar login: {str(e)}")

    def _on_closing(self):
        # Garante que o aplicativo feche se a janela de login for fechada sem sucesso
        self.parent.destroy()
        self.destroy()