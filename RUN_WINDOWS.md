# Como rodar Ntropy no Windows

## 🪟 Método 1 - Script .bat (MAIS SIMPLES)

✅ **Jeito mais rápido!** Basta clicar duas vezes.

### Passo 1: Ter Python instalado

Baixe e instale Python em: https://www.python.org/downloads/

**IMPORTANTE:** Durante a instalação, marque a opção:
```
☑ Add Python to PATH
```

### Passo 2: Executar o app

1. Vá até a pasta `ntropy`
2. Dê dois cliques em **`ntropy.bat`**
3. Pronto! O app vai abrir 🎉

**Vantagens:**
- Instantâneo, não precisa compilar
- Fácil de modificar código se necessário
- Funciona imediatamente

**Desvantagens:**
- Precisa do Python instalado
- Abre uma janela do terminal junto

---

## 🚀 Método 2 - Executável .exe (RECOMENDADO)

Não precisa do Python instalado! Perfeito para distribuir para outras pessoas.

### Opção A - Usar o build_exe.bat (automático)

1. Vá até a pasta `ntropy`
2. Dê dois cliques em **`build_exe.bat`**
3. Aguarde a compilação (pode demorar 2-3 minutos)
4. O executável estará em: `dist\Ntropy.exe`
5. Dê dois cliques em `Ntropy.exe` para executar

### Opção B - Criar manualmente via CMD

Abra o CMD (ou PowerShell) na pasta do projeto e execute:

```cmd
pip install pyinstaller
pyinstaller --onefile --windowed --name="Ntropy" main.py
```

O executável estará em: `dist\Ntropy.exe`

**Vantagens:**
- Não precisa do Python instalado
- Um único arquivo .exe
- Sem janela de terminal
- Pode distribuir para qualquer pessoa

**Desvantagens:**
- Arquivo grande (~50-100 MB)
- Precisa recompilar se mudar o código
- Antivírus pode bloquear (falso positivo)

---

## 📋 Requisitos do Sistema (Windows)

### Para rodar o .bat (Método 1):

1. **Python 3.8 ou superior**
   - Download: https://www.python.org/downloads/
   - Marque "Add Python to PATH" na instalação

2. **Tesseract OCR**
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Instale e anote o caminho (ex: `C:\Program Files\Tesseract-OCR`)

3. **Bibliotecas Python**
   ```cmd
   pip install -r requirements.txt
   ```

   Ou manualmente:
   ```cmd
   pip install Pillow pytesseract pynput psutil
   ```

### Para rodar o .exe (Método 2):

✅ **Nenhum requisito!** O .exe já tem tudo incluído.

---

## 🎮 Como usar o Ntropy

### 1. Primeira execução

Na primeira vez que rodar, o app vai criar automaticamente:
- `config.json` - Configurações dos jogos
- `data.json` - Dados capturados (será criado na primeira captura)

### 2. Configurar regiões de captura

Para cada jogo:
1. Abra o jogo
2. Abra o Ntropy
3. Pressione **F3** (ou F4 no Zenless) para abrir a tela de valores
4. Clique em "Selecionar Região Convertidos"
5. Arraste o mouse sobre a área dos valores convertidos
6. Clique em "Selecionar Região Inteiros"
7. Arraste o mouse sobre a área dos valores inteiros

### 3. Capturar valores

**Captura automática:**
- Pressione **F3** no jogo (Genshin, HSR, Wuthering Waves)
- Pressione **F4** no jogo (Zenless Zone Zero)
- O app espera 3 segundos e captura automaticamente

**Captura manual:**
- Pressione **F9** a qualquer momento

### 4. Ver histórico

Clique em "Ver Comparação" para ver os valores dos 4 jogos lado a lado.

---

## 🔧 Problemas Comuns

### "Python não é reconhecido como comando"

**Solução:**
1. Python não está instalado OU não está no PATH
2. Baixe em: https://www.python.org/downloads/
3. Durante instalação, marque "Add Python to PATH"
4. Reinicie o terminal/CMD após instalar

