# ============================================================
#  ControloStock · Backend API (Flask + MySQL)
#  Autor : Gonçalo Chapatica
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import hashlib
import secrets
import re
import os

app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return jsonify({
        "mensagem": "ControlStock Backend Online",
        "status": "OK"
    })
# Sessões activas: { token: { id, username, nome } }
_sessoes = {}


# ----------------------------------------------------------
# BASE DE DADOS
# ----------------------------------------------------------

def db_connect():
    """Cria e retorna uma ligação à base de dados MySQL."""
    return mysql.connector.connect(
        host     = os.environ.get("DB_HOST",     "db"),
        user     = os.environ.get("DB_USER",     "root"),
        password = os.environ.get("DB_PASSWORD", "senha123"),
        database = os.environ.get("DB_NAME",     "controlstock")
    )


# ----------------------------------------------------------
# UTILITÁRIOS
# ----------------------------------------------------------

def sha256(text):
    """Retorna o hash SHA-256 de uma string."""
    return hashlib.sha256(text.encode()).hexdigest()


def autenticado(req):
    """Verifica se o pedido contém um token de sessão válido."""
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    return token in _sessoes


def get_token(req):
    """Extrai o token do cabeçalho Authorization."""
    return req.headers.get("Authorization", "").replace("Bearer ", "")


# ----------------------------------------------------------
# AUTENTICAÇÃO
# ----------------------------------------------------------

@app.route("/auth/registo", methods=["POST"])
def registo():
    """Cria uma nova conta de utilizador."""
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
        conn   = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO utilizadores (nome, username, email, senha) VALUES (%s, %s, %s, %s)",
            (nome, username, email, sha256(senha))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Conta criada. Podes fazer login agora."}), 201

    except mysql.connector.IntegrityError as err:
        campo = "utilizador" if "username" in str(err) else "email"
        return jsonify({"erro": f"Este {campo} já está registado."}), 409


@app.route("/auth/login", methods=["POST"])
def login():
    """Autentica um utilizador e retorna um token de sessão."""
    body     = request.get_json()
    username = body.get("username", "").strip()
    senha    = body.get("senha",    "")

    if not username or not senha:
        return jsonify({"erro": "Preenche o utilizador e a senha."}), 400

    conn   = db_connect()
    cursor = conn.cursor(dictionary=True)
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
    """Termina a sessão do utilizador."""
    _sessoes.pop(get_token(request), None)
    return jsonify({"mensagem": "Sessão terminada."})


# ----------------------------------------------------------
# PRODUTOS — CRUD
# ----------------------------------------------------------

@app.route("/produtos", methods=["GET"])
def listar():
    """Retorna todos os produtos ordenados por id descendente."""
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401

    conn   = db_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(produtos)


@app.route("/produtos", methods=["POST"])
def criar():
    """Insere um novo produto na base de dados."""
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
        "INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES (%s, %s, %s, %s)",
        (nome, categoria, quantidade, preco)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Produto criado.", "id": novo_id}), 201


@app.route("/produtos/<int:pid>", methods=["PUT"])
def actualizar(pid):
    """Actualiza os dados de um produto existente."""
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
    """Remove um produto da base de dados."""
    if not autenticado(request):
        return jsonify({"erro": "Não autorizado."}), 401

    conn   = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Produto eliminado."})


# ----------------------------------------------------------
# ENTRADA
# ----------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
