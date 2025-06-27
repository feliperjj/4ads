import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class HistoricoAuditoria(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Histórico de Auditoria")
        self.geometry("1000x600")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg="#F0F0F0")
        self.style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 10))

        self._criar_interface()
        self._atualizar_historico()

    def _criar_interface(self):
        # Frame de filtros
        frame_filtros = ttk.Frame(self, padding="5 5 5 5")
        frame_filtros.pack(padx=10, pady=5, fill='x')

        ttk.Label(frame_filtros, text="Buscar Usuário/Ação:").pack(side=tk.LEFT, padx=5)
        self.busca_entry = ttk.Entry(frame_filtros)
        self.busca_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.busca_entry.bind('<KeyRelease>', self._filtrar_historico)

        self.tree_auditoria = ttk.Treeview(self, columns=('ID', 'Usuário', 'Ação', 'Data', 'Detalhes'), show='headings')
        self.tree_auditoria.heading('ID', text='ID')
        self.tree_auditoria.heading('Usuário', text='Usuário')
        self.tree_auditoria.heading('Ação', text='Ação')
        self.tree_auditoria.heading('Data', text='Data/Hora')
        self.tree_auditoria.heading('Detalhes', text='Detalhes')

        self.tree_auditoria.column('ID', width=50, anchor=tk.CENTER)
        self.tree_auditoria.column('Usuário', width=100)
        self.tree_auditoria.column('Ação', width=150)
        self.tree_auditoria.column('Data', width=180, anchor=tk.CENTER)
        self.tree_auditoria.column('Detalhes', width=400)

        self.tree_auditoria.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.tree_auditoria, orient=tk.VERTICAL, command=self.tree_auditoria.yview)
        self.tree_auditoria.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _filtrar_historico(self, event=None):
        for item in self.tree_auditoria.get_children():
            self.tree_auditoria.delete(item)

        termo_busca = self.busca_entry.get().lower()

        query = '''SELECT a.id, u.username, a.acao, a.data, a.detalhes
                   FROM auditoria a
                   LEFT JOIN usuarios u ON a.usuario_id = u.id
                   WHERE 1=1'''
        params = []

        if termo_busca:
            query += " AND (LOWER(u.username) LIKE ? OR LOWER(a.acao) LIKE ? OR LOWER(a.detalhes) LIKE ?)"
            params.append(f'%{termo_busca}%')
            params.append(f'%{termo_busca}%')
            params.append(f'%{termo_busca}%')

        query += " ORDER BY a.data DESC"

        auditorias = self.db.executar(query, tuple(params)).fetchall()
        for aud in auditorias:
            # Substitui None por 'N/A' para usuários excluídos
            username = aud[1] if aud[1] else "N/A (Usuário Excluído)"
            self.tree_auditoria.insert('', tk.END, values=(aud[0], username, aud[2], aud[3], aud[4]))

    def _atualizar_historico(self):
        self._filtrar_historico()