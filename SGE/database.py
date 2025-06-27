import sqlite3
import hashlib  # Para hash de senhas


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('estoque.db')
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._criar_tabelas()
        self._criar_usuario_admin_padrao() # Novo: Cria um admin padrão se não existir

    def _criar_tabelas(self):
        scripts = [
            '''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nome TEXT NOT NULL,
                categoria_id INTEGER,
                preco_custo REAL,
                preco_venda REAL,
                quantidade INTEGER DEFAULT 0,
                quantidade_minima INTEGER DEFAULT 0,
                FOREIGN KEY(categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                contato TEXT,
                endereco TEXT,
                cnpj TEXT,
                email TEXT
            );''',
            '''CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                tipo TEXT CHECK(tipo IN ('entrada', 'saida', 'devolucao_cliente', 'devolucao_fornecedor', 'ajuste')),
                quantidade INTEGER,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                fornecedor_id INTEGER,
                usuario_id INTEGER, 
                FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nivel_acesso TEXT CHECK(nivel_acesso IN ('administrador', 'operador')) NOT NULL DEFAULT 'operador'
            );''',
            '''CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                acao TEXT NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detalhes TEXT,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            );'''
        ]
        for script in scripts:
            self.conn.execute(script)
        self.conn.commit()

    def _criar_usuario_admin_padrao(self):
        cursor = self.conn.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password = 'admin'  # Senha padrão, idealmente deve ser mais forte ou gerada
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.conn.execute("INSERT INTO usuarios (username, password_hash, nivel_acesso) VALUES (?, ?, ?)",
                              ('admin', password_hash, 'administrador'))
            self.conn.commit()
            print("Usuário 'admin' criado com a senha 'admin'. Por favor, altere a senha!")

    def executar(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro no banco de dados: {str(e)}")

    def registrar_auditoria(self, usuario_id, acao, detalhes=None):
        try:
            self.executar("INSERT INTO auditoria (usuario_id, acao, detalhes) VALUES (?, ?, ?)",
                          (usuario_id, acao, detalhes))
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")
