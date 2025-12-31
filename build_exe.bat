@echo off
REM Build Ntropy.exe with embedded Tesseract OCR
REM Este script cria um executavel auto-contido que nao precisa de instalacao

echo ========================================
echo Ntropy - Build Executavel Windows
echo ========================================
echo.

REM Verificar se pasta tesseract existe
if not exist "tesseract\" (
    echo [ERRO] Pasta 'tesseract\' nao encontrada!
    echo.
    echo Para criar um executavel auto-contido, voce precisa:
    echo.
    echo 1. Baixar Tesseract portable de:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo    ^(Escolha a versao "tesseract-ocr-w64-setup" e instale^)
    echo.
    echo 2. Copiar os arquivos para a pasta 'tesseract\':
    echo    - tesseract.exe
    echo    - Todos os arquivos .dll
    echo    - Pasta tessdata\ com eng.traineddata
    echo.
    echo Estrutura esperada:
    echo    tesseract\
    echo    ├── tesseract.exe
    echo    ├── *.dll
    echo    └── tessdata\
    echo        └── eng.traineddata
    echo.
    echo Ou execute: download_tesseract.bat ^(se disponivel^)
    echo.
    pause
    exit /b 1
)

echo [OK] Pasta tesseract\ encontrada
echo.

REM Verificar arquivos essenciais
if not exist "tesseract\tesseract.exe" (
    echo [ERRO] tesseract\tesseract.exe nao encontrado!
    pause
    exit /b 1
)

if not exist "tesseract\tessdata\eng.traineddata" (
    echo [AVISO] tesseract\tessdata\eng.traineddata nao encontrado
    echo         O OCR pode nao funcionar corretamente
    echo.
)

echo [1/3] Instalando PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar PyInstaller
    pause
    exit /b 1
)

echo.
echo [2/3] Compilando aplicacao com Tesseract embutido...
echo       ^(Isso pode demorar alguns minutos^)
echo.

REM Usar o arquivo .spec para build
pyinstaller ntropy.spec --noconfirm

if errorlevel 1 (
    echo.
    echo [ERRO] Falha na compilacao!
    echo Verifique os erros acima.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [3/3] Build completo!
echo ========================================
echo.
echo O executavel foi criado em: dist\Ntropy.exe
echo.
echo Este executavel JA INCLUI o Tesseract OCR!
echo O usuario final so precisa baixar e executar.
echo.
echo Tamanho aproximado: 80-100 MB
echo.

REM Mostrar tamanho do arquivo
for %%A in (dist\Ntropy.exe) do echo Tamanho real: %%~zA bytes ^(%%~zA / 1048576 MB^)

echo.
pause
