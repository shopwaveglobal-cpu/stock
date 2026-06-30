@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist bin\ffmpeg.exe (
  echo Missing bin\ffmpeg.exe
  exit /b 1
)
if not exist bin\ffprobe.exe (
  echo Missing bin\ffprobe.exe
  exit /b 1
)
python -m pytest -q
python -m PyInstaller --noconfirm --onedir --windowed --name "1IM Video Tool" --add-binary "bin\ffmpeg.exe;bin" --add-binary "bin\ffprobe.exe;bin" app.py
if not exist "dist\1IM Video Tool\bin" mkdir "dist\1IM Video Tool\bin"
copy /Y "bin\ffmpeg.exe" "dist\1IM Video Tool\bin\ffmpeg.exe" >nul
copy /Y "bin\ffprobe.exe" "dist\1IM Video Tool\bin\ffprobe.exe" >nul
copy /Y "README.md" "dist\1IM Video Tool\README.md" >nul
copy /Y "THIRD_PARTY_NOTICES.md" "dist\1IM Video Tool\THIRD_PARTY_NOTICES.md" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Force -Path 'dist\1IM Video Tool' -DestinationPath 'dist\1IM_Video_Tool_Portable.zip'"
