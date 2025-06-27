import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self, app_root, db):
        self.app_root = app_root
        self.db = db
        self.style = ttk.Style(self.app_root)
        self._carregar_tema_preferido()

    def _carregar_tema_preferido(self):
        # Em um sistema real, você carregaria a preferência de tema do banco de dados
        # ou de um arquivo de configuração por usuário.
        # Por enquanto, vamos manter um tema padrão ou carregar de um mock.
        # self.style.theme_use('clam') # Tema padrão
        pass

    def apply_theme(self, theme_name):
        try:
            self.style.theme_use(theme_name)
            # Você pode querer persistir essa escolha no banco de dados para o usuário logado
            # self.db.executar("UPDATE usuarios SET tema_preferido = ? WHERE id = ?", (theme_name, self.usuario_logado['id']))
        except tk.TclError:
            messagebox.showerror("Erro de Tema", f"Tema '{theme_name}' não disponível.")

    def get_available_themes(self):
        return self.style.theme_names()

    def open_theme_selector(self):
        theme_selector_window = tk.Toplevel(self.app_root)
        theme_selector_window.title("Selecionar Tema")
        theme_selector_window.geometry("300x200")
        theme_selector_window.grab_set()

        ttk.Label(theme_selector_window, text="Escolha um Tema:").pack(pady=10)

        theme_var = tk.StringVar(theme_selector_window)
        current_theme = self.style.theme_use()
        if current_theme in self.get_available_themes():
            theme_var.set(current_theme)
        else:
            theme_var.set(self.get_available_themes()[0]) # Seleciona o primeiro como padrão

        theme_dropdown = ttk.Combobox(theme_selector_window, textvariable=theme_var, values=self.get_available_themes(), state='readonly')
        theme_dropdown.pack(pady=5)

        def apply_selected_theme():
            selected_theme = theme_var.get()
            self.apply_theme(selected_theme)
            messagebox.showinfo("Tema Aplicado", f"Tema '{selected_theme}' aplicado com sucesso.")
            theme_selector_window.destroy()

        ttk.Button(theme_selector_window, text="Aplicar Tema", command=apply_selected_theme).pack(pady=10)