import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "database/faketrace.db"

def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class User:
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get_by_email(email):
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if row:
            return User(*row)
        return None

    @staticmethod
    def create(email, password):
        password_hash = generate_password_hash(password)
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
            conn.commit()
        except Exception as e:
            conn.close()
            return None
        user = User.get_by_email(email)
        return user

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

if __name__ == "__main__":
    create_users_table()
    print("users tablosu oluşturuldu veya zaten mevcut.")