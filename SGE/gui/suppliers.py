import tkinter as tk
from tkinter import ttk, messagebox


class GerenciarFornecedores(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Gerenciar Fornecedores")
        self.geometry("350x150")
        self.transient(parent)
        self.grab_set()
        self._criar_interface()

    def _criar_interface(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome_entry = ttk.Entry(frame)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Contato (Tel/Email):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.contato_entry = ttk.Entry(frame)
        self.contato_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

        btn_salvar = ttk.Button(self, text="Salvar Fornecedor", command=self._salvar)
        btn_salvar.pack(pady=10)

        self.nome_entry.focus_set()

    def _salvar(self):
        nome = self.nome_entry.get()
        contato = self.contato_entry.get()

        if not nome:
            messagebox.showerror("Erro de Validação", "O nome do fornecedor é obrigatório.", parent=self)
            return

        try:
            self.db.executar('''
                             INSERT INTO fornecedores (nome, contato)
                             VALUES (?, ?)
                             ''', (nome, contato))

            messagebox.showinfo("Sucesso", "Fornecedor salvo com sucesso!", parent=self)

            self.nome_entry.delete(0, tk.END)
            self.contato_entry.delete(0, tk.END)
            self.nome_entry.focus_set()

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e), parent=self)
