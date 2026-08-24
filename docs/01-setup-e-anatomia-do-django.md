# Módulo 1 — Setup e anatomia do Django

## Objetivo

Criar o Django project, compreender os ficheiros gerados, distinguir project de app e seguir um pedido HTTP desde o routing até uma view.

## Estado inicial

- Python 3.13
- Django 5.2
- Dependências geridas com `uv`
- Package de configuração: `config`
- Primeira Django app: `cards`

## 1. Project e app

Na terminologia Django:

- **project**: aplicação web completa e respetiva configuração global;
- **app**: módulo funcional integrado no project.

```text
MTG Manager (project)
├── config
├── cards (app)
├── collections (app futura)
└── decks (app futura)
```

Uma app pode conter models, views, URLs, templates, migrations, comandos, integração com o admin e testes. Não é obrigada a expor endpoints: pode fornecer apenas persistência, regras de domínio ou tarefas internas.

A aproximação em .NET é uma feature ou módulo funcional; em alguns casos, pode recordar uma class library, embora a equivalência não seja exata.

## 2. Criar o Django project

```powershell
uv run django-admin startproject config .
```

- `uv run`: executa no ambiente do projeto;
- `django-admin`: CLI geral instalada com Django;
- `startproject`: cria o scaffold de um Django project;
- `config`: nome do package de configuração;
- `.`: cria os ficheiros no diretório atual.

Estrutura criada:

```text
manage.py
config/
├── __init__.py
├── asgi.py
├── settings.py
├── urls.py
└── wsgi.py
```

## 3. `django-admin` e `manage.py`

`django-admin` é a ferramenta geral disponível depois de instalar Django. Foi necessária para criar o project, pois ainda não existia `manage.py`.

`manage.py` é o wrapper específico deste project. Define o módulo de settings e entrega os argumentos ao sistema de management commands do Django.

```text
django-admin
→ CLI geral do framework

python manage.py
→ CLI associada a config.settings
```

Exemplos:

```powershell
uv run python manage.py check
uv run python manage.py runserver
uv run python manage.py startapp cards
```

## 4. Anatomia de `manage.py`

A linha principal de configuração é:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
```

Isto indica ao processo Python que o módulo de configuração é `config.settings`. A alteração existe no ambiente do processo atual, não é gravada globalmente no Windows e não modifica retroativamente a sessão PowerShell.

Depois é importada uma função do Django:

```python
from django.core.management import execute_from_command_line
```

Ela recebe `sys.argv`, identifica o management command e encaminha a execução para o comando correspondente:

```text
python manage.py check
→ sys.argv contém "check"
→ Django encontra o comando check
→ executa a validação
```

O bloco:

```python
if __name__ == "__main__":
    main()
```

chama `main()` apenas quando `manage.py` é executado diretamente. Num import normal, o código de topo do módulo é processado, mas `main()` não é chamada por este bloco.

## 5. `config/__init__.py`

O ficheiro identifica `config` como package Python tradicional. Por isso são possíveis imports como:

```python
from config import settings
```

Estar vazio é normal. Se contivesse código de topo, esse código seria executado quando o package fosse importado pela primeira vez no processo.

## 6. Settings principais

`config/settings.py` é código Python executável usado para configurar o runtime Django.

| Setting | Responsabilidade |
|---|---|
| `BASE_DIR` | Raiz do repositório |
| `SECRET_KEY` | Assinaturas de segurança do Django |
| `DEBUG` | Comportamento detalhado de desenvolvimento |
| `ALLOWED_HOSTS` | Hosts HTTP aceites |
| `INSTALLED_APPS` | Django apps ativadas |
| `MIDDLEWARE` | Pipeline HTTP |
| `ROOT_URLCONF` | Ponto de entrada do routing |
| `TEMPLATES` | Configuração de templates |
| `DATABASES` | Ligações à base de dados |
| `LANGUAGE_CODE` | Idioma por omissão |
| `TIME_ZONE` | Fuso horário |
| `STATIC_URL` | Prefixo dos assets estáticos |

### `BASE_DIR`

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Parte de `config/settings.py` e sobe duas pastas para obter a raiz do repositório.

### Segurança de desenvolvimento

```python
DEBUG = True
```

É útil localmente, mas não deve ser usado em produção porque as páginas de erro podem expor informação interna. A `SECRET_KEY` de produção também não deve ficar escrita no repositório.

### `INSTALLED_APPS`

```text
uv add <package>
→ instala uma dependência Python

INSTALLED_APPS
→ ativa uma Django app no runtime
```

Nem todos os packages Python são Django apps e nem todos precisam de aparecer em `INSTALLED_APPS`.

### `MIDDLEWARE`

Middleware são componentes ordenados que processam pedidos e respostas:

```text
Request
→ Middleware A
→ Middleware B
→ View
→ Middleware B
→ Middleware A
→ Response
```

Podem ser fornecidos pelo Django, por terceiros ou pelo próprio projeto. Também podem interromper a pipeline e devolver uma resposta antes da view.

## 7. Criar a app `cards`

```powershell
uv run python manage.py startapp cards
```

Estrutura criada:

```text
cards/
├── migrations/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

`urls.py` não é criado, porque uma Django app não é obrigada a expor endpoints.

### `CardsConfig`

```python
from django.apps import AppConfig


class CardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cards"
```

`AppConfig` é uma classe-base do sistema de apps do Django. O comando `startapp cards` gerou automaticamente `CardsConfig` e `name = "cards"`.

