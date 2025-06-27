import tkinter as tk
from tkinter import ttk, messagebox


class CadastroProduto(tk.Toplevel):
    def __init__(self, parent, db, atualizar_lista_callback, usuario_logado,
                 produto_data=None):  # Adicionado usuario_logado
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.atualizar_lista_callback = atualizar_lista_callback
        self.usuario_logado = usuario_logado  # Armazena o usuário logado
        self.produto_data = produto_data
        self.title("Cadastro de Produto" if not produto_data else "Editar Produto")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        self._criar_formulario()
        if self.produto_data:
            self._preencher_formulario()

    def _criar_formulario(self):
        campos = [
            ('Código:', 'codigo'),
            ('Nome:', 'nome'),
            ('Preço Custo:', 'preco_custo'),
            ('Preço Venda:', 'preco_venda'),
            ('Quantidade Mínima:', 'quantidade_minima'),
            ('Quantidade Inicial:', 'quantidade')
        ]

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.entries = {}
        for idx, (label, field) in enumerate(campos):
            ttk.Label(main_frame, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(main_frame)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky='ew')
            self.entries[field] = entry

        ttk.Button(main_frame, text="Salvar", command=self._salvar).grid(row=len(campos), columnspan=2, pady=10)

        main_frame.grid_columnconfigure(1, weight=1)

    def _preencher_formulario(self):
        self.entries['codigo'].insert(0, self.produto_data[1])
        self.entries['nome'].insert(0, self.produto_data[2])
        if self.produto_data[3]:  # Categoria pode ser None
            # self.entries['categoria'].insert(0, self.produto_data[3]) # Se a categoria for adicionada ao formulário
            pass  # Categoria não está no formulário atualmente, então ignoramos
        self.entries['preco_custo'].insert(0, self.produto_data[4])
        self.entries['preco_venda'].insert(0, self.produto_data[5])
        self.entries['quantidade'].insert(0, self.produto_data[6])
        self.entries['quantidade_minima'].insert(0, self.produto_data[7])

    def _salvar(self):
        try:
            codigo = self.entries['codigo'].get()
            nome = self.entries['nome'].get()
            preco_custo = float(self.entries['preco_custo'].get())
            preco_venda = float(self.entries['preco_venda'].get())
            quantidade_minima = int(self.entries['quantidade_minima'].get())
            quantidade = int(self.entries['quantidade'].get())

            if self.produto_data:  # Edição
                produto_id = self.produto_data[0]
                self.db.executar('''UPDATE produtos SET 
                                  codigo = ?, nome = ?, preco_custo = ?, preco_venda = ?, quantidade = ?, quantidade_minima = ?
                                  WHERE id = ?''',
                                 (codigo, nome, preco_custo, preco_venda, quantidade, quantidade_minima, produto_id))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Atualização de Produto',
                                            f"Produto '{nome}' (ID: {produto_id})")
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            else:  # Cadastro
                self.db.executar('''INSERT INTO produtos 
                                  (codigo, nome, preco_custo, preco_venda, quantidade_minima, quantidade)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                                 (codigo, nome, preco_custo, preco_venda, quantidade_minima, quantidade))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Cadastro de Produto',
                                            f"Produto '{nome}' (Código: {codigo})")
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")

            self.atualizar_lista_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Entrada",
                                 "Por favor, insira valores numéricos válidos para preço e quantidade.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))