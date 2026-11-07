"""
Database module — Setup SQLite, semua operasi CRUD.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_NAME = "perpustakaan.db"


def get_connection():
    """Buat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    """Hash password menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Inisialisasi tabel dan seed akun admin default."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            stock INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_date DATETIME NOT NULL,
            return_date DATETIME,
            status TEXT NOT NULL DEFAULT 'dipinjam',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    # Seed akun admin default (NIM: admin, Password: admin123)
    admin_pw = hash_password("admin123")
    c.execute(
        "INSERT OR IGNORE INTO users (nim, nama, password, role) VALUES (?, ?, ?, ?)",
        ("admin", "Administrator", admin_pw, "admin"),
    )

    conn.commit()
    conn.close()


# =====================================================================
#  USER OPERATIONS
# =====================================================================

def create_user(nim, nama, password, role="user"):
    """Register user baru. Return (success, message)."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (nim, nama, password, role) VALUES (?, ?, ?, ?)",
            (nim, nama, hash_password(password), role),
        )
        conn.commit()
        return True, "Registrasi berhasil!"
    except sqlite3.IntegrityError:
        return False, "NIM sudah terdaftar!"
    finally:
        conn.close()


def authenticate(nim, password):
    """Login user. Return dict user jika berhasil, None jika gagal."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE nim = ? AND password = ?",
        (nim, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users():
    """Ambil semua user (tanpa password)."""
    conn = get_connection()
    users = conn.execute(
        "SELECT id, nim, nama, role, created_at FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]


# =====================================================================
#  BOOK OPERATIONS
# =====================================================================

def add_book(title, author, year, genre, stock):
    """Tambah buku baru."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO books (title, author, year, genre, stock) VALUES (?, ?, ?, ?, ?)",
        (title, author, year, genre, stock),
    )
    conn.commit()
    conn.close()


def get_all_books():
    """Ambil semua buku."""
    conn = get_connection()
    books = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
    conn.close()
    return [dict(b) for b in books]


def get_book_by_id(book_id):
    """Ambil buku berdasarkan ID."""
    conn = get_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return dict(book) if book else None


def search_books(keyword):
    """Cari buku berdasarkan judul, penulis, atau genre."""
    conn = get_connection()
    pattern = f"%{keyword}%"
    books = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?",
        (pattern, pattern, pattern),
    ).fetchall()
    conn.close()
    return [dict(b) for b in books]


def update_book(book_id, title, author, year, genre, stock):
    """Update informasi buku."""
    conn = get_connection()
    conn.execute(
        "UPDATE books SET title=?, author=?, year=?, genre=?, stock=? WHERE id=?",
        (title, author, year, genre, stock, book_id),
    )
    conn.commit()
    conn.close()


def delete_book(book_id):
    """Hapus buku. Gagal jika masih ada peminjaman aktif. Return (success, message)."""
    conn = get_connection()
    active = conn.execute(
        "SELECT COUNT(*) FROM borrowings WHERE book_id = ? AND status = 'dipinjam'",
        (book_id,),
    ).fetchone()[0]

    if active > 0:
        conn.close()
        return False, "Buku tidak bisa dihapus, masih ada peminjaman aktif!"

    conn.execute("DELETE FROM borrowings WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, "Buku berhasil dihapus!"


# =====================================================================
#  BORROWING OPERATIONS
# =====================================================================

def borrow_book(user_id, book_id):
    """Pinjam buku. Maks 3 buku, deadline 7 hari. Return (success, message)."""
    conn = get_connection()

    # Cek jumlah peminjaman aktif
    active_count = conn.execute(
        "SELECT COUNT(*) FROM borrowings WHERE user_id = ? AND status = 'dipinjam'",
        (user_id,),
    ).fetchone()[0]
    if active_count >= 3:
        conn.close()
        return False, "Sudah mencapai batas maksimal peminjaman (3 buku)!"

    # Cek apakah sudah meminjam buku yang sama
    already = conn.execute(
        "SELECT COUNT(*) FROM borrowings WHERE user_id = ? AND book_id = ? AND status = 'dipinjam'",
        (user_id, book_id),
    ).fetchone()[0]
    if already > 0:
        conn.close()
        return False, "Kamu sudah meminjam buku ini!"

    # Cek stok
    book = conn.execute("SELECT title, stock FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        return False, "Buku tidak ditemukan!"
    if book["stock"] <= 0:
        conn.close()
        return False, "Stok buku habis!"

    # Proses peminjaman
    due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO borrowings (user_id, book_id, due_date) VALUES (?, ?, ?)",
        (user_id, book_id, due_date),
    )
    conn.execute("UPDATE books SET stock = stock - 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, f"Buku '{book['title']}' berhasil dipinjam! Batas kembali: {due_date[:10]}"


def return_book(user_id, borrowing_id):
    """Kembalikan buku. Return (success, message)."""
    conn = get_connection()

    borrowing = conn.execute(
        "SELECT * FROM borrowings WHERE id = ? AND user_id = ? AND status = 'dipinjam'",
        (borrowing_id, user_id),
    ).fetchone()

    if not borrowing:
        conn.close()
        return False, "Data peminjaman tidak ditemukan!"

    return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE borrowings SET status = 'dikembalikan', return_date = ? WHERE id = ?",
        (return_date, borrowing_id),
    )
    conn.execute(
        "UPDATE books SET stock = stock + 1 WHERE id = ?", (borrowing["book_id"],)
    )
    conn.commit()
    conn.close()
    return True, "Buku berhasil dikembalikan!"


def get_user_borrowings(user_id):
    """Ambil semua history peminjaman user."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT b.id, bk.title, bk.author,
               b.borrow_date, b.due_date, b.return_date, b.status
        FROM borrowings b
        JOIN books bk ON b.book_id = bk.id
        WHERE b.user_id = ?
        ORDER BY b.borrow_date DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_borrowings(user_id):
    """Ambil peminjaman aktif user (belum dikembalikan)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT b.id, bk.title, b.borrow_date, b.due_date
        FROM borrowings b
        JOIN books bk ON b.book_id = bk.id
        WHERE b.user_id = ? AND b.status = 'dipinjam'
        ORDER BY b.borrow_date DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_borrowings():
    """Ambil semua data peminjaman (admin view)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT b.id, u.nim, u.nama, bk.title,
               b.borrow_date, b.due_date, b.return_date, b.status
        FROM borrowings b
        JOIN users u ON b.user_id = u.id
        JOIN books bk ON b.book_id = bk.id
        ORDER BY b.borrow_date DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