Registo explícito em `config/settings.py`:

```python
INSTALLED_APPS = [
    # Apps Django...
    "cards.apps.CardsConfig",
]
```

Também seria possível usar apenas `"cards"`, permitindo a descoberta automática da configuração.

## 8. Primeira view

`cards/views.py`:

```python
from django.http import HttpResponse


def index(request):
    return HttpResponse("MTG Manager — Card catalogue")
```

O nome `index` foi escolhido pelo developer; Django não procura obrigatoriamente uma função com esse nome.

A view recebe um `HttpRequest` e devolve um `HttpResponse`:

```text
input:  request
output: response
```

O Django constrói o request, executa middleware, resolve a URL e chama conceptualmente:

```python
response = views.index(request)
```

O import `render` criado pelo scaffold foi removido porque ainda não estamos a renderizar um template.

## 9. Routing da app

Foi criado manualmente `cards/urls.py`:

```python
from django.urls import path

from . import views


app_name = "cards"

urlpatterns = [
    path("", views.index, name="index"),
]
```

- `path` é uma função que cria uma regra de routing;
- `urlpatterns` é a lista ordenada de regras;
- `app_name` cria o namespace de nomes de rotas, não um prefixo URL;
- `name="index"` permite referir a rota como `cards:index`.

## 10. Routing global

`config/urls.py` delega o prefixo à app:

```python
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("cards/", include("cards.urls")),
]
```

Para `GET /cards/`:

```text
config/urls.py corresponde a "cards/"
→ include entrega o restante caminho a cards/urls.py
→ cards/urls.py corresponde a ""
→ Django chama views.index(request)
→ a view devolve HttpResponse
```

A app é ligada ao routing global uma vez. Novas rotas de cards são depois adicionadas apenas a `cards/urls.py`:

```python
urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("<int:card_id>/", views.detail, name="detail"),
]
```

## 11. Servidor de desenvolvimento

```powershell
uv run python manage.py runserver
```

Por omissão, fica disponível em:

```text
http://127.0.0.1:8000/
```

- `127.0.0.1`: loopback/local machine;
- `8000`: porta predefinida de `runserver`.

Alterar a porta:

```powershell
uv run python manage.py runserver 5000
```

`runserver` é apenas para desenvolvimento. Não oferece a robustez, segurança e gestão de processos esperadas em produção.

O URL configurado neste módulo é:

```text
http://127.0.0.1:8000/cards/
```

O `CommonMiddleware` pode redirecionar `/cards` para `/cards/` quando existe uma rota válida com a barra final.

## 12. WSGI e ASGI

WSGI e ASGI são contratos entre um servidor de aplicação Python e Django. Não são servidores nem reverse proxies.

```text
Cliente
→ reverse proxy opcional
→ servidor de aplicação Python
→ WSGI ou ASGI
→ Django
```

### WSGI

**Web Server Gateway Interface**: interface tradicional e síncrona para aplicações web Python.

`config/wsgi.py` define as settings e expõe:

```python
application = get_wsgi_application()
```

Um servidor WSGI pode carregar o objeto através da referência:

```text
config.wsgi:application
```

### ASGI

**Asynchronous Server Gateway Interface**: interface com suporte assíncrono, WebSockets, eventos e conexões duradouras.

`config/asgi.py` expõe:

```python
application = get_asgi_application()
```

Um servidor ASGI pode carregar:

```text
config.asgi:application
```

Uma aplicação não fica automaticamente mais rápida por usar ASGI. A escolha depende dos requisitos e será retomada no deployment.

## 13. Comparações aproximadas com ASP.NET Core

| Django | ASP.NET Core |
|   ---  |     ---      |
| `settings.py` | `appsettings` + configuração em `Program.cs` |
| URLconf | Endpoint routing |
| Django view | Controller action/handler |
| `HttpResponse` | `IActionResult`/resultado HTTP |
| Middleware | Middleware ASP.NET Core |
| Django app | Feature ou módulo funcional |
| Servidor WSGI/ASGI | Papel parcialmente semelhante a Kestrel |

Estas são analogias de aprendizagem, não equivalências exatas.

## 14. Ciclo completo do primeiro pedido

```text
Browser envia GET /cards/
→ servidor de desenvolvimento recebe o pedido
→ Django cria HttpRequest
→ middleware processa o pedido
→ config.urls delega "cards/"
→ cards.urls encontra a rota vazia
→ Django chama cards.views.index(request)
→ a view cria HttpResponse
→ middleware processa a resposta no regresso
→ browser apresenta o texto
```

## 15. Comandos de validação

```powershell
uv run python manage.py check
uv run python manage.py runserver
```

Verificação opcional dos entry points:

```powershell
uv run python -c "from config.wsgi import application; print(type(application))"
uv run python -c "from config.asgi import application; print(type(application))"
```

## Pontos essenciais a recordar

1. O project representa a aplicação completa; uma app representa uma área funcional.
2. `manage.py` executa comandos no contexto de `config.settings`.
3. `INSTALLED_APPS` ativa apps; não instala packages Python.
4. `MIDDLEWARE` define uma pipeline ordenada de pedido e resposta.
5. O URLconf mapeia caminhos para views e pode delegar routing com `include`.
6. Uma view recebe um request e devolve uma response.
7. `runserver` é apenas um servidor de desenvolvimento.
8. WSGI e ASGI são contratos usados por servidores para carregar Django.
