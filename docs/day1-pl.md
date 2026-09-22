## Dzień 1: Tooling i semantyka Pythona (`uv`, `Ruff`, `dict`, `for`, comprehensions)

**Cel:** Postawić projekt i umieć z głowy złożyć funkcje, pętle, słowniki i comprehensions — bez szukania składni w necie.

Tekst poniżej to ściąga językowa na **dziś**. Zadania są na końcu dnia. Przykłady w notatkach są celowo o liczbach i imionach, nie o logach — logi liczysz sam.

---

### 1. Konfiguracja środowiska

- Zainstaluj `uv` (jeśli jeszcze nie masz): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Inicjalizacja projektu: `uv init python-week1 && cd python-week1`
- Dodaj Ruff: `uv add --dev ruff`
- Linter i formatter: `uv run ruff check .` oraz `uv run ruff format .`
- Uruchom kod: `uv run python-week1` (z katalogu `python-week1`). To woła `python_week1:main` z `pyproject.toml`. `uv run` używa lokalnego `.venv`, nie musisz go aktywować ręcznie.
- `uv run python -m python_week1` nic nie wykona, dopóki w pakiecie nie ma `__main__.py`, a `main()` nie jest wołane przy imporcie.

---

### 2. Jak Python czyta plik

Plik `.py` to **moduł**. Interpreter wczytuje go od góry do dołu i wykonuje każdą instrukcję.

`def nazwa(...):` **definiuje** funkcję: wiąże nazwę z obiektem funkcji. Ciało `def` w tym momencie się **nie** wykonuje. Wykonanie następuje dopiero przy wywołaniu `nazwa(...)`.

Dlatego w module możesz napisać `main()` na górze pliku, a `login_durations` poniżej. `uv` importuje moduł (wszystkie `def` już istnieją), **potem** woła `main()`. Gdybyś wywołał funkcję w linijce *nad* jej `def`, przy starcie dostałbyś `NameError`.

Komentarz: od `#` do końca linii. Python go pomija.

---

### 3. Wcięcia zamiast klamer

Blok (`def`, `if`, `for`) otwiera dwukropek `:`. Ciało jest **wcięte** (w tym projekcie 4 spacje). Dedent kończy blok. Nie ma `{ }`.

```python
if n > 0:
    print("dodatnie")
print("zawsze")  # poza if, bo mniejsze wcięcie
```

Mieszanie tabów i spacji psuje parser. Ruff/format to wyrównają.

---

### 4. Nazwy i przypisanie

`x = 1` nie deklaruje typu ani „pudełka”. Wiąże nazwę `x` z obiektem `1`.

Kolejny `x = 2` wiąże tę samą nazwę z innym obiektem. Stary obiekt, jeśli nic na niego nie wskazuje, znika.

Dwa zapisy, dwa znaczenia:

- `x = x + 1` albo `x += 1` — nowe wiązanie nazwy (dla liczb).
- `xs.append(3)` — **mutacja** istniejącej listy; nazwa `xs` nadal wskazuje ten sam obiekt.

Konwencja nazw: `snake_case` (`last_login`, nie `lastLogin`). To styl, nie składnia.

---

### 5. Typy, których dziś używasz

| Typ | Literał | Co to jest |
| --- | --- | --- |
| `int` | `120` | liczba całkowita |
| `str` | `"login"` | tekst; cudzysłów `"..."` albo `'...'` |
| `bool` | `True` / `False` | wynik porównań |
| `list` | `[1, 2, 3]` | uporządkowany ciąg; ten sam element może się powtórzyć |
| `dict` | `{"a": 1}` | mapowanie klucz → wartość |

`==` porównuje **wartości** (`"login" == "login"` jest `True`). `=` to przypisanie, nie porównanie.

Adnotacje typów (`n: int`, `def f(xs: list[int]) -> int`) są dla Ciebie i dla checkerów (dzień 7). **Runtime ich nie wymusza.** Możesz napisać `-> dict[int, int]` i zwrócić coś innego — program i tak się wykona, dopóki nie użyjesz wyniku w sposób, który wywali wyjątek.

`list[dict]` znaczy: lista, której elementy są słownikami. Jakie klucze mają te słowniki, ta adnotacja **nie** opisuje.

