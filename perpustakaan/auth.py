"""
Auth module — Register & Login.
"""

from database import create_user, authenticate
from display import clear_screen, show_header, get_input, show_success, show_error


def register():
    """Proses registrasi akun baru."""
    clear_screen()
    show_header("📝 REGISTRASI AKUN BARU")

    nim = get_input("NIM")
    nama = get_input("Nama Lengkap")

    while True:
        password = get_input("Password")
        if len(password) < 4:
            show_error("Password minimal 4 karakter!")
            continue
        password2 = get_input("Konfirmasi Password")
        if password != password2:
            show_error("Password tidak cocok!")
            continue
        break

    success, message = create_user(nim, nama, password)
    if success:
        show_success(message)
    else:
        show_error(message)


def login():
    """Proses login. Return dict user jika berhasil, None jika gagal."""
    clear_screen()
    show_header("🔐 LOGIN")

    nim = get_input("NIM")
    password = get_input("Password")

    user = authenticate(nim, password)
    if user:
        show_success(f"Login berhasil! Selamat datang, {user['nama']}!")
        return user
    else:
        show_error("NIM atau password salah!")
        return None
