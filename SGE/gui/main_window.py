import tkinter as tk
from tkinter import ttk, messagebox
from SGE.gui.products import CadastroProduto
from SGE.gui.movements import MovimentacaoEstoque, HistoricoMovimentacoes
from SGE.gui.suppliers import GerenciarFornecedores


class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("SGE - Sistema de Gerenciamento de Estoque")
        self.geometry("1200x800")

        # 1. Escolher um tema ttk
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # Experimente 'clam', 'alt', 'default', 'classic'

        # 2. Configurar algumas cores e fontes globais (opcional, pode ser mais granular)
        self.configure(bg="#ECECEC")  # Cor de fundo da janela principal
        self.style.configure('TFrame', background='#ECECEC')
        self.style.configure('TLabel', background='#ECECEC', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        self.style.configure('Treeview', font=('Helvetica', 10))

        self._criar_menu()
        self._criar_widgets()
        self._verificar_alertas()

    def _criar_menu(self):
        menu_bar = tk.Menu(self)
        operacoes_menu = tk.Menu(menu_bar, tearoff=0)
        operacoes_menu.add_command(label="Cadastrar Produto", command=self.abrir_cadastro_produto)
        operacoes_menu.add_command(label="Movimentação de Estoque", command=self.abrir_movimentacao)
        operacoes_menu.add_command(label="Histórico de Movimentações", command=self.abrir_historico_movimentacoes)
        operacoes_menu.add_command(label="Gerenciar Fornecedores", command=self.abrir_fornecedores)
        menu_bar.add_cascade(label="Operações", menu=operacoes_menu)
        self.config(menu=menu_bar)

    def _criar_widgets(self):
        # Frame para a lista de produtos e botões de ação
        frame_produtos = ttk.Frame(self, padding="10 10 10 10")  # Adicionado padding
        frame_produtos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label de título para a lista de produtos
        ttk.Label(frame_produtos, text="Estoque de Produtos", font=('Helvetica', 14, 'bold')).pack(pady=10)

        self.tree_produtos = ttk.Treeview(frame_produtos,
                                          columns=('ID', 'Código', 'Nome', 'Quantidade', 'Preço Custo', 'Preço Venda',
                                                   'Quantidade Mínima'), show='headings')
        self.tree_produtos.heading('ID', text='ID')
        self.tree_produtos.heading('Código', text='Código')
        self.tree_produtos.heading('Nome', text='Nome')
        self.tree_produtos.heading('Quantidade', text='Quantidade')
        self.tree_produtos.heading('Preço Custo', text='Preço Custo')
        self.tree_produtos.heading('Preço Venda', text='Preço Venda')
        self.tree_produtos.heading('Quantidade Mínima', text='Qtd Mínima')

        self.tree_produtos.column('ID', width=50, anchor=tk.CENTER)
        self.tree_produtos.column('Código', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Nome', width=200)
        self.tree_produtos.column('Quantidade', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Preço Custo', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Preço Venda', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Quantidade Mínima', width=100, anchor=tk.CENTER)

        self.tree_produtos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para a treeview
        scrollbar = ttk.Scrollbar(frame_produtos, orient=tk.VERTICAL, command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões de ação para produtos
        frame_botoes_produtos = ttk.Frame(self, padding="10 0 10 10")  # Adicionado padding
        frame_botoes_produtos.pack(pady=5)

        ttk.Button(frame_botoes_produtos, text="Adicionar Produto", command=self.abrir_cadastro_produto).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_produtos, text="Editar Produto", command=self.editar_produto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_produtos, text="Excluir Produto", command=self.excluir_produto).pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Button(frame_botoes_produtos, text="Atualizar Lista", command=self._atualizar_lista).pack(side=tk.LEFT,
                                                                                                      padx=5)

        self._atualizar_lista()

    def _atualizar_lista(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        produtos = self.db.executar(
            "SELECT id, codigo, nome, quantidade, preco_custo, preco_venda, quantidade_minima FROM produtos").fetchall()
        for produto in produtos:
            self.tree_produtos.insert('', tk.END, values=produto)

    def _verificar_alertas(self):
        produtos = self.db.executar('''SELECT nome, quantidade, quantidade_minima 
                                     FROM produtos WHERE quantidade <= quantidade_minima''').fetchall()
        if produtos:
            nomes_produtos = ", ".join([p[0] for p in produtos])
            messagebox.showwarning("Alerta de Estoque Baixo",
                                   f"Os seguintes produtos precisam de reposição: {nomes_produtos}")

    def abrir_cadastro_produto(self):
        CadastroProduto(self, self.db, self._atualizar_lista)

    def editar_produto(self):
        selected_item = self.tree_produtos.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        produto_id = self.tree_produtos.item(selected_item)['values'][0]
        produto_data = self.db.executar("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

        if produto_data:
            CadastroProduto(self, self.db, self._atualizar_lista, produto_data)

    def excluir_produto(self):
        selected_item = self.tree_produtos.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return

        produto_id = self.tree_produtos.item(selected_item)['values'][0]
        nome_produto = self.tree_produtos.item(selected_item)['values'][2]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto '{nome_produto}'?"):
            try:
                self.db.executar("DELETE FROM produtos WHERE id = ?", (produto_id,))
                self._atualizar_lista()
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir produto: {str(e)}")

    def abrir_movimentacao(self):
        MovimentacaoEstoque(self, self.db, self._atualizar_lista)

    def abrir_historico_movimentacoes(self):
        HistoricoMovimentacoes(self, self.db)

    def abrir_fornecedores(self):
        GerenciarFornecedores(self, self.db)