---

### 6. Dwa sposoby odczytu: `[]` i `.`

- `obiekt["klucz"]` — odczyt **wpisu w mapowaniu** (słownik). Klucz jest wyrażeniem, zwykle `str` albo `int`.
- `obiekt.atrybut` — odczyt **atrybutu** obiektu (pole albo metoda zapisane na obiekcie), np. `logs.append`.

Słownik trzyma pary klucz–wartość wewnątrz siebie. Dostęp do nich jest przez `[]`. Metody słownika (np. `.keys()`) są atrybutami, więc idą przez kropkę.

```python
log = {"user_id": 1, "action": "login"}
log["action"]   # "login" — klucz
log["user_id"]  # 1
```

Brak klucza: `log["missing"]` rzuca `KeyError`.

Zapis (wstawienie albo nadpisanie):

```python
ages = {}
ages["Ada"] = 3
ages["Ada"] = 4   # ten sam klucz: zostaje 4, trójka znika
```

Klucz w `dict` jest unikalny. Drugie przypisanie pod ten sam klucz **zastępuje** wartość. Dlatego dict comprehension „sumuje” tylko pozornie — tak naprawdę zostawia ostatnią wartość.

---

### 7. Lista

```python
xs = [10, 20, 30]
xs[0]          # 10 — indeks od zera
xs.append(40)  # teraz [10, 20, 30, 40]
len(xs)        # 4
```

Lista pamięta kolejność. Indeks poza zakresem: `IndexError`.

---

### 8. `if`

```python
if log["action"] == "login":
    ...
elif log["action"] == "logout":
    ...
else:
    ...
```

Warunek to wyrażenie, które Python sprowadza do prawdy/fałszu. Nawiasy wokół warunku są zbędne (to nie C/JS).

Dziś wystarczy `==` i ewentualnie `and` / `or` / `not`.

---

### 9. Pętla `for`

Pythonowski `for` **nie** jest `for (i = 0; i < n; i++)`. Iteruje po **elementach** kolekcji.

```python
for n in [10, 20, 30]:
    print(n)
```

Wypisze `10`, potem `20`, potem `30`. W każdej turze nazwa pętli (`n`) jest związana z **kolejnym elementem**, nie z indeksem.

Po liście słowników:

```python
for log in logs:
    print(log["action"], log["duration"])
```

`log` to cały słownik tej turze. Pola bierzesz przez `log["..."]`.

Złożenie nowej listy pętlą (akumulator):

```python
squares = []
for n in [1, 2, 3, 4]:
    if n % 2 == 0:
        squares.append(n * n)
# squares == [4, 16]
```

`%` to reszta z dzielenia. `n % 2 == 0` znaczy „parzyste”.

To jest model mentalny list comprehension: idź po kolekcji, ewentualnie pomiń wiersz, dodaj wyrażenie do wyniku.

---

### 10. Funkcje

```python
def double(n: int) -> int:
    return n * 2

x = double(21)  # 42
```

- `def` + nazwa + lista parametrów w `()`.
- `return wyrażenie` kończy funkcję i oddaje wartość wywołującemu. Bez `return` funkcja zwraca `None`.
- Parametr (`n`) to nazwa lokalna, związana z argumentem (`21`) na czas wywołania.
- Wywołanie: `nazwa(arg1, arg2)`.

Funkcja, która ma coś policzyć i pokazać, zwykle **zwraca** wynik; `print` zostawiasz w `main()`.

```python
def main() -> None:
    xs = [1, 2, 3]
    print(double(xs[0]))
```

`-> None` znaczy: ta funkcja nic pożytecznego nie zwraca (efekt to `print` albo mutacja).

---

### 11. `import`

Kod z innego modułu wciągasz na górze pliku:

```python
from collections import defaultdict
```

`collections` jest w bibliotece standardowej. `defaultdict` to klasa z tego modułu. Po tym imporcie używasz nazwy `defaultdict` w pliku.

---

### 12. `print`

`print(x)` wypisuje czytelny obraz wartości i kończy linię. Kilka argumentów rozdziela spacją: `print(a, b)`.

Listy i słowniki drukują się swoją literałową postacią, np. `[120, 110]` albo `{1: 150, 2: 110}`. Tego użyjesz do sprawdzenia zadań.

