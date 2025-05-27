from flask import Flask, request, redirect, jsonify, abort
import sqlite3
import random
import string

app = Flask(__name__)
# DATABASE = "database.db"

# 🔌 Veritabanı bağlantı fonksiyonu
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
app.get_db_connection = get_db_connection

# 🔨 Veritabanını oluştur
def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()

# 🔑 Rastgele kısa kod üret
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# 🌐 Anasayfa
@app.route("/")
def home():
    return "URL Kısaltıcı API'ye Hoş Geldiniz!"

# 🔗 URL kısaltma endpoint'i
@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL alanı zorunludur."}), 400

    conn = app.get_db_connection()
    cursor = conn.cursor()

    # URL için eşsiz kısa kod üret
    while True:
        short_code = generate_short_code()
        cursor.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,))
        if cursor.fetchone() is None:
            break

    cursor.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code)
    )
    conn.commit()
    conn.close()

    return jsonify({"short_url": request.host_url + short_code})

# 🔁 Kısa URL ile yönlendirme
@app.route("/<string:short_code>")
def redirect_to_url(short_code):
    conn = app.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return redirect(row[0])
    else:
        abort(404)

# 🚀 Uygulamayı başlat
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

