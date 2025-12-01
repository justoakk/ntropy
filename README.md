# Ntropy

Aplicação desktop para capturar e armazenar valores numéricos da tela usando OCR (Reconhecimento Óptico de Caracteres).

## Funcionalidades

- **Captura de Valores**: Capture números de uma região específica da tela
- **OCR Automático**: Reconhecimento de números usando Tesseract OCR
- **Histórico**: Armazene e visualize todas as capturas com data/hora
- **Estatísticas**: Veja total, média, mínimo e máximo dos valores capturados
- **Atalho Rápido**: Use F9 para capturar rapidamente
- **Exportação**: Exporte o histórico para CSV
- **Interface Simples**: Interface gráfica intuitiva e fácil de usar

## Requisitos do Sistema

### Sistema Operacional
- Linux (Ubuntu/Debian testado)
- Windows (deve funcionar, mas não testado)
- macOS (deve funcionar, mas não testado)

### Software Necessário
- **Python 3.8 ou superior**
- **Tesseract OCR** (pacote do sistema)

## Instalação

### 1. Instalar Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

#### Fedora/RHEL:
```bash
sudo dnf install tesseract tesseract-langpack-por
```

#### Windows:
- Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
- Instale e adicione ao PATH

#### macOS:
```bash
brew install tesseract
```

### 2. Instalar Dependências Python

```bash
cd cash_tracker
pip install -r requirements.txt
```

Ou instale manualmente:
```bash
pip install Pillow pytesseract pynput
```

## Uso

### Primeira Execução

1. **Iniciar a aplicação:**
   ```bash
   python main.py
   ```

2. **Configurar a região de captura:**
   - Na primeira execução, você será solicitado a configurar a região
   - Uma tela semi-transparente aparecerá sobre toda a tela
   - Clique e arraste para selecionar a área onde os números aparecem
   - Pressione **ENTER** para confirmar ou **ESC** para cancelar

3. **Testar a captura:**
   - Clique no botão **CAPTURAR** ou pressione **F9**
   - O valor será extraído e aparecerá no histórico

### Uso Diário

1. **Abra a aplicação:**
   ```bash
   python main.py
   ```

2. **Capturar valores:**
   - Pressione **F9** a qualquer momento (funciona mesmo com a janela minimizada)
   - Ou clique no botão **CAPTURAR**

3. **Ver histórico:**
   - Todos os valores capturados aparecem na tabela
   - Clique com botão direito em uma entrada para deletar

4. **Exportar dados:**
   - Menu: **Dados** → **Exportar para CSV**
   - Escolha o local para salvar o arquivo

### Atalhos

- **F9**: Capturar valor
- **Ctrl+C**: Copiar (quando tabela está selecionada)
- **ESC**: Cancelar seleção de região

## Configurações

### Menu Configurações

- **Configurar Região**: Redefinir a área de captura
- **Sempre no Topo**: Manter janela sempre visível
- **Testar OCR**: Verificar se o Tesseract está funcionando

### Menu Dados

- **Exportar para CSV**: Exportar histórico completo
- **Limpar Histórico**: Deletar todos os dados (irreversível)

## Estrutura de Arquivos

```
cash_tracker/
├── main.py              # Ponto de entrada da aplicação
├── gui.py               # Interface gráfica principal
├── capture.py           # Módulo de captura de tela
├── ocr_processor.py     # Processamento OCR
├── storage.py           # Gerenciamento de dados
├── region_selector.py   # Seletor de região interativo
├── config.json          # Configurações (criado automaticamente)
├── data.json            # Dados de captura (criado automaticamente)
├── requirements.txt     # Dependências Python
└── README.md            # Este arquivo
```

## Solução de Problemas

### OCR não está funcionando

**Sintoma:** Mensagem "Não foi possível ler o número"

**Soluções:**
1. Verifique se o Tesseract está instalado:
   ```bash
   tesseract --version
   ```

2. Teste o OCR pelo menu: **Configurações** → **Testar OCR**

3. Certifique-se de que os números na tela estão:
   - Claros e legíveis
   - Em fonte grande o suficiente
   - Com bom contraste (texto escuro em fundo claro ou vice-versa)

### Região configurada está errada

**Solução:** Menu **Configurações** → **Configurar Região** para redefinir

### Atalho F9 não funciona

**Causa:** Biblioteca `pynput` pode não estar instalada

**Solução:**
```bash
pip install pynput
```

### Valores capturados estão incorretos

**Causas possíveis:**
1. Região de captura inclui elementos além dos números
2. Números têm fonte complexa ou estilizada
3. Baixo contraste entre texto e fundo

**Soluções:**
1. Redefina a região para capturar apenas os números
2. Ajuste as configurações do jogo para melhor contraste
3. Aumente o tamanho da fonte no jogo se possível

### Erro de permissão no Linux

**Sintoma:** Erro ao capturar tela

**Solução:** Pode ser necessário rodar com permissões de captura de tela. No Wayland, alguns jogos podem bloquear captura.

## Dicas de Uso

1. **Melhor Precisão OCR:**
   - Use fontes simples e claras
   - Mantenha bom contraste
   - Capture apenas a área necessária

2. **Performance:**
   - Feche outras aplicações pesadas durante o uso
   - A captura leva 1-3 segundos dependendo do hardware

3. **Backup:**
   - Exporte regularmente para CSV
   - Os arquivos `config.json` e `data.json` podem ser copiados para backup

## Desenvolvimento

### Estrutura do Código

- **main.py**: Inicialização e verificação de dependências
- **gui.py**: Interface Tkinter e coordenação geral
- **capture.py**: Captura de tela usando Pillow
- **ocr_processor.py**: Extração de números com pytesseract
- **storage.py**: Persistência em JSON
- **region_selector.py**: Interface de seleção de região

### Melhorias Futuras

- [ ] Suporte a múltiplas regiões
- [ ] Gráficos e tendências
- [ ] Temas personalizáveis
- [ ] Sincronização em nuvem
- [ ] Captura automática (detecção de mudança)
- [ ] Suporte a múltiplos monitores

## Licença

Este projeto é fornecido "como está" sem garantias.

## Suporte

Para problemas ou sugestões, crie um relatório detalhado incluindo:
- Sistema operacional e versão
- Versão do Python (`python --version`)
- Versão do Tesseract (`tesseract --version`)
- Descrição do problema
- Mensagens de erro (se houver)

---

**Desenvolvido com Python, Tkinter e Tesseract OCR**
