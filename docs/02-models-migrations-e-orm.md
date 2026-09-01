# Módulo 2 — Models, migrations e ORM

## Objetivo

Criar o primeiro model persistente do projeto, compreender a separação entre models, migrations e schema da base de dados e executar as operações CRUD fundamentais através do ORM do Django.

Este módulo usou a Django shell como ambiente de aprendizagem e diagnóstico. Numa aplicação real, estas operações serão normalmente desencadeadas por views, forms, comandos ou outros serviços da aplicação.

## Estado inicial

- App `cards` registada em `INSTALLED_APPS`;
- SQLite configurado como base de dados de desenvolvimento;
- ainda não existiam models próprios nem tabelas da app `cards`.

## 1. Primeiro model

`cards/models.py`:

```python
from django.db import models


class Card(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
```

Um model é uma classe Python que descreve dados persistentes e comportamento associado. Neste caso, `Card` possui um field declarado, `name`.

O Django acrescenta implicitamente uma primary key quando não declaramos uma:

```text
id → BigAutoField → primary key gerada pela base de dados
```

Por convenção, a tabela recebe o nome:

```text
<app label>_<model name>
```

Neste caso:

```text
cards_card
```

O método `__str__` altera apenas a representação textual do objeto em Python. Não altera o schema e, por isso, não requer uma migration.

## 2. Models, migrations e schema

Os três conceitos representam estados diferentes:

```text
models.py
→ estado pretendido pela aplicação

ficheiros de migration
→ histórico versionado das alterações

base de dados
→ schema efetivamente aplicado
```

O fluxo habitual é:

```text
alterar models.py
→ makemigrations
→ rever a migration
→ migrate
→ schema atualizado
```

### Criar migrations

```powershell
uv run python manage.py makemigrations
```

Este comando compara o estado dos models com o estado descrito pelas migrations e gera novas operações quando necessário. Não modifica a base de dados.

Para confirmar se existem alterações por converter numa migration, sem criar ficheiros:

```powershell
uv run python manage.py makemigrations --check
```

Resultado esperado quando tudo está sincronizado:

```text
No changes detected
```

### Inspecionar o SQL

```powershell
uv run python manage.py sqlmigrate cards 0001
```

Este comando apresenta o SQL correspondente à migration para o backend configurado, sem o executar.

Para a primeira migration de `Card`, o SQLite produziu conceptualmente:

```sql
CREATE TABLE "cards_card" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(200) NOT NULL
);
```

Embora SQLite apresente `varchar(200)`, não impõe necessariamente esse comprimento da mesma forma que outros backends. `max_length=200` continua a fazer parte do contrato e da metadata do model e é usado pela validação do Django.

Chamar `save()` diretamente não executa automaticamente toda a validação do model. Quando necessário, a validação explícita pode ser feita com `full_clean()`; forms também participam na validação, como veremos mais tarde.

### Consultar migrations

```powershell
uv run python manage.py showmigrations
uv run python manage.py showmigrations cards
```

Legenda:

```text
[ ] migration conhecida, mas não aplicada
[X] migration aplicada
```

As apps incorporadas, como `auth`, `admin`, `contenttypes` e `sessions`, trazem os seus próprios models e migrations. O Django calcula a ordem de execução através de um grafo de dependências.

### Aplicar migrations

```powershell
uv run python manage.py migrate
```

`migrate` aplica as migrations pendentes e regista o histórico na tabela:

```text
django_migrations
```

O comando não compara diretamente `models.py` com o schema para inventar alterações. Se um model mudar, é necessário gerar primeiro a respetiva migration.

Executar novamente `migrate` sem migrations pendentes não recria as tabelas:

```text
No migrations to apply.
```

## 3. Django shell

```powershell
uv run python manage.py shell
```

A management shell inicia Python com os settings, o registo de apps e os models do Django preparados.

Não está limitada ao SQLite. Utiliza a base de dados definida em `DATABASES`, que pode ser PostgreSQL num container Docker ou qualquer outro backend suportado e corretamente configurado.

Nas versões atuais do Django, alguns models podem ser importados automaticamente na shell. No código normal, o import explícito continua a ser preferível:

```python
from cards.models import Card
```

## 4. Manager e QuerySet

Por omissão, o Django acrescenta um Manager ao model:

```python
Card.objects
```

Comparação aproximada com .NET:

```text
Card.objects ≈ DbSet<Card>
QuerySet ≈ IQueryable<Card>
```

O Manager é o ponto de entrada para operações sobre o conjunto de objetos. Métodos como `all()` e `filter()` devolvem QuerySets.

```python
Card.objects.all()
Card.objects.filter(name="Black Lotus")
Card.objects.filter(name__icontains="ring")
```

Um QuerySet guarda a descrição da consulta e é geralmente lazy: pode ser composto antes de executar SQL.