---

### 13. List comprehension

To **wyrażenie**, które buduje nową listę. Semantyka jest ta sama co pętla z `.append`, tylko w jednej linijce.

```python
[wyrażenie for element in kolekcja if warunek]
```

Kolejność ewaluacji:

1. Weź kolejny `element` z `kolekcja`.
2. Jeśli jest `if warunek` i warunek jest fałszywy — pomiń.
3. Policz `wyrażenie` (może używać `element`).
4. Dołącz wynik do nowej listy.
5. Powtórz, aż kolekcja się skończy.

`for` i `if` wewnątrz `[...]` należą do tej składni. To nie jest osobna instrukcja `for`.

```python
[n * 2 for n in [1, 2, 3, 4] if n % 2 == 0]
# 1. n=1 nieparzyste → skip
# 2. n=2 → 4
# 3. n=3 skip
# 4. n=4 → 8
# wynik: [4, 8]
```

Równoważna pętla jest w §9. Dziś w zadaniach 3a/3b piszesz comprehension, nie `.map()` / `.filter()` (to metody z innych języków / z innego idiomu; tu uczymy składni Pythona).

---

### 14. Dict comprehension

To samo, ale wynikiem jest `dict`. Po lewej klucz, po prawej wartość:

```python
{klucz: wartość for element in kolekcja if warunek}
```

```python
{n: n * n for n in [1, 2, 3]}
# {1: 1, 2: 4, 3: 9}
```

Jeśli ten sam klucz wyjdzie drugi raz, zostaje **późniejsza** para — dokładnie jak `d[k] = v` w pętli. Dict comprehension **nie dodaje** wartości pod kluczem. Do sumy potrzebujesz akumulatora (następna sekcja).

```python
{c: 1 for c in ["a", "b", "a"]}
# {"a": 1, "b": 1}  — drugie "a" nadpisało pierwsze
```

---

### 15. `defaultdict` i `+=`

Zwykły `dict`: odczyt nieistniejącego klucza → `KeyError`. Żeby zliczać, musiałbyś za każdym razem sprawdzać, czy klucz już jest.

`defaultdict(fabryka)` przy **pierwszym** odczycie brakującego klucza woła `fabryka()` i wstawia wynik.

`int` jako fabryka: `int()` zwraca `0`. Stąd `defaultdict(int)` — brakujący klucz zachowuje się jak `0`.

```python
from collections import defaultdict

counts = defaultdict(int)
counts["a"] += 1
counts["a"] += 1
counts["b"] += 5
# counts["a"] == 2, counts["b"] == 5
```

`counts["a"] += 1` znaczy: odczytaj obecną wartość (albo `0`), dodaj `1`, zapisz z powrotem.

`defaultdict` jest podklasą `dict`. Przy `print` wygląda podobnie. Różnica: odczyt brakującego klucza **wstawia** `0`, zamiast rzucić `KeyError`. Dlatego wynik funkcji często zwracasz jako zwykły słownik:

```python
plain = dict(counts)  # kopia par klucz→wartość, typ dict
```

`dict(counts)` nie zmienia `counts`; buduje nowy, zwykły `dict`.

Sumowanie „po kluczu” to pętla-instrukcja plus `+=`. Comprehension tu nie zastępuje pętli.

---

### 16. Zadania — logi zdarzeń

Dane (jedna lista w `main()`, trzy funkcje, `print` każdej):

```python
logs = [
    {"user_id": 1, "action": "login", "duration": 120},
    {"user_id": 2, "action": "login", "duration": 110},
    {"user_id": 1, "action": "logout", "duration": 90},
    {"user_id": 1, "action": "login", "duration": 30},
]
```

Każdy element to słownik z kluczami `"user_id"` (`int`), `"action"` (`str`), `"duration"` (`int`).

**3a.** `login_durations(logs: list[dict]) -> list[int]`

List comprehension: wartości `"duration"` z wierszy, których `"action"` to `"login"`.

Oczekiwany wynik: `[120, 110, 30]`.

**3b.** `last_login_duration(logs: list[dict]) -> dict[int, int]`

Dict comprehension: `user_id → duration` **ostatniego** loginu (kolejność listy = kolejność nadpisywania).

