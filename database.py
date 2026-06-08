import sqlite3

DB_NAME = "medidor.sqlite"

def obter_conexao():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas paciente, endereco e medida caso não existam e realiza migrações se necessário."""
    conn = obter_conexao()
    cursor = conn.cursor()

    # Cria a tabela paciente com cartao_sus opcional por padrão (para novos bancos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS paciente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_nascimento DATE NOT NULL,
        cpf TEXT UNIQUE,
        cartao_sus TEXT UNIQUE,
        telefone TEXT,
        email TEXT
    )''')

    # Migração em background para banco existente que tenha cartao_sus como NOT NULL
    cursor.execute("PRAGMA table_info(paciente)")
    colunas = cursor.fetchall()
    
    cartao_sus_not_null = False
    for col in colunas:
        if col[1] == "cartao_sus" and col[3] == 1:
            cartao_sus_not_null = True
            break

    if cartao_sus_not_null:
        print("[DATABASE] Executando migração: tornando campo 'cartao_sus' opcional (permitindo NULL)...")
        try:
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            cursor.execute('''CREATE TABLE paciente_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nascimento DATE NOT NULL,
                cpf TEXT UNIQUE,
                cartao_sus TEXT UNIQUE,
                telefone TEXT,
                email TEXT
            )''')
            
            cursor.execute('''INSERT INTO paciente_new (id, nome, data_nascimento, cpf, cartao_sus, telefone, email)
                              SELECT id, nome, data_nascimento, cpf, cartao_sus, telefone, email FROM paciente''')
            
            cursor.execute("DROP TABLE paciente")
            cursor.execute("ALTER TABLE paciente_new RENAME TO paciente")
            
            conn.commit()
            print("[DATABASE] Migração concluída com sucesso.")
        except Exception as e:
            conn.rollback()
            print(f"[DATABASE] Falha na migração: {e}")
        finally:
            cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''CREATE TABLE IF NOT EXISTS endereco (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER UNIQUE NOT NULL,
        cep TEXT NOT NULL,
        rua TEXT NOT NULL,
        numero TEXT NOT NULL,
        bairro TEXT NOT NULL,
        cidade TEXT NOT NULL,
        estado TEXT NOT NULL,
        complemento TEXT,
        FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS medida (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        peso REAL,
        sistolica INTEGER,
        diastolica INTEGER,
        pulsacao INTEGER,
        temperatura REAL,
        FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

def listar_pacientes():
    """Retorna uma lista de tuplas (id, nome, cartao_sus) de todos os pacientes."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cartao_sus FROM paciente")
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

def cadastrar_paciente(nome, data_nascimento, cpf, cartao_sus, telefone, email):
    """Insere um novo paciente no banco de dados, tratando campos opcionais vazios como None (NULL)."""
    sus_val = cartao_sus.strip() if cartao_sus else None
    if not sus_val:
        sus_val = None
        
    cpf_val = cpf.strip() if cpf else None
    if not cpf_val:
        cpf_val = None

    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO paciente (nome, data_nascimento, cpf, cartao_sus, telefone, email) 
                      VALUES (?, ?, ?, ?, ?, ?)""", (nome, data_nascimento, cpf_val, sus_val, telefone, email))
    conn.commit()
    conn.close()

def registrar_medida(paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura):
    """Insere uma nova medida no banco de dados."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO medida (paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura))
    conn.commit()
    conn.close()

def obter_medidas_paciente(paciente_id):
    """Retorna o histórico de medidas de um paciente específico."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_hora, peso, sistolica, diastolica, pulsacao, temperatura
        FROM medida
        WHERE paciente_id=?
    """, (paciente_id,))
    medidas = cursor.fetchall()
    conn.close()
    return medidas
