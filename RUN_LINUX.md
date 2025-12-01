# Como rodar Ntropy no Linux

## 🐧 Método 1 - Script .sh (RECOMENDADO)

✅ **Jeito mais simples e eficiente para Linux!**

### Passo 1: Dar permissão de execução

```bash
cd /home/olavo/Documentos/gitntropy/ntropy
chmod +x ntropy.sh
```

### Passo 2: Executar

```bash
./ntropy.sh
```

**Vantagens:**
- Nativo do Linux, roda perfeitamente
- Mais rápido que Wine
- Usa o Python 3 do sistema
- Não precisa instalar nada extra

---

## 🍷 Método 2 - Rodar .exe Windows via Wine

Se você já tem o `Ntropy.exe` do Windows e quer rodar no Linux:

### Passo 1: Instalar Wine

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install wine wine64

# Fedora
sudo dnf install wine

# Arch
sudo pacman -S wine
```

### Passo 2: Verificar instalação

```bash
wine --version
```

Deve mostrar algo como: `wine-8.0` ou similar.

### Passo 3: Rodar o .exe

```bash
cd /home/olavo/Documentos/gitntropy/ntropy/dist
wine Ntropy.exe
```

**Desvantagens do Wine:**
- Mais lento
- Pode ter problemas de compatibilidade
- Captura de tela pode não funcionar corretamente
- Hotkeys (F3, F4, F9) podem não funcionar

**⚠️ IMPORTANTE:** O método Wine NÃO é recomendado para este app, pois:
- A captura de tela precisa acessar o sistema diretamente
- As hotkeys precisam funcionar a nível de sistema
- O Wine pode bloquear essas funcionalidades

---

## 🚀 Método 3 - Executável Nativo Linux (PyInstaller)

Se quiser criar um executável nativo para Linux (sem precisar do Python instalado):

### Passo 1: Instalar PyInstaller

```bash
cd /home/olavo/Documentos/gitntropy/ntropy
pip3 install pyinstaller
```

### Passo 2: Criar o executável

```bash
pyinstaller --onefile --windowed --name="Ntropy" main.py
```

### Passo 3: Executar

```bash
./dist/Ntropy
```

O executável estará em `dist/Ntropy` (sem extensão .exe).

---

## 📋 Requisitos do Sistema (Linux)

### Pacotes necessários:

```bash
# Ubuntu/Debian
sudo apt install python3 python3-tk python3-pip tesseract-ocr

# Fedora
sudo dnf install python3 python3-tkinter python3-pip tesseract

# Arch
sudo pacman -S python python-tk python-pip tesseract
```

### Bibliotecas Python:

```bash
pip3 install -r requirements.txt
```

Ou manualmente:

```bash
pip3 install Pillow pytesseract pynput psutil
```

---

## 🎮 Detecção de Jogos no Linux

Para detectar os jogos rodando, você precisa ter `xdotool` ou `wmctrl`:

```bash
# Ubuntu/Debian
sudo apt install xdotool wmctrl

# Fedora
sudo dnf install xdotool wmctrl

# Arch
sudo pacman -S xdotool wmctrl
```

**Nota:** Se você roda os jogos via Proton/Wine, o Ntropy conseguirá detectá-los.

---

## 🔧 Problemas Comuns

### "python3: command not found"
```bash
sudo apt install python3
```

### "No module named 'tkinter'"
```bash
sudo apt install python3-tk
```

### "TesseractNotFoundError"
```bash
sudo apt install tesseract-ocr
```

### Hotkeys não funcionam
- Verifique se você tem permissões de entrada
- Alguns ambientes desktop bloqueiam teclas globais
- Execute com `sudo` se necessário (não recomendado, mas funciona)

### Captura de tela não funciona
- Instale `scrot` ou `gnome-screenshot`:
```bash
sudo apt install scrot
```

---

## 📁 Estrutura de Arquivos

```
ntropy/
├── main.py              ← Arquivo principal
├── ntropy.sh            ← Script Linux (RECOMENDADO)
├── ntropy.bat           ← Script Windows
├── config.json          ← Configurações (criado automaticamente)
├── data.json            ← Dados capturados (criado automaticamente)
├── requirements.txt     ← Dependências Python
├── BUILD_WINDOWS.md     ← Tutorial Windows
└── RUN_LINUX.md         ← Este arquivo
```

---

## ⚡ Quick Start (Linux)

Copie e cole no terminal:

```bash
cd /home/olavo/Documentos/gitntropy/ntropy
chmod +x ntropy.sh
./ntropy.sh
```

Pronto! 🎉

---

## 🎯 Recomendação Final

**Para usar no Linux:**
→ Use `./ntropy.sh` (método 1)
→ É nativo, rápido e funciona perfeitamente

**NÃO use Wine** para este app:
→ Problemas com captura de tela
→ Hotkeys podem não funcionar
→ Mais lento e instável

**Se quiser distribuir:**
→ Use PyInstaller para criar executável Linux nativo
→ Ou simplesmente compartilhe o código Python + requirements.txt

---

## 🆘 Precisa de Ajuda?

Se algo não funcionar:

1. Verifique se todos os pacotes estão instalados
2. Teste se o Python funciona: `python3 --version`
3. Teste se o Tkinter funciona: `python3 -m tkinter`
4. Verifique as permissões: `chmod +x ntropy.sh`
5. Execute direto com Python: `python3 main.py`
