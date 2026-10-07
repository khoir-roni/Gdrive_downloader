#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Folder Downloader & Incremental Sync Tool
======================================================
Mendownload dan menyinkronkan folder Google Drive secara rekursif.
Mendukung mode Incremental Sync (--sync) untuk mengunduh hanya file baru/berubah.
"""

import os
import re
import sys
import argparse

try:
    import gdown
except ImportError:
    print("[!] Modul 'gdown' belum terinstal.")
    print("[*] Menginstal gdown secara otomatis...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

# Import fungsi sinkronisasi dari sync_gdrive jika ada
try:
    from sync_gdrive import sync_folder, DEFAULT_FOLDER_ID, DEFAULT_DESTINATION, MODERN_USER_AGENT
except ImportError:
    # Fallback jika dijalankan terpisah
    DEFAULT_FOLDER_ID = "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH"
    DEFAULT_DESTINATION = "kuliah_s2"
    MODERN_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
    sync_folder = None


def extract_folder_id(url_or_id: str) -> str:
    """
    Mengekstrak folder ID dari URL Google Drive atau mengembalikan ID langsung.
    Contoh link:
    - https://drive.google.com/drive/folders/1ABCxyz...
    - https://drive.google.com/drive/u/0/folders/1ABCxyz...
    - 1ABCxyz...
    """
    url_or_id = url_or_id.strip()
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    
    match_query = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url_or_id)
    if match_query:
        return match_query.group(1)

    return url_or_id


def download_gdrive_folder(folder_url_or_id: str, output_folder: str = "downloads"):
    """
    Mendownload folder Google Drive beserta seluruh subfolder dan isinya secara standar.
    """
    folder_id = extract_folder_id(folder_url_or_id)
    gdrive_url = f"https://drive.google.com/drive/folders/{folder_id}"

    abs_output = os.path.abspath(output_folder)
    os.makedirs(abs_output, exist_ok=True)
    
    print("=" * 60)
    print("Google Drive Folder Downloader (Standard Mode)")
    print("=" * 60)
    print(f"[*] Folder ID    : {folder_id}")
    print(f"[*] Folder URL   : {gdrive_url}")
    print(f"[*] Folder Tujuan: {abs_output}")
    print("=" * 60)
    print("[*] Memulai download... Harap tunggu, proses ini bergantung pada ukuran data.")

    try:
        downloaded = gdown.download_folder(
            id=folder_id,
            output=abs_output,
            quiet=False,
            use_cookies=True,
            resume=True,
            retries=5,
            user_agent=MODERN_USER_AGENT
        )
        
        if downloaded is not None:
            print("\n[V] Download selesai dengan sukses!")
            print(f"[V] File tersimpan di: {abs_output}")
        else:
            print("\n[!] Gagal mendownload atau tidak ada file yang ditemukan.")
            print("[!] Pastikan link folder diatur ke: 'Siapa saja yang memiliki link dapat melihat' (Public / Anyone with the link).")
    except Exception as e:
        print(f"\n[X] Terjadi kesalahan: {e}")
        print("[!] Tips: Pastikan akses folder Google Drive sudah diatur publik atau memiliki izin akses.")


def main():
    parser = argparse.ArgumentParser(
        description="Download atau Sinkronisasi Folder Google Drive secara rekursif."
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        help=f"URL Google Drive folder atau Folder ID (default: Semester I 2026/2027)",
        default=None
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Nama/Path folder tujuan penyimpanan lokal",
        default=None
    )
    parser.add_argument(
        "--sync", "-s",
        action="store_true",
        help="Gunakan mode Incremental Sync (hanya mengunduh file baru/terupdate, menghemat bandwidth)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Cek perbandingan file lokal vs Google Drive tanpa mendownload (hanya berlaku pada mode sync)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Paksa unduh ulang seluruh file"
    )

    args = parser.parse_args()

    url_input = args.url
    output_input = args.output
    use_sync = args.sync

    # Mode interaktif jika argumen tidak diberikan lewat CLI
    if not url_input and not output_input and not use_sync:
        print("=" * 65)
        print("       GOOGLE DRIVE DOWNLOADER & SYNC TOOL")
        print("=" * 65)
        print("Pilih Mode Pengoperasian:")
        print("  1. Incremental Sync (SANGAT DIREKOMENDASIKAN)")
        print("     -> Hanya unduh file baru atau yang belum ada di lokal.")
        print("  2. Standard / Full Download")
        print("     -> Unduh folder secara konvensional.")
        print("=" * 65)
        mode_choice = input("Pilihan mode (1 atau 2, default: 1): ").strip()
        use_sync = False if mode_choice == "2" else True

        default_url_hint = f"tekan Enter untuk default 'Semester I 2026/2027' [{DEFAULT_FOLDER_ID}]"
        url_input = input(f"Masukkan URL Folder Google Drive atau Folder ID\n({default_url_hint}):\n> ").strip()
        if not url_input:
            url_input = DEFAULT_FOLDER_ID

        default_out = DEFAULT_DESTINATION if use_sync else "downloads"
        custom_folder = input(f"Masukkan nama folder penyimpanan (tekan Enter untuk default '{default_out}'):\n> ").strip()
        output_input = custom_folder if custom_folder else default_out
    else:
        # Fallback default jika tidak ada url
        if not url_input:
            url_input = DEFAULT_FOLDER_ID
        if not output_input:
            output_input = DEFAULT_DESTINATION if use_sync else "downloads"

    if use_sync and sync_folder is not None:
        sync_folder(
            folder_url_or_id=url_input,
            destination_dir=output_input,
            dry_run=args.dry_run,
            force=args.force
        )
    else:
        download_gdrive_folder(url_input, output_input)


if __name__ == "__main__":
    main()
