import tkinter as tk
from tkinter import ttk, messagebox
import hashlib


class GerenciarUsuarios(tk.Toplevel):
    def __init__(self, parent, db, usuario_logado):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario_logado = usuario_logado
        self.title("Gerenciar Usuários")
        self.geometry("700x500")

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
        self._atualizar_lista_usuarios()

    def _criar_interface(self):
        frame_input = ttk.LabelFrame(self, text="Dados do Usuário", padding="10")
        frame_input.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_input, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.username_entry = ttk.Entry(frame_input)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(frame_input, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_input, text="Nível de Acesso:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.nivel_acesso_combobox = ttk.Combobox(frame_input, values=["administrador", "operador"], state='readonly')
        self.nivel_acesso_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.nivel_acesso_combobox.set("operador")  # Valor padrão

        frame_botoes = ttk.Frame(frame_input)
        frame_botoes.grid(row=3, columnspan=2, pady=10)
        ttk.Button(frame_botoes, text="Adicionar", command=self._adicionar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar", command=self._atualizar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self._excluir_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Campos", command=self._limpar_campos).pack(side=tk.LEFT, padx=5)

        frame_input.grid_columnconfigure(1, weight=1)

        self.tree_usuarios = ttk.Treeview(self, columns=('ID', 'Username', 'Nível de Acesso'), show='headings')
        self.tree_usuarios.heading('ID', text='ID')
        self.tree_usuarios.heading('Username', text='Username')
        self.tree_usuarios.heading('Nível de Acesso', text='Nível de Acesso')

        self.tree_usuarios.column('ID', width=50, anchor=tk.CENTER)
        self.tree_usuarios.column('Username', width=200)
        self.tree_usuarios.column('Nível de Acesso', width=150, anchor=tk.CENTER)

        self.tree_usuarios.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.tree_usuarios, orient=tk.VERTICAL, command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_usuarios.bind('<<TreeviewSelect>>', self._carregar_usuario_selecionado)

    def _atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        usuarios = self.db.executar("SELECT id, username, nivel_acesso FROM usuarios").fetchall()
        for user in usuarios:
            self.tree_usuarios.insert('', tk.END, values=user)

    def _adicionar_usuario(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        nivel_acesso = self.nivel_acesso_combobox.get()

        if not username or not password or not nivel_acesso:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return

        if self.usuario_logado['nivel_acesso'] != 'administrador':
            messagebox.showerror("Permissão Negada", "Você não tem permissão para adicionar usuários.")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.db.executar("INSERT INTO usuarios (username, password_hash, nivel_acesso) VALUES (?, ?, ?)",
                             (username, password_hash, nivel_acesso))
            self.db.registrar_auditoria(self.usuario_logado['id'], 'Adição de Usuário',
                                        f"Usuário '{username}' adicionado.")
            messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso!")
            self._limpar_campos()
            self._atualizar_lista_usuarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar usuário: {str(e)}")

    def _carregar_usuario_selecionado(self, event):
        selected_item = self.tree_usuarios.focus()
        if selected_item:
            values = self.tree_usuarios.item(selected_item)['values']
            self._limpar_campos(limpar_id=False)
            self.username_entry.insert(0, values[1])
            self.nivel_acesso_combobox.set(values[2])
            self.selected_user_id = values[0]
            # Não carregamos a senha por segurança
        else:
            self.selected_user_id = None

    def _atualizar_usuario(self):
        if not hasattr(self, 'selected_user_id') or not self.selected_user_id:
            messagebox.showwarning("Aviso", "Selecione um usuário para atualizar.")
            return

        username = self.username_entry.get()
        password = self.password_entry.get()  # Opcional: só atualiza se preenchido
        nivel_acesso = self.nivel_acesso_combobox.get()

        if not username or not nivel_acesso:
            messagebox.showwarning("Aviso", "Username e Nível de Acesso são obrigatórios.")
            return

        if self.usuario_logado['nivel_acesso'] != 'administrador':
            messagebox.showerror("Permissão Negada", "Você não tem permissão para atualizar usuários.")
            return

        if self.selected_user_id == self.usuario_logado['id'] and nivel_acesso != 'administrador':
            messagebox.showwarning("Aviso", "Você não pode rebaixar seu próprio nível de acesso.")
            return

        try:
            if password:  # Se a senha foi preenchida, atualiza o hash
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                self.db.executar("UPDATE usuarios SET username = ?, password_hash = ?, nivel_acesso = ? WHERE id = ?",
                                 (username, password_hash, nivel_acesso, self.selected_user_id))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Atualização de Usuário (com senha)',
                                            f"Usuário '{username}' (ID: {self.selected_user_id}) atualizado.")
            else:  # Mantém a senha existente
                self.db.executar("UPDATE usuarios SET username = ?, nivel_acesso = ? WHERE id = ?",
                                 (username, nivel_acesso, self.selected_user_id))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Atualização de Usuário',
                                            f"Usuário '{username}' (ID: {self.selected_user_id}) atualizado (sem alteração de senha).")

            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            self._limpar_campos()
            self._atualizar_lista_usuarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")

    def _excluir_usuario(self):
        if not hasattr(self, 'selected_user_id') or not self.selected_user_id:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir.")
            return

        if self.usuario_logado['nivel_acesso'] != 'administrador':
            messagebox.showerror("Permissão Negada", "Você não tem permissão para excluir usuários.")
            return

        if self.selected_user_id == self.usuario_logado['id']:
            messagebox.showwarning("Aviso", "Você não pode excluir seu próprio usuário.")
            return

        username = self.username_entry.get()
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o usuário '{username}'?"):
            try:
                self.db.executar("DELETE FROM usuarios WHERE id = ?", (self.selected_user_id,))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Exclusão de Usuário',
                                            f"Usuário '{username}' (ID: {self.selected_user_id}) excluído.")
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
                self._limpar_campos()
                self._atualizar_lista_usuarios()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")

    def _limpar_campos(self, limpar_id=True):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.nivel_acesso_combobox.set("operador")
        if limpar_id:
            self.selected_user_id = None
        self.tree_usuarios.selection_remove(self.tree_usuarios.focus())