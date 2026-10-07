@echo off
:: =========================================================================
:: Script Konfigurasi Windows Task Scheduler untuk Google Drive Sync Otomatis
:: =========================================================================
title Setup Windows Task Scheduler - GDrive Sync
cd /d "%~dp0"

echo =========================================================================
echo    PENDAFTARAN JADWAL OTOMATIS (WINDOWS TASK SCHEDULER) - GDRIVE SYNC
echo =========================================================================
echo.
echo Script ini akan mendaftarkan Task Scheduler di Windows agar sinkronisasi
echo materi kuliah S2 dijalankan secara otomatis di latar belakang.
echo.
echo Pilihan Jadwal:
echo   [1] Jalankan setiap hari jam 06:00 pagi
echo   [2] Jalankan setiap hari jam 18:00 sore (setelah jam kuliah)
echo   [3] Jalankan setiap 4 jam sekali
echo   [4] Hapus Jadwal Otomatis yang sudah terdaftar
echo   [5] Batal / Keluar
echo.
set /p "opt=Pilih opsi [1-5]: "

set "TASK_NAME=GDrive_KuliahS2_Sync"
set "PYTHON_EXE=python.exe"
set "SCRIPT_PATH=%~dp0sync_gdrive.py"

if "%opt%"=="1" (
    echo [*] Mendaftarkan jadwal harian jam 06:00...
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --output \"%~dp0kuliah_s2\"" /sc daily /st 06:00 /f
    goto verify
)

if "%opt%"=="2" (
    echo [*] Mendaftarkan jadwal harian jam 18:00...
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --output \"%~dp0kuliah_s2\"" /sc daily /st 18:00 /f
    goto verify
)

if "%opt%"=="3" (
    echo [*] Mendaftarkan jadwal setiap 4 jam...
    schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --output \"%~dp0kuliah_s2\"" /sc hourly /mo 4 /f
    goto verify
)

if "%opt%"=="4" (
    echo [*] Menghapus task "%TASK_NAME%"...
    schtasks /delete /tn "%TASK_NAME%" /f
    goto done
)

if "%opt%"=="5" (
    goto done
)

:verify
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [V] Task Scheduler "%TASK_NAME%" BERHASIL didaftarkan!
    echo [*] Folder target: %~dp0kuliah_s2
    echo [*] Anda dapat melihat atau mengelolanya lewat Windows Task Scheduler (taskschd.msc).
) else (
    echo.
    echo [!] Gagal mendaftarkan task. Jalankan file .bat ini dengan "Run as Administrator" jika diperlukan hak akses tambahan.
)

:done
echo.
pause