Exemplos que avaliam um QuerySet:

```python
list(query)
for card in query:
    ...
len(query)
bool(query)
```

Para observar a representação SQL:

```python
print(query.query)
```

Esta representação é útil para diagnóstico, mas não deve ser tratada como o SQL executável exato, pois a execução real utiliza parâmetros através do driver.

## 5. Criar — `INSERT`

### Instanciar e guardar

```python
card = Card(name="Black Lotus")
card.id
# None

card.save()
card.id
# valor gerado pela base de dados
```

Instanciar o model cria apenas um objeto Python. O primeiro `save()` persiste-o e origina normalmente um `INSERT`.

### Criar através do Manager

```python
card = Card.objects.create(name="Sol Ring")
```

`create()` equivale conceptualmente a:

```python
card = Card(name="Sol Ring")
card.save()
```

Por isso, a instância devolvida por `create()` já possui `id`.

## 6. Ler — `SELECT`

### Todos os objetos

```python
Card.objects.all()
```

### Exatamente um objeto

```python
Card.objects.get(pk=1)
```

`get()` exige exatamente um resultado:

- zero resultados: `Card.DoesNotExist`;
- mais de um resultado: `Card.MultipleObjectsReturned`;
- exatamente um: devolve a instância.

### Zero, um ou vários objetos

```python
Card.objects.filter(name="Sol Ring")
```

`filter()` devolve sempre um QuerySet, que pode estar vazio ou conter vários objetos.

### Lookups

```python
Card.objects.filter(name__icontains="ring")
```

O lookup divide-se em:

```text
name        → field
icontains   → contém texto, ignorando maiúsculas/minúsculas
```

### `pk` como alias

```python
Card.objects.get(pk=1)
```

`pk` refere-se à primary key, independentemente do seu nome concreto. No model atual, corresponde a `id`.

Uma primary key identifica inequivocamente uma linha. `name` não oferece essa garantia porque não possui uma constraint `unique`.

## 7. Atualizar — `UPDATE`

```python
card = Card.objects.get(pk=3)
card.name = "Lightning Bolt Updated"
card.save()
```

A atribuição modifica apenas o objeto Python. A base de dados só é alterada no `save()`.

Uma instância já persistida possui identidade conhecida e o `save()` origina normalmente um `UPDATE`.

Ao contrário do EF Core, não existe neste fluxo um `DbContext` persistente a acompanhar alterações e um `SaveChanges()` global. Cada instância é guardada individualmente.

Por omissão, não devemos assumir que o Django deteta e escreve apenas os fields alterados. É possível restringir explicitamente a atualização:

```python
card.save(update_fields=["name"])
```

## 8. Eliminar — `DELETE`

```python
result = card.delete()
```

O resultado tem a forma:

```python
(total_eliminado, {"app.Model": quantidade})
```

Depois de uma eliminação bem-sucedida, o Django repõe a primary key da instância como `None`:

```python
card.id
# None
```

O objeto Python continua a existir e conserva os restantes atributos, mas já não representa uma linha existente na base de dados.

Para verificar ausência sem lançar uma exceção:

```python
Card.objects.filter(name="Temporary Card")
# <QuerySet []>
```

## 9. Estado interno da instância

Para observação didática, consultámos:

```python
card._state.adding
```

Comportamento observado:

```text
instância nova               → True
instância depois de save()   → False
```

`_state` é informação interna do Django e não deve ser usada como API habitual da aplicação.

Modelo mental suficiente:

```text
objeto novo
→ save()
→ normalmente INSERT

objeto persistido com primary key
→ save()
→ normalmente UPDATE
```

Existem casos avançados, especialmente com primary keys atribuídas manualmente, que exigem mais detalhe. Não são necessários nesta fase.

## 10. Comandos de referência

```powershell
# Validar o projeto
uv run python manage.py check

# Gerar migrations
uv run python manage.py makemigrations

# Verificar se faltam migrations, sem criar ficheiros
uv run python manage.py makemigrations --check

# Mostrar o SQL de uma migration
uv run python manage.py sqlmigrate cards 0001

# Consultar o estado das migrations
uv run python manage.py showmigrations
uv run python manage.py showmigrations cards

# Aplicar migrations pendentes
uv run python manage.py migrate

# Abrir a shell configurada pelo Django
uv run python manage.py shell
```

## 11. Estado final

- `Card` existe como model da app `cards`;
- a migration inicial foi criada e aplicada;
- a tabela `cards_card` existe;
- `Card.__str__()` apresenta o nome da carta;
- foram praticadas operações CRUD com o ORM;
- ficaram compreendidos `Manager`, `QuerySet`, lazy evaluation, lookups, `get()`, `filter()` e `pk`;
- ficou distinguido o comportamento do ORM Django do change tracking do EF Core;
- o módulo está concluído e o projeto pode avançar para interfaces web, templates e forms.
