# Como Publicar uma Release

Guia para criar releases do Ntropy no GitHub.

## Passo 1: Gerar o Executável

No Windows, na pasta do projeto:

```bash
# Primeira vez: configurar Tesseract
setup_tesseract.bat

# Gerar o executável
build_exe.bat
```

O executável será criado em `dist/Ntropy.exe`

## Passo 2: Commit e Tag

```bash
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

**Dica:** Use versionamento semântico:
- `v1.0.0` → Versão inicial
- `v1.0.1` → Correção de bugs
- `v1.1.0` → Novas funcionalidades
- `v2.0.0` → Mudanças grandes/incompatíveis

## Passo 3: Criar Release no GitHub

1. Acesse seu repositório no GitHub
2. Clique em **Releases** (na barra lateral direita)
3. Clique em **Create a new release**
4. Preencha:
   - **Tag**: Selecione `v1.0.0`
   - **Título**: `Ntropy v1.0.0`
   - **Descrição**: Escreva as novidades (veja modelo abaixo)
5. Em **Attach binaries**, arraste o arquivo `dist/Ntropy.exe`
6. Clique em **Publish release**

## Modelo de Descrição

```markdown
## O que há de novo

- Funcionalidade X adicionada
- Bug Y corrigido
- Melhoria Z implementada

## Download

Baixe o `Ntropy.exe` abaixo e execute. Não precisa instalar nada!

## Requisitos

- Windows 10/11
```

## Resultado

Após publicar, os usuários podem baixar em:

```
https://github.com/SEU_USUARIO/ntropy/releases/latest
```

Ou link direto para o arquivo:

```
https://github.com/SEU_USUARIO/ntropy/releases/download/v1.0.0/Ntropy.exe
```

## Checklist de Release

- [ ] Testar o programa localmente
- [ ] Gerar executável com `build_exe.bat`
- [ ] Testar o executável gerado
- [ ] Criar commit e tag
- [ ] Push para o GitHub
- [ ] Criar release e anexar .exe
- [ ] Testar download da release
