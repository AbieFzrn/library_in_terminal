"""
Display module — Semua tampilan CLI menggunakan Rich.
"""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


def clear_screen():
    """Bersihkan layar terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def show_header(title):
    """Tampilkan header panel."""
    console.print()
    console.print(
        Panel(
            Text(title, justify="center", style="bold white"),
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


def show_menu(title, options, user_info=None):
    """Tampilkan menu utama dengan opsi."""
    clear_screen()
    header_text = f"📚 {title}"
    if user_info:
        header_text += f"\n{user_info}"
    show_header(header_text)

    for key, label in options:
        if key == "0":
            console.print(f"  [red]{key}[/red]. {label}")
        else:
            console.print(f"  [cyan]{key}[/cyan]. {label}")
    console.print()


# =====================================================================
#  INPUT HELPERS
# =====================================================================

def get_input(prompt, required=True):
    """Ambil input dari user. Ulangi jika required dan kosong."""
    while True:
        value = console.input(f"[yellow]{prompt}[/yellow]: ").strip()
        if value or not required:
            return value
        console.print("[red]  Input tidak boleh kosong![/red]")


def get_int_input(prompt, min_val=None, max_val=None):
    """Ambil input integer dengan validasi range."""
    while True:
        value = get_input(prompt)
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                console.print(f"[red]  Nilai minimal {min_val}![/red]")
                continue
            if max_val is not None and num > max_val:
                console.print(f"[red]  Nilai maksimal {max_val}![/red]")
                continue
            return num
        except ValueError:
            console.print("[red]  Masukkan angka yang valid![/red]")


# =====================================================================
#  MESSAGE HELPERS
# =====================================================================

def show_success(message):
    console.print(f"\n[green]  ✅ {message}[/green]")


def show_error(message):
    console.print(f"\n[red]  ❌ {message}[/red]")


def show_info(message):
    console.print(f"\n[cyan]  ℹ️  {message}[/cyan]")


def pause():
    """Tunggu user tekan Enter."""
    console.input("\n[dim]  Tekan Enter untuk melanjutkan...[/dim]")


# =====================================================================
#  TABLE DISPLAYS
# =====================================================================

def show_books_table(books, title="Daftar Buku"):
    """Tampilkan tabel daftar buku."""
    if not books:
        show_info("Tidak ada buku.")
        return

    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="cyan", justify="center", width=5)
    table.add_column("Judul", style="white", min_width=20)
    table.add_column("Penulis", style="white", min_width=15)
    table.add_column("Tahun", justify="center", width=6)
    table.add_column("Genre", style="magenta", width=12)
    table.add_column("Stok", justify="center", width=6)

    for b in books:
        stock_style = "green" if b["stock"] > 0 else "red bold"
        stock_text = f"[{stock_style}]{b['stock']}[/{stock_style}]"
        table.add_row(
            str(b["id"]),
            b["title"],
            b["author"],
            str(b["year"]) if b["year"] else "-",
            b["genre"] or "-",
            stock_text,
        )

    console.print()
    console.print(table)


def show_users_table(users):
    """Tampilkan tabel data user."""
    if not users:
        show_info("Tidak ada data user.")
        return

    table = Table(title="Data User Terdaftar", box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="cyan", justify="center", width=5)
    table.add_column("NIM", style="white", width=15)
    table.add_column("Nama", style="white", min_width=20)
    table.add_column("Role", justify="center", width=8)
    table.add_column("Terdaftar", width=12)

    for u in users:
        role_style = "yellow bold" if u["role"] == "admin" else "green"
        table.add_row(
            str(u["id"]),
            u["nim"],
            u["nama"],
            f"[{role_style}]{u['role'].upper()}[/{role_style}]",
            u["created_at"][:10] if u["created_at"] else "-",
        )

    console.print()
    console.print(table)


def show_borrowings_table(borrowings, title="Data Peminjaman"):
    """Tampilkan tabel data peminjaman (admin & user history)."""
    if not borrowings:
        show_info("Tidak ada data peminjaman.")
        return

    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="cyan", justify="center", width=5)

    # Admin view punya NIM & Nama
    has_user_info = "nim" in borrowings[0]
    if has_user_info:
        table.add_column("NIM", style="white", width=12)
        table.add_column("Nama", style="white", min_width=12)

    table.add_column("Judul Buku", style="white", min_width=18)
    table.add_column("Tgl Pinjam", width=12)
    table.add_column("Batas Kembali", width=14)
    table.add_column("Tgl Kembali", width=12)
    table.add_column("Status", justify="center", width=14)

    for br in borrowings:
        if br["status"] == "dikembalikan":
            status_text = "[green]✅ Kembali[/green]"
        else:
            status_text = "[yellow]📖 Dipinjam[/yellow]"

        return_date = br["return_date"][:10] if br["return_date"] else "-"

        row = [str(br["id"])]
        if has_user_info:
            row.extend([br["nim"], br["nama"]])

        row.extend([
            br["title"],
            br["borrow_date"][:10] if br["borrow_date"] else "-",
            br["due_date"][:10] if br["due_date"] else "-",
            return_date,
            status_text,
        ])
        table.add_row(*row)

    console.print()
    console.print(table)


def show_active_borrowings_table(borrowings):
    """Tampilkan tabel buku yang sedang dipinjam (untuk kembalikan buku)."""
    if not borrowings:
        show_info("Tidak ada buku yang sedang dipinjam.")
        return

    table = Table(
        title="📖 Buku yang Sedang Dipinjam", box=box.ROUNDED, show_lines=True
    )
    table.add_column("ID Pinjam", style="cyan", justify="center", width=10)
    table.add_column("Judul Buku", style="white", min_width=20)
    table.add_column("Tgl Pinjam", width=12)
    table.add_column("Batas Kembali", width=14)

    for br in borrowings:
        table.add_row(
            str(br["id"]),
            br["title"],
            br["borrow_date"][:10] if br["borrow_date"] else "-",
            br["due_date"][:10] if br["due_date"] else "-",
        )

    console.print()
    console.print(table)
