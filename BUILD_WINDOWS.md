# Como criar executável para Windows

## Método 1 - Script .bat (Mais simples)

✅ **Já está pronto!** Basta clicar duas vezes em `ntropy.bat`

**Vantagens:**
- Instantâneo, não precisa compilar
- Fácil de modificar código
- Funciona imediatamente

**Desvantagens:**
- Precisa do Python instalado
- Abre janela do terminal

---

## Método 2 - Executável .exe (Recomendado para distribuição)

### Passo 1: Instalar PyInstaller

Abra o CMD/PowerShell e execute:
```bash
pip install pyinstaller
```

### Passo 2: Criar o .exe

**Opção A - Executável único (mais simples):**
```bash
cd C:\caminho\para\ntropy
pyinstaller --onefile --windowed --name="Ntropy" main.py
```

**Opção B - Com todas as dependências separadas:**
```bash
pyinstaller --windowed --name="Ntropy" main.py
```

### Passo 3: Encontrar o executável

Após a compilação:
- O executável estará em: `dist\Ntropy.exe`
- Você pode copiar esse arquivo para qualquer lugar
- **IMPORTANTE**: Copie também `config.json` e `data.json` junto

---

## Método 3 - Executável com Ícone personalizado

1. Baixe/crie um ícone `.ico` e salve como `icon.ico` na pasta ntropy
2. Execute:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="Ntropy" main.py
```

---

## Problemas comuns

### "Python não é reconhecido como comando"
→ Python não está instalado ou não está no PATH
→ Baixe em: https://www.python.org/downloads/
→ Durante instalação, marque "Add Python to PATH"

### "pip não é reconhecido como comando"
→ Execute: `python -m pip install pyinstaller`

### Executável muito grande (>100MB)
→ É normal! PyInstaller inclui o Python inteiro
→ Use `--onefile` para um único arquivo

### Antivírus bloqueia o .exe
→ Normal com PyInstaller
→ Adicione exceção no antivírus
→ Ou use o script `.bat` que não tem esse problema

---

## Estrutura para distribuição

Ao distribuir o app, inclua:
```
Ntropy/
├── Ntropy.exe          ← Executável
├── config.json         ← Configurações (será criado na 1ª execução)
├── data.json           ← Dados (será criado na 1ª captura)
└── README.txt          ← Instruções para o usuário
```

---

## Comandos úteis PyInstaller

```bash
# Básico
pyinstaller main.py

# Um arquivo único + sem console
pyinstaller --onefile --windowed main.py

# Com nome personalizado
pyinstaller --onefile --windowed --name="Ntropy" main.py

# Com ícone
pyinstaller --onefile --windowed --icon=icon.ico --name="Ntropy" main.py

# Limpar builds anteriores
rmdir /s /q build dist
del *.spec
```

---

## Recomendação final

**Para você usar:**
→ Use `ntropy.bat` (mais prático durante desenvolvimento)

**Para distribuir para outras pessoas:**
→ Use PyInstaller e crie `Ntropy.exe`
→ Assim elas não precisam instalar Python
