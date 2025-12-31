@echo off
REM Script para configurar o Tesseract para build do Ntropy
REM Baixa e extrai o Tesseract portable automaticamente

echo ========================================
echo Configurar Tesseract para Build
echo ========================================
echo.

REM Verificar se ja existe
if exist "tesseract\tesseract.exe" (
    echo [INFO] Tesseract ja esta configurado!
    echo        Pasta: tesseract\
    echo.
    pause
    exit /b 0
)

echo Este script vai ajudar a configurar o Tesseract.
echo.
echo Como o Tesseract nao pode ser baixado automaticamente
echo de forma confiavel, siga estes passos:
echo.
echo ========================================
echo PASSO 1: Baixar o Tesseract
echo ========================================
echo.
echo 1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Baixe a versao mais recente para Windows 64-bit:
echo    "tesseract-ocr-w64-setup-X.XX.X.exe"
echo.
echo 3. Execute o instalador e instale em qualquer pasta
echo    ^(por exemplo: C:\Program Files\Tesseract-OCR^)
echo.
echo Pressione qualquer tecla apos instalar...
pause > nul

echo.
echo ========================================
echo PASSO 2: Copiar arquivos
echo ========================================
echo.

REM Criar pasta tesseract
if not exist "tesseract" mkdir tesseract
if not exist "tesseract\tessdata" mkdir tesseract\tessdata

echo Pasta 'tesseract\' criada.
echo.
echo Agora copie os seguintes arquivos da instalacao do Tesseract:
echo.
echo DE: C:\Program Files\Tesseract-OCR\ ^(ou onde voce instalou^)
echo PARA: %CD%\tesseract\
echo.
echo Arquivos necessarios:
echo   - tesseract.exe
echo   - Todos os arquivos .dll ^(leptonica, libgcc, etc^)
echo.
echo DE: C:\Program Files\Tesseract-OCR\tessdata\
echo PARA: %CD%\tesseract\tessdata\
echo.
echo Arquivos necessarios:
echo   - eng.traineddata ^(ingles - essencial^)
echo   - por.traineddata ^(portugues - opcional^)
echo.
echo Pressione qualquer tecla apos copiar os arquivos...
pause > nul

echo.
echo ========================================
echo VERIFICANDO...
echo ========================================
echo.

if exist "tesseract\tesseract.exe" (
    echo [OK] tesseract.exe encontrado
) else (
    echo [ERRO] tesseract.exe NAO encontrado
)

if exist "tesseract\tessdata\eng.traineddata" (
    echo [OK] eng.traineddata encontrado
) else (
    echo [ERRO] eng.traineddata NAO encontrado
)

echo.
echo Se tudo estiver OK, execute build_exe.bat para criar o executavel.
echo.
pause
