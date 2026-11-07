"""
User module — Menu & fungsi khusus user/mahasiswa (pinjam, kembalikan, history).
"""

from database import (
    get_all_books,
    search_books,
    borrow_book,
    return_book,
    get_user_borrowings,
    get_active_borrowings,
)
from display import (
    show_menu,
    show_books_table,
    show_borrowings_table,
    show_active_borrowings_table,
    get_input,
    get_int_input,
    show_success,
    show_error,
    show_info,
    pause,
)


def user_menu(user):
    """Loop menu utama user."""
    while True:
        options = [
            ("1", "Lihat Daftar Buku"),
            ("2", "Cari Buku"),
            ("3", "Pinjam Buku"),
            ("4", "Kembalikan Buku"),
            ("5", "History Peminjaman"),
            ("0", "Logout"),
        ]
        user_info = f"Halo, {user['nama']} (NIM: {user['nim']})! 👋"
        show_menu("MENU USER", options, user_info)

        choice = get_input("Pilih menu")

        if choice == "1":
            lihat_buku()
        elif choice == "2":
            cari_buku()
        elif choice == "3":
            pinjam_buku(user)
        elif choice == "4":
            kembalikan_buku(user)
        elif choice == "5":
            history_peminjaman(user)
        elif choice == "0":
            show_info("Logout berhasil.")
            pause()
            break
        else:
            show_error("Menu tidak valid!")
            pause()


def lihat_buku():
    """Tampilkan semua buku yang tersedia."""
    books = get_all_books()
    show_books_table(books, "📚 Daftar Buku Perpustakaan")
    pause()


def cari_buku():
    """Cari buku berdasarkan keyword."""
    keyword = get_input("Cari (judul/penulis/genre)")
    books = search_books(keyword)
    show_books_table(books, f"🔍 Hasil Pencarian: '{keyword}'")
    pause()


def pinjam_buku(user):
    """Proses peminjaman buku."""
    books = get_all_books()
    show_books_table(books, "📚 Pilih Buku untuk Dipinjam")

    if not books:
        pause()
        return

    book_id = get_int_input("\nMasukkan ID buku yang ingin dipinjam")
    success, message = borrow_book(user["id"], book_id)

    if success:
        show_success(message)
    else:
        show_error(message)
    pause()


def kembalikan_buku(user):
    """Proses pengembalian buku."""
    active = get_active_borrowings(user["id"])

    if not active:
        show_info("Tidak ada buku yang sedang dipinjam.")
        pause()
        return

    show_active_borrowings_table(active)

    borrowing_id = get_int_input("\nMasukkan ID Pinjam yang ingin dikembalikan")
    success, message = return_book(user["id"], borrowing_id)

    if success:
        show_success(message)
    else:
        show_error(message)
    pause()


def history_peminjaman(user):
    """Tampilkan history peminjaman user."""
    borrowings = get_user_borrowings(user["id"])
    show_borrowings_table(borrowings, "📋 History Peminjaman Kamu")
    pause()
