# RPA UiBank

![CI](https://github.com/EdisonCintra/rpa-uibank/actions/workflows/ci.yml/badge.svg)

Automação RPA que baixa uma planilha de solicitações de empréstimo do Google
Drive, preenche o formulário de empréstimo do UiBank para cada solicitante,
captura o resultado retornado pelo próprio site e grava esse resultado de
volta na planilha original.

## Objetivo

Teste técnico para vaga de Programador RPA. Fluxo completo:

1. Baixar a planilha de solicitantes de uma pasta do Google Drive.
2. Ler e validar os dados de cada solicitante (fail-fast).
3. Preencher o formulário de empréstimo em
   `https://uibank.uipath.com/loans/apply` para cada um.
4. Capturar o resultado (aprovado/negado) devolvido pelo próprio UiBank —
   nenhuma decisão de negócio é calculada por este projeto.
5. Exibir o resultado no console e gravá-lo de volta na planilha.

## Tecnologias

- **Python 3.12+** (testado em 3.12 e 3.13)
- **Selenium** — navegação e leitura de elementos da página
- **PyAutoGUI** — digitação em nível de sistema operacional
- **pandas** / **openpyxl** — leitura e escrita da planilha `.xlsx`
- **pytest** — testes unitários com mocks, sem depender de navegador
- **uv** (opcional) — ambiente virtual e gerenciamento de dependências
  (alternativa: `python -m venv` + `pip`)

## Estrutura

```
src/
├── config.py               # constantes e configuração do Chrome
├── downloader.py           # baixa a planilha do Drive
├── reader.py                # lê e valida a planilha
├── formulario.py            # preenche e submete o formulário
├── resultado.py              # captura o resultado + evidência (screenshot)
├── atualizador_planilha.py    # grava o resultado de volta na planilha
└── main.py                    # orquestrador — chama os módulos em ordem

tests/                        # 16 testes, sem navegador nem internet
```

## Como rodar

### Pré-requisitos

- **Python 3.12+** (obrigatório).
- **Google Chrome** instalado — o Selenium Manager cuida do chromedriver
  automaticamente, mas o navegador precisa existir na máquina.
- **Tela gráfica real** (não headless) e teclado/mouse livres durante a
  execução — o PyAutoGUI digita em nível de SO.
- Acesso de rede à pasta pública do Google Drive e ao formulário do UiBank.

### Instalação

```bash
git clone https://github.com/EdisonCintra/rpa-uibank.git
cd rpa-uibank

# opção A — com uv (https://docs.astral.sh/uv/)
uv venv
uv pip install -r requirements.txt

# opção B — com venv + pip (sem uv)
python -m venv .venv
# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt
# Linux/Mac
.venv/bin/python -m pip install -r requirements.txt
```

### Executar o fluxo

```bash
# Windows
.venv\Scripts\python.exe -m src.main

# Linux/Mac
.venv/bin/python -m src.main
```

> **Importante:** sempre rode como módulo (`-m src.main`), nunca
> `python src/main.py` direto — isso quebra os imports internos
> (`from src.config import ...`), porque o Python coloca `src/` no
> `sys.path` em vez da raiz do projeto quando o arquivo é executado
> diretamente.

Ao rodar, uma janela do Chrome é aberta pra cada solicitante processado —
**não interaja com o teclado/mouse durante a execução**, já que o PyAutoGUI
atua em nível de sistema operacional.

## Rodando os testes

```bash
# instalar dependências (uv OU pip)
uv pip install -r requirements.txt
# ou:  .venv\Scripts\python.exe -m pip install -r requirements.txt

.venv\Scripts\python.exe -m pytest tests/ -v
.venv\Scripts\python.exe -m flake8 src/ tests/ --max-line-length=100
```

## Além do que foi pedido

O enunciado original pedia até: baixar a planilha, extrair os dados,
preencher o formulário, enviar e **exibir o resultado no console**. Pra
deixar o projeto mais completo, também foram adicionados:

- **Grava o resultado de volta na planilha** (`atualizador_planilha.py`) —
  a planilha baixada já vinha com as colunas `Status do Empréstimo`, `ID do
  Empréstimo` e `APR` vazias, então a automação as preenche sozinha ao
  final, inclusive nos casos negados (mostrando o motivo da recusa em vez
  de deixar as células em branco).
- **Evidência em screenshot por solicitante** — cada resultado gera uma
  captura de tela nomeada com o e-mail e o status (ex.:
  `maria_aprovado_....png`), pra facilitar auditoria.
- **Tradução automática do motivo de recusa** — o UiBank devolve a
  mensagem de negação em inglês; o projeto traduz pra português antes de
  exibir no console e gravar na planilha.
- **Saída no console alinhada** em colunas, mais fácil de ler quando há
  vários solicitantes de uma vez.
- **Suíte de 16 testes automatizados** (sem precisar de navegador) e **CI
  no GitHub Actions**, rodando lint e testes a cada push.

## CI

O GitHub Actions (`.github/workflows/ci.yml`) roda lint (`flake8`) e os 16
testes automatizados a cada `push`/`pull request`. O fluxo completo
(`main.py`) não roda em CI, porque depende de acesso real ao Google
Drive/UiBank via navegador — algo que não faz sentido automatizar num runner
sem interação.

## Limitações conhecidas

- `formulario.py` usa `pygetwindow` para contornar um comportamento
  específico de foco de janela do **Windows** — foi desenvolvido e validado
  nesse sistema operacional. `pyautogui`/`pygetwindow` também exigem uma
  tela real (não funcionam em modo totalmente headless).
- Não há segredos/credenciais no projeto — a pasta do Drive e o formulário
  do UiBank são públicos, por isso não é necessário nenhum arquivo `.env`.
