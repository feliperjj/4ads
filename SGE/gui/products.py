import tkinter as tk
from tkinter import ttk, messagebox


class CadastroProduto(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Cadastro de Produto")
        self._criar_formulario()

    def _criar_formulario(self):
        campos = [
            ('Código:', 'codigo'),
            ('Nome:', 'nome'),
            ('Preço Custo:', 'preco_custo'),
            ('Quantidade Mínima:', 'quantidade_minima'),
            ('Quantidade Inicial:', 'quantidade')
        ]
        
        self.entries = {}
        for idx, (label, field) in enumerate(campos):
            ttk.Label(self, text=label).grid(row=idx, column=0, padx=5, pady=5)
            entry = ttk.Entry(self)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries[field] = entry
        
        ttk.Button(self, text="Salvar", command=self._salvar).grid(row=len(campos), columnspan=2, pady=10)

    def _salvar(self):
        try:
            self.db.executar('''INSERT INTO produtos 
                              (codigo, nome, preco_custo, quantidade_minima, quantidade)
                              VALUES (?, ?, ?, ?, ?)''',
                              (self.entries['codigo'].get(),
                               self.entries['nome'].get(),
                               float(self.entries['preco_custo'].get()),
                               int(self.entries['quantidade_minima'].get()),
                               int(self.entries['quantidade'].get())))
            self.parent._atualizar_lista()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
