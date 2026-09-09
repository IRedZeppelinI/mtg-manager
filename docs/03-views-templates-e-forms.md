# Módulo 3 — Views, templates e forms

## Objetivo

Construir o primeiro fluxo web completo do MTG Manager: receber um pedido HTTP, resolver a respetiva rota, consultar dados através do ORM, renderizar HTML e processar um formulário de criação com validação e proteção CSRF.

O módulo cobre os fundamentos necessários para avançar com aplicações Django server-rendered sem transformar o projeto de aprendizagem num CRUD completo.

## 1. Fluxo geral de um pedido

Quando o browser pede:

```text
http://127.0.0.1:8000/cards/
```

o fluxo conceptual é:

```text
Browser
→ middleware
→ config/urls.py
→ cards/urls.py
→ view
→ ORM
→ template + context
→ HttpResponse com HTML
→ browser
```

As responsabilidades principais são:

| Componente | Responsabilidade |
|---|---|
| URLconf | Associar um padrão de URL a uma view |
| View | Receber o pedido, coordenar lógica e devolver uma resposta |
| Model/ORM | Ler e persistir dados |
| Context | Transportar objetos Python para o template |
| Template | Produzir a apresentação HTML |
| Form | Receber, converter e validar dados submetidos |

Uma aproximação útil a ASP.NET Core é tratar a view Django como próxima de uma action de controller. A equivalência não é exata: uma view pode devolver HTML, JSON, um redirecionamento ou qualquer outro `HttpResponse`.

## 2. Registo da app

A app `cards` já estava registada em `config/settings.py`:

```python
INSTALLED_APPS = [
    # Apps Django...
    "cards.apps.CardsConfig",
]
```

Não se altera `INSTALLED_APPS` sempre que se cria uma view, rota ou template. O registo é feito uma vez e permite ao Django descobrir a configuração, models, migrations e templates da app.

## 3. URLconf do projeto e da app

O URLconf do projeto delega o prefixo `cards/` na app:

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("cards/", include("cards.urls")),
]
```

`include()` permite que a app mantenha as suas próprias rotas. Para `/cards/`, o URLconf do projeto consome `cards/` e entrega a parte restante a `cards.urls`.

```python
# cards/urls.py
from django.urls import path

from . import views


app_name = "cards"

urlpatterns = [
    path("", views.card_list, name="list"),
    path("new/", views.card_create, name="create"),
]
```

### `urlpatterns`

É a lista ordenada de regras que o Django procura num URLconf. Cada chamada a `path()` cria uma regra.

```python
path("", views.card_list, name="list")
```

Os argumentos principais são:

| Argumento | Função |
|---|---|
| `route` | Padrão de URL relativo ao prefixo já consumido |
| `view` | Função chamada quando há correspondência |
| `name` | Nome simbólico usado para resolução reversa |

Passamos uma referência à função:

```python
views.card_list
```

e não a executamos:

```python
views.card_list()
```

O Django chamará a view quando existir um pedido compatível.

### Composição dos URLs

```text
config/urls.py:  cards/
cards/urls.py:   ""
URL final:       /cards/

config/urls.py:  cards/
cards/urls.py:   new/
URL final:       /cards/new/
```

### Namespace e nomes das rotas

```python
app_name = "cards"
```

cria um namespace para os nomes das rotas. Não cria o prefixo `/cards/`.

Com:

```python
path("", views.card_list, name="list")
```

o nome completo é:

```text
cards:list
```

Isto evita colisões futuras:

```text
cards:list
decks:list
collections:list
```

Uma rota nomeada pode ser resolvida no template:

```django
{% url "cards:list" %}
```

ou em Python:

```python
from django.urls import reverse

reverse("cards:list")
```

Assim, o código não fica dependente de URLs literais espalhados pelo projeto.

## 4. Views e `HttpRequest`

A view de listagem:

```python
from django.shortcuts import render

from .models import Card


def card_list(request):
    cards = Card.objects.all().order_by("name")

    context = {
        "cards": cards,
    }

    return render(request, "cards/card_list.html", context)
