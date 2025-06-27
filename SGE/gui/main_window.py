import tkinter as tk
from tkinter import ttk, messagebox
import csv
from tkinter import filedialog
from datetime import datetime

from SGE.gui.products import CadastroProduto
from SGE.gui.movements import MovimentacaoEstoque, HistoricoMovimentacoes
from SGE.gui.suppliers import GerenciarFornecedores
from SGE.gui.reports import RelatoriosVendas
from SGE.gui.users import GerenciarUsuarios  # Novo import
from SGE.gui.auditoria import HistoricoAuditoria  # Novo import
from SGE.gui.theme_manager import ThemeManager   # Novo import
from SGE.gui.categories import GerenciarCategorias


class MainWindow(tk.Tk):
    def __init__(self, db, usuario_logado):
        super().__init__()
        self.db = db
        self.usuario_logado = usuario_logado  # Armazena o usuário logado
        self.title(f"SGE - Sistema de Gerenciamento de Estoque (Usuário: {usuario_logado['username']})")
        self.geometry("1200x800")

        self.theme_manager = ThemeManager(self, self.db)  # Inicializa o gerenciador de temas
        self.theme_manager.apply_theme('clam')  # Define um tema inicial

        self.configure(bg="#ECECEC")
        self.style = ttk.Style(self)  # Obtém a instância de Style da janela principal
        self.style.configure('TFrame', background='#ECECEC')
        self.style.configure('TLabel', background='#ECECEC', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        self.style.configure('Treeview', font=('Helvetica', 10))

        self._criar_menu()
        self._criar_widgets()
        self._verificar_alertas()

        # Notificações sonoras e visuais
        self.after(60000, self._checar_alertas_periodicamente)  # Verifica alertas a cada 1 minuto

    def _criar_menu(self):
        menu_bar = tk.Menu(self)

        operacoes_menu = tk.Menu(menu_bar, tearoff=0)
        operacoes_menu.add_command(label="Cadastrar Produto", command=self.abrir_cadastro_produto)
        operacoes_menu.add_command(label="Movimentação de Estoque", command=self.abrir_movimentacao)
        operacoes_menu.add_command(label="Histórico de Movimentações", command=self.abrir_historico_movimentacoes)
        # NOVO: Item de menu para gerenciar categorias
        operacoes_menu.add_separator()
        operacoes_menu.add_command(label="Gerenciar Categorias", command=self.abrir_gerenciar_categorias)
        menu_bar.add_cascade(label="Operações", menu=operacoes_menu)

        fornecedores_menu = tk.Menu(menu_bar, tearoff=0)
        fornecedores_menu.add_command(label="Gerenciar Fornecedores", command=self.abrir_gerenciar_fornecedores)
        menu_bar.add_cascade(label="Fornecedores", menu=fornecedores_menu)

        relatorios_menu = tk.Menu(menu_bar, tearoff=0)
        relatorios_menu.add_command(label="Relatórios de Vendas", command=self.abrir_relatorios_vendas)
        menu_bar.add_cascade(label="Relatórios", menu=relatorios_menu)

        # Novo menu de Sistema
        sistema_menu = tk.Menu(menu_bar, tearoff=0)
        if self.usuario_logado and self.usuario_logado['nivel_acesso'] == 'administrador':
            sistema_menu.add_command(label="Gerenciar Usuários", command=self.abrir_gerenciar_usuarios)
            sistema_menu.add_command(label="Histórico de Auditoria", command=self.abrir_historico_auditoria)
        sistema_menu.add_command(label="Mudar Tema", command=self.theme_manager.open_theme_selector)
        sistema_menu.add_separator()
        sistema_menu.add_command(label="Sair", command=self.on_closing)
        menu_bar.add_cascade(label="Sistema", menu=sistema_menu)

        # Novo menu de Exportar
        exportar_menu = tk.Menu(menu_bar, tearoff=0)
        exportar_menu.add_command(label="Exportar Produtos para CSV", command=self.exportar_produtos_csv)
        exportar_menu.add_command(label="Exportar Movimentações para CSV", command=self.exportar_movimentacoes_csv)
        menu_bar.add_cascade(label="Exportar", menu=exportar_menu)

        self.config(menu=menu_bar)

    def _criar_widgets(self):
        frame_produtos = ttk.Frame(self, padding="10 10 10 10")
        frame_produtos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_produtos, text="Estoque de Produtos", font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Barra de Pesquisa Global para Produtos
        frame_busca_produtos = ttk.Frame(frame_produtos)
        frame_busca_produtos.pack(fill=tk.X, pady=5)

        ttk.Label(frame_busca_produtos, text="Pesquisar Produto:").pack(side=tk.LEFT, padx=5)
        self.busca_produto_entry = ttk.Entry(frame_busca_produtos)
        self.busca_produto_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.busca_produto_entry.bind('<KeyRelease>', self._filtrar_produtos)  # Filtra ao digitar

        ttk.Label(frame_busca_produtos, text="Categoria:").pack(side=tk.LEFT, padx=(10, 5))
        self.categoria_filtro_combobox = ttk.Combobox(frame_busca_produtos, state='readonly', width=30)
        self.categoria_filtro_combobox.pack(side=tk.LEFT, padx=5)
        self.categoria_filtro_combobox.bind('<<ComboboxSelected>>', self._filtrar_produtos)
        self._carregar_categorias_filtro() # Carrega as categorias no filtro

        self.tree_produtos = ttk.Treeview(frame_produtos,
                                          columns=('ID', 'Código', 'Nome', 'Categoria', 'Quantidade', 'Preço Custo', 'Preço Venda', 'Quantidade Mínima'),
                                          show='headings')

        # Cabeçalhos e ordenação
        for col in ['ID', 'Código', 'Nome', 'Categoria', 'Quantidade', 'Preço Custo', 'Preço Venda', 'Quantidade Mínima']:
            self.tree_produtos.heading(col, text=col,
                                       command=lambda c=col: self._sort_treeview(self.tree_produtos, c, False))

        # MODIFICADO: Ajuste das colunas
        self.tree_produtos.column('ID', width=50, anchor=tk.CENTER)
        self.tree_produtos.column('Código', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Nome', width=250)
        self.tree_produtos.column('Categoria', width=150) # Nova coluna
        self.tree_produtos.column('Quantidade', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Preço Custo', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Preço Venda', width=100, anchor=tk.CENTER)
        self.tree_produtos.column('Quantidade Mínima', width=120, anchor=tk.CENTER)

        self.tree_produtos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_produtos, orient=tk.VERTICAL, command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_botoes_produtos = ttk.Frame(self, padding="10 0 10 10")
        frame_botoes_produtos.pack(pady=5)

        ttk.Button(frame_botoes_produtos, text="Adicionar Produto", command=self.abrir_cadastro_produto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_produtos, text="Editar Produto", command=self.editar_produto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_produtos, text="Excluir Produto", command=self.excluir_produto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_produtos, text="Atualizar Lista", command=self._atualizar_lista).pack(side=tk.LEFT, padx=5)

        self._atualizar_lista()

    # --- Funções de Ordenação---
    def _carregar_categorias_filtro(self):
        categorias = self.db.executar("SELECT nome FROM categorias ORDER BY nome").fetchall()
        valores_filtro = ["Todas as Categorias"] + [cat[0] for cat in categorias]
        self.categoria_filtro_combobox['values'] = valores_filtro
        self.categoria_filtro_combobox.set("Todas as Categorias")

        if len(valores_filtro) <= 1:
            self.categoria_filtro_combobox.config(state='disabled')
        else:
            self.categoria_filtro_combobox.config(state='readonly')

    def _sort_treeview(self, tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if isinstance(float(t[0]), (int, float)) else t[0], reverse=reverse)
        except (ValueError, TypeError):
            data.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, item) in enumerate(data):
            tree.move(item, '', index)  # Move os itens para a nova posição

        # Troca a direção da ordenação para o próximo clique
        tree.heading(col, command=lambda: self._sort_treeview(tree, col, not reverse))

    # --- Funções de Filtro---
    def _filtrar_produtos(self, event=None):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        termo_busca = self.busca_produto_entry.get().lower()
        categoria_selecionada = self.categoria_filtro_combobox.get()

        query = '''SELECT p.id, p.codigo, p.nome, IFNULL(c.nome, 'Sem Categoria'), 
                   p.quantidade, p.preco_custo, p.preco_venda, p.quantidade_minima
                   FROM produtos p
                   LEFT JOIN categorias c ON p.categoria_id = c.id
                   WHERE (LOWER(p.nome) LIKE ? OR LOWER(p.codigo) LIKE ?)'''

        params = [f'%{termo_busca}%', f'%{termo_busca}%']

        if categoria_selecionada and categoria_selecionada != "Todas as Categorias":
            query += " AND c.nome = ?"
            params.append(categoria_selecionada)

        produtos = self.db.executar(query, tuple(params)).fetchall()
        for produto in produtos:
            self.tree_produtos.insert('', tk.END, values=produto)

    def _atualizar_lista(self):
        self.busca_produto_entry.delete(0, tk.END)
        self._carregar_categorias_filtro()
        self._filtrar_produtos()  # Chama o filtro sem termo de busca para listar todos

    def _verificar_alertas(self):
        produtos = self.db.executar('''SELECT nome, quantidade, quantidade_minima 
                                     FROM produtos WHERE quantidade <= quantidade_minima''').fetchall()
        if produtos:
            nomes_produtos = ", ".join([p[0] for p in produtos])
            messagebox.showwarning("Alerta de Estoque Baixo",
                                   f"Os seguintes produtos precisam de reposição: {nomes_produtos}")
            # Notificação Sonora (Exemplo simples, requer uma biblioteca como playsound)
            # from playsound import playsound
            # playsound('caminho/para/seu/som_alerta.mp3') # Você precisaria de um arquivo de som

            # Notificação Visual (Exemplo: mudar a cor da janela ou de um ícone)
            self.flash_window()  # Flash na barra de tarefas

    def _checar_alertas_periodicamente(self):
        self._verificar_alertas()
        self.after(60000, self._checar_alertas_periodicamente)  # Chama novamente após 1 minuto

    def flash_window(self):
        # Isso fará com que a janela pisque na barra de tarefas (depende do SO)
        try:
            self.attributes('-topmost', 1)
            self.attributes('-topmost', 0)
        except tk.TclError:
            pass  # Nem todos os sistemas operacionais suportam isso

    # --- Abertura de Janelas ---
    def abrir_cadastro_produto(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Cadastro de Produto')
        CadastroProduto(self, self.db, self._atualizar_lista, self.usuario_logado)

    def editar_produto(self):
        selected_item = self.tree_produtos.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        produto_id = self.tree_produtos.item(selected_item)['values'][0]
        produto_data = self.db.executar("SELECT id, codigo, nome, categoria_id, preco_custo, preco_venda, quantidade, quantidade_minima FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        if produto_data:
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Edição de Produto', f"Produto ID: {produto_id}")
            CadastroProduto(self, self.db, self._atualizar_lista, self.usuario_logado, produto_data)

    def excluir_produto(self):
        selected_item = self.tree_produtos.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
        produto_id = self.tree_produtos.item(selected_item)['values'][0]
        nome_produto = self.tree_produtos.item(selected_item)['values'][2]
        if self.usuario_logado['nivel_acesso'] != 'administrador':
            messagebox.showerror("Permissão Negada", "Você não tem permissão para excluir produtos.")
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto '{nome_produto}'?"):
            try:
                self.db.executar("DELETE FROM produtos WHERE id = ?", (produto_id,))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Excluiu Produto', f"Produto '{nome_produto}' (ID: {produto_id})")
                self._atualizar_lista()
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir produto: {str(e)}")

    def abrir_movimentacao(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Movimentação de Estoque')
        MovimentacaoEstoque(self, self.db, self._atualizar_lista, self.usuario_logado)

    def abrir_historico_movimentacoes(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Histórico de Movimentações')
        HistoricoMovimentacoes(self, self.db)

    def abrir_gerenciar_fornecedores(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Gerenciar Fornecedores')
        GerenciarFornecedores(self, self.db)

    def abrir_relatorios_vendas(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Relatórios de Vendas')
        RelatoriosVendas(self, self.db)

    def abrir_gerenciar_categorias(self):
        self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Gerenciar Categorias')
        GerenciarCategorias(self, self.db, self._atualizar_lista)

    def abrir_gerenciar_usuarios(self):
        if self.usuario_logado['nivel_acesso'] == 'administrador':
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Gerenciar Usuários')
            GerenciarUsuarios(self, self.db, self.usuario_logado)
        else:
            messagebox.showerror("Permissão Negada", "Você não tem permissão para gerenciar usuários.")
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Tentativa de Acesso Negado', 'Tentou acessar Gerenciar Usuários')

    def abrir_historico_auditoria(self):
        if self.usuario_logado['nivel_acesso'] == 'administrador':
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Abriu Histórico de Auditoria')
            HistoricoAuditoria(self, self.db)
        else:
            messagebox.showerror("Permissão Negada", "Você não tem permissão para visualizar o histórico de auditoria.")
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Tentativa de Acesso Negado', 'Tentou acessar Histórico de Auditoria')

    def exportar_produtos_csv(self):
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                    title="Salvar Produtos como CSV")
        if not file_path:
            return
        try:
            query = '''SELECT p.id, p.codigo, p.nome, IFNULL(c.nome, ''), 
                       p.preco_custo, p.preco_venda, p.quantidade, p.quantidade_minima
                       FROM produtos p
                       LEFT JOIN categorias c ON p.categoria_id = c.id'''
            produtos = self.db.executar(query).fetchall()
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Código', 'Nome', 'Categoria', 'Preço Custo', 'Preço Venda', 'Quantidade',
                                 'Quantidade Mínima'])
                writer.writerows(produtos)
            messagebox.showinfo("Exportação", "Produtos exportados com sucesso para CSV!")
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Exportou Dados', 'Exportou lista de produtos para CSV')
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Erro ao exportar produtos: {str(e)}")

    def exportar_movimentacoes_csv(self):
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                    title="Salvar Movimentações como CSV")
        if not file_path:
            return
        try:
            movimentacoes = self.db.executar('''SELECT m.id, p.nome, m.tipo, m.quantidade, m.data, m.observacao, f.nome, u.username
                                               FROM movimentacoes m
                                               JOIN produtos p ON m.produto_id = p.id
                                               LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
                                               LEFT JOIN usuarios u ON m.usuario_id = u.id
                                               ORDER BY m.data DESC''').fetchall()
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID Movimentacao', 'Produto', 'Tipo', 'Quantidade', 'Data', 'Observacao', 'Fornecedor', 'Usuario'])
                writer.writerows(movimentacoes)
            messagebox.showinfo("Exportação", "Movimentações exportadas com sucesso para CSV!")
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Exportou Dados', 'Exportou histórico de movimentações para CSV')
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Erro ao exportar movimentações: {str(e)}")

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Logout', 'Usuário saiu do sistema')
            self.destroy()
