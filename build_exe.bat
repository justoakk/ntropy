@echo off
REM Build Ntropy.exe using PyInstaller

echo ========================================
echo Building Ntropy.exe...
echo ========================================
echo.

REM Instala PyInstaller se necessário
echo [1/3] Instalando PyInstaller...
pip install pyinstaller --quiet

echo.
echo [2/3] Compilando aplicacao...
echo (Isso pode demorar alguns minutos)
echo.

REM Cria o executável
pyinstaller --onefile --windowed --name="Ntropy" main.py

echo.
echo ========================================
echo [3/3] Build completo!
echo ========================================
echo.
echo O executavel foi criado em: dist\Ntropy.exe
echo.
echo Para usar:
echo 1. Va para a pasta dist\
echo 2. Execute Ntropy.exe
echo.
echo IMPORTANTE: Os arquivos config.json e data.json
echo serao criados automaticamente na primeira execucao.
echo.
pause
