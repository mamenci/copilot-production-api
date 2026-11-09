# Product API

API didattica in Python (FastAPI) per creare, elencare e aggiornare prodotti.
I dati sono **solo in memoria**: si perdono al riavvio e non sono condivisi tra
processi, quindi usare un solo worker.

## Struttura

| File | Ruolo |
| --- | --- |
| `main.py` | Applicazione FastAPI (`create_app()`, `app`) ed endpoint |
| `models.py` | Modelli Pydantic e regole di validazione |
| `service.py` | Logica di business: catalogo in memoria |
| `tests/` | Test HTTP (`test_api.py`) e del servizio (`test_service.py`) |
| `.walden/specs/product-api/` | Requisiti, design e piano dell'esercizio |

## Avvio

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m uvicorn main:app
```

Documentazione interattiva su <http://127.0.0.1:8000/docs>.

## Endpoint

| Metodo | Percorso | Risposta |
| --- | --- | --- |
| `POST` | `/products` | 201 e prodotto creato |
| `GET` | `/products` | 200 e array (anche vuoto) |
| `PATCH` | `/products/{id}` | 200 e prodotto aggiornato; 404 se assente |

Un prodotto ha `id`, `name`, `price` e `quantity`. `PATCH` modifica solo i
campi inviati; `{}` non cambia nulla.

## Regole di validazione (errore 422, catalogo invariato)

- `name`: obbligatorio, senza spazi iniziali/finali, da 1 a 200 caratteri.
- `price`: numero (non booleano) finito, da 0 a 9000000.
- `quantity`: intero (non booleano), da 0 a 1000000. Un valore come `3.0` o
  `1.5` viene respinto.
- Campi sconosciuti e valori `null` espliciti sono respinti.

## Verifiche

```bash
.venv/bin/python -m pytest tests
.venv/bin/python -m ruff check main.py models.py service.py tests
.venv/bin/python -m ruff format --check main.py models.py service.py tests
```
