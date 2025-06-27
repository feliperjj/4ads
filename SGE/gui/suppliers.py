import tkinter as tk
from tkinter import ttk, messagebox


class GerenciarFornecedores(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Gerenciar Fornecedores")
        self.geometry("800x600")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))
        self.style.configure('TLabelframe', background='#F0F0F0')
        self.style.configure('TLabelframe.Label', background='#F0F0F0', font=('Arial', 12, 'bold'))

        self._criar_interface()
        self._atualizar_lista()

    def _criar_interface(self):
        # Frame para entrada de dados
        frame_input = ttk.LabelFrame(self, text="Dados do Fornecedor", padding="10 10 10 10")
        frame_input.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_input, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nome_entry = ttk.Entry(frame_input)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Contato:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.contato_entry = ttk.Entry(frame_input)
        self.contato_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Endereço:").grid(row=2, column=0, padx=5, pady=5, sticky='w')  # Novo campo
        self.endereco_entry = ttk.Entry(frame_input)
        self.endereco_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="CNPJ:").grid(row=3, column=0, padx=5, pady=5, sticky='w')  # Novo campo
        self.cnpj_entry = ttk.Entry(frame_input)
        self.cnpj_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Email:").grid(row=4, column=0, padx=5, pady=5, sticky='w')  # Novo campo
        self.email_entry = ttk.Entry(frame_input)
        self.email_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # Botões de ação
        frame_botoes = ttk.Frame(frame_input)
        frame_botoes.grid(row=5, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Adicionar", command=self._salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar", command=self._atualizar_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self._excluir_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Campos", command=self._limpar_campos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Ver Histórico de Compras", command=self._ver_historico_compras).pack(
            side=tk.LEFT, padx=5)  # Novo Botão

        frame_input.grid_columnconfigure(1, weight=1)

        # Treeview para exibir fornecedores
        self.tree_fornecedores = ttk.Treeview(self, columns=('ID', 'Nome', 'Contato', 'Endereço', 'CNPJ', 'Email'),
                                              show='headings')
        self.tree_fornecedores.heading('ID', text='ID')
        self.tree_fornecedores.heading('Nome', text='Nome')
        self.tree_fornecedores.heading('Contato', text='Contato')
        self.tree_fornecedores.heading('Endereço', text='Endereço')  # Nova coluna
        self.tree_fornecedores.heading('CNPJ', text='CNPJ')  # Nova coluna
        self.tree_fornecedores.heading('Email', text='Email')  # Nova coluna

        self.tree_fornecedores.column('ID', width=50, anchor=tk.CENTER)
        self.tree_fornecedores.column('Nome', width=150)
        self.tree_fornecedores.column('Contato', width=120)
        self.tree_fornecedores.column('Endereço', width=200)
        self.tree_fornecedores.column('CNPJ', width=120, anchor=tk.CENTER)
        self.tree_fornecedores.column('Email', width=150)

        self.tree_fornecedores.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.tree_fornecedores, orient=tk.VERTICAL, command=self.tree_fornecedores.yview)
        self.tree_fornecedores.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_fornecedores.bind('<<TreeviewSelect>>', self._carregar_fornecedor_selecionado)

        # Campo de busca
        frame_busca = ttk.Frame(self, padding="5 5 5 5")
        frame_busca.pack(padx=10, pady=5, fill='x')
        ttk.Label(frame_busca, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.busca_entry = ttk.Entry(frame_busca)
        self.busca_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.busca_entry.bind('<KeyRelease>', self._filtrar_fornecedores)  # Filtra ao digitar

    def _filtrar_fornecedores(self, event=None):
        termo_busca = self.busca_entry.get().lower()
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)

        fornecedores = self.db.executar(
            "SELECT id, nome, contato, endereco, cnpj, email FROM fornecedores WHERE LOWER(nome) LIKE ? OR LOWER(contato) LIKE ? OR LOWER(cnpj) LIKE ?",
            (f'%{termo_busca}%', f'%{termo_busca}%', f'%{termo_busca}%')).fetchall()
        for fornecedor in fornecedores:
            self.tree_fornecedores.insert('', tk.END, values=fornecedor)

    def _atualizar_lista(self):
        self.busca_entry.delete(0, tk.END)  # Limpa o campo de busca
        self._filtrar_fornecedores()  # Chama o método de filtro para atualizar a lista completa

    def _salvar(self):
        try:
            nome = self.nome_entry.get()
            contato = self.contato_entry.get()
            endereco = self.endereco_entry.get()  # Novo campo
            cnpj = self.cnpj_entry.get()  # Novo campo
            email = self.email_entry.get()  # Novo campo

            if not nome:
                messagebox.showwarning("Aviso", "O nome do fornecedor é obrigatório.")
                return

            self.db.executar(
                '''INSERT INTO fornecedores (nome, contato, endereco, cnpj, email) VALUES (?, ?, ?, ?, ?)''',
                (nome, contato, endereco, cnpj, email))
            messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
            self._limpar_campos()
            self._atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar fornecedor: {str(e)}")

    def _carregar_fornecedor_selecionado(self, event):
        selected_item = self.tree_fornecedores.focus()
        if selected_item:
            values = self.tree_fornecedores.item(selected_item)['values']
            self._limpar_campos(limpar_id=False)  # Não limpa o ID selecionado
            self.nome_entry.insert(0, values[1])
            self.contato_entry.insert(0, values[2])
            self.endereco_entry.insert(0, values[3])  # Preenche novo campo
            self.cnpj_entry.insert(0, values[4])  # Preenche novo campo
            self.email_entry.insert(0, values[5])  # Preenche novo campo
            self.selected_fornecedor_id = values[0]
        else:
            self.selected_fornecedor_id = None

    def _atualizar_fornecedor(self):
        if not hasattr(self, 'selected_fornecedor_id') or not self.selected_fornecedor_id:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para atualizar.")
            return

        try:
            nome = self.nome_entry.get()
            contato = self.contato_entry.get()
            endereco = self.endereco_entry.get()  # Novo campo
            cnpj = self.cnpj_entry.get()  # Novo campo
            email = self.email_entry.get()  # Novo campo

            if not nome:
                messagebox.showwarning("Aviso", "O nome do fornecedor é obrigatório.")
                return

            self.db.executar(
                "UPDATE fornecedores SET nome = ?, contato = ?, endereco = ?, cnpj = ?, email = ? WHERE id = ?",
                (nome, contato, endereco, cnpj, email, self.selected_fornecedor_id))
            messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
            self._limpar_campos()
            self._atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar fornecedor: {str(e)}")

    def _excluir_fornecedor(self):
        if not hasattr(self, 'selected_fornecedor_id') or not self.selected_fornecedor_id:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para excluir.")
            return

        nome_fornecedor = self.nome_entry.get()
        if messagebox.askyesno("Confirmar Exclusão",
                               f"Tem certeza que deseja excluir o fornecedor '{nome_fornecedor}'?"):
            try:
                self.db.executar("DELETE FROM fornecedores WHERE id = ?", (self.selected_fornecedor_id,))
                messagebox.showinfo("Sucesso", "Fornecedor excluído com sucesso!")
                self._limpar_campos()
                self._atualizar_lista()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir fornecedor: {str(e)}")

    def _limpar_campos(self, limpar_id=True):
        self.nome_entry.delete(0, tk.END)
        self.contato_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)  # Limpa novo campo
        self.cnpj_entry.delete(0, tk.END)  # Limpa novo campo
        self.email_entry.delete(0, tk.END)  # Limpa novo campo
        if limpar_id:
            self.selected_fornecedor_id = None
        self.tree_fornecedores.selection_remove(self.tree_fornecedores.focus())

    def _ver_historico_compras(self):
        if not hasattr(self, 'selected_fornecedor_id') or not self.selected_fornecedor_id:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para ver o histórico de compras.")
            return

        nome_fornecedor = self.nome_entry.get()
        HistoricoComprasFornecedor(self, self.db, self.selected_fornecedor_id, nome_fornecedor)


