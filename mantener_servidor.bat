@echo off
rem Mantiene vivo el servidor del brochure en el puerto 8787.
rem Si python se cae (o alguien lo cierra), lo vuelve a levantar a los 3 s.
rem Todo lo que escriba el servidor queda en servidor.log, para poder ver
rem por que se cayo si se vuelve a caer.
cd /d "%~dp0"
:otra
echo. >> servidor.log
echo ===== arranque %date% %time% ===== >> servidor.log
python servidor.py --sin-navegador >> servidor.log 2>&1
echo ----- se cerro %date% %time% (codigo %errorlevel%) ----- >> servidor.log
timeout /t 3 /nobreak >nul
goto otra
