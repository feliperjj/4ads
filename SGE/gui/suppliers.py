
import tkinter as tk
from tkinter import ttk, messagebox


class GerenciarFornecedores(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Gerenciar Fornecedores")
        self._criar_interface()

    def _criar_interface(self):
        ttk.Label(self, text="Nome:").grid(row=0, column=0)
        self.nome_entry = ttk.Entry(self)
        self.nome_entry.grid(row=0, column=1)

        ttk.Label(self, text="Contato:").grid(row=1, column=0)
        self.contato_entry = ttk.Entry(self)
        self.contato_entry.grid(row=1, column=1)

        ttk.Button(self, text="Salvar", command=self._salvar).grid(row=2, columnspan=2, pady=10)

    def _salvar(self):
        try:
            self.db.executar('''INSERT INTO fornecedores
                                    (nome, contato)
                                VALUES (?, ?)''',
                             (self.nome_entry.get(),
                              self.contato_entry.get()))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))