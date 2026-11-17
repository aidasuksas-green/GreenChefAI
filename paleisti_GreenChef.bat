@echo off
chcp 65001 >nul
title GreenChef AI
cd /d "%~dp0"
echo.
echo  GreenChef AI paleidziama... Narsykle atsidarys po keliu sekundziu.
echo  NEUZDARYKITE sio lango, kol naudojates programele.
echo.

rem Kiekvienas Python tikrinamas: ar jis tikras ir ar jame idiegtas streamlit.

rem 1) Anaconda / Miniconda
for %%D in ("%USERPROFILE%\anaconda3" "%USERPROFILE%\miniconda3" "%LOCALAPPDATA%\anaconda3" "%LOCALAPPDATA%\miniconda3" "C:\ProgramData\anaconda3" "C:\ProgramData\miniconda3") do (
    if exist "%%~D\python.exe" (
        "%%~D\python.exe" -c "import streamlit" >nul 2>nul
        if not errorlevel 1 (
            echo  Naudojamas Python: %%~D
            call "%%~D\Scripts\activate.bat" "%%~D" >nul 2>nul
            "%%~D\python.exe" -m streamlit run app.py
            goto pabaiga
        )
    )
)

rem 2) Iprastas Python (py)
py -c "import streamlit" >nul 2>nul
if not errorlevel 1 (
    py -m streamlit run app.py
    goto pabaiga
)

rem 3) Iprastas Python (python)
python -c "import streamlit" >nul 2>nul
if not errorlevel 1 (
    python -m streamlit run app.py
    goto pabaiga
)

echo.
echo  KLAIDA: nerastas Python su idiegtomis bibliotekomis.
echo  Atidarykite "Anaconda Prompt" (arba cmd) siame aplanke ir paleiskite:
echo      python -m pip install -r requirements.txt
echo  Tada vel dukart spustelekite si faila.

:pabaiga
echo.
pause
