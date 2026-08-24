# Módulo 0 — Diagnóstico e preparação do ambiente

## Objetivo

Preparar um projeto Python isolado e reproduzível, compreender ambientes virtuais e adotar um workflow moderno de dependências com `pyproject.toml`, `uv.lock` e `uv`.

## Ambiente utilizado

- Windows
- PowerShell
- Visual Studio Code
- Python 3.13.3
- Git
- Docker

## Estrutura inicial

```text
mtg-manager/
├── .venv/             # Ambiente virtual local; não é guardado no Git
├── docs/
├── .gitignore
├── README.md
├── pyproject.toml     # Dependências e metadados declarados
└── uv.lock            # Resolução exata das dependências
```

## Repositório Git

```powershell
git init
git status
```

O Git guarda o código e os ficheiros declarativos, mas não deve guardar o ambiente virtual `.venv/`.

Exemplo de primeiro commit:

```powershell
git add .gitignore README.md docs/roadmap.md
git commit -m "chore: initialize project structure"
```

É preferível fazer commits por unidade lógica funcional, e não apenas um commit no fim de cada módulo.

## Ambiente virtual: `.venv`

Um ambiente virtual isola os packages Python de cada projeto, evitando instalações no Python global da máquina.

Criação manual:

```powershell
py -m venv .venv
```

Ativação no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Desativação:

```powershell
deactivate
```

Confirmação do interpretador ativo:

```powershell
python -c "import sys; print(sys.executable)"
```

O resultado deve apontar para `.venv\Scripts\python.exe`.

### Significado de `-m`

`-m` significa **module**. Pede ao Python que procure um módulo e o execute como programa.

```powershell
py -m venv .venv
```

- `py`: launcher de Python do Windows;
- `-m venv`: executa o módulo `venv` da standard library;
- `.venv`: argumento passado ao módulo, indicando a pasta a criar.

Outro exemplo:

```powershell
python -m pip --version
```

Esta forma garante que é utilizado o `pip` pertencente ao interpretador `python` selecionado.

### Significado de `-c`

`-c` significa **command**. Executa diretamente o código Python contido na string seguinte.

```powershell
python -c "import sys; print(sys.executable)"
```

É útil para pequenos diagnósticos sem criar um ficheiro `.py`.

## `pyproject.toml`

`pyproject.toml` é o nome standard que as ferramentas Python procuram automaticamente. TOML significa **Tom's Obvious Minimal Language**.

Exemplo mínimo:

```toml
[project]
name = "mtg-manager"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "Django~=5.2.0",
]
```

O ficheiro declara:

- identidade e versão do projeto;
- versões de Python suportadas;
- dependências diretas da aplicação;
- futuramente, configuração de ferramentas.

O ficheiro não instala nada sozinho. Uma ferramenta como `uv` lê-o e sincroniza o ambiente.

## `uv`

`uv` é o nome de uma ferramenta de gestão de projetos e dependências Python. Não deve ser interpretado como uma sigla com uma expansão necessária.

Neste projeto, automatiza:

- criação ou reutilização de `.venv`;
- adição e remoção de dependências;
- resolução de versões transitivas;
- criação e atualização de `uv.lock`;
- sincronização do ambiente;
- execução de comandos no ambiente correto.

Instalação no Windows com WinGet:

```powershell
winget install --id=astral-sh.uv -e
uv --version
```

Inicialização mínima num repositório existente:

```powershell
uv init --bare --no-package
```

- `--bare`: cria apenas a configuração mínima;
- `--no-package`: não prepara a aplicação para ser publicada como uma biblioteca/package Python.

## Adicionar Django

```powershell
uv add "Django~=5.2.0"
```

O comando atualiza três níveis:

1. `pyproject.toml`: regista a dependência direta e o intervalo aceite;
2. `uv.lock`: regista as versões exatas resolvidas;
3. `.venv`: instala essas versões no ambiente local.

`Django~=5.2.0` permite versões `>=5.2.0` e `<5.3.0`. O lock file escolhe e fixa uma versão concreta dentro desse intervalo.

## Compreender `uv run`

`uv run <comando>` executa um comando dentro do ambiente sincronizado do projeto.

```powershell
uv run python -m django --version
```

Decomposição:

- `uv run`: encontra o projeto, verifica/sincroniza `.venv` e executa o restante comando nesse ambiente;
- `python`: inicia o Python de `.venv`;
- `-m django`: executa o módulo `django`;
- `--version`: pede ao Django que apresente a versão.

O objetivo do comando é simultaneamente confirmar que Django está instalado e que o `uv` está a utilizar o ambiente correto.

Com o `.venv` ativado, também seria possível executar:

```powershell
python -m django --version
```

`uv run` evita depender da ativação manual do ambiente, algo especialmente útil em scripts e CI/CD.

Outras verificações:

```powershell
uv run python -c "import sys; print(sys.executable)"
uv tree
```

`uv tree` mostra as dependências diretas e transitivas resolvidas.

## Workflow diário

Adicionar uma dependência:

```powershell
uv add <package>
```

Remover uma dependência:

```powershell
uv remove <package>
```

Reconstruir/sincronizar o ambiente depois de clonar ou mudar de branch:

```powershell
uv sync
```

Executar um comando no ambiente:

```powershell
uv run <comando>
```

Os ficheiros `pyproject.toml` e `uv.lock` devem ser guardados no Git. `.venv/` deve permanecer ignorado.

## CI/CD

O uso de `uv` não dificulta uma pipeline. O fluxo base é direto:

```text
checkout do repositório
→ instalar uv
→ uv sync --locked
→ uv run <testes ou comandos>
```

`--locked` faz a pipeline falhar se `pyproject.toml` e `uv.lock` estiverem dessincronizados, em vez de alterar o lock file durante o build.

Exemplo conceptual:

```powershell
uv sync --locked
uv run python -m django check
uv run pytest
```

Ainda não instalámos `pytest`; o comando aparece apenas como exemplo futuro. `pytest` é aproximadamente equivalente ao xUnit no ecossistema .NET, embora Django também inclua ferramentas de teste baseadas em `unittest`.

Se uma plataforma aceitar apenas `requirements.txt`, este pode ser exportado a partir da fonte principal em vez de ser mantido manualmente:

```powershell
uv export --format requirements-txt --output-file requirements.txt
```

## Modelo mental final

```text
pyproject.toml  → o que o projeto aceita
uv.lock         → versões concretas escolhidas
.venv           → packages instalados localmente
uv              → ferramenta que mantém tudo sincronizado
uv run          → execução dentro do ambiente do projeto
```

## Comandos de validação

```powershell
uv --version
Get-Content pyproject.toml
uv tree
uv run python -m django --version
uv run python -c "import sys; print(sys.executable)"
git status
```

## Pontos a recordar

- `.venv` é descartável; o código do projeto não vive dentro dele.
- `pyproject.toml` é declarativo e deve ser versionado.
- `uv.lock` garante instalações reproduzíveis e deve ser versionado para esta aplicação.
- `uv run` torna explícito que o comando deve usar o ambiente do projeto.
- Dependências diretas e transitivas são conceitos diferentes.
- O lock file não impede atualizações; torna-as deliberadas e controladas.