```

Uma view recebe um `HttpRequest` e deve devolver um `HttpResponse`.

O pedido contém informação como:

```python
request.method
request.path
request.GET
request.POST
request.headers
request.user
```

Para a página de listagem:

```text
request.method → "GET"
request.path   → "/cards/"
```

### Ordenação

```python
Card.objects.all().order_by("name")
```

constrói um QuerySet ordenado alfabeticamente por `name`. Sem `order_by()`, não se deve assumir uma ordem estável dos resultados da base de dados.

## 5. Context

O contexto é um dicionário que associa nomes usados no template a objetos Python:

```python
context = {
    "cards": cards,
}
```

Neste exemplo:

```text
"cards" → nome disponível no template
cards   → QuerySet criado na view
```

O contexto não constrói a query. A query foi construída anteriormente pelo ORM. O contexto transporta o QuerySet para o template.

A chave não precisa de ter o mesmo nome da variável Python, mas fazê-lo melhora a clareza.

## 6. `render()`

A assinatura relevante é:

```python
render(
    request,
    template_name,
    context=None,
    content_type=None,
    status=None,
    using=None,
)
```

Uso habitual:

```python
return render(request, "cards/card_list.html", context)
```

| Argumento | Responsabilidade |
|---|---|
| `request` | Pedido atual, usado na renderização dependente do request e pelos context processors |
| `template_name` | Nome lógico do template a localizar |
| `context` | Dicionário de valores disponíveis no template |
| `content_type` | Tipo MIME opcional; normalmente `text/html` |
| `status` | Status HTTP opcional; por omissão `200` |
| `using` | Template engine opcional quando existem vários |

Conceptualmente, `render()`:

```text
localiza o template
→ combina template, context e request
→ produz uma string HTML
→ coloca-a num HttpResponse
→ devolve a resposta
```

O `request` não é enviado novamente: é usado para construir a resposta correspondente. Permite também que context processors forneçam dados dependentes do pedido e participa em funcionalidades como o suporte CSRF.

## 7. Descoberta de templates

O diretório `templates` não é criado por `startapp`; deve ser criado manualmente. Não necessita de `__init__.py`, porque contém recursos e não módulos Python.

### Templates específicos da app

```text
cards/
└── templates/
    └── cards/
        ├── card_list.html
        └── card_form.html
```

A segunda pasta `cards` funciona como namespace convencional e evita colisões com templates de outras apps.

```python
render(request, "cards/card_list.html", context)
```

### Templates globais

O layout geral foi colocado na raiz do projeto:

```text
mtg-manager/
├── cards/
├── config/
├── templates/
│   └── base.html
└── manage.py
```

Em `config/settings.py`:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

Os dois mecanismos são complementares:

| Configuração | Pesquisa |
|---|---|
| `DIRS` | Diretórios globais indicados explicitamente |
| `APP_DIRS=True` | Pastas `templates` das apps instaladas |

## 8. Template inheritance

`templates/base.html` contém a estrutura comum:

```django
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>
        {% block title %}MTG Manager{% endblock %}
    </title>
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'cards:list' %}">MTG Manager</a>
        </nav>
    </header>

    <main>
        {% block content %}
        {% endblock %}
    </main>
</body>
</html>
```

Um `block` define uma região que templates descendentes podem substituir:

```django
{% block content %}
{% endblock %}
```

Um bloco pode incluir conteúdo por omissão:

```django
{% block title %}MTG Manager{% endblock %}
```

O template descendente declara a herança no início:

```django
{% extends "base.html" %}
```

e substitui os blocos necessários:

```django
{% block title %}Cards — MTG Manager{% endblock %}

