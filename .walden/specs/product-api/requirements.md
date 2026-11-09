---
walden_schema_version: v1alpha1
status: approved
approved_at: 2026-11-09T08:32:15Z
last_modified: 2026-11-09T08:32:15Z
approved_fingerprint: sha256:521a948286946a04c00b71b59e2a31da0af9001c85a075d5ba20fd6f3e5b5f7a
---

# Requirements Document

## Introduction

API didattica per creare, elencare e aggiornare prodotti. Ogni prodotto
ha `id`, `name`, `price` e `quantity`. La base concordata e Python con
FastAPI e dati in memoria.

Proposta da approvare: usare `POST /products`, `GET /products` e
`PATCH /products/{id}`. L'aggiornamento e parziale: modifica solo i
campi inviati. Non si tratta di un servizio pronto per la produzione.

## Requirements

### R1 Creazione prodotto

**User Story:** Come utente dell'API, voglio creare un prodotto per
inserirlo nel catalogo in memoria.

#### Acceptance Criteria

1. `R1.AC1` WHEN a valid product is submitted to POST /products, the system SHALL return HTTP 201 with the created product.
   - Acceptance check: la risposta contiene `name`, `price` e `quantity` corrispondenti ai valori inviati, oltre a `id`.
2. `R1.AC2` The system SHALL assign a distinct identifier to each created product.
   - Acceptance check: due creazioni riuscite restituiscono identificatori diversi.
3. `R1.AC3` WHEN a product is successfully created, the system SHALL include that product in subsequent catalog reads.
   - Acceptance check: un elenco richiesto nello stesso processo contiene il prodotto appena creato.

### R2 Elenco prodotti

**User Story:** Come utente dell'API, voglio leggere il catalogo per
visualizzare i prodotti disponibili.

#### Acceptance Criteria

1. `R2.AC1` WHEN GET /products is requested, the system SHALL return HTTP 200 with the complete list of stored products.
   - Acceptance check: dopo due creazioni, la risposta contiene entrambi i prodotti e i rispettivi identificatori.
2. `R2.AC2` WHILE the catalog contains no products, WHEN GET /products is requested, the system SHALL return an empty JSON array.
   - Acceptance check: la risposta iniziale e `[]`, non un errore o un valore nullo.

### R3 Aggiornamento parziale

**User Story:** Come utente dell'API, voglio aggiornare un prodotto
esistente senza dover reinviare tutti i campi.

#### Acceptance Criteria

1. `R3.AC1` WHEN valid changes are submitted to PATCH /products/{id} for an existing product, the system SHALL return HTTP 200 with the updated product.
   - Acceptance check: la risposta e un successivo elenco mostrano i nuovi valori.
2. `R3.AC2` WHEN an existing product is partially updated, the system SHALL preserve its omitted fields.
   - Acceptance check: una modifica della sola `quantity` lascia invariati `name`, `price` e `id`.
3. `R3.AC3` IF the requested product identifier does not exist, THEN the system SHALL return HTTP 404.
   - Acceptance check: una richiesta valida per un identificatore assente produce un errore leggibile e non crea un prodotto.

### R4 Validazione e integrita dei dati

**User Story:** Come utente dell'API, voglio errori comprensibili per
input non validi, senza alterare il catalogo.

#### Acceptance Criteria

1. `R4.AC1` IF a creation request omits name, price or quantity, THEN the system SHALL return HTTP 422.
   - Acceptance check: richieste prive di ciascun campo obbligatorio vengono respinte.
2. `R4.AC2` IF a submitted name is empty or contains only whitespace, THEN the system SHALL return HTTP 422.
   - Acceptance check: sia creazione sia aggiornamento respingono `""` e `"   "` come nome.
3. `R4.AC3` IF a submitted price is a boolean, negative or non-finite, THEN the system SHALL return HTTP 422.
   - Acceptance check: un prezzo booleano o negativo viene respinto; zero e un prezzo positivo sono accettati. Valori non finiti non entrano nel catalogo.
4. `R4.AC4` IF a submitted quantity is negative or fractional, THEN the system SHALL return HTTP 422.
   - Acceptance check: quantita negative e frazionarie vengono respinte; zero e interi positivi sono accettati.
5. `R4.AC5` IF a product request is rejected as invalid, THEN the system SHALL leave the catalog unchanged.
   - Acceptance check: confrontare l'elenco prima e dopo una creazione o un aggiornamento non valido; contenuto e valori restano identici.
6. `R4.AC6` IF a submitted name is longer than 200 characters, a price is greater than 9000000 or a quantity is greater than 1000000, THEN the system SHALL return HTTP 422.
   - Acceptance check: nome di 200 caratteri, prezzo 9000000 e quantita 1000000 sono accettati; 201 caratteri, 9000000.01 e 1000001 vengono respinti sia in creazione sia in aggiornamento.

## Non-Functional Requirements

- `NFR1` Integrita del catalogo nelle richieste respinte, osservabile tramite `R4.AC5`. Nessun obiettivo prestazionale per questo esercizio.

## Constraints And Dependencies

- `C1` Python e FastAPI, come concordato.
- `C2` Dati esclusivamente in memoria: nessuna conservazione dopo il riavvio e nessuna condivisione tra processi.
- `C3` Endpoint, modelli e logica di business separati in `main.py`, `models.py` e `service.py`.
- `C4` Sviluppo incrementale, con test e revisione sotto supervisione umana.

## Out Of Scope

- Database e persistenza.
- Eliminazione prodotti e ricerca del singolo prodotto.
- Autenticazione, interfaccia grafica e distribuzione in produzione.
- Vincoli di unicita del nome, paginazione e gestione avanzata del magazzino.
