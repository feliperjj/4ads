import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MovimentacaoEstoque(tk.Toplevel):
    def __init__(self, parent, db, atualizar_lista_callback):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.atualizar_lista_callback = atualizar_lista_callback
        self.title("Movimentação de Estoque")
        self.geometry("400x200")
        self._criar_interface()

    def _criar_interface(self):
        ttk.Label(self, text="Código do Produto:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.codigo_entry = ttk.Entry(self)
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.quantidade_entry = ttk.Entry(self)
        self.quantidade_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(self, text="Entrada", command=lambda: self._processar('entrada')).grid(row=2, column=0, pady=10)
        ttk.Button(self, text="Saída", command=lambda: self._processar('saida')).grid(row=2, column=1, pady=10)

        self.grid_columnconfigure(1, weight=1)

    def _processar(self, tipo):
        codigo = self.codigo_entry.get()
        quantidade_str = self.quantidade_entry.get()

        if not codigo or not quantidade_str:
            messagebox.showwarning("Aviso", "Por favor, preencha o código do produto e a quantidade.")
            return

        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                messagebox.showwarning("Aviso", "A quantidade deve ser um número positivo.")
                return

            produto = self.db.executar("SELECT id, quantidade, nome FROM produtos WHERE codigo = ?",
                                       (codigo,)).fetchone()

            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado com o código fornecido.")
                return

            produto_id, quantidade_atual, nome_produto = produto

            if tipo == 'entrada':
                nova_quantidade = quantidade_atual + quantidade
            else:  # Saída
                if quantidade > quantidade_atual:
                    messagebox.showwarning("Aviso",
                                           f"Não há quantidade suficiente em estoque para '{nome_produto}'. Disponível: {quantidade_atual}")
                    return
                nova_quantidade = quantidade_atual - quantidade

            self.db.executar("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))
            self.db.executar('''INSERT INTO movimentacoes 
                              (produto_id, tipo, quantidade, data)
                              VALUES (?, ?, ?, ?)''',
                             (produto_id, tipo, quantidade, datetime.now()))

            messagebox.showinfo("Sucesso",
                                f"Movimentação de '{tipo}' realizada com sucesso para '{nome_produto}'. Nova quantidade: {nova_quantidade}")
            self.atualizar_lista_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Entrada", "A quantidade deve ser um número inteiro.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))


class HistoricoMovimentacoes(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Histórico de Movimentações")
        self.geometry("800x600")
        self._criar_interface()
        self._atualizar_historico()

    def _criar_interface(self):
        self.tree_historico = ttk.Treeview(self, columns=('ID Movimentação', 'Produto', 'Tipo', 'Quantidade', 'Data'),
                                           show='headings')
        self.tree_historico.heading('ID Movimentação', text='ID Mov.')
        self.tree_historico.heading('Produto', text='Produto')
        self.tree_historico.heading('Tipo', text='Tipo')
        self.tree_historico.heading('Quantidade', text='Quantidade')
        self.tree_historico.heading('Data', text='Data/Hora')

        self.tree_historico.column('ID Movimentação', width=70)
        self.tree_historico.column('Produto', width=200)
        self.tree_historico.column('Tipo', width=80)
        self.tree_historico.column('Quantidade', width=100)
        self.tree_historico.column('Data', width=150)

        self.tree_historico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_historico, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        # Juntar com a tabela de produtos para mostrar o nome do produto
        movimentacoes = self.db.executar('''SELECT m.id, p.nome, m.tipo, m.quantidade, m.data 
                                           FROM movimentacoes m
                                           JOIN produtos p ON m.produto_id = p.id
                                           ORDER BY m.data DESC''').fetchall()
        for mov in movimentacoes:
            self.tree_historico.insert('', tk.END, values=mov)
