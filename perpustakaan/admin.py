"""
Admin module — Menu & fungsi khusus admin (CRUD buku, data peminjaman, data user).
"""

from database import (
    get_all_books,
    get_book_by_id,
    add_book,
    update_book,
    delete_book,
    get_all_borrowings,
    get_all_users,
)
from display import (
    show_menu,
    show_books_table,
    show_users_table,
    show_borrowings_table,
    get_input,
    get_int_input,
    show_success,
    show_error,
    show_info,
    pause,
)


def admin_menu(user):
    """Loop menu utama admin."""
    while True:
        options = [
            ("1", "Tambah Buku"),
            ("2", "Lihat Semua Buku"),
            ("3", "Update Buku"),
            ("4", "Hapus Buku"),
            ("5", "Data Peminjaman"),
            ("6", "Data User"),
            ("0", "Logout"),
        ]
        show_menu("MENU ADMIN", options, f"Halo, {user['nama']}! 👋")

        choice = get_input("Pilih menu")

        if choice == "1":
            tambah_buku()
        elif choice == "2":
            lihat_buku()
        elif choice == "3":
            update_buku_menu()
        elif choice == "4":
            hapus_buku_menu()
        elif choice == "5":
            data_peminjaman()
        elif choice == "6":
            data_user()
        elif choice == "0":
            show_info("Logout berhasil.")
            pause()
            break
        else:
            show_error("Menu tidak valid!")
            pause()


def tambah_buku():
    """Tambah buku baru ke perpustakaan."""
    show_info("Masukkan data buku baru:")
    title = get_input("  Judul")
    author = get_input("  Penulis")
    year = get_int_input("  Tahun Terbit", min_val=1000, max_val=2030)
    genre = get_input("  Genre")
    stock = get_int_input("  Jumlah Stok", min_val=1)

    add_book(title, author, year, genre, stock)
    show_success(f"Buku '{title}' berhasil ditambahkan!")
    pause()


def lihat_buku():
    """Tampilkan semua buku."""
    books = get_all_books()
    show_books_table(books)
    pause()


def update_buku_menu():
    """Update informasi buku."""
    books = get_all_books()
    show_books_table(books)

    if not books:
        pause()
        return

    book_id = get_int_input("\nMasukkan ID buku yang ingin diupdate")
    book = get_book_by_id(book_id)

    if not book:
        show_error("Buku tidak ditemukan!")
        pause()
        return

    show_info(f"Update buku: '{book['title']}' — kosongkan jika tidak diubah\n")

    title = get_input(f"  Judul [{book['title']}]", required=False) or book["title"]
    author = get_input(f"  Penulis [{book['author']}]", required=False) or book["author"]
    year_input = get_input(f"  Tahun [{book['year']}]", required=False)
    year = int(year_input) if year_input else book["year"]
    genre = get_input(f"  Genre [{book['genre']}]", required=False) or book["genre"]
    stock_input = get_input(f"  Stok [{book['stock']}]", required=False)
    stock = int(stock_input) if stock_input else book["stock"]

    update_book(book_id, title, author, year, genre, stock)
    show_success("Buku berhasil diupdate!")
    pause()


def hapus_buku_menu():
    """Hapus buku dari perpustakaan."""
    books = get_all_books()
    show_books_table(books)

    if not books:
        pause()
        return

    book_id = get_int_input("\nMasukkan ID buku yang ingin dihapus")
    book = get_book_by_id(book_id)

    if not book:
        show_error("Buku tidak ditemukan!")
        pause()
        return

    confirm = get_input(f"  Yakin hapus '{book['title']}'? (y/n)")
    if confirm.lower() == "y":
        success, message = delete_book(book_id)
        if success:
            show_success(message)
        else:
            show_error(message)
    else:
        show_info("Batal menghapus.")
    pause()


def data_peminjaman():
    """Tampilkan semua data peminjaman."""
    borrowings = get_all_borrowings()
    show_borrowings_table(borrowings, "📋 Data Semua Peminjaman")
    pause()


def data_user():
    """Tampilkan semua data user terdaftar."""
    users = get_all_users()
    show_users_table(users)
    pause()
