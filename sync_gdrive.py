#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Incremental Sync Tool
==================================
Mendownload file dari Google Drive secara cerdas (Incremental Sync):
- Mengambil daftar file dari Google Drive secara rekursif (tanpa download ulang file yang sudah ada).
- Membandingkan daftar file Drive dengan file yang sudah ada di lokal.
- Hanya mengunduh file baru atau file yang belum lengkap/rusak (0 bytes).
- Mencatat riwayat unduhan ke dalam manifest (.sync_manifest.json).
- Membersihkan path secara aman untuk kompatibilitas Windows (misal karakter colon ':').
"""

import os
import re
import sys
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional

try:
    import gdown
except ImportError:
    print("[!] Modul 'gdown' belum terinstal.")
    print("[*] Menginstal gdown secara otomatis...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown


MODERN_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

DEFAULT_FOLDER_ID = "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH"
DEFAULT_DESTINATION = "kuliah_s2"
MANIFEST_FILENAME = ".sync_manifest.json"


def format_size(size_bytes: int) -> str:
    """Mengubah ukuran bytes ke format yang mudah dibaca manusia."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def extract_folder_id(url_or_id: str) -> str:
    """
    Mengekstrak folder ID dari URL Google Drive atau mengembalikan ID langsung.
    Contoh:
    - https://drive.google.com/drive/folders/10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH
    - https://drive.google.com/drive/u/0/folders/10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH
    - 10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH
    """
    url_or_id = url_or_id.strip()
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    
    match_query = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url_or_id)
    if match_query:
        return match_query.group(1)

    return url_or_id


def sanitize_path_for_os(rel_path: str) -> str:
    """
    Membersihkan karakter yang dilarang pada sistem operasi Windows (< > : \" / \\ | ? *).
    Mengganti titik dua ':' menjadi ' - ' agar nama dosen/topik tetap terbaca rapi.
    """
    # Pisahkan setiap bagian direktori
    normalized = rel_path.replace("/", "\\")
    parts = normalized.split("\\")
    sanitized_parts = []
    for part in parts:
        clean = part.replace(":", " -")
        clean = re.sub(r'[<>"/\\|?*]', "_", clean).strip()
        # Windows tidak mengizinkan spasi atau titik di akhir nama folder
        clean = clean.rstrip(". ")
        if not clean:
            clean = "_"
        sanitized_parts.append(clean)
    return os.path.join(*sanitized_parts)


def load_manifest(manifest_path: str) -> Dict:
    """Memuat file manifest lokal jika ada."""
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Gagal membaca manifest ({manifest_path}): {e}")
    return {"version": 1, "created_at": datetime.now().isoformat(), "files": {}}


def save_manifest(manifest_path: str, manifest_data: dict) -> None:
    """Menyimpan manifest ke file json."""
    try:
        manifest_data["last_updated"] = datetime.now().isoformat()
        temp_path = manifest_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        if os.path.exists(manifest_path):
            os.replace(temp_path, manifest_path)
        else:
            os.rename(temp_path, manifest_path)
    except Exception as e:
        print(f"[!] Gagal menyimpan manifest: {e}")


def get_remote_file_list(folder_id: str, user_agent: str = MODERN_USER_AGENT) -> List[Dict]:
    """
    Mengambil seluruh daftar file dari Google Drive secara rekursif
    tanpa melakukan proses download file (skip_download=True).
    """
    print(f"[*] Menghubungi Google Drive untuk membaca struktur folder (ID: {folder_id})...")
    print("[*] Proses inspeksi struktur direktori sedang berjalan...")
    start_time = time.time()
    
    # gdown.download_folder dengan skip_download=True mengembalikan list GoogleDriveFileToDownload
    items = gdown.download_folder(
        id=folder_id,
        skip_download=True,
        user_agent=user_agent,
        quiet=True,
        use_cookies=True
    )
    
    elapsed = time.time() - start_time
    print(f"[V] Berhasil menemukan {len(items)} file dari Google Drive dalam {elapsed:.1f} detik.")

    remote_files = []
    for item in items:
        raw_rel_path = os.path.normpath(item.path)
        safe_rel_path = sanitize_path_for_os(raw_rel_path)
        remote_files.append({
            "id": item.id,
            "raw_rel_path": raw_rel_path,
            "rel_path": safe_rel_path,
            "filename": os.path.basename(safe_rel_path)
        })
    return remote_files


