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
    
    # Jika memasukkan id=... di query parameter
    match_query = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url_or_id)
    if match_query:
        return match_query.group(1)

    # Asumsi user langsung memasukkan ID
    return url_or_id


def download_gdrive_folder(folder_url_or_id: str, output_folder: str = "downloads"):
    """
    Mendownload folder Google Drive beserta seluruh subfolder dan isinya.
    """
    folder_id = extract_folder_id(folder_url_or_id)
    gdrive_url = f"https://drive.google.com/drive/folders/{folder_id}"

    # Pastikan folder output ada, jika belum ada maka buat folder baru
    abs_output = os.path.abspath(output_folder)
    os.makedirs(abs_output, exist_ok=True)
    
    print("=" * 60)
    print("Google Drive Folder Downloader")
    print("=" * 60)
    print(f"[*] Folder ID    : {folder_id}")
    print(f"[*] Folder URL   : {gdrive_url}")
    print(f"[*] Folder Tujuan: {abs_output}")
    print("=" * 60)
    print("[*] Memulai download... Harap tunggu, proses ini bergantung pada ukuran data.")

    try:
        modern_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
        downloaded = gdown.download_folder(
            id=folder_id,
            output=abs_output,
            quiet=False,
            use_cookies=True,
            resume=True,
            retries=5,
            user_agent=modern_user_agent
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
    parser = argparse.ArgumentParser(description="Download folder Google Drive beserta isinya secara rekursif.")
    parser.add_argument("--url", "-u", type=str, help="URL Google Drive folder atau Folder ID", default=None)
    parser.add_argument("--output", "-o", type=str, help="Nama/Path folder tujuan penyimpanan", default=None)

    args = parser.parse_args()

    url_input = args.url
    output_input = args.output

    # Mode interaktif jika argumen tidak diberikan lewat CLI
    if not url_input:
        print("=" * 60)
        print("  GOOGLE DRIVE FOLDER DOWNLOADER")
        print("=" * 60)
        url_input = input("Masukkan URL Folder Google Drive atau Folder ID:\n> ").strip()

    if not url_input:
        print("[X] URL atau Folder ID tidak boleh kosong!")
        sys.exit(1)

    if not output_input:
        folder_default = "downloads"
        custom_folder = input(f"Masukkan nama folder penyimpanan (tekan Enter untuk default '{folder_default}'):\n> ").strip()
        output_input = custom_folder if custom_folder else folder_default

    download_gdrive_folder(url_input, output_input)


if __name__ == "__main__":
    main()
