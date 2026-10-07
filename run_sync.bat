@echo off
:: ========================================================
:: Google Drive Incremental Sync Launcher
:: Otomatis mendownload hanya file baru / belum ada di lokal
:: ========================================================
title Google Drive Incremental Sync - S2 Kerma PLN
cd /d "%~dp0"

echo ======================================================================
echo          GOOGLE DRIVE INCREMENTAL SYNC - UNIVERSITAS / KULIAH S2
echo ======================================================================
echo Target Folder: Semester I 2026/2027 (ID: 10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH)
echo Lokasi Lokal : %~dp0kuliah_s2
echo ======================================================================
echo.
echo Pilih Aksi:
echo   [1] Mulai Sinkronisasi Cepat (Unduh file baru ke folder kuliah_s2)
echo   [2] Cek File Baru (Dry-Run: hanya melihat daftar file tanpa mengunduh)
echo   [3] Sinkronisasi Folder Google Drive Kustom (Input URL sendiri)
echo   [4] Mode Pemantauan Otomatis (Periksa berkala setiap N menit)
echo   [5] Keluar
echo.
set /p "choice=Pilihan Anda [1-5] (default: 1): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo [*] Menjalankan Sinkronisasi Inkremental ke folder kuliah_s2...
    python sync_gdrive.py --url "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH" --output "kuliah_s2"
    goto end
)

if "%choice%"=="2" (
    echo.
    echo [*] Menjalankan Pengecekan Dry-Run (tanpa mendownload)...
    python sync_gdrive.py --url "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH" --output "kuliah_s2" --dry-run
    goto end
)

if "%choice%"=="3" (
    echo.
    set /p "custom_url=Masukkan URL Folder Google Drive atau Folder ID: "
    set /p "custom_out=Masukkan Folder Tujuan (default: kuliah_s2): "
    if "%custom_out%"=="" set custom_out=kuliah_s2
    python sync_gdrive.py --url "%custom_url%" --output "%custom_out%"
    goto end
)

if "%choice%"=="4" (
    echo.
    set /p "interval_mins=Masukkan interval pengecekan dalam menit (contoh: 60): "
    if "%interval_mins%"=="" set interval_mins=60
    echo [*] Menjalankan pemantauan setiap %interval_mins% menit...
    python sync_gdrive.py --url "10sEl0HylyMFCflcrTJ2HGDv3avRqaZAH" --output "kuliah_s2" --interval %interval_mins%
    goto end
)

if "%choice%"=="5" (
    goto exit_no_pause
)

:end
echo.
echo ======================================================================
echo Proses telah selesai.
echo ======================================================================
pause

:exit_no_pause