def analyze_sync(
    remote_files: List[Dict],
    destination_dir: str,
    manifest: Dict,
    force: bool = False
) -> Tuple[List[Dict], List[Dict]]:
    """
    Menganalisis perbandingan antara Google Drive dan lokal.
    Mengembalikan: (to_download, already_synced)
    """
    to_download = []
    already_synced = []
    manifest_files = manifest.get("files", {})

    for item in remote_files:
        rel_path = item["rel_path"]
        raw_rel_path = item["raw_rel_path"]
        file_id = item["id"]
        
        # Cek path lokal (baik yang sudah disanitasi maupun raw jika ada)
        local_abs = os.path.join(destination_dir, rel_path)
        raw_local_abs = os.path.join(destination_dir, raw_rel_path)
        
        target_path = local_abs
        if not os.path.exists(target_path) and os.path.exists(raw_local_abs):
            target_path = raw_local_abs

        item_info = dict(item)
        item_info["local_path"] = target_path

        if force:
            item_info["reason"] = "FORCE_DOWNLOAD"
            to_download.append(item_info)
            continue

        if not os.path.exists(target_path):
            item_info["reason"] = "FILE_BARU (Belum ada di lokal)"
            to_download.append(item_info)
        elif os.path.getsize(target_path) == 0:
            item_info["reason"] = "FILE_KOSONG / RUSAK (Ukuran 0 byte)"
            to_download.append(item_info)
        else:
            local_size = os.path.getsize(target_path)
            item_info["local_size"] = local_size
            item_info["reason"] = "SUDAH_ADA"
            already_synced.append(item_info)
            
            # Update manifest jika file lokal ada tapi belum tercatat
            if file_id not in manifest_files:
                manifest_files[file_id] = {
                    "rel_path": rel_path,
                    "local_size": local_size,
                    "verified_at": datetime.now().isoformat()
                }

    return to_download, already_synced


