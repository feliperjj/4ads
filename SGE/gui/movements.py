import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MovimentacaoEstoque(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Movimentação de Estoque")
        self.geometry("350x150")
        self.transient(parent)
        self.grab_set()
        self._criar_interface()

    def _criar_interface(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Código do Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.codigo_entry = ttk.Entry(frame)
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantidade_entry = ttk.Entry(frame)
        self.quantidade_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Registrar Entrada", command=lambda: self._processar('entrada')).pack(side="left",
                                                                                                         padx=5)
        ttk.Button(btn_frame, text="Registrar Saída", command=lambda: self._processar('saida')).pack(side="left",
                                                                                                     padx=5)

        self.codigo_entry.focus_set()

    def _processar(self, tipo):
        codigo = self.codigo_entry.get()

        try:
            quantidade = int(self.quantidade_entry.get())
            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser um número positivo.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número válido.", parent=self)
            return

        try:
            produto_info = self.db.executar("SELECT id, quantidade FROM produtos WHERE codigo = ?",
                                            (codigo,)).fetchone()

            if not produto_info:
                messagebox.showerror("Erro", f"Produto com código '{codigo}' não encontrado.", parent=self)
                return

            produto_id, estoque_atual = produto_info

            if tipo == 'saida' and estoque_atual < quantidade:
                messagebox.showerror("Erro", f"Estoque insuficiente. Disponível: {estoque_atual}", parent=self)
                return

            nova_quantidade = estoque_atual + (quantidade if tipo == 'entrada' else -quantidade)

            self.db.executar("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))

            self.db.executar('''
                             INSERT INTO movimentacoes (produto_id, tipo, quantidade, data)
                             VALUES (?, ?, ?, ?)
                             ''', (produto_id, tipo, quantidade, datetime.now()))

            messagebox.showinfo("Sucesso", f"Movimentação ({tipo}) registrada com sucesso!", parent=self)
            self.parent._atualizar_lista()
            self.parent._verificar_alertas()  # Re-verifica os alertas após a movimentação
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro Inesperado", str(e), parent=self)
