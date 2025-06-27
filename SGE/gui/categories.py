import tkinter as tk
from tkinter import ttk, messagebox


class GerenciarCategorias(tk.Toplevel):
    def __init__(self, parent, db, main_window_callback):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.main_window_callback = main_window_callback

        self.title("Gerenciar Categorias")
        self.geometry("500x400")
        self.grab_set()

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))

        self.selected_category_id = None

        self._criar_interface()
        self._atualizar_lista_categorias()

        # Garante que a janela principal será atualizada ao fechar
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _criar_interface(self):
        frame_input = ttk.LabelFrame(self, text="Dados da Categoria", padding="10")
        frame_input.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_input, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nome_entry = ttk.Entry(frame_input)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        frame_botoes = ttk.Frame(frame_input)
        frame_botoes.grid(row=1, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Adicionar", command=self._adicionar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar", command=self._atualizar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self._excluir_categoria).pack(side=tk.LEFT, padx=5)

        frame_input.grid_columnconfigure(1, weight=1)

        self.tree_categorias = ttk.Treeview(self, columns=('ID', 'Nome'), show='headings')
        self.tree_categorias.heading('ID', text='ID')
        self.tree_categorias.heading('Nome', text='Nome')
        self.tree_categorias.column('ID', width=50, anchor=tk.CENTER)
        self.tree_categorias.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.tree_categorias.bind('<<TreeviewSelect>>', self._carregar_categoria_selecionada)

    def _atualizar_lista_categorias(self):
        for item in self.tree_categorias.get_children():
            self.tree_categorias.delete(item)
        categorias = self.db.executar("SELECT id, nome FROM categorias ORDER BY nome").fetchall()
        for cat in categorias:
            self.tree_categorias.insert('', tk.END, values=cat)
        self._limpar_campos()

    def _adicionar_categoria(self):
        nome = self.nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O nome da categoria é obrigatório.", parent=self)
            return
        try:
            self.db.executar("INSERT INTO categorias (nome) VALUES (?)", (nome,))
            messagebox.showinfo("Sucesso", "Categoria adicionada com sucesso!", parent=self)
            self._atualizar_lista_categorias()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar categoria: {e}\n\nPossivelmente o nome já existe.",
                                 parent=self)

    def _atualizar_categoria(self):
        nome = self.nome_entry.get().strip()
        if not self.selected_category_id:
            messagebox.showwarning("Aviso", "Selecione uma categoria para atualizar.", parent=self)
            return
        if not nome:
            messagebox.showwarning("Aviso", "O nome da categoria é obrigatório.", parent=self)
            return
        try:
            self.db.executar("UPDATE categorias SET nome = ? WHERE id = ?", (nome, self.selected_category_id))
            messagebox.showinfo("Sucesso", "Categoria atualizada com sucesso!", parent=self)
            self._atualizar_lista_categorias()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar categoria: {e}", parent=self)

    def _excluir_categoria(self):
        if not self.selected_category_id:
            messagebox.showwarning("Aviso", "Selecione uma categoria para excluir.", parent=self)
            return
        nome_cat = self.nome_entry.get()
        if messagebox.askyesno("Confirmar Exclusão",
                               f"Tem certeza que deseja excluir a categoria '{nome_cat}'?\nOs produtos nesta categoria ficarão como 'Sem Categoria'.",
                               parent=self):
            try:
                self.db.executar("DELETE FROM categorias WHERE id = ?", (self.selected_category_id,))
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!", parent=self)
                self._atualizar_lista_categorias()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir categoria: {e}", parent=self)

    def _limpar_campos(self):
        self.nome_entry.delete(0, tk.END)
        self.selected_category_id = None
        if self.tree_categorias.selection():
            self.tree_categorias.selection_remove(self.tree_categorias.selection()[0])

    def _carregar_categoria_selecionada(self, event):
        selected_item = self.tree_categorias.focus()
        if selected_item:
            values = self.tree_categorias.item(selected_item)['values']
            self.selected_category_id = values[0]
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, values[1])

    def _on_close(self):
        self.main_window_callback()
        self.destroy()
