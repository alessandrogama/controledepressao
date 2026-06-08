import sqlite3
import hashlib
import secrets

DB_NAME = "medidor.sqlite"

def hash_password(password: str) -> str:
    """Retorna o hash da senha gerado com PBKDF2-HMAC-SHA256 (seguro para MVP)."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256$100000${salt}${key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    try:
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = parts[2]
        stored_key = parts[3]
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return secrets.compare_digest(key.hex(), stored_key)
    except Exception:
        return False

def registrar_log_auditoria(usuario_id: int | None, username: str | None, role: str | None, evento: str, detalhes: str):
    """Grava um registro na trilha de auditoria de forma resiliente a falhas."""
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO log_auditoria (usuario_id, username, role, evento, detalhes)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, username, role, evento, detalhes))
        conn.commit()
    except Exception as e:
        print(f"[AUDIT TRAIL ERROR] Falha ao registrar log de auditoria ({evento}): {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def obter_logs_auditoria() -> list:
    """Retorna os 150 registros mais recentes da trilha de auditoria para o administrador."""
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data_hora, username, role, evento, detalhes
            FROM log_auditoria
            ORDER BY id DESC
            LIMIT 150
        """)
        logs = cursor.fetchall()
        conn.close()
        return logs
    except Exception as e:
        print(f"[AUDIT TRAIL ERROR] Falha ao recuperar logs de auditoria: {e}")
        return []

def autenticar_usuario(username, password) -> dict | None:
    """
    Autentica o usuário no banco de dados e retorna a sessão do usuário se bem-sucedido.
    Retorna None em caso de falha de credenciais.
    """
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM usuario WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_id, user_name, stored_hash, role = row
        if verify_password(password, stored_hash):
            session = {"id": user_id, "username": user_name, "role": role}
            registrar_log_auditoria(user_id, user_name, role, "LOGIN_SUCCESS", "Acesso autenticado com sucesso.")
            return session
        else:
            registrar_log_auditoria(user_id, user_name, role, "LOGIN_FAILURE", "Falha de login: senha incorreta.")
    else:
        registrar_log_auditoria(None, username, None, "LOGIN_FAILURE", "Tentativa de login com usuário inexistente.")
    return None

def obter_conexao():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas paciente, endereco, medida, usuario e log_auditoria caso não existam."""
    conn = obter_conexao()
    cursor = conn.cursor()

    # Cria a tabela usuario
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    # Cria a tabela log_auditoria
    cursor.execute('''CREATE TABLE IF NOT EXISTS log_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        username TEXT,
        role TEXT,
        evento TEXT NOT NULL,
        detalhes TEXT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
    )''')

    # Seed de usuários padrão (Apenas ambiente de desenvolvimento e testes)
    # AVISO: Substitua ou remova estas contas em ambientes de produção real para garantir a segurança.
    cursor.execute("SELECT COUNT(*) FROM usuario")
    if cursor.fetchone()[0] == 0:
        usuarios_seed = [
            ("admin", "admin", "administrador"),
            ("recepcionista1", "recepcionista", "recepcionista"),
            ("enfermeiro1", "enfermeiro", "enfermeiro"),
            ("medico1", "medico", "medico")
        ]
        for user, pwd, role in usuarios_seed:
            pwd_hash = hash_password(pwd)
            cursor.execute("INSERT INTO usuario (username, password_hash, role) VALUES (?, ?, ?)",
                           (user, pwd_hash, role))

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

def cadastrar_paciente(nome, data_nascimento, cpf, cartao_sus, telefone, email, operador_session=None):
    """Insere um novo paciente no banco de dados e registra a ação na auditoria."""
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
    
    # Obter ID gerado do paciente
    cursor.execute("SELECT last_insert_rowid()")
    paciente_id = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()

    if operador_session:
        registrar_log_auditoria(
            operador_session.get("id"),
            operador_session.get("username"),
            operador_session.get("role"),
            "PATIENT_CREATED",
            f"patient_id={paciente_id}"
        )

def registrar_medida(paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura, operador_session=None):
    """Insere uma nova medida no banco de dados e registra a ação na auditoria."""
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO medida (paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura))
    
    # Obter ID gerado da medida
    cursor.execute("SELECT last_insert_rowid()")
    medida_id = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()

    if operador_session:
        registrar_log_auditoria(
            operador_session.get("id"),
            operador_session.get("username"),
            operador_session.get("role"),
            "MEASUREMENT_RECORDED",
            f"measurement_id={medida_id}, patient_id={paciente_id}"
        )

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
