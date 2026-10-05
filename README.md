# Google Drive Folder Downloader

Script Python untuk mendownload folder Google Drive beserta seluruh subfolder dan file di dalamnya secara otomatis dan rekursif.

---

## 📁 Lokasi Script
Folder ini telah dibuat di:
`D:\study_s2\gdrive_downloader`

---

## 🚀 Cara Menjalankan

### Cara 1: Langsung Klik Dua Kali (Paling Mudah di Windows)
Klik dua kali file **`run_downloader.bat`**. Jendela konsol akan terbuka dan menanyakan:
1. Link Google Drive atau Folder ID.
2. Nama folder penyimpanan (secara default akan masuk ke folder `downloads/`).

---

### Cara 2: Menjalankan via Terminal (PowerShell / CMD)

Masuk ke folder project:
```powershell
cd D:\study_s2\gdrive_downloader
```

**Mode Interaktif (Tanya Jawab):**
```powershell
python download_gdrive.py
```

**Mode Langsung dengan Parameter:**
```powershell
python download_gdrive.py --url "https://drive.google.com/drive/folders/1ABCxyz..." --output "downloads/nama_folder"
```

---

## ⚠️ Catatan Penting
1. **Hak Akses Folder Google Drive:**
   - Pastikan link folder Google Drive sudah diatur ke **"Siapa saja yang memiliki link dapat melihat"** (*Anyone with the link can view*).
2. **File / Subfolder Bertingkat:**
   - Script ini otomatis menjaga struktur folder asli (subfolder di dalam folder akan didownload persis seperti di Google Drive).
3. **Folder Baru:**
   - Script akan otomatis membuat folder tujuan (misal `downloads/`) jika belum ada.
