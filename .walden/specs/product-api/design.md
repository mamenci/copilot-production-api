---
walden_schema_version: v1alpha1
status: approved
approved_at: 2026-11-09T08:33:15Z
last_modified: 2026-11-09T08:33:15Z
approved_fingerprint: sha256:f3b75552d34830dd5e3c952bfab866c221626d7307cf8064705b966cbffad21f
source_requirements_approved_at: 2026-11-09T08:32:15Z
source_requirements_fingerprint: sha256:521a948286946a04c00b71b59e2a31da0af9001c85a075d5ba20fd6f3e5b5f7a
---

# Feature Design

## Architecture

API FastAPI con un servizio prodotti in memoria per istanza applicativa.
Il flusso e: richiesta HTTP -> modello validato -> servizio -> risposta.

Struttura prevista:

```text
copilot-production-api/
  main.py
  models.py
  service.py
  requirements.txt
  requirements-dev.txt
  pyproject.toml
  .gitignore
  tests/
    test_api.py
    test_service.py
```

| Modulo | Responsabilita |
| --- | --- |
| `main.py` | `create_app()`, istanza `app`, endpoint e conversione del prodotto inesistente in HTTP 404. |
| `models.py` | Modelli Pydantic `ProductCreate`, `ProductUpdate` e `Product`; vincoli condivisi dei campi. |
| `service.py` | `ProductService.create`, `.list` e `.update`; catalogo, identificatori e `ProductNotFoundError`. Nessuna dipendenza da FastAPI. |
| `tests/test_api.py` | Test HTTP con FastAPI TestClient e una nuova applicazione per ogni test. |
| `tests/test_service.py` | Test diretti del servizio, inclusa l'integrita del catalogo e l'isolamento delle istanze. |

`ProductCreate` richiede `name`, `price` e `quantity`. `Product`
aggiunge `id`, un intero positivo assegnato dal servizio.
`ProductUpdate` consente di omettere ciascun campo; i campi esplicitamente
inviati devono rispettare gli stessi vincoli della creazione.
Un valore `null` esplicito non equivale a un campo omesso.

Il nome deve essere una stringa non vuota dopo il controllo degli spazi,
con al massimo 200 caratteri. Il prezzo e un numero finito, non booleano,
tra 0 e 9000000; la quantita e un intero tra 0 e 1000000, non un booleano. Gli stessi validatori vengono riutilizzati
per creazione e aggiornamento.

<!-- assumed: prezzo rappresentato come float finito; nessun calcolo finanziario nel perimetro didattico -->
<!-- assumed: campi sconosciuti respinti con 422, per individuare errori di digitazione -->
<!-- assumed: un PATCH con oggetto vuoto e un aggiornamento senza modifiche e restituisce il prodotto esistente -->

| Operazione | Endpoint | Risposta |
| --- | --- | --- |
| Creazione | `POST /products` | 201 e prodotto creato. |
| Elenco | `GET /products` | 200 e array, anche vuoto. |
| Aggiornamento parziale | `PATCH /products/{id}` | 200 e prodotto aggiornato; 404 se assente. |
| Input non valido | POST o PATCH | 422 tramite la validazione FastAPI/Pydantic. |

Il servizio conserva un dizionario indicizzato per `id` e un contatore.
Gli identificatori vengono assegnati nella stessa sezione critica
dell'inserimento. Un lock protegge le operazioni sul catalogo dagli
accessi concorrenti dei normali endpoint sincroni FastAPI.

L'aggiornamento costruisce e valida un nuovo prodotto completo prima
di sostituire quello precedente; un errore non altera lo stato.
Il servizio restituisce modelli immutabili e un nuovo elenco, evitando
che il chiamante modifichi accidentalmente i prodotti memorizzati.
La validazione resta nei modelli, non viene duplicata negli endpoint.

`create_app()` crea un nuovo servizio, disponibile tramite una dipendenza
FastAPI. Non ci sono cataloghi globali condivisi tra applicazioni o test.
Il modulo espone `app` per l'avvio con Uvicorn.

Dipendenze runtime: FastAPI, Pydantic e Uvicorn. Dipendenze di sviluppo:
pytest, httpx per TestClient e Ruff per controllo e formattazione.
I file delle dipendenze verranno creati e le versioni compatibili
verificate durante l'implementazione, usando un ambiente virtuale.

## Options Considered

Scelta: tre moduli e un servizio concreto in memoria. Consente test
isolati e mantiene la separazione prevista dall'esercizio.

Alternativa: endpoint e dizionario globale interamente in `main.py`.
Richiede meno codice iniziale, ma accoppia HTTP e business, rende piu
difficile isolare i test e non rispetta la struttura multi-file richiesta.