### "pip não é reconhecido como comando"

**Solução:**
```cmd
python -m pip install pyinstaller
python -m pip install -r requirements.txt
```

### "TesseractNotFoundError"

**Solução:**
1. Instale o Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Adicione ao PATH ou configure no código

### Executável muito grande (>100MB)

**Isso é normal!** PyInstaller inclui o Python inteiro no .exe.

Para reduzir:
```cmd
pyinstaller --onefile --windowed --name="Ntropy" main.py
```

### Antivírus bloqueia o .exe

**Isso é comum com PyInstaller (falso positivo).**

**Soluções:**
1. Adicione exceção no Windows Defender
2. Use o método `.bat` que não tem esse problema
3. Envie o .exe para análise no VirusTotal para comprovar que é seguro

### Hotkeys não funcionam

- Rode o app como Administrador (clique direito → "Executar como administrador")
- Verifique se nenhum outro programa está usando F3/F4/F9

### Captura não funciona no jogo

- Execute o jogo em modo **Janela sem bordas** ou **Janela**
- Modo tela cheia pode bloquear capturas
- Rode o app como Administrador

---

## 📁 Estrutura para Distribuição

Se você quer compartilhar o Ntropy com amigos:

```
Ntropy/
├── Ntropy.exe           ← Executável (criado pelo PyInstaller)
├── config.json          ← Criado automaticamente na 1ª execução
├── data.json            ← Criado na primeira captura
└── LEIA-ME.txt          ← Instruções para o usuário
```

**Passos para distribuir:**
1. Compile com `build_exe.bat`
2. Copie `dist\Ntropy.exe` para uma pasta
3. Crie um arquivo `LEIA-ME.txt` com instruções básicas
4. Compacte em .zip e envie

---

## ⚡ Quick Start (Windows)

**Método rápido com .bat:**
1. Instale Python: https://www.python.org/downloads/
2. Instale Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
3. Abra CMD na pasta do projeto:
   ```cmd
   pip install -r requirements.txt
   ```
4. Dê dois cliques em `ntropy.bat`

**Método rápido com .exe:**
1. Dê dois cliques em `build_exe.bat`
2. Aguarde compilação
3. Dê dois cliques em `dist\Ntropy.exe`

Pronto! 🎉

---

## 🎯 Qual Método Escolher?

**Para você usar durante desenvolvimento:**
→ Use `ntropy.bat` (mais prático, rápido de testar mudanças)

**Para distribuir para outras pessoas:**
→ Use `build_exe.bat` e crie `Ntropy.exe`
→ Assim elas não precisam instalar Python/Tesseract

**Se antivírus bloqueiar:**
→ Volte para o método `.bat`
→ Ou adicione exceção no antivírus

---

## 🛠️ Comandos Úteis PyInstaller

```cmd
REM Executável básico
pyinstaller main.py

REM Arquivo único + sem console
pyinstaller --onefile --windowed main.py

REM Com nome personalizado
pyinstaller --onefile --windowed --name="Ntropy" main.py

REM Com ícone personalizado
pyinstaller --onefile --windowed --icon=icon.ico --name="Ntropy" main.py

REM Limpar builds anteriores
rmdir /s /q build dist
del *.spec
```

---

## 🆘 Precisa de Ajuda?

Se algo não funcionar:

1. Verifique se Python está instalado: `python --version`
2. Verifique se pip está instalado: `pip --version`
3. Teste se Tkinter funciona: `python -m tkinter`
4. Reinstale dependências: `pip install -r requirements.txt --force-reinstall`
5. Rode como Administrador
6. Verifique se o antivírus não está bloqueando

---

## 📚 Outros Tutoriais

- **BUILD_WINDOWS.md** - Guia técnico detalhado de compilação
- **RUN_LINUX.md** - Como rodar no Linux
- **requirements.txt** - Lista de dependências Python