Oczekiwany wynik: `{1: 30, 2: 110}`.

**3c.** `total_login_duration(logs: list[dict]) -> dict[int, int]`

`defaultdict(int)` i pętla `for`. Zlicz `"duration"` tylko tam, gdzie `"action"` to `"login"`. Zwróć `dict(...)` albo sam `defaultdict`.

Oczekiwany wynik: `{1: 150, 2: 110}`.

Sprawdzenie: `uv run python-week1` z katalogu `python-week1`.

---

## Dzień 2: Dunder Methods, OOP i Context Manager

**Cel:** Zrozumienie, jak obiekty w Pythonie wchodzą w interakcję ze składnią języka.

1. **Zadanie kodowe – Magiczne metody:**

- Stwórz klasę `RateLimiter`, która przyjmuje `max_requests: int` oraz `window_seconds: int`.
- Zaimplementuj metodę `__call__(self, user_id: str) -> bool`, aby instancja klasy była wywoływalna jak funkcja (`limiter("user_123")`).
- Zaimplementuj `__repr__`, aby wywołanie `print(limiter)` dawało czytelny string debugowy: `RateLimiter(max_requests=10, window=60)`.

1. **Zadanie kodowe – Custom Context Manager:**

- Napisz klasę `Timer` używającą protokołu Context Managera (`__enter__` i `__exit__`).
- Użycie: `with Timer("DB Query"): ...` ma automatycznie zmierzyć czas wykonania bloku kodu i wydrukować go po wyjściu z bloku.

---

## Dzień 3: Typing i Pydantic v2 (Pythonowy "Zod")

**Cel:** Modele danych na granicy I/O z pełną walidacją i statycznym typowaniem.

### Wprowadzenie do dekoratorów

W Pythonie funkcja jest obiektem. Możesz przekazać ją do innej funkcji tak samo jak liczbę albo string.

Dekorator to funkcja, która dostaje funkcję i zwraca funkcję. Zwykle zwraca nową funkcję: ta woła oryginał i dokłada własne zachowanie. Zapis `@` jest skrótem. Python bierze funkcję z `def` w linii pod spodem i od razu przepuszcza ją przez dekorator.

```python
def twice(fn):
    def wrapped(n: int) -> int:
        return fn(n) * 2

    return wrapped


@twice
def add_one(n: int) -> int:
    return n + 1


add_one(3)  # 8
```

`@twice` stoi w linii nad `def`. Po definicji nazwa `add_one` wskazuje już wynik `twice(...)`, czyli `wrapped`. Wywołanie `add_one(3)` wchodzi w `wrapped`: ta woła oryginał (`3 + 1`) i mnoży wynik przez 2.

To samo bez `@`:

```python
def add_one(n: int) -> int:
    return n + 1


add_one = twice(add_one)
```

`@` wykonuje się raz, w momencie definicji, przy wczytywaniu modułu. Późniejsze wywołania idą już w owiniętą funkcję.

Dekorator bywa fabryką. Sam przyjmuje argumenty i zwraca właściwy dekorator. Nawiasy są wtedy częścią zapisu: najpierw wołasz fabrykę, a to, co zwróci, owija funkcję.

```python
def tag(label: str):
    def decorator(fn):
        fn.label = label
        return fn

    return decorator


@tag("points")
def check(value: int) -> int:
    return value


check.label  # "points"
```

`@tag("points")` znaczy `check = tag("points")(check)`.

Kilka dekoratorów układa się jeden nad drugim. Python stosuje je od dołu: najbliższy `def` owija pierwszy.

```python
@outer
@inner
def f():
    ...
```

to `f = outer(inner(f))`.

`@field_validator(...)` i `@model_validator(...)` z zadania poniżej to dekoratory napisane w Pydantic. Konfigurujesz je w nawiasie, a owijają metodę z `def` pod spodem — tym samym mechanizmem co `twice` i `tag`.

### Wprowadzenie do walidacji w Pydantic

Model to klasa dziedzicząca po `BaseModel`. Pola zostają adnotacjami. Walidacja to metoda pod dekoratorem. Pydantic woła ją sam, kiedy budujesz obiekt z danych.

