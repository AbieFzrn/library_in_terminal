"""
Database module — Semua operasi CRUD menggunakan file JSON (tanpa database).
"""

import json
import hashlib
import os
from datetime import datetime, timedelta

# =====================================================================
#  FILE PATHS
# =====================================================================

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
BORROWINGS_FILE = os.path.join(DATA_DIR, "borrowings.json")


# =====================================================================
#  JSON HELPERS
# =====================================================================

def _read(filepath):
    """Baca data dari file JSON. Return list kosong jika file belum ada."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(filepath, data):
    """Tulis data ke file JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _next_id(records):
    """Generate ID auto-increment dari list records."""
    if not records:
        return 1
    return max(r["id"] for r in records) + 1


# =====================================================================
#  UTILITY
# =====================================================================

def hash_password(password):
    """Hash password menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================================
#  INIT
# =====================================================================

def init_db():
    """Inisialisasi file data dan seed akun admin default."""
    # Buat file JSON jika belum ada
    for filepath in (USERS_FILE, BOOKS_FILE, BORROWINGS_FILE):
        if not os.path.exists(filepath):
            _write(filepath, [])

    # Seed akun admin default (NIM: admin, Password: admin123)
    users = _read(USERS_FILE)
    if not any(u["nim"] == "admin" for u in users):
        users.append({
            "id": _next_id(users),
            "nim": "admin",
            "nama": "Administrator",
            "password": hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        _write(USERS_FILE, users)


# =====================================================================
#  USER OPERATIONS
# =====================================================================

def create_user(nim, nama, password, role="user"):
    """Register user baru. Return (success, message)."""
    users = _read(USERS_FILE)
    if any(u["nim"] == nim for u in users):
        return False, "NIM sudah terdaftar!"

    users.append({
        "id": _next_id(users),
        "nim": nim,
        "nama": nama,
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    _write(USERS_FILE, users)
    return True, "Registrasi berhasil!"


def authenticate(nim, password):
    """Login user. Return dict user jika berhasil, None jika gagal."""
    users = _read(USERS_FILE)
    hashed = hash_password(password)
    for u in users:
        if u["nim"] == nim and u["password"] == hashed:
            return u
    return None


def get_all_users():
    """Ambil semua user (tanpa password)."""
    users = _read(USERS_FILE)
    return [
        {k: v for k, v in u.items() if k != "password"}
        for u in users
    ]


# =====================================================================
#  BOOK OPERATIONS
# =====================================================================

def add_book(title, author, year, genre, stock):
    """Tambah buku baru."""
    books = _read(BOOKS_FILE)
    books.append({
        "id": _next_id(books),
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "stock": stock,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    _write(BOOKS_FILE, books)


def get_all_books():
    """Ambil semua buku."""
    return _read(BOOKS_FILE)


def get_book_by_id(book_id):
    """Ambil buku berdasarkan ID."""
    books = _read(BOOKS_FILE)
    for b in books:
        if b["id"] == book_id:
            return b
    return None


def search_books(keyword):
    """Cari buku berdasarkan judul, penulis, atau genre."""
    kw = keyword.lower()
    books = _read(BOOKS_FILE)
    return [
        b for b in books
        if kw in (b.get("title") or "").lower()
        or kw in (b.get("author") or "").lower()
        or kw in (b.get("genre") or "").lower()
    ]


def update_book(book_id, title, author, year, genre, stock):
    """Update informasi buku."""
    books = _read(BOOKS_FILE)
    for b in books:
        if b["id"] == book_id:
            b["title"] = title
            b["author"] = author
            b["year"] = year
            b["genre"] = genre
            b["stock"] = stock
            break
    _write(BOOKS_FILE, books)


def delete_book(book_id):
    """Hapus buku. Gagal jika masih ada peminjaman aktif. Return (success, message)."""
    borrowings = _read(BORROWINGS_FILE)
    active = [
        br for br in borrowings
        if br["book_id"] == book_id and br["status"] == "dipinjam"
    ]
    if active:
        return False, "Buku tidak bisa dihapus, masih ada peminjaman aktif!"

    books = _read(BOOKS_FILE)
    new_books = [b for b in books if b["id"] != book_id]
    # Hapus juga history peminjaman buku ini
    new_borrowings = [br for br in borrowings if br["book_id"] != book_id]
    _write(BOOKS_FILE, new_books)
    _write(BORROWINGS_FILE, new_borrowings)
    return True, "Buku berhasil dihapus!"


# =====================================================================
#  BORROWING OPERATIONS
# =====================================================================

def borrow_book(user_id, book_id):
    """Pinjam buku. Maks 3 buku, deadline 7 hari. Return (success, message)."""
    borrowings = _read(BORROWINGS_FILE)

    # Cek jumlah peminjaman aktif
    active_count = sum(
        1 for br in borrowings
        if br["user_id"] == user_id and br["status"] == "dipinjam"
    )
    if active_count >= 3:
        return False, "Sudah mencapai batas maksimal peminjaman (3 buku)!"

    # Cek apakah sudah meminjam buku yang sama
    already = any(
        br for br in borrowings
        if br["user_id"] == user_id and br["book_id"] == book_id and br["status"] == "dipinjam"
    )
    if already:
        return False, "Kamu sudah meminjam buku ini!"

    # Cek stok
    books = _read(BOOKS_FILE)
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return False, "Buku tidak ditemukan!"
    if book["stock"] <= 0:
        return False, "Stok buku habis!"

    # Proses peminjaman
    due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    borrowings.append({
        "id": _next_id(borrowings),
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": borrow_date,
        "due_date": due_date,
        "return_date": None,
        "status": "dipinjam",
    })

    # Kurangi stok
    for b in books:
        if b["id"] == book_id:
            b["stock"] -= 1
            break

    _write(BORROWINGS_FILE, borrowings)
    _write(BOOKS_FILE, books)
    return True, f"Buku '{book['title']}' berhasil dipinjam! Batas kembali: {due_date[:10]}"


def return_book(user_id, borrowing_id):
    """Kembalikan buku. Return (success, message)."""
    borrowings = _read(BORROWINGS_FILE)
    borrowing = next(
        (br for br in borrowings
         if br["id"] == borrowing_id and br["user_id"] == user_id and br["status"] == "dipinjam"),
        None,
    )
    if not borrowing:
        return False, "Data peminjaman tidak ditemukan!"

    return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    borrowing["status"] = "dikembalikan"
    borrowing["return_date"] = return_date

    # Tambah stok kembali
    books = _read(BOOKS_FILE)
    for b in books:
        if b["id"] == borrowing["book_id"]:
            b["stock"] += 1
            break

    _write(BORROWINGS_FILE, borrowings)
    _write(BOOKS_FILE, books)
    return True, "Buku berhasil dikembalikan!"


def get_user_borrowings(user_id):
    """Ambil semua history peminjaman user."""
    borrowings = _read(BORROWINGS_FILE)
    books = {b["id"]: b for b in _read(BOOKS_FILE)}
    result = []
    for br in borrowings:
        if br["user_id"] != user_id:
            continue
        book = books.get(br["book_id"], {})
        result.append({
            "id": br["id"],
            "title": book.get("title", "?"),
            "author": book.get("author", "?"),
            "borrow_date": br["borrow_date"],
            "due_date": br["due_date"],
            "return_date": br["return_date"],
            "status": br["status"],
        })
    # Urutkan: terbaru dulu
    result.sort(key=lambda x: x["borrow_date"], reverse=True)
    return result


def get_active_borrowings(user_id):
    """Ambil peminjaman aktif user (belum dikembalikan)."""
    borrowings = _read(BORROWINGS_FILE)
    books = {b["id"]: b for b in _read(BOOKS_FILE)}
    result = []
    for br in borrowings:
        if br["user_id"] != user_id or br["status"] != "dipinjam":
            continue
        book = books.get(br["book_id"], {})
        result.append({
            "id": br["id"],
            "title": book.get("title", "?"),
            "borrow_date": br["borrow_date"],
            "due_date": br["due_date"],
        })
    result.sort(key=lambda x: x["borrow_date"], reverse=True)
    return result


def get_all_borrowings():
    """Ambil semua data peminjaman (admin view)."""
    borrowings = _read(BORROWINGS_FILE)
    users = {u["id"]: u for u in _read(USERS_FILE)}
    books = {b["id"]: b for b in _read(BOOKS_FILE)}
    result = []
    for br in borrowings:
        user = users.get(br["user_id"], {})
        book = books.get(br["book_id"], {})
        result.append({
            "id": br["id"],
            "nim": user.get("nim", "?"),
            "nama": user.get("nama", "?"),
            "title": book.get("title", "?"),
            "borrow_date": br["borrow_date"],
            "due_date": br["due_date"],
            "return_date": br["return_date"],
            "status": br["status"],
        })
    result.sort(key=lambda x: x["borrow_date"], reverse=True)
    return result
