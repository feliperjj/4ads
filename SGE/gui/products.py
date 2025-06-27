import tkinter as tk
from tkinter import ttk, messagebox


class CadastroProduto(tk.Toplevel):
    def __init__(self, parent, db, atualizar_lista_callback, usuario_logado, produto_data=None):  # Adicionado usuario_logado
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.atualizar_lista_callback = atualizar_lista_callback
        self.usuario_logado = usuario_logado  # Armazena o usuário logado
        self.produto_data = produto_data
        self.title("Cadastro de Produto" if not produto_data else "Editar Produto")
        self.grab_set()

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        self.categorias_map = {}

        self._criar_formulario()
        self._carregar_categorias()

        if self.produto_data:
            self._preencher_formulario()

    def _criar_formulario(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.entries = {}

        ttk.Label(main_frame, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entries['codigo'] = ttk.Entry(main_frame)
        self.entries['codigo'].grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(main_frame, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entries['nome'] = ttk.Entry(main_frame)
        self.entries['nome'].grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # NOVO: Campo de Categoria com Combobox
        ttk.Label(main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.categoria_combobox = ttk.Combobox(main_frame, state='readonly')
        self.categoria_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.entries['categoria'] = self.categoria_combobox  # Adicionado para fácil acesso

        ttk.Label(main_frame, text="Preço Custo:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.entries['preco_custo'] = ttk.Entry(main_frame)
        self.entries['preco_custo'].grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(main_frame, text="Preço Venda:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.entries['preco_venda'] = ttk.Entry(main_frame)
        self.entries['preco_venda'].grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(main_frame, text="Quantidade Mínima:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.entries['quantidade_minima'] = ttk.Entry(main_frame)
        self.entries['quantidade_minima'].grid(row=5, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(main_frame, text="Quantidade Inicial:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.entries['quantidade'] = ttk.Entry(main_frame)
        self.entries['quantidade'].grid(row=6, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(main_frame, text="Salvar", command=self._salvar).grid(row=7, columnspan=2, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)

    def _carregar_categorias(self):
        categorias = self.db.executar("SELECT id, nome FROM categorias ORDER BY nome").fetchall()
        categoria_nomes = ["Nenhuma"]
        self.categorias_map = {"Nenhuma": None}
        for cat_id, cat_nome in categorias:
            categoria_nomes.append(cat_nome)
            self.categorias_map[cat_nome] = cat_id
        self.categoria_combobox['values'] = categoria_nomes
        self.categoria_combobox.set("Nenhuma")

    def _preencher_formulario(self):
        self.entries['codigo'].insert(0, self.produto_data[1])
        self.entries['nome'].insert(0, self.produto_data[2])

        categoria_id = self.produto_data[3]
        if categoria_id:
            categoria_nome = self.db.executar("SELECT nome FROM categorias WHERE id = ?", (categoria_id,)).fetchone()
            if categoria_nome:
                self.categoria_combobox.set(categoria_nome[0])

        self.entries['preco_custo'].insert(0, self.produto_data[4])
        self.entries['preco_venda'].insert(0, self.produto_data[5])
        self.entries['quantidade'].insert(0, self.produto_data[6])
        self.entries['quantidade_minima'].insert(0, self.produto_data[7])

    def _salvar(self):
        try:
            codigo = self.entries['codigo'].get()
            nome = self.entries['nome'].get()

            categoria_nome_selecionada = self.categoria_combobox.get()
            categoria_id = self.categorias_map.get(categoria_nome_selecionada)

            preco_custo = float(self.entries['preco_custo'].get())
            preco_venda = float(self.entries['preco_venda'].get())
            quantidade_minima = int(self.entries['quantidade_minima'].get())
            quantidade = int(self.entries['quantidade'].get())

            if self.produto_data:  # Edição
                produto_id = self.produto_data[0]
                self.db.executar('''UPDATE produtos
                                    SET codigo            = ?,
                                        nome              = ?,
                                        categoria_id      = ?,
                                        preco_custo       = ?,
                                        preco_venda       = ?,
                                        quantidade        = ?,
                                        quantidade_minima = ?
                                    WHERE id = ?''',
                                 (codigo, nome, categoria_id, preco_custo, preco_venda, quantidade, quantidade_minima,
                                  produto_id))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Atualização de Produto',
                                            f"Produto '{nome}' (ID: {produto_id})")
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!", parent=self)
            else:  # Cadastro
                self.db.executar('''INSERT INTO produtos
                                    (codigo, nome, categoria_id, preco_custo, preco_venda, quantidade_minima,
                                     quantidade)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                 (codigo, nome, categoria_id, preco_custo, preco_venda, quantidade_minima, quantidade))
                self.db.registrar_auditoria(self.usuario_logado['id'], 'Cadastro de Produto',
                                            f"Produto '{nome}' (Código: {codigo})")
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!", parent=self)

            self.atualizar_lista_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Entrada",
                                 "Por favor, insira valores numéricos válidos para preço e quantidade.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
