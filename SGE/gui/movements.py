import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MovimentacaoEstoque(tk.Toplevel):
    def __init__(self, parent, db, atualizar_lista_callback, usuario_logado):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.atualizar_lista_callback = atualizar_lista_callback
        self.usuario_logado = usuario_logado
        self.title("Movimentação de Estoque")
        self.geometry("500x350")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        self._criar_interface()
        self._carregar_fornecedores()

    def _criar_interface(self):
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="Código do Produto:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.codigo_entry = ttk.Entry(input_frame)
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.quantidade_entry = ttk.Entry(input_frame)
        self.quantidade_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Tipo de Movimentação:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.tipo_mov_combobox = ttk.Combobox(input_frame,
                                              values=["entrada", "saida", "devolucao_cliente", "devolucao_fornecedor",
                                                      "ajuste"], state='readonly')
        self.tipo_mov_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.tipo_mov_combobox.set("entrada")
        self.tipo_mov_combobox.bind('<<ComboboxSelected>>', self._habilitar_desabilitar_fornecedor)

        ttk.Label(input_frame, text="Fornecedor (Entrada/Dev. Forn.):").grid(row=3, column=0, padx=5, pady=5,
                                                                             sticky='w')
        self.fornecedor_combobox = ttk.Combobox(input_frame, state='readonly')
        self.fornecedor_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.fornecedores_map = {}

        ttk.Label(input_frame, text="Observação:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.observacao_entry = ttk.Entry(input_frame)
        self.observacao_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        processar_button = ttk.Button(self, text="Processar Movimentação", command=self._processar)
        processar_button.pack(pady=15)

        input_frame.grid_columnconfigure(1, weight=1)

    def _habilitar_desabilitar_fornecedor(self, event=None):
        tipo_selecionado = self.tipo_mov_combobox.get()
        if tipo_selecionado in ['entrada', 'devolucao_fornecedor']:
            self.fornecedor_combobox.config(state='readonly')
        else:
            self.fornecedor_combobox.set("")
            self.fornecedor_combobox.config(state='disabled')

    def _carregar_fornecedores(self):
        fornecedores = self.db.executar("SELECT id, nome FROM fornecedores ORDER BY nome").fetchall()
        fornecedor_nomes = [""]
        self.fornecedores_map = {"": None}
        for f_id, f_nome in fornecedores:
            fornecedor_nomes.append(f_nome)
            self.fornecedores_map[f_nome] = f_id
        self.fornecedor_combobox['values'] = fornecedor_nomes
        self.fornecedor_combobox.set("")
        self._habilitar_desabilitar_fornecedor()

    def _processar(self):
        codigo = self.codigo_entry.get()
        quantidade_str = self.quantidade_entry.get()
        tipo = self.tipo_mov_combobox.get()
        observacao = self.observacao_entry.get()
        fornecedor_nome_selecionado = self.fornecedor_combobox.get()
        fornecedor_id = self.fornecedores_map.get(fornecedor_nome_selecionado)

        if not codigo or not quantidade_str or not tipo:
            messagebox.showwarning("Aviso",
                                   "Por favor, preencha o código do produto, a quantidade e o tipo de movimentação.")
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
            nova_quantidade = quantidade_atual

            # Lógica de validação e cálculo da nova quantidade
            if tipo == 'entrada':
                nova_quantidade = quantidade_atual + quantidade
                if not fornecedor_id:
                    messagebox.showwarning("Aviso", "Selecione um fornecedor para movimentações de ENTRADA.")
                    return
            elif tipo == 'saida':
                if quantidade > quantidade_atual:
                    messagebox.showwarning("Aviso",
                                           f"Não há quantidade suficiente em estoque para '{nome_produto}'. Disponível: {quantidade_atual}")
                    return
                nova_quantidade = quantidade_atual - quantidade
                fornecedor_id = None
            elif tipo == 'devolucao_cliente':
                nova_quantidade = quantidade_atual + quantidade
                fornecedor_id = None
            elif tipo == 'devolucao_fornecedor':
                if quantidade > quantidade_atual:
                    messagebox.showwarning("Aviso",
                                           f"Não há quantidade suficiente em estoque para devolver para o fornecedor. Disponível: {quantidade_atual}")
                    return
                nova_quantidade = quantidade_atual - quantidade
                if not fornecedor_id:
                    messagebox.showwarning("Aviso", "Selecione um fornecedor para DEVOLUÇÃO PARA FORNECEDOR.")
                    return
            elif tipo == 'ajuste':
                # Para ajuste, a "quantidade" no campo é a quantidade a ser adicionada/subtraída
                # Ajuste positivo aumenta, ajuste negativo diminui
                # Se for ajuste, o campo observação é obrigatório
                if not observacao.strip():
                    messagebox.showwarning("Aviso", "É obrigatório adicionar uma observação para ajustes de estoque.")
                    return

                # Se a quantidade for positiva, adiciona. Se for negativa, subtrai.
                nova_quantidade = quantidade_atual + quantidade
                fornecedor_id = None

            self.db.executar("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))
            self.db.executar('''INSERT INTO movimentacoes
                                (produto_id, tipo, quantidade, data, observacao, fornecedor_id, usuario_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (produto_id, tipo, quantidade, datetime.now(), observacao, fornecedor_id,
                              self.usuario_logado['id']))

            self.db.registrar_auditoria(self.usuario_logado['id'], f"Movimentação de {tipo}",
                                        f"Produto '{nome_produto}' (ID: {produto_id}), Qtd: {quantidade}. Nova Qtd: {nova_quantidade}")
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
        self.geometry("1200x600")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))

        self._criar_interface()
        self._atualizar_historico()

    def _criar_interface(self):
        # Frame de busca e filtros
        frame_filtros = ttk.Frame(self, padding="5 5 5 5")
        frame_filtros.pack(padx=10, pady=5, fill='x')

        ttk.Label(frame_filtros, text="Buscar Produto:").pack(side=tk.LEFT, padx=5)
        self.busca_produto_entry = ttk.Entry(frame_filtros)
        self.busca_produto_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.busca_produto_entry.bind('<KeyRelease>', self._filtrar_historico)

        ttk.Label(frame_filtros, text="Tipo:").pack(side=tk.LEFT, padx=(15, 5))
        self.tipo_combobox = ttk.Combobox(frame_filtros,
                                          values=["", "entrada", "saida", "devolucao_cliente", "devolucao_fornecedor",
                                                  "ajuste"], state='readonly')
        self.tipo_combobox.set("")
        self.tipo_combobox.pack(side=tk.LEFT, padx=5)
        self.tipo_combobox.bind('<<ComboboxSelected>>', self._filtrar_historico)

        # Adicionar filtros de data
        ttk.Label(frame_filtros, text="De:").pack(side=tk.LEFT, padx=(15, 5))
        self.data_inicio_entry = ttk.Entry(frame_filtros, width=10)
        self.data_inicio_entry.pack(side=tk.LEFT, padx=5)
        self.data_inicio_entry.bind('<KeyRelease>', self._filtrar_historico)

        ttk.Label(frame_filtros, text="Até:").pack(side=tk.LEFT, padx=5)
        self.data_fim_entry = ttk.Entry(frame_filtros, width=10)
        self.data_fim_entry.pack(side=tk.LEFT, padx=5)
        self.data_fim_entry.bind('<KeyRelease>', self._filtrar_historico)

        self.tree_historico = ttk.Treeview(self,
                                           columns=('ID Mov.', 'Produto', 'Categoria', 'Tipo', 'Quantidade', 'Data',
                                                    'Observação',
                                                    'Fornecedor', 'Usuário'), show='headings')
        self.tree_historico.heading('ID Mov.', text='ID Mov.')
        self.tree_historico.heading('Produto', text='Produto')
        self.tree_historico.heading('Categoria', text='Categoria')
        self.tree_historico.heading('Tipo', text='Tipo')
        self.tree_historico.heading('Quantidade', text='Quantidade')
        self.tree_historico.heading('Data', text='Data/Hora')
        self.tree_historico.heading('Observação', text='Observação')
        self.tree_historico.heading('Fornecedor', text='Fornecedor')
        self.tree_historico.heading('Usuário', text='Usuário')

        self.tree_historico.column('ID Mov.', width=60, anchor=tk.CENTER)
        self.tree_historico.column('Produto', width=150)
        self.tree_historico.column('Categoria', width=120)
        self.tree_historico.column('Tipo', width=100, anchor=tk.CENTER)
        self.tree_historico.column('Quantidade', width=80, anchor=tk.CENTER)
        self.tree_historico.column('Data', width=140, anchor=tk.CENTER)
        self.tree_historico.column('Observação', width=200)
        self.tree_historico.column('Fornecedor', width=120)
        self.tree_historico.column('Usuário', width=100)

        self.tree_historico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.tree_historico, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _filtrar_historico(self, event=None):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        termo_busca = self.busca_produto_entry.get().lower()
        tipo_selecionado = self.tipo_combobox.get()
        data_inicio_str = self.data_inicio_entry.get()
        data_fim_str = self.data_fim_entry.get()

        query = '''SELECT m.id, \
                          p.nome, \
                          IFNULL(c.nome, 'Sem Categoria'), \
                          m.tipo, \
                          m.quantidade,
                          m.data, \
                          m.observacao, \
                          f.nome, \
                          u.username
                   FROM movimentacoes m
                            JOIN produtos p ON m.produto_id = p.id
                            LEFT JOIN categorias c ON p.categoria_id = c.id
                            LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
                            LEFT JOIN usuarios u ON m.usuario_id = u.id
                   WHERE 1 = 1'''
        params = []

        if termo_busca:
            query += " AND (LOWER(p.nome) LIKE ? OR LOWER(c.nome) LIKE ?)"
            params.extend([f'%{termo_busca}%', f'%{termo_busca}%'])

        if tipo_selecionado:
            query += " AND m.tipo = ?"
            params.append(tipo_selecionado)

        if data_inicio_str:
            try:
                datetime.strptime(data_inicio_str, '%Y-%m-%d')
                query += " AND m.data >= ?"
                params.append(data_inicio_str + ' 00:00:00')
            except ValueError:
                pass

        if data_fim_str:
            try:
                datetime.strptime(data_fim_str, '%Y-%m-%d')
                query += " AND m.data <= ?"
                params.append(data_fim_str + ' 23:59:59')
            except ValueError:
                pass

        query += " ORDER BY m.data DESC"

        movimentacoes = self.db.executar(query, tuple(params)).fetchall()
        for mov in movimentacoes:
            mov_list = list(mov)
            fornecedor_nome = mov_list[7] if mov_list[7] else "N/A"
            usuario_nome = mov_list[8] if mov_list[8] else "N/A"

            display_values = (
                mov_list[0],  # ID Mov.
                mov_list[1],  # Produto
                mov_list[2],  # Categoria
                mov_list[3],  # Tipo
                mov_list[4],  # Quantidade
                mov_list[5],  # Data
                mov_list[6],  # Observação
                fornecedor_nome,
                usuario_nome
            )
            self.tree_historico.insert('', tk.END, values=display_values)

    def _atualizar_historico(self):
        self._filtrar_historico()