Każdy z tych dekoratorów dostaje własny `def`. `@field_validator` i `@model_validator` uruchamiają się w innym momencie i dostają inne argumenty.

**Jedno pole.** `@field_validator("nazwa")` owija metodę, która dostaje wartość tego pola. W v2 jest to `@classmethod`: pierwszy argument to klasa (`cls`), drugi to wartość. Zwracasz wartość, która ma zostać w polu. Złą wartość odrzucasz przez `raise ValueError("...")`.

```python
from pydantic import BaseModel, field_validator


class Score(BaseModel):
    points: int

    @field_validator("points")
    @classmethod
    def non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("points must be >= 0")
        return value
```

`Score(points=-1)` nie powstanie: Pydantic zamienia `ValueError` na `ValidationError`. `Score(points=3)` przechodzi, bo metoda zwróciła `3`.

**Kilka pól naraz.** `@model_validator(mode="after")` owija metodę instancji. Pydantic woła ją, gdy pola są już ustawione. Czytasz je przez `self` i zwracasz `self`. Reguła, która łączy pola, też rzuca `ValueError`.

```python
from typing import Self

from pydantic import BaseModel, model_validator


class Pair(BaseModel):
    left: int
    right: int

    @model_validator(mode="after")
    def left_not_above_right(self) -> Self:
        if self.left > self.right:
            raise ValueError("left must be <= right")
        return self
```

Nazwy metod (`non_negative`, `left_not_above_right`) wybierasz sam. Liczy się dekorator, argumenty i to, czy zwracasz wartość, czy rzucasz `ValueError`. Reguły dla `UserPayload` piszesz osobno, na tym samym kształcie.

1. **Przygotowanie:**

- Dodaj Pydantic i Pyright/Mypy: `uv add pydantic` oraz `uv add --dev pyright`

1. **Zadanie kodowe:**

- Stwórz model Pydantic `UserPayload`:
- `id`: `UUID`
- `email`: `EmailStr`
- `roles`: `list[Literal["admin", "user", "guest"]]`
- `created_at`: `datetime` (z automatyczną domyślną wartością strefy UTC)
- Dodaj `@field_validator` dla pola `roles`, który zgłosi błąd, jeśli lista jest pusta.
- Dodaj `@model_validator(mode="after")` wymuszający, że jeśli `email` kończy się na `@company.com`, użytkownik musi posiadać rolę `"admin"`.
- Przetestuj deserializację niepoprawnego JSON-a i obsłuż `ValidationError`.

---

## Dzień 4: Asynchroniczność w `asyncio`

**Cel:** Zrozumienie jawnej pętli zdarzeń i unikanie blokowania event loopa.

### Wprowadzenie do `asyncio`

Zwykła funkcja, gdy w niej stoisz, trzyma wątek do `return`. Reszta programu czeka. `async def` definiuje **korutynę**: funkcję, która umie się zatrzymać na `await` i oddać sterowanie pętli zdarzeń. Pętla w tym czasie prowadzi inne korutyny, a potem wraca.

Sam `async def` nic nie uruchamia. Korutynę startuje `asyncio.run` — raz, na szczycie programu. W środku korutyny kolejne wołasz przez `await`.

```python
import asyncio


async def boil(item: str) -> str:
    await asyncio.sleep(0.1)
    return item


async def cook() -> None:
    ready = await boil("water")
    print(ready)


asyncio.run(cook())
```

`asyncio.sleep` oddaje pętlę na podany czas. `time.sleep` trzyma wątek: pętla stoi, dopóki sen się nie skończy, i żadna inna korutyna w tym czasie nie ruszy.

`asyncio.gather` startuje kilka korutyn i czeka, aż wszystkie skończą. Wynik to lista w tej samej kolejności co argumenty.

```python
async def cook() -> None:
    ready = await asyncio.gather(boil("water"), boil("pasta"), boil("sauce"))
    print(ready)  # ["water", "pasta", "sauce"]
```

`asyncio.Semaphore(n)` trzyma licznik wejść. `async with` zajmuje jedno wejście na czas bloku i oddaje je na wyjściu. `gather` może wystartować wiele korutyn, a semafor pilnuje, żeby w bloku było ich naraz co najwyżej `n`.

