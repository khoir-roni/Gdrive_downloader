# Google Drive Downloader & Incremental Sync

Toolkit Python untuk mendownload dan menyinkronkan folder Google Drive secara rekursif, dengan dukungan penuh **Incremental Sync** (hanya mengunduh file baru/terupdate tanpa membuang kuota dan waktu mengunduh ulang file yang sudah ada).

---

## 📁 Struktur Direktori & File

- `sync_gdrive.py`: Mesin utama **Incremental Sync** (paling efisien & hemat bandwidth).
- `download_gdrive.py`: Downloader universal dengan dukungan mode standar dan `--sync`.
- `run_sync.bat`: Launcher praktis berbasis menu Windows untuk menjalankan sinkronisasi atau dry-run.
- `run_downloader.bat`: Launcher downloader interaktif standar.
- `setup_task_scheduler.bat`: Helper untuk mendaftarkan jadwal otomatis di Windows Task Scheduler.
- `kuliah_s2/`: Direktori penyimpanan file kuliah S2 Kerma PLN (Semester I 2026/2027).
- `kuliah_s2/.sync_manifest.json`: Catatan metadata file yang telah tersinkronisasi.

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan Launcher Windows (.bat) - Paling Praktis
1. **Sinkronisasi Kuliah S2:**
   - Klik dua kali **`run_sync.bat`**.
   - Pilih menu:
     - `1`: Langsung unduh file baru ke `kuliah_s2`.
     - `2`: Dry-run (cek daftar file baru tanpa mengunduh).
     - `3`: Sinkronisasi folder Google Drive kustom.
     - `4`: Jalankan mode pemantauan berkala (daemon loop setiap N menit).

2. **Downloader Standar:**
   - Klik dua kali **`run_downloader.bat`**.

---

### Cara 2: Menjalankan via Terminal (PowerShell / CMD)

Masuk ke direktori:
```powershell
cd D:\study_s2\gdrive_downloader
```

#### A. Incremental Sync (`sync_gdrive.py`)
```powershell
# Cek perbedaan tanpa download (Dry-Run)
python sync_gdrive.py --dry-run

# Unduh hanya file baru ke folder kuliah_s2
python sync_gdrive.py

# Menentukan URL dan folder tujuan lain
python sync_gdrive.py --url "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH" --output "kuliah_s2"

# Jalankan pemantauan otomatis setiap 60 menit
python sync_gdrive.py --interval 60
```

#### B. Melalui `download_gdrive.py` dengan Opsi `--sync`
```powershell
# Jalankan mode sync
python download_gdrive.py --sync --output "kuliah_s2"

# Mode interaktif
python download_gdrive.py
```

---

## ⏰ Konfigurasi Sinkronisasi Otomatis (Windows Task Scheduler)

Untuk menjaga agar materi kuliah selalu terupdate tanpa perlu menjalankan script secara manual:

### Opsi A: Menggunakan Script Helper
Klik dua kali **`setup_task_scheduler.bat`** (pilih **Run as Administrator** jika diminta):
- Pilih opsi jadwal: Harian jam 06:00, jam 18:00, atau setiap 4 jam.

### Opsi B: Menggunakan Perintah CMD / PowerShell Manual
Jalankan di Command Prompt (Administrator):
```cmd
schtasks /create /tn "GDrive_KuliahS2_Sync" /tr "\"python.exe\" \"D:\study_s2\gdrive_downloader\sync_gdrive.py\" --output \"D:\study_s2\gdrive_downloader\kuliah_s2\"" /sc daily /st 06:00 /f
```

---

## 🔍 Cara Kerja Fitur Incremental Sync

1. **Fast Tree Discovery:** Mengambil struktur direktori dan daftar file Google Drive secara rekursif via `gdown` (`skip_download=True`) dalam waktu ~25-30 detik tanpa transfer payload file.
2. **Local Comparison:** Membandingkan setiap file Google Drive dengan file lokal di `kuliah_s2/`:
   - File belum ada di lokal -> Ditandai untuk diunduh.
   - File berukuran 0 byte (gagal/korup) -> Ditandai untuk diunduh ulang.
   - File sudah ada dan lengkap (> 0 byte) -> Dilewati (*Skip*), menghemat belasan gigabyte bandwidth.
3. **Download File Baru:** Hanya mengunduh file yang belum ada menggunakan `gdown.download` dengan resume support dan retry otomatis.
4. **Manifest Tracking:** Menyimpan status unduhan ke `.sync_manifest.json` untuk verifikasi konsistensi.
