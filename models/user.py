import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_connection


class User:
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get_by_email(email):
        conn = get_connection()
        try:
            row = conn.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                return User(row['id'], row['email'], row['password_hash'])
            return None
        finally:
            conn.close()

    @staticmethod
    def create(email, password):
        password_hash = generate_password_hash(password)
        conn = get_connection()
        try:
            conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
            conn.commit()
        except Exception:
            return None
        finally:
            conn.close()
        return User.get_by_email(email)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)