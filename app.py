from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-super-secreta"  # TROQUE POR UMA SEGURA!

# ---------------------------
# Função auxiliar do banco
# ---------------------------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# Criar tabela se não existir
# ---------------------------
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Rota: Página inicial (login)
# ---------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------------------
# Rota: Registro
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        hashed_pw = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, hashed_pw))
            conn.commit()
            flash("Conta criada com sucesso! Faça login.", "success")
            return redirect(url_for("login"))
        except:
            flash("Nome de usuário já existe!", "danger")
        finally:
            conn.close()

    return render_template("register.html")

# ---------------------------
# Rota: Login
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", 
                            (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Login realizado!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos!", "danger")

    return render_template("login.html")

# ---------------------------
# Rota: Dashboard (protegida)
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Faça login para acessar o painel.", "warning")
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["username"])

# ---------------------------
# Logout
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta!", "info")
    return redirect(url_for("login"))

# ---------------------------
# Rodar servidor
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)

