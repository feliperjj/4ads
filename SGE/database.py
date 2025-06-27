import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('estoque.db')
        self._criar_tabelas()

    def _criar_tabelas(self):
        scripts = [
            '''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nome TEXT NOT NULL,
                categoria TEXT,
                preco_custo REAL,
                preco_venda REAL,
                quantidade INTEGER DEFAULT 0,
                quantidade_minima INTEGER DEFAULT 0
            );''',
            '''CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE, -- Nome do fornecedor agora é UNIQUE
                contato TEXT
            );''',
            '''CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                tipo TEXT CHECK(tipo IN ('entrada', 'saida')),
                quantidade INTEGER,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE CASCADE
            );'''  # Adicionado ON DELETE CASCADE para movimentações
        ]

        for script in scripts:
            self.conn.execute(script)
        self.conn.commit()

    def executar(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            # Rollback em caso de erro para evitar estados inconsistentes
            self.conn.rollback()
            raise Exception(f"Erro no banco de dados: {str(e)}")
