@echo off
chcp 65001 >nul
title GreenChef AI - kainu atnaujinimas
cd /d "%~dp0"
echo.
echo  Atnaujinamos ingredientu kainos is Barbora.lt (uztrunka kelias minutes)...
echo.

set "ARGS=%*"
if /i "%~1"=="/auto" set "ARGS="

rem Pirmiausia ieskomas Python su pandas ir requests (kaip paleisti_GreenChef.bat).
for %%D in ("%USERPROFILE%\anaconda3" "%USERPROFILE%\miniconda3" "%LOCALAPPDATA%\anaconda3" "%LOCALAPPDATA%\miniconda3" "C:\ProgramData\anaconda3" "C:\ProgramData\miniconda3") do (
    if exist "%%~D\python.exe" (
        "%%~D\python.exe" -c "import pandas, requests" >nul 2>nul
        if not errorlevel 1 (
            "%%~D\python.exe" code\update_prices.py %ARGS%
            goto pabaiga
        )
    )
)
py -c "import pandas, requests" >nul 2>nul
if not errorlevel 1 (
    py code\update_prices.py %ARGS%
    goto pabaiga
)
python -c "import pandas, requests" >nul 2>nul
if not errorlevel 1 (
    python code\update_prices.py %ARGS%
    goto pabaiga
)
echo  KLAIDA: nerastas Python su pandas ir requests. Paleiskite:  python -m pip install -r requirements.txt

:pabaiga
rem Paleidus is Uzduociu planuoklio (su parametru /auto) langas neuzlaikomas.
if /i not "%~1"=="/auto" pause