def sync_folder(
    folder_url_or_id: str = DEFAULT_FOLDER_ID,
    destination_dir: str = DEFAULT_DESTINATION,
    dry_run: bool = False,
    force: bool = False,
    manifest_file: Optional[str] = None,
    user_agent: str = MODERN_USER_AGENT,
    max_retries: int = 5
) -> bool:
    """
    Menjalankan proses Incremental Sync Google Drive folder ke direktori lokal.
    """
    folder_id = extract_folder_id(folder_url_or_id)
    abs_destination = os.path.abspath(destination_dir)
    os.makedirs(abs_destination, exist_ok=True)

    if not manifest_file:
        manifest_file = os.path.join(abs_destination, MANIFEST_FILENAME)

    print("=" * 70)
    print("      GOOGLE DRIVE INCREMENTAL SYNC - UNIVERSITAS / KULIAH")
    print("=" * 70)
    print(f"[*] Target Folder ID : {folder_id}")
    print(f"[*] Direktori Tujuan : {abs_destination}")
    print(f"[*] File Manifest    : {manifest_file}")
    print(f"[*] Mode Dry Run     : {'AKTIF (Hanya cek, tidak mendownload)' if dry_run else 'TIDAK (Download aktif)'}")
    print(f"[*] Mode Force Sync  : {'AKTIF' if force else 'TIDAK (Hanya download file baru/hilang)'}")
    print("=" * 70)

    manifest = load_manifest(manifest_file)
    
    # 1. Ambil daftar file dari Google Drive
    try:
        remote_files = get_remote_file_list(folder_id, user_agent=user_agent)
    except Exception as e:
        print(f"\n[X] Gagal membaca daftar folder dari Google Drive: {e}")
        print("[!] Tips: Pastikan tautan folder dapat diakses publik atau koneksi internet stabil.")
        return False

    if not remote_files:
        print("[!] Tidak ada file yang ditemukan di dalam folder Google Drive tersebut.")
        return True

    # 2. Analisis perbandingan file lokal vs Drive
    to_download, already_synced = analyze_sync(
        remote_files, abs_destination, manifest, force=force
    )

    print("\n" + "-" * 70)
    print("HASIL ANALISIS SINKRONISASI:")
    print(f"  • Total File di Google Drive : {len(remote_files)} file")
    print(f"  • File Sudah Ada di Lokal    : {len(already_synced)} file (Akan dilewati / Skip)")
    print(f"  • File Baru / Perlu Unduh    : {len(to_download)} file")
    print("-" * 70)

    if already_synced:
        total_existing_size = sum(f.get("local_size", 0) for f in already_synced)
        print(f"[*] Ukuran data lokal yang dihemat (tidak perlu diunduh ulang): {format_size(total_existing_size)}")

    if not to_download:
        print("\n[V] SEMUA FILE SUDAH TERSINKRONISASI!")
        print(f"[V] Tidak ada file baru yang perlu diunduh di {abs_destination}.")
        save_manifest(manifest_file, manifest)
        return True

    # Tampilkan daftar file yang akan diunduh
    print(f"\n[*] Daftar file yang perlu diunduh ({len(to_download)} file):")
    for idx, item in enumerate(to_download, 1):
        print(f"  {idx:2d}. [{item['reason']}]")
        print(f"      {item['rel_path']}")

    if dry_run:
        print("\n[!] Mode DRY-RUN selesai. Tidak ada file yang diunduh.")
        save_manifest(manifest_file, manifest)
        return True

    # 3. Proses Unduh Hanya File yang Belum Ada
    print("\n" + "=" * 70)
    print(f"[*] MEMULAI PROSES UNDUH ({len(to_download)} FILE)...")
    print("=" * 70)

    downloaded_count = 0
    failed_count = 0
    start_sync_time = time.time()

    for idx, item in enumerate(to_download, 1):
        file_id = item["id"]
        rel_path = item["rel_path"]
        local_path = item["local_path"]
        
        print(f"\n[{idx}/{len(to_download)}] Mengunduh: {rel_path}")
        print(f"[*] File ID: {file_id}")
        
        try:
            # Buat subdirektori secara aman
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            downloaded = gdown.download(
                id=file_id,
                output=local_path,
                quiet=False,
                resume=True,
                retries=max_retries,
                user_agent=user_agent
            )

            if downloaded and os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                downloaded_size = os.path.getsize(local_path)
                print(f"[V] Selesai: {rel_path} ({format_size(downloaded_size)})")
                
                # Catat ke manifest
                manifest.setdefault("files", {})[file_id] = {
                    "rel_path": rel_path,
                    "local_size": downloaded_size,
                    "downloaded_at": datetime.now().isoformat()
                }
                save_manifest(manifest_file, manifest)
                downloaded_count += 1
            else:
                print(f"[X] Unduhan gagal atau file kosong: {rel_path}")
                failed_count += 1
        except Exception as e:
            print(f"[X] Gagal mengunduh file {rel_path}: {e}")
            failed_count += 1

    total_time = time.time() - start_sync_time
    save_manifest(manifest_file, manifest)

    print("\n" + "=" * 70)
    print("RINGKASAN SINKRONISASI:")
    print(f"  • Berhasil diunduh : {downloaded_count} file")
    print(f"  • Gagal diunduh    : {failed_count} file")
    print(f"  • Sudah ada (skip) : {len(already_synced)} file")
    print(f"  • Waktu proses     : {total_time:.1f} detik")
    print(f"  • Direktori lokal  : {abs_destination}")
    print("=" * 70)

    return failed_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Google Drive Incremental Sync - Unduh hanya file baru atau yang terupdate secara efisien."
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        default=DEFAULT_FOLDER_ID,
        help=f"URL Google Drive folder atau Folder ID (default: Semester I 2026/2027 ID: {DEFAULT_FOLDER_ID})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=DEFAULT_DESTINATION,
        help=f"Folder tujuan penyimpanan lokal (default: '{DEFAULT_DESTINATION}')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Cek daftar file yang belum tersinkronisasi tanpa mendownload"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Paksa unduh ulang semua file meskipun sudah ada di lokal"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=0,
        help="Jalankan sinkronisasi secara berkala setiap N menit (0 = jalankan sekali lalu selesai)"
    )

    args = parser.parse_args()

    # Jika berjalan dengan opsi interval (daemon / watcher mode)
    if args.interval > 0:
        print(f"[*] Memulai mode pemantauan berkala setiap {args.interval} menit.")
        print("[*] Tekan Ctrl+C untuk menghentikan pemantauan.")
        try:
            while True:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[>>> SIKLUS SINKRONISASI: {now_str} <<<]")
                sync_folder(
                    folder_url_or_id=args.url,
                    destination_dir=args.output,
                    dry_run=args.dry_run,
                    force=args.force
                )
                print(f"\n[*] Menunggu {args.interval} menit sebelum pengecekan berikutnya...")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\n[*] Pemantauan dihentikan oleh pengguna.")
            sys.exit(0)
    else:
        success = sync_folder(
            folder_url_or_id=args.url,
            destination_dir=args.output,
            dry_run=args.dry_run,
            force=args.force
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
