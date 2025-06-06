import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class MovimentacaoEstoque(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Movimentação de Estoque")
        self._criar_interface()

    def _criar_interface(self):
        ttk.Label(self, text="Código do Produto:").grid(row=0, column=0)
        self.codigo_entry = ttk.Entry(self)
        self.codigo_entry.grid(row=0, column=1)
        
        ttk.Label(self, text="Quantidade:").grid(row=1, column=0)
        self.quantidade_entry = ttk.Entry(self)
        self.quantidade_entry.grid(row=1, column=1)
        
        ttk.Button(self, text="Entrada", command=lambda: self._processar('entrada')).grid(row=2, column=0)
        ttk.Button(self, text="Saída", command=lambda: self._processar('saida')).grid(row=2, column=1)

    def _processar(self, tipo):
        codigo = self.codigo_entry.get()
        quantidade = self.quantidade_entry.get()
        
        try:
            produto = self.db.executar("SELECT id, quantidade FROM produtos WHERE codigo = ?", (codigo,)).fetchone()
            nova_quantidade = int(produto[1]) + (int(quantidade) if tipo == 'entrada' else -int(quantidade))
            
            self.db.executar("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto[0]))
            self.db.executar('''INSERT INTO movimentacoes 
                              (produto_id, tipo, quantidade, data)
                              VALUES (?, ?, ?, ?)''',
                              (produto[0], tipo, quantidade, datetime.now()))
            self.parent._atualizar_lista()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))