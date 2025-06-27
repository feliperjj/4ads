import tkinter as tk
from tkinter import ttk, messagebox


class GerenciarFornecedores(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Gerenciar Fornecedores")
        self.geometry("600x400")  # Tamanho inicial
        self._criar_interface()
        self._atualizar_lista()

    def _criar_interface(self):
        # Frame para entrada de dados
        frame_input = ttk.LabelFrame(self, text="Dados do Fornecedor")
        frame_input.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_input, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nome_entry = ttk.Entry(frame_input)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Contato:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.contato_entry = ttk.Entry(frame_input)
        self.contato_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Botões de ação
        frame_botoes = ttk.Frame(frame_input)
        frame_botoes.grid(row=2, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Adicionar", command=self._salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar", command=self._atualizar_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self._excluir_fornecedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Campos", command=self._limpar_campos).pack(side=tk.LEFT, padx=5)

        frame_input.grid_columnconfigure(1, weight=1)  # Para expandir o campo de entrada

        # Treeview para exibir fornecedores
        self.tree_fornecedores = ttk.Treeview(self, columns=('ID', 'Nome', 'Contato'), show='headings')
        self.tree_fornecedores.heading('ID', text='ID')
        self.tree_fornecedores.heading('Nome', text='Nome')
        self.tree_fornecedores.heading('Contato', text='Contato')

        self.tree_fornecedores.column('ID', width=50)
        self.tree_fornecedores.column('Nome', width=200)
        self.tree_fornecedores.column('Contato', width=200)

        self.tree_fornecedores.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar para a treeview
        scrollbar = ttk.Scrollbar(self.tree_fornecedores, orient=tk.VERTICAL, command=self.tree_fornecedores.yview)
        self.tree_fornecedores.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_fornecedores.bind('<<TreeviewSelect>>', self._carregar_fornecedor_selecionado)

    def _atualizar_lista(self):
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)
        fornecedores = self.db.executar("SELECT id, nome, contato FROM fornecedores").fetchall()
        for fornecedor in fornecedores:
            self.tree_fornecedores.insert('', tk.END, values=fornecedor)

    def _salvar(self):
        try:
            nome = self.nome_entry.get()
            contato = self.contato_entry.get()

            if not nome:
                messagebox.showwarning("Aviso", "O nome do fornecedor é obrigatório.")
                return

            self.db.executar('''INSERT INTO fornecedores (nome, contato) VALUES (?, ?)''', (nome, contato))
            messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
            self._limpar_campos()
            self._atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar fornecedor: {str(e)}")

    def _carregar_fornecedor_selecionado(self, event):
        selected_item = self.tree_fornecedores.focus()
        if selected_item:
            values = self.tree_fornecedores.item(selected_item)['values']
            self._limpar_campos()
            self.nome_entry.insert(0, values[1])
            self.contato_entry.insert(0, values[2])
            self.selected_fornecedor_id = values[0]  # Armazena o ID para atualização/exclusão
        else:
            self.selected_fornecedor_id = None

    def _atualizar_fornecedor(self):
        if not hasattr(self, 'selected_fornecedor_id') or not self.selected_fornecedor_id:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para atualizar.")
            return

        try:
            nome = self.nome_entry.get()
            contato = self.contato_entry.get()

            if not nome:
                messagebox.showwarning("Aviso", "O nome do fornecedor é obrigatório.")
                return

            self.db.executar("UPDATE fornecedores SET nome = ?, contato = ? WHERE id = ?",
                             (nome, contato, self.selected_fornecedor_id))
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

    def _limpar_campos(self):
        self.nome_entry.delete(0, tk.END)
        self.contato_entry.delete(0, tk.END)
        self.selected_fornecedor_id = None
        self.tree_fornecedores.selection_remove(self.tree_fornecedores.focus())  # Desseleciona na treeview
