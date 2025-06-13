import tkinter as tk
from tkinter import ttk, messagebox


class CadastroProduto(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Cadastro de Produto")
        self.geometry("350x250")
        self.transient(parent)
        self.grab_set()  # Modal
        self._criar_formulario()

    def _criar_formulario(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        campos = [
            ('Código:', 'codigo'),
            ('Nome:', 'nome'),
            ('Preço Custo:', 'preco_custo'),
            ('Quantidade Mínima:', 'quantidade_minima'),
            ('Quantidade Inicial:', 'quantidade')
        ]

        self.entries = {}
        for idx, (label_text, field) in enumerate(campos):
            label = ttk.Label(frame, text=label_text)
            label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(frame)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
            self.entries[field] = entry

        frame.grid_columnconfigure(1, weight=1)

        btn_salvar = ttk.Button(self, text="Salvar", command=self._salvar)
        btn_salvar.pack(pady=10)

        self.entries['codigo'].focus_set()

    def _salvar(self):
        try:
            codigo = self.entries['codigo'].get()
            nome = self.entries['nome'].get()
            preco_custo = float(self.entries['preco_custo'].get().replace(',', '.'))
            quantidade_minima = int(self.entries['quantidade_minima'].get())
            quantidade = int(self.entries['quantidade'].get())

            if not codigo or not nome:
                messagebox.showerror("Erro de Validação", "Código e Nome são obrigatórios.", parent=self)
                return

            self.db.executar('''
                             INSERT INTO produtos (codigo, nome, preco_custo, quantidade_minima, quantidade)
                             VALUES (?, ?, ?, ?, ?)
                             ''', (codigo, nome, preco_custo, quantidade_minima, quantidade))

            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!", parent=self)
            self.parent._atualizar_lista()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro de Formato",
                                 "Verifique se os campos numéricos (preço, quantidade) estão corretos.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e), parent=self)
