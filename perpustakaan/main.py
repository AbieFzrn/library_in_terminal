#!/usr/bin/env python3
"""
📚 Sistem Perpustakaan CLI
Aplikasi manajemen perpustakaan berbasis terminal.

Login Admin Default:
  NIM     : admin
  Password: admin123
"""

from database import init_db
from auth import register, login
from admin import admin_menu
from user import user_menu
from display import show_menu, get_input, show_error, show_info, pause


def main():
    """Entry point aplikasi."""
    init_db()

    while True:
        options = [
            ("1", "Register"),
            ("2", "Login"),
            ("0", "Keluar"),
        ]
        show_menu("SISTEM PERPUSTAKAAN", options)

        choice = get_input("Pilih menu")

        if choice == "1":
            register()
            pause()

        elif choice == "2":
            current_user = login()
            if current_user:
                pause()
                if current_user["role"] == "admin":
                    admin_menu(current_user)
                else:
                    user_menu(current_user)
            else:
                pause()

        elif choice == "0":
            show_info("Terima kasih telah menggunakan Sistem Perpustakaan! 👋")
            break

        else:
            show_error("Menu tidak valid!")
            pause()


if __name__ == "__main__":
    main()