class HistoricoComprasFornecedor(tk.Toplevel):
    def __init__(self, parent, db, fornecedor_id, nome_fornecedor):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.fornecedor_id = fornecedor_id
        self.nome_fornecedor = nome_fornecedor
        self.title(f"Histórico de Compras - {self.nome_fornecedor}")
        self.geometry("700x500")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))

        self._criar_interface()
        self._atualizar_historico()

    def _criar_interface(self):
        ttk.Label(self, text=f"Movimentações de Entrada/Devolução para {self.nome_fornecedor}",
                  font=('Helvetica', 12, 'bold')).pack(pady=10)

        self.tree_historico = ttk.Treeview(self,
                                           columns=('ID Mov.', 'Produto', 'Tipo', 'Quantidade', 'Data', 'Observação'),
                                           show='headings')
        self.tree_historico.heading('ID Mov.', text='ID Mov.')
        self.tree_historico.heading('Produto', text='Produto')
        self.tree_historico.heading('Tipo', text='Tipo')
        self.tree_historico.heading('Quantidade', text='Quantidade')
        self.tree_historico.heading('Data', text='Data/Hora')
        self.tree_historico.heading('Observação', text='Observação')

        self.tree_historico.column('ID Mov.', width=70, anchor=tk.CENTER)
        self.tree_historico.column('Produto', width=150)
        self.tree_historico.column('Tipo', width=100, anchor=tk.CENTER)
        self.tree_historico.column('Quantidade', width=100, anchor=tk.CENTER)
        self.tree_historico.column('Data', width=150, anchor=tk.CENTER)
        self.tree_historico.column('Observação', width=200)

        self.tree_historico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.tree_historico, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _atualizar_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        # Filtra movimentações de entrada e devolução de fornecedor associadas a este fornecedor
        movimentacoes = self.db.executar('''SELECT m.id, p.nome, m.tipo, m.quantidade, m.data, m.observacao
                                           FROM movimentacoes m
                                           JOIN produtos p ON m.produto_id = p.id
                                           WHERE m.fornecedor_id = ? AND (m.tipo = 'entrada' OR m.tipo = 'devolucao_fornecedor')
                                           ORDER BY m.data DESC''', (self.fornecedor_id,)).fetchall()
        for mov in movimentacoes:
            self.tree_historico.insert('', tk.END, values=mov)