# ============================================================
#  ControloStock · Backend API (Flask + PostgreSQL)
#  Autor : Gonçalo Chapatica
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import hashlib
import secrets
import re
import os

app = Flask(__name__)
CORS(app)

_sessoes = {}


def db_connect():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "senha123"),
        dbname=os.environ.get("DB_NAME", "controlstock")
    )


def init_db():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizadores (
            id           SERIAL PRIMARY KEY,
            nome         VARCHAR(100) NOT NULL,
            username     VARCHAR(50)  NOT NULL UNIQUE,
            email        VARCHAR(100) NOT NULL UNIQUE,
            senha        VARCHAR(64)  NOT NULL,
            data_registo TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id           SERIAL PRIMARY KEY,
            nome         VARCHAR(100)  NOT NULL,
            categoria    VARCHAR(100)  NOT NULL,
            quantidade   INTEGER       NOT NULL DEFAULT 0,
            preco        NUMERIC(10,2) NOT NULL,
            data_registo TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        INSERT INTO utilizadores (nome, username, email, senha)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, ('Administrador', 'admin', 'admin@controlstock.mz',
          '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'))
    conn.commit()
    cursor.close()
    conn.close()


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def autenticado(req):
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    return token in _sessoes


def get_token(req):
    return req.headers.get("Authorization", "").replace("Bearer ", "")


@app.route("/auth/registo", methods=["POST"])
def registo():
    body     = request.get_json()
    nome     = body.get("nome",     "").strip()
    username = body.get("username", "").strip()
    email    = body.get("email",    "").strip()
    senha    = body.get("senha",    "")

    if not all([nome, username, email, senha]):
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400
    if len(senha) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres."}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"erro": "Endereço de email inválido."}), 400

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO utilizadores (nome, username, email, senha) VALUES (%s, %s, %s, %s)",
            (nome, username, email, sha256(senha))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Conta criada. Podes fazer login agora."}), 201
    except Exception as e:
        err = str(e)
        if "username" in err:
            return jsonify({"erro": "Este utilizador já existe."}), 409
        if "email" in err:
            return jsonify({"erro": "Este email já está registado."}), 409
        return jsonify({"erro": "Erro ao criar conta."}), 409


@app.route("/auth/login", methods=["POST"])
def login():
    body     = request.get_json()
    username = body.get("username", "").strip()
    senha    = body.get("senha",    "")

    if not username or not senha:
        return jsonify({"erro": "Preenche o utilizador e a senha."}), 400

    conn   = db_connect()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM utilizadores WHERE (username = %s OR email = %s) AND senha = %s",
        (username, username, sha256(senha))
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"erro": "Utilizador ou senha incorrectos."}), 401

    token = secrets.token_hex(32)
    _sessoes[token] = {"id": user["id"], "username": user["username"], "nome": user["nome"]}
    return jsonify({"token": token, "nome": user["nome"], "username": user["username"]})


@app.route("/auth/logout", methods=["POST"])
def logout():
    _sessoes.pop(get_token(request), None)
    return jsonify({"mensagem": "Sessão terminada."})


@app.route("/produtos", methods=["GET"])
def listar():
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401
    conn   = db_connect()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(p) for p in produtos])


@app.route("/produtos", methods=["POST"])
def criar():
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401
    body      = request.get_json()
    nome      = body.get("nome",      "").strip()
    categoria = body.get("categoria", "").strip()
    quantidade = body.get("quantidade")
    preco     = body.get("preco")

    if not nome or not categoria or quantidade is None or preco is None:
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

    conn   = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES (%s, %s, %s, %s) RETURNING id",
        (nome, categoria, quantidade, preco)
    )
    novo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Produto criado.", "id": novo_id}), 201


@app.route("/produtos/<int:pid>", methods=["PUT"])
def actualizar(pid):
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401
    body   = request.get_json()
    conn   = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET nome=%s, categoria=%s, quantidade=%s, preco=%s WHERE id=%s",
        (body.get("nome"), body.get("categoria"), body.get("quantidade"), body.get("preco"), pid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Produto actualizado."})


@app.route("/produtos/<int:pid>", methods=["DELETE"])
def eliminar(pid):
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401
    conn   = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Produto eliminado."})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