Un livello repository o un ORM non aggiunge valore al catalogo volatile
concordato; non viene introdotto.

## Simplicity And Elegance Review

Un solo servizio, tre operazioni, nessuna gerarchia di repository,
DTO duplicato, framework aggiuntivo o configurazione di database.
La factory applicativa serve all'isolamento dei test; il lock tutela
il catalogo senza introdurre una infrastruttura concorrente.
I tipi condivisi evitano divergenze tra moduli.

Revisione di semplicita: un dizionario globale eliminerebbe la factory,
ma peggiorerebbe isolamento e responsabilita. Una lista renderebbe
la ricerca per identificatore meno diretta. Restano factory e dizionario.

## Failure Modes And Tradeoffs

| Caso | Gestione o limite accettato |
| --- | --- |
| Nome vuoto o oltre 200 caratteri, prezzo booleano/negativo/non finito/oltre 9000000, quantita negativa/frazionaria/oltre 1000000 o campo obbligatorio mancante | 422 prima di modificare il catalogo. |
| Campo PATCH esplicitamente nullo | 422; non cancella il valore memorizzato. |
| Prodotto inesistente | Eccezione di dominio convertita in 404. |
| Aggiornamento non valido | Validazione del nuovo prodotto prima della sostituzione; originale preservato. |
| Richieste concorrenti nello stesso processo | Lock attorno alle operazioni sul catalogo e all'assegnazione degli id. |
| Riavvio o piu processi server | Dati persi al riavvio e cataloghi distinti tra processi; usare un solo worker nell'esercizio. |
| Prezzi decimali | Float adeguato per memorizzazione didattica; non adatto come scelta automatica per calcoli monetari di produzione. |
| Crescita del catalogo | Nessuna persistenza o paginazione: limite accettato per l'esercizio locale. |

Nessuna garanzia di produzione, autenticazione o durabilita viene
dedotta dai test.

## Verification Plan

Le implementazioni incrementali avranno test nuovi per il comportamento
introdotto; i comandi selettivi saranno dichiarati nel documento tasks.

| Gruppo | Osservazioni da verificare |
| --- | --- |
| Creazione (`R1`) | 201, valori restituiti, id distinti, prodotto presente nel catalogo del servizio e poi nell'elenco HTTP. |
| Elenco (`R2`) | 200 e `[]` a catalogo vuoto; tutti i prodotti dopo piu creazioni. |
| Aggiornamento (`R3`) | 200, modifiche visibili nell'elenco, campi omessi e id invariati; 404 senza creazione implicita. |
| Validazione (`R4`) | Ciascun campo obbligatorio assente, nomi vuoti/spazi o oltre 200 caratteri, prezzi booleani/negativi/non finiti/oltre 9000000, quantita negative/frazionarie/oltre 1000000; zero e valori limite validi. |
| Integrita (`NFR1`) | Confronto del catalogo prima e dopo creazioni/aggiornamenti respinti; nessuna modifica parziale. |
| Dettagli di design | PATCH nullo respinto e vuoto senza modifiche; istanze isolate, modelli immutabili, id distinti nelle creazioni concorrenti. |

Verifica finale prevista, dall'ambiente virtuale Linux:

```text
.venv/bin/python -m pytest tests/test_api.py tests/test_service.py
.venv/bin/python -m ruff check main.py models.py service.py tests
.venv/bin/python -m ruff format --check main.py models.py service.py tests
```

pytest restituisce un errore se non raccoglie test; i task aggiungeranno
asserzioni e selettori specifici, non solo una verifica di importazione.
Lint e controllo formato non riscrivono file durante la verifica.

Prova manuale finale con Uvicorn su localhost e un solo worker:
creare un prodotto, elencarlo, modificarne la quantita, verificare 404
per un id assente e 422 per input non valido. Verificare anche che il
catalogo rimanga invariato dopo l'errore. Il server di verifica verra
arrestato al termine. La pagina `/docs` consentira prove interattive
quando il server sara avviato dall'utente.

## Requirement Coverage

| Requirement | Covered By |
| --- | --- |
| `R1` | `ProductCreate`, `ProductService.create`, POST; test di creazione, id distinti e lettura successiva. |
| `R2` | `ProductService.list`, GET; test di catalogo vuoto e di piu prodotti. |
| `R3` | `ProductUpdate`, `ProductService.update`, PATCH e gestione 404; test di aggiornamento parziale e prodotto assente. |
| `R4` | Validatori condivisi (inclusi tipi e limiti) e sostituzione solo dopo validazione; test parametrizzati di input invalidi, valori limite e confronto del catalogo. |
| `NFR1` | `R4.AC5`: nessuna mutazione su errore, verificata prima/dopo POST e PATCH non validi. |
