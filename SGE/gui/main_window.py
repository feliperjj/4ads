import tkinter as tk
from tkinter import ttk, messagebox
from products import CadastroProduto


from movements import MovimentacaoEstoque
from suppliers import GerenciarFornecedores

class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("SGE - Sistema de Gerenciamento de Estoque")
        self.geometry("1200x800")
        self._criar_menu()
        self._criar_widgets()
        self._verificar_alertas()

    def _criar_menu(self):
        menu_bar = tk.Menu(self)
        operacoes_menu = tk.Menu(menu_bar, tearoff=0)
        operacoes_menu.add_command(label="Cadastrar Produto", command=self.abrir_cadastro_produto)
        operacoes_menu.add_command(label="Movimentação", command=self.abrir_movimentacao)
        operacoes_menu.add_command(label="Fornecedores", command=self.abrir_fornecedores)
        menu_bar.add_cascade(label="Operações", menu=operacoes_menu)
        self.config(menu=menu_bar)

    def _criar_widgets(self):
        self.tree_produtos = ttk.Treeview(self, columns=('ID', 'Código', 'Nome', 'Quantidade'), show='headings')
        self.tree_produtos.heading('ID', text='ID')
        self.tree_produtos.heading('Código', text='Código')
        self.tree_produtos.heading('Nome', text='Nome')
        self.tree_produtos.heading('Quantidade', text='Quantidade')
        self.tree_produtos.pack(fill=tk.BOTH, expand=True)
        self._atualizar_lista()

    def _atualizar_lista(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        produtos = self.db.executar("SELECT id, codigo, nome, quantidade FROM produtos").fetchall()
        for produto in produtos:
            self.tree_produtos.insert('', tk.END, values=produto)

    def _verificar_alertas(self):
        produtos = self.db.executar('''SELECT nome, quantidade, quantidade_minima 
                                     FROM produtos WHERE quantidade <= quantidade_minima''').fetchall()
        if produtos:
            messagebox.showwarning("Alerta", "Produtos precisando de reposição!")

    def abrir_cadastro_produto(self):
        CadastroProduto(self, self.db)

    def abrir_movimentacao(self):
        MovimentacaoEstoque(self, self.db)

    def abrir_fornecedores(self):
        GerenciarFornecedores(self, self.db)