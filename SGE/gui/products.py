import tkinter as tk
from tkinter import ttk, messagebox


class CadastroProduto(tk.Toplevel):
    def __init__(self, parent, db, atualizar_lista_callback, produto_data=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.atualizar_lista_callback = atualizar_lista_callback
        self.produto_data = produto_data  # Para edição
        self.title("Cadastro de Produto" if not produto_data else "Editar Produto")
        self._criar_formulario()
        if self.produto_data:
            self._preencher_formulario()

    def _criar_formulario(self):
        campos = [
            ('Código:', 'codigo'),
            ('Nome:', 'nome'),
            ('Preço Custo:', 'preco_custo'),
            ('Preço Venda:', 'preco_venda'),  # Adicionado Preço Venda
            ('Quantidade Mínima:', 'quantidade_minima'),
            ('Quantidade Inicial:', 'quantidade')
        ]

        self.entries = {}
        for idx, (label, field) in enumerate(campos):
            ttk.Label(self, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(self)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky='ew')
            self.entries[field] = entry

        ttk.Button(self, text="Salvar", command=self._salvar).grid(row=len(campos), columnspan=2, pady=10)

        self.grid_columnconfigure(1, weight=1)  # Para expandir o campo de entrada

    def _preencher_formulario(self):
        # O produto_data é uma tupla, os índices correspondem à ordem das colunas no SELECT *
        # id, codigo, nome, categoria, preco_custo, preco_venda, quantidade, quantidade_minima
        self.entries['codigo'].insert(0, self.produto_data[1])
        self.entries['nome'].insert(0, self.produto_data[2])
        # self.entries['categoria'].insert(0, self.produto_data[3]) # Se a categoria for adicionada ao formulário
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
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            else:  # Cadastro
                self.db.executar('''INSERT INTO produtos 
                                  (codigo, nome, preco_custo, preco_venda, quantidade_minima, quantidade)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                                 (codigo, nome, preco_custo, preco_venda, quantidade_minima, quantidade))
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")

            self.atualizar_lista_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Entrada",
                                 "Por favor, insira valores numéricos válidos para preço e quantidade.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