```python
async def cook() -> None:
    burners = asyncio.Semaphore(2)

    async def one(item: str) -> str:
        async with burners:
            return await boil(item)

    ready = await asyncio.gather(*(one(item) for item in ["water", "pasta", "sauce"]))
    print(ready)
```

Semafor twórz wewnątrz korutyny, którą odpala `asyncio.run`. Obiekt stworzony przy imporcie modułu może zostać przywiązany do innej pętli.

Gdy musisz wołać funkcję, która blokuje wątek (`time.sleep`, zwykłe I/O bez `await`), przenieś ją poza pętlę. `asyncio.to_thread` uruchamia ją w wątku i zwraca awaitable: pętla w tym czasie prowadzi resztę.

```python
import time


def slow_label(item: str) -> str:
    time.sleep(1)
    return item.upper()


async def cook() -> None:
    label = await asyncio.to_thread(slow_label, "water")
    print(label)
```

Argumenty funkcji idą po niej: `to_thread(slow_label, "water")` znaczy `slow_label("water")` w wątku.

1. **Zadanie kodowe – Async Fetcher & Rate Limiting:**

- Napisz asynchroniczną funkcję `fetch_metrics(service_id: int) -> dict`, która symuluje zapytanie HTTP (`await asyncio.sleep(0.5)`).
- Wywołaj współbieżnie pobieranie danych dla 20 serwisów (`service_id` od 1 do 20) przy użyciu `asyncio.gather`.
- Nałóż limit maksymalnie 3 równoległych zapytań naraz, używając `asyncio.Semaphore`.
- **Pułapka do przetestowania:** Dodaj do jednej z funkcji synchroniczne `time.sleep(2)` i zobacz, jak blokuje cały event loop. Napraw to, przenosząc blokujące wywołanie do osobnego wątku za pomocą `asyncio.to_thread`.

---

## Dzień 5: TDD z `pytest` i Fixtures

**Cel:** Pisanie idiomaticznych testów z wykorzystaniem fixture'ów i parametryzacji.

### Wprowadzenie do `pytest`

Test to funkcja `test_...` w pliku `test_*.py`. `pytest` sam je zbiera. Uruchomienie z katalogu `python-week1`: `uv run pytest`. Asercja to zwykłe `assert`. Fałsz kończy test i pokazuje wartości po obu stronach porównania.

Fixture przygotowuje obiekt przed testem. `@pytest.fixture` stoi nad `def`, tak jak dekoratory z Dnia 3. Test dostaje wynik fixture'a przez argument o tej samej nazwie. Domyślnie fixture wykonuje się od nowa przed każdym testem, który o niego prosi.

```python
import pytest


class Stack:
    def __init__(self) -> None:
        self.items: list[int] = []

    def push(self, n: int) -> None:
        if n < 0:
            raise ValueError("negative")
        self.items.append(n)


@pytest.fixture
def stack() -> Stack:
    return Stack()


def test_push(stack: Stack) -> None:
    stack.push(1)
    assert stack.items == [1]
```

`@pytest.mark.parametrize` odpala ten sam test raz na każdy element listy. Nazwa w napisie musi pokrywać się z argumentem funkcji.

```python
@pytest.mark.parametrize("n", [-1, -5])
def test_rejects_negative(stack: Stack, n: int) -> None:
    with pytest.raises(ValueError):
        stack.push(n)
```

`pytest.raises` jest context managerem: wyjątek w bloku `with` zalicza test. Brak wyjątku, albo inny typ, test oblewa.

Test asynchroniczny to `async def`. Sam `pytest` go nie uruchomi. Po `pytest-asyncio` oznaczasz go `@pytest.mark.asyncio`, a w środku używasz `await` jak w Dniu 4.

```python
import asyncio

import pytest


@pytest.mark.asyncio
async def test_pause() -> None:
    await asyncio.sleep(0)
    assert True
```

1. **Przygotowanie:**

- Dodaj pytest: `uv add --dev pytest pytest-asyncio`

1. **Zadanie kodowe:**