{% block content %}
    ...
{% endblock %}
```

Em termos de ASP.NET Core, `base.html` aproxima-se de um layout e os blocos de regiões substituíveis. A Django Template Language é mais limitada do que executar C# em Razor.

## 9. Django Template Language

A sintaxe chama-se **Django Template Language**, ou **DTL**. Não é Python escrito dentro de HTML.

### Apresentar valores

```django
{{ card.name }}
{{ page_title }}
```

`{{ ... }}` avalia um valor e escreve o resultado no HTML.

### Template tags

```django
{% if cards %}
{% for card in cards %}
{% extends "base.html" %}
{% url "cards:list" %}
{% csrf_token %}
```

`{% ... %}` controla o processamento do template. Estruturas como `if`, `for` e `block` possuem tags de fecho:

```django
{% if cards %}
    ...
{% endif %}
```

### Comentários

```django
{# Comentário que não aparece no HTML final #}
```

### Filtros

A barra vertical aplica um template filter:

```django
{{ valor|filtro }}
```

Os filtros podem ser encadeados:

```django
{{ cards|length|pluralize }}
```

Conceptualmente:

```text
cards
→ length
→ pluralize
→ apresentar resultado
```

Em:

```django
{{ cards|length }} card{{ cards|length|pluralize }}
```

`pluralize` devolve, por omissão, uma string vazia para `1` e `s` nos restantes casos:

```text
1 card
3 cards
```

Pode receber terminações personalizadas:

```django
{{ count }} category{{ count|pluralize:"y,ies" }}
```

## 10. Template da lista

```django
{% extends "base.html" %}

{% block title %}Cards — MTG Manager{% endblock %}

{% block content %}
    <h1>Cards</h1>

    <p>
        <a href="{% url 'cards:create' %}">Add card</a>
    </p>

    <p>{{ cards|length }} card{{ cards|length|pluralize }}</p>

    {% if cards %}
        <ul>
            {% for card in cards %}
                <li>{{ card.name }}</li>
            {% endfor %}
        </ul>
    {% else %}
        <p>No cards have been registered.</p>
    {% endif %}
{% endblock %}
```

Ao iterar o QuerySet, o template necessita dos resultados e provoca normalmente a sua avaliação.

## 11. `ModelForm`

`cards/forms.py`:

```python
from django import forms

from .models import Card


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["name"]
```

`CardForm` é um nome escolhido segundo a convenção; não é obrigatório. O elemento estrutural é a herança:

```python
class CardForm(forms.ModelForm):
```

Em Python, os parênteses numa declaração de classe indicam as classes-base. Não representam uma chamada ao construtor.

`Meta`, pelo contrário, é o nome exato que a API do Django procura. A inner class guarda configuração declarativa associada ao formulário:

```text
CardForm
├── comportamento herdado de ModelForm
└── Meta
    ├── model = Card
    └── fields = ["name"]
```

Declarar explicitamente `fields` é preferível a `"__all__"`, pois evita expor automaticamente fields futuros que não devam fazer parte do formulário.

O Django infere do model:

- o tipo de input;
- o label;
- se o valor é obrigatório;
- o comprimento máximo;
- conversão e validação;
- construção da instância de `Card`.

## 12. View de criação: GET e POST

```python
from django.shortcuts import redirect, render

from .forms import CardForm
from .models import Card


def card_create(request):
    if request.method == "POST":
        form = CardForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("cards:list")
    else:
        form = CardForm()

    context = {
        "form": form,
    }

    return render(request, "cards/card_form.html", context)
```

### GET

```python
form = CardForm()
```

Cria um formulário vazio, ou **unbound**, para apresentação inicial.

### POST

```python
form = CardForm(request.POST)
```

Cria um formulário **bound** com os dados submetidos. `request.POST` é um `QueryDict`, não um model nem um registo persistido.

### Validação

```python
if form.is_valid():
```

valida e converte os dados, preenche `cleaned_data` e regista erros no próprio formulário.

Se a validação falhar, o formulário bound volta a ser renderizado com os valores submetidos e mensagens de erro. `form.as_p` apresenta os erros padrão sem configuração adicional.

### Persistência

```python
card = form.save()
```

Num formulário de criação, constrói e guarda uma instância através do ORM e devolve-a já persistida. Conceptualmente:

```python
card = Card(name=form.cleaned_data["name"])
card.save()
```

Com uma instância existente:

```python
form = CardForm(request.POST, instance=card)
```

`form.save()` atualizaria normalmente esse registo.

Para completar uma instância antes da persistência:

```python
card = form.save(commit=False)
card.some_field = some_value
card.save()
```

## 13. Template do formulário

`cards/templates/cards/card_form.html`:

```django
{% extends "base.html" %}

{% block title %}Add card — MTG Manager{% endblock %}

{% block content %}
    <h1>Add card</h1>

    <form method="post">
        {% csrf_token %}

        {{ form.as_p }}

        <button type="submit">Save</button>
    </form>

    <p>
        <a href="{% url 'cards:list' %}">Back to cards</a>
    </p>
{% endblock %}
```

Sem `action`, o formulário é submetido para o URL atual. `method="post"` envia uma operação de alteração em vez de codificar os valores no query string.

`form.as_p` renderiza fields, labels e erros, envolvendo-os em parágrafos. É adequado para começar; renderização manual oferece mais controlo visual.

## 14. CSRF

```django
{% csrf_token %}
```

insere um token que permite ao Django verificar que o `POST` foi originado no contexto legítimo da aplicação. Sem ele, um formulário interno protegido produzirá normalmente `403 Forbidden`.

CSRF e CORS não são o mesmo mecanismo:

- CSRF protege contra pedidos autenticados forjados;
- CORS controla interações entre origens no browser.

Num frontend React ou Angular separado que utilize cookies/sessão, CSRF continua normalmente relevante, mas o token é enviado através de mecanismos como um header, em vez de uma template tag.

## 15. Post/Redirect/Get

Depois de guardar:

```python
return redirect("cards:list")
```

o fluxo é:

```text
POST /cards/new/
→ validar
→ INSERT
→ resposta de redirecionamento
→ browser executa GET /cards/
```

Este padrão evita que atualizar a página repita acidentalmente o `POST` e crie um registo duplicado.

## 16. Validação no browser, servidor e base de dados

De `max_length=200`, o `ModelForm` gera aproximadamente:

```html
<input type="text" name="name" maxlength="200" required>
```

O browser impede normalmente a introdução de mais de 200 caracteres. Isto melhora a experiência, mas não é uma garantia de segurança porque o cliente pode ser alterado ou contornado.

O `ModelForm` volta a validar no servidor:

```python
form = CardForm({"name": "x" * 201})
form.is_valid()
# False

form.errors
```

As camadas são:

```text
browser
→ feedback e restrições de interface

servidor / ModelForm
→ validação confiável da entrada

base de dados
→ constraints finais de integridade, dependentes do backend
```

No SQLite, `varchar(200)` não impõe necessariamente o comprimento. Contornar o formulário e chamar diretamente o ORM pode, portanto, aceitar um valor demasiado longo. PostgreSQL aplica a restrição de `varchar(200)`.

## 17. Templates Django versus frontend separado

Com Django server-rendered:

```text
ModelForm
→ HTML
→ POST
→ validação
→ ORM
→ redirect/template
```

Com React ou Angular separados:

```text
frontend constrói formulário
→ envia JSON
→ API valida novamente
→ ORM
→ API devolve JSON
→ frontend atualiza a interface
```

Mantêm-se models, ORM, migrations e validação do servidor, mas deixam normalmente de ser usados diretamente DTL, `form.as_p`, template inheritance e `{% csrf_token %}`.

Em APIs Django, serializers — frequentemente através de Django REST Framework — cumprem parte do papel de tradução e validação entre JSON e models que o `ModelForm` desempenha entre formulários HTML e models.

## 18. Testes no Django

`startapp` criou:

```text
cards/tests.py
```

É um módulo inicial onde podem ser colocados testes da app. Não está limitado a testes unitários puros. O Django fornece ferramentas para:

- testar funções e regras isoladas;
- criar uma base de dados de teste;
- testar models e queries;
- simular pedidos com o test client;
- verificar status HTTP, templates, context e redirects;
- testar formulários, validação, autenticação e permissões.

Não se deve testar que o próprio Django funciona. Deve testar-se a configuração e o comportamento que pertencem à aplicação.

Exemplos relevantes para este projeto seriam:

- `/cards/` responde com status `200`;
- a view utiliza o template esperado;
- cartas persistidas aparecem na lista;
- um POST válido cria uma carta e redireciona;
- um nome vazio não cria uma carta e apresenta erros;
- páginas protegidas exigem autenticação.

Mesmo quando uma funcionalidade tem pouca regra de negócio, estes testes verificam a nossa integração entre routing, views, templates, forms e models.

A prática estruturada fica reservada ao módulo 7 — Testes e qualidade — para evitar interromper agora o avanço funcional.

## 19. Comandos de referência

```powershell
# Validar a configuração e componentes do projeto
uv run python manage.py check

# Iniciar o servidor de desenvolvimento
uv run python manage.py runserver

# Abrir a shell configurada pelo Django
uv run python manage.py shell
```

URLs criados:

```text
GET  /cards/      → listar cartas
GET  /cards/new/  → apresentar formulário
POST /cards/new/  → validar e criar carta
```

## 20. Estado final

- existe uma página server-rendered com a lista de cartas;
- as cartas são obtidas pelo ORM e transportadas através do context;
- existe um template base global e herança de templates;
- são usados namespaces e nomes de rotas;
- existe um `ModelForm` ligado a `Card`;
- a criação funciona através de GET, POST, validação, CSRF e redirect;
- ficaram distinguidas validação do browser, do servidor e da base de dados;
- o módulo está concluído sem repetir todo o CRUD.
