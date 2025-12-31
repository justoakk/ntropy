# Como criar executável para Windows

## Opção 1: Executável Auto-Contido (Recomendado)

Cria um `.exe` que **já inclui o Tesseract OCR**. O usuário final apenas baixa e executa.

### Passo 1: Configurar Tesseract

Execute `setup_tesseract.bat` e siga as instruções, ou faça manualmente:

1. Baixe o Tesseract de: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale normalmente
3. Copie os arquivos para a pasta `tesseract/`:

```
tesseract/
├── tesseract.exe
├── *.dll (todas as DLLs)
└── tessdata/
    └── eng.traineddata
```

### Passo 2: Criar o Executável

```bash
build_exe.bat
```

O executável será criado em `dist/Ntropy.exe` (~80-100MB).

### Resultado

- Usuário baixa `Ntropy.exe`
- Executa diretamente
- Funciona sem instalar nada

---

## Opção 2: Executável Simples (Requer Tesseract no sistema)

Para quem já tem Tesseract instalado no Windows.

### Criar o .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Ntropy" main.py
```

O executável estará em `dist/Ntropy.exe` (~30-40MB).

**Nota:** O usuário final precisa ter o Tesseract instalado.

---

## Opção 3: Script .bat (Desenvolvimento)

Para desenvolvimento, use `ntropy.bat`:

```bash
ntropy.bat
```

Requer Python e dependências instaladas.

---

## Arquivos de Build

| Arquivo | Descrição |
|---------|-----------|
| `build_exe.bat` | Cria executável com Tesseract embutido |
| `setup_tesseract.bat` | Ajuda a configurar pasta tesseract/ |
| `ntropy.spec` | Configuração PyInstaller detalhada |
| `ntropy.bat` | Launcher simples (requer Python) |

---

## Estrutura para Distribuição

Ao distribuir, inclua apenas:

```
Ntropy.exe          <- O executável (já contém tudo)
```

Os arquivos `config.json` e `data.json` serão criados automaticamente na primeira execução.

---

## Problemas Comuns

### Antivírus bloqueia o .exe
Normal com PyInstaller. Adicione exceção no antivírus.

### Executável muito grande
O executável com Tesseract embutido tem ~80-100MB. Isso é esperado pois inclui:
- Python runtime
- Bibliotecas (Pillow, pynput, etc)
- Tesseract OCR completo

### OCR não funciona no executável
Verifique se a pasta `tesseract/` foi configurada corretamente antes do build.