- Zbuduj prosty klasowy serwis `UserService` z pamięcią podręczną (słownik).
- Napisz zestaw testów w `pytest`:
- Użyj `@pytest.fixture` do przygotowania czystej instancji `UserService` przed każdym testem.
- Użyj `@pytest.mark.parametrize` do przetestowania walidacji adresów e-mail na 5 różnych prawidłowych i nieprawidłowych ciągach znaków w jednym teście.
- Użyj `pytest.raises(ValueError)` do weryfikacji rzucanych wyjątków.

---

## Dzień 6: Mini-CLI w oparciu o wszystko, co powiązałeś

**Cel:** Połączenie narzędzi w spójny skrypt.

### Wprowadzenie do CLI, plików i JSON

`uv run python-week1` woła `main()`. Dodatkowe słowa po nazwie polecenia lądują w `sys.argv`. `argparse` je czyta i zgłasza błąd, gdy brakuje wymaganego argumentu.

```python
import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    text = Path(args.path).read_text(encoding="utf-8")
    print(text)
```

Wywołanie: `uv run python-week1 notes.txt`. `Path.read_text` zwraca całą treść pliku jako `str`. `Path.write_text` nadpisuje plik podaną treścią.

`json.loads` zamienia tekst JSON na obiekty Pythona. Tablica JSON staje się `list`, obiekt JSON staje się `dict`. `json.dumps` idzie w drugą stronę: z obiektu Pythona robi tekst.

```python
import json
from pathlib import Path

raw = Path("nums.json").read_text(encoding="utf-8")
rows = json.loads(raw)  # np. [{"n": 1}, {"n": 2}]
Path("summary.json").write_text(
    json.dumps({"count": len(rows)}),
    encoding="utf-8",
)
```

Jeden obiekt JSON, który ma pasować do modelu Pydantic, podajesz jako tekst do `model_validate_json`. Lista takich obiektów: najpierw `json.loads`, potem `model_validate` na każdym słowniku. Zły wpis rzuca `ValidationError`, tak jak w Dniu 3.

`main()` jest zwykłą funkcją. Korutyny z Dnia 4 startujesz z niej przez `asyncio.run(...)`. Każdy nowy `def` ma adnotacje argumentów i typu zwracanego — Dzień 7 włączy tryb, który ich wymaga.

1. **Zadanie:**

- Stwórz narzędzie CLI, które przyjmuje ścieżkę do pliku JSON z listą użytkowników, waliduje każdy wpis przez Pydantic, asynchronicznie "przetwarza" ich (simulated I/O) i zapisuje zagregowane statystyki do nowego pliku.
- Całość powinna być w pełni otypowana, sformatowana przez `ruff` i mieć przechodzące testy w `pytest`.

---

## Dzień 7: Code Review i Pyright Strict Mode

**Cel:** Weryfikacja jakości kodu według standardów produkcyjnych.

### Wprowadzenie do trybu strict

Pyright w trybie strict czyta adnotacje i odrzuca miejsca, w których typ może być czymkolwiek. W `python-week1/pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

Albo, jeśli używasz Mypy:

```toml
[tool.mypy]
strict = true
```

Funkcja, która czasem nic nie znajduje, zwraca `str | None`. Samo `-> str` strict odrzuci, bo `None` nie jest `str`. Zanim użyjesz wartości `str | None` jak stringa, sprawdzasz `None`.

```python
def first(items: list[str]) -> str | None:
    if not items:
        return None
    return items[0]


def shout(name: str | None) -> str:
    if name is None:
        return ""
    return name.upper()
```

`Any` wyłącza sprawdzanie w tym miejscu. Strict nadal pozwoli je wpisać, a zadanie każe takie miejsca usunąć: argument, wynik i atrybut dostają konkretny typ.

Cztery polecenia z katalogu `python-week1` sprawdzają co innego. `ruff check` szuka błędów stylu i oczywistych bugów. `ruff format --check` porównuje układ pliku z formaterem i nic nie zmienia. `pyright` sprawdza typy. `pytest` odpala testy.

1. Włącz w `pyproject.toml` ścisłą kontrolę typów dla Pyright (`typeCheckingMode = "strict"`) lub Mypy (`strict = true`).
2. Przejrzyj kod z Dnia 6 i wyeliminuj wszystkie ostrzeżenia typowania (brakujące `None`, typy `Any`, niezgodności z `Optional`).
3. Uruchom pełny ciąg kontroli:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```
