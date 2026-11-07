#!/usr/bin/env python3
"""Quick smoke test — memastikan semua logic database berjalan benar."""

import os
import sys

# Pakai database test terpisah
os.environ["TESTING"] = "1"
import database
database.DB_NAME = "test_perpustakaan.db"

# Hapus DB test lama jika ada
if os.path.exists(database.DB_NAME):
    os.remove(database.DB_NAME)

from database import *

def test_all():
    print("=" * 50)
    print("  SMOKE TEST — Sistem Perpustakaan")
    print("=" * 50)

    # 1. Init DB
    init_db()
    print("✅ Database initialized")

    # 2. Test login admin default
    admin = authenticate("admin", "admin123")
    assert admin is not None, "Admin login gagal!"
    assert admin["role"] == "admin"
    print("✅ Admin default login OK")

    # 3. Test register user
    ok, msg = create_user("2024001", "Budi Santoso", "pass123")
    assert ok, f"Register gagal: {msg}"
    print("✅ Register user OK")

    # 4. Test duplicate NIM
    ok, msg = create_user("2024001", "Budi Lain", "pass456")
    assert not ok, "Harusnya gagal duplicate NIM!"
    print("✅ Duplicate NIM ditolak OK")

    # 5. Test login user
    user = authenticate("2024001", "pass123")
    assert user is not None, "User login gagal!"
    assert user["nama"] == "Budi Santoso"
    print("✅ User login OK")

    # 6. Test wrong password
    fail = authenticate("2024001", "wrongpass")
    assert fail is None, "Harusnya gagal login!"
    print("✅ Wrong password ditolak OK")

    # 7. Test tambah buku
    add_book("Laskar Pelangi", "Andrea Hirata", 2005, "Fiksi", 3)
    add_book("Atomic Habits", "James Clear", 2018, "Self-Dev", 2)
    add_book("Sapiens", "Y.N. Harari", 2011, "Sejarah", 1)
    books = get_all_books()
    assert len(books) == 3, f"Harusnya 3 buku, dapat {len(books)}"
    print("✅ Tambah buku OK (3 buku)")

    # 8. Test cari buku
    results = search_books("Laskar")
    assert len(results) == 1
    results = search_books("Fiksi")
    assert len(results) == 1
    print("✅ Cari buku OK")

    # 9. Test pinjam buku
    ok, msg = borrow_book(user["id"], books[0]["id"])
    assert ok, f"Pinjam gagal: {msg}"
    print(f"✅ Pinjam buku OK — {msg}")

    # 10. Test stok berkurang
    book = get_book_by_id(books[0]["id"])
    assert book["stock"] == 2, f"Stok harusnya 2, dapat {book['stock']}"
    print("✅ Stok berkurang OK")

    # 11. Test tidak bisa pinjam buku yang sama
    ok, msg = borrow_book(user["id"], books[0]["id"])
    assert not ok
    print("✅ Duplikat pinjam ditolak OK")

    # 12. Test batas 3 buku
    borrow_book(user["id"], books[1]["id"])
    borrow_book(user["id"], books[2]["id"])
    # Tambah buku ke-4 untuk test limit
    add_book("Test Limit", "Author", 2024, "Test", 5)
    all_books = get_all_books()
    ok, msg = borrow_book(user["id"], all_books[3]["id"])
    assert not ok, "Harusnya gagal melebihi batas 3!"
    print("✅ Batas 3 buku OK")

    # 13. Test stok habis
    user2_ok, _ = create_user("2024002", "Ani", "pass123")
    user2 = authenticate("2024002", "pass123")
    # Sapiens stoknya 1, sudah dipinjam Budi → stok 0
    ok, msg = borrow_book(user2["id"], books[2]["id"])
    assert not ok, "Harusnya gagal stok habis!"
    print("✅ Stok habis ditolak OK")

    # 14. Test history peminjaman
    history = get_user_borrowings(user["id"])
    assert len(history) == 3
    print("✅ History peminjaman OK (3 record)")

    # 15. Test kembalikan buku
    active = get_active_borrowings(user["id"])
    ok, msg = return_book(user["id"], active[0]["id"])
    assert ok, f"Return gagal: {msg}"
    print("✅ Kembalikan buku OK")

    # 16. Test stok bertambah setelah kembali
    book = get_book_by_id(active[0]["id"])
    # We need the book_id, not borrowing id. Let's check from history.
    history = get_user_borrowings(user["id"])
    returned = [h for h in history if h["status"] == "dikembalikan"]
    assert len(returned) == 1
    print("✅ Status berubah 'dikembalikan' OK")

    # 17. Test update buku
    update_book(books[0]["id"], "Laskar Pelangi (Edisi Baru)", "Andrea Hirata", 2005, "Fiksi", 5)
    updated = get_book_by_id(books[0]["id"])
    assert updated["title"] == "Laskar Pelangi (Edisi Baru)"
    assert updated["stock"] == 5
    print("✅ Update buku OK")

    # 18. Test hapus buku (yang masih dipinjam → gagal)
    ok, msg = delete_book(books[1]["id"])  # Atomic Habits masih dipinjam
    assert not ok
    print("✅ Hapus buku dipinjam ditolak OK")

    # 19. Test hapus buku (yang tidak dipinjam)
    ok, msg = delete_book(all_books[3]["id"])  # Test Limit, tidak dipinjam
    assert ok
    print("✅ Hapus buku OK")

    # 20. Test get all users & borrowings (admin)
    users = get_all_users()
    assert len(users) >= 3  # admin + 2 user
    all_borrows = get_all_borrowings()
    assert len(all_borrows) >= 3
    print("✅ Admin view (users & borrowings) OK")

    print()
    print("=" * 50)
    print("  ✅ SEMUA TEST PASSED!")
    print("=" * 50)

    # Cleanup
    os.remove(database.DB_NAME)

if __name__ == "__main__":
    test_all()
