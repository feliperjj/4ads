import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class RelatoriosVendas(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Relatórios de Vendas")
        self.geometry("900x600")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))

        self._criar_interface()

    def _criar_interface(self):
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(self, text="Filtros e Período", padding="10")
        frame_filtros.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_filtros, text="Data Início (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.data_inicio_entry = ttk.Entry(frame_filtros)
        self.data_inicio_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.data_inicio_entry.insert(0, (datetime.now().replace(day=1)).strftime('%Y-%m-%d'))  # Primeiro dia do mês

        ttk.Label(frame_filtros, text="Data Fim (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.data_fim_entry = ttk.Entry(frame_filtros)
        self.data_fim_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.data_fim_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Data atual

        ttk.Button(frame_filtros, text="Gerar Relatório", command=self._gerar_relatorio).grid(row=2, columnspan=2,
                                                                                              pady=10)

        frame_filtros.grid_columnconfigure(1, weight=1)

        # Frame de resultados
        frame_resultados = ttk.Frame(self, padding="10")
        frame_resultados.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(frame_resultados)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de Produtos Mais Vendidos
        self.frame_mais_vendidos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_mais_vendidos, text="Produtos Mais Vendidos")
        self._criar_tab_mais_vendidos(self.frame_mais_vendidos)

        # Aba de Vendas por Período
        self.frame_vendas_periodo = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_vendas_periodo, text="Vendas por Período")
        self._criar_tab_vendas_periodo(self.frame_vendas_periodo)

        # Aba de Valor Total de Vendas
        self.frame_valor_total = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_valor_total, text="Valor Total de Vendas")
        self._criar_tab_valor_total(self.frame_valor_total)

    def _criar_tab_mais_vendidos(self, parent_frame):
        self.tree_mais_vendidos = ttk.Treeview(parent_frame, columns=('Produto', 'Quantidade Total Vendida'),
                                               show='headings')
        self.tree_mais_vendidos.heading('Produto', text='Produto')
        self.tree_mais_vendidos.heading('Quantidade Total Vendida', text='Quantidade Total Vendida')

        self.tree_mais_vendidos.column('Produto', width=300)
        self.tree_mais_vendidos.column('Quantidade Total Vendida', width=200, anchor=tk.CENTER)

        self.tree_mais_vendidos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.tree_mais_vendidos, orient=tk.VERTICAL, command=self.tree_mais_vendidos.yview)
        self.tree_mais_vendidos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _criar_tab_vendas_periodo(self, parent_frame):
        self.tree_vendas_periodo = ttk.Treeview(parent_frame, columns=('Data', 'Produto', 'Quantidade', 'Valor Total'),
                                                show='headings')
        self.tree_vendas_periodo.heading('Data', text='Data')
        self.tree_vendas_periodo.heading('Produto', text='Produto')
        self.tree_vendas_periodo.heading('Quantidade', text='Quantidade')
        self.tree_vendas_periodo.heading('Valor Total', text='Valor Total (R$)')

        self.tree_vendas_periodo.column('Data', width=120, anchor=tk.CENTER)
        self.tree_vendas_periodo.column('Produto', width=250)
        self.tree_vendas_periodo.column('Quantidade', width=100, anchor=tk.CENTER)
        self.tree_vendas_periodo.column('Valor Total', width=150, anchor=tk.CENTER)

        self.tree_vendas_periodo.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.tree_vendas_periodo, orient=tk.VERTICAL, command=self.tree_vendas_periodo.yview)
        self.tree_vendas_periodo.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _criar_tab_valor_total(self, parent_frame):
        self.label_valor_total = ttk.Label(parent_frame, text="Valor Total de Vendas no Período: R$ 0.00",
                                           font=('Helvetica', 16, 'bold'))
        self.label_valor_total.pack(pady=50)

    def _limpar_tabelas(self):
        for item in self.tree_mais_vendidos.get_children():
            self.tree_mais_vendidos.delete(item)
        for item in self.tree_vendas_periodo.get_children():
            self.tree_vendas_periodo.delete(item)
        self.label_valor_total.config(text="Valor Total de Vendas no Período: R$ 0.00")

    def _gerar_relatorio(self):
        self._limpar_tabelas()

        data_inicio_str = self.data_inicio_entry.get()
        data_fim_str = self.data_fim_entry.get()

        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            if data_inicio > data_fim:
                messagebox.showwarning("Erro de Data", "A data de início não pode ser posterior à data fim.")
                return
        except ValueError:
            messagebox.showerror("Erro de Formato de Data", "Use o formato YYYY-MM-DD para as datas.")
            return

        # Relatório de Produtos Mais Vendidos
        query_mais_vendidos = '''
            SELECT p.nome, SUM(m.quantidade) AS total_vendido
            FROM movimentacoes m
            JOIN produtos p ON m.produto_id = p.id
            WHERE m.tipo = 'saida' AND m.data BETWEEN ? AND ?
            GROUP BY p.nome
            ORDER BY total_vendido DESC
        '''
        produtos_mais_vendidos = self.db.executar(query_mais_vendidos, (data_inicio_str + ' 00:00:00',
                                                                        data_fim_str + ' 23:59:59')).fetchall()
        for produto, quantidade in produtos_mais_vendidos:
            self.tree_mais_vendidos.insert('', tk.END, values=(produto, quantidade))

        # Relatório de Vendas por Período
        query_vendas_periodo = '''
            SELECT DATE(m.data) AS data_venda, p.nome, m.quantidade, (m.quantidade * p.preco_venda) AS valor_total_item
            FROM movimentacoes m
            JOIN produtos p ON m.produto_id = p.id
            WHERE m.tipo = 'saida' AND m.data BETWEEN ? AND ?
            ORDER BY m.data ASC
        '''
        vendas_periodo = self.db.executar(query_vendas_periodo,
                                          (data_inicio_str + ' 00:00:00', data_fim_str + ' 23:59:59')).fetchall()
        for data_venda, produto_nome, quantidade, valor_total_item in vendas_periodo:
            self.tree_vendas_periodo.insert('', tk.END,
                                            values=(data_venda, produto_nome, quantidade, f"{valor_total_item:.2f}"))

        # Relatório de Valor Total de Vendas
        query_valor_total = '''
            SELECT SUM(m.quantidade * p.preco_venda)
            FROM movimentacoes m
            JOIN produtos p ON m.produto_id = p.id
            WHERE m.tipo = 'saida' AND m.data BETWEEN ? AND ?
        '''
        valor_total_vendas = \
        self.db.executar(query_valor_total, (data_inicio_str + ' 00:00:00', data_fim_str + ' 23:59:59')).fetchone()[0]
        if valor_total_vendas is None:
            valor_total_vendas = 0.00
        self.label_valor_total.config(text=f"Valor Total de Vendas no Período: R$ {valor_total_vendas:.2f}")

        messagebox.showinfo("Relatório Gerado", "Relatório de vendas gerado com sucesso!")