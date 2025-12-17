"""
FakeTrace - Veritabanı İşlemleri
"""

import sqlite3
from datetime import datetime, timedelta
import os

# Veritabanı dosyasının yolu
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'faketrace.db')

# Ensure the database directory exists so sqlite can create the file there
DB_DIR = os.path.dirname(DATABASE_PATH)
if not os.path.exists(DB_DIR):
    try:
        os.makedirs(DB_DIR, exist_ok=True)
    except Exception:
        # Best-effort: if we cannot create the directory, let sqlite3 raise later
        pass


def get_connection():
    """Veritabanına bağlantı oluşturur"""
    # Ensure folder exists at connect time (extra safety for deployments)
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Veritabanı tablolarını oluşturur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ana içerik tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content_type TEXT NOT NULL,
            original_url TEXT,
            original_text TEXT,
            title TEXT,
            text_hash TEXT,
            image_path TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            reliability_score REAL DEFAULT 0,
            is_fake INTEGER DEFAULT 0
        )
    ''')
    
    # Analiz sonuçları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            score REAL,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES contents(id)
        )
    ''')
    
    # Yayılma noktaları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spread_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            found_url TEXT NOT NULL,
            source_name TEXT,
            country_code TEXT,
            latitude REAL,
            longitude REAL,
            found_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            similarity_score REAL,
            FOREIGN KEY (content_id) REFERENCES contents(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    # Avoid printing non-ASCII characters here to prevent encoding errors on some consoles
    print("Veritabanı hazır!")


def add_content(user_id, content_type, original_url=None, original_text=None, title=None, 
                text_hash=None, image_path=None, reliability_score=0, is_fake=0):
    """Yeni içerik ekler"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contents 
        (user_id, content_type, original_url, original_text, title, text_hash, image_path, reliability_score, is_fake)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, content_type, original_url, original_text, title, text_hash, image_path, reliability_score, is_fake))
    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return content_id
def get_contents_by_user_id(user_id):
    """Belirli bir kullanıcıya ait içerikleri getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contents WHERE user_id = ? ORDER BY submitted_at DESC', (user_id,))
    contents = [dict(row) for row in cursor.fetchall()]
    # Tarihleri +3 saat olarak göster
    for c in contents:
        submitted = c.get('submitted_at')
        if submitted:
            try:
                dt = datetime.strptime(submitted, '%Y-%m-%d %H:%M:%S')
                dt = dt + timedelta(hours=3)
                c['submitted_at'] = dt.strftime('%d.%m.%Y %H:%M')
            except Exception:
                pass
    conn.close()
    return contents


def add_analysis_result(content_id, analysis_type, score, details):
    """Analiz sonucu ekler"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor. execute('''
        INSERT INTO analysis_results (content_id, analysis_type, score, details)
        VALUES (?, ?, ?, ?)
    ''', (content_id, analysis_type, score, details))
    
    conn.commit()
    conn.close()


def add_spread_point(content_id, found_url, source_name=None, country_code=None,
                     latitude=None, longitude=None, similarity_score=None):
    """Yayılma noktası ekler"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO spread_points 
        (content_id, found_url, source_name, country_code, latitude, longitude, similarity_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (content_id, found_url, source_name, country_code, latitude, longitude, similarity_score))
    
    point_id = cursor. lastrowid
    conn.commit()
    conn.close()
    
    return point_id


def get_content_by_id(content_id):
    """ID'ye göre içerik getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor. execute('SELECT * FROM contents WHERE id = ? ', (content_id,))
    content = cursor.fetchone()
    
    conn.close()
    return dict(content) if content else None


def get_analysis_results(content_id):
    """Bir içeriğin analiz sonuçlarını getirir"""
    conn = get_connection()
    cursor = conn. cursor()
    
    cursor.execute('SELECT * FROM analysis_results WHERE content_id = ?', (content_id,))
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results


def get_spread_points(content_id):
    """Bir içeriğin yayılma noktalarını getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM spread_points WHERE content_id = ?  ORDER BY found_at', (content_id,))
    points = [dict(row) for row in cursor. fetchall()]
    
    conn.close()
    return points


def get_all_contents():
    """Tüm içerikleri getirir"""
    conn = get_connection()
    cursor = conn. cursor()
    
    cursor.execute('SELECT * FROM contents ORDER BY submitted_at DESC')
    contents = [dict(row) for row in cursor.fetchall()]
    # Tarihleri +3 saat olarak göster
    for c in contents:
        submitted = c.get('submitted_at')
        if submitted:
            try:
                dt = datetime.strptime(submitted, '%Y-%m-%d %H:%M:%S')
                dt = dt + timedelta(hours=3)
                c['submitted_at'] = dt.strftime('%d.%m.%Y %H:%M')
            except Exception:
                pass
    
    conn.close()
    return contents


def update_content_score(content_id, reliability_score, is_fake):
    """İçerik skorunu günceller"""
    conn = get_connection()
    cursor = conn. cursor()
    
    cursor.execute('''
        UPDATE contents 
        SET reliability_score = ?, is_fake = ? 
        WHERE id = ?
    ''', (reliability_score, is_fake, content_id))
    
    conn.commit()
    conn.close()