# Project Constitution

This file captures stable project-wide context that applies across all features. It is optional and does not participate in the approval workflow.

## Project Summary

Esercizio didattico: sviluppare una API prodotti con Copilot tramite
pianificazione, implementazione multi-file, verifica e revisione iterative.

## Tech Stack

Python e FastAPI, con dati conservati in memoria. Nessun database.

## Conventions

Separare endpoint in `main.py`, modelli in `models.py` e logica di business
in `service.py`, come previsto dall'esercizio. Non sono state definite
convenzioni aggiuntive di branching o commit.

## Sanity Checks

I comandi di verifica saranno definiti nel piano tecnico prima
dell'implementazione. Verificare casi validi, input non validi e prodotti
inesistenti; completare anche una prova HTTP manuale.

## Key Files

`main.py`, `models.py`, `service.py` e i test, da creare nelle iterazioni
successive. Specifiche dell'esercizio in `.walden/specs/product-api/`.

## Hard Rules

Dati non persistenti: il riavvio perde i prodotti. Mantenere il controllo
umano sulle decisioni e verificare ogni incremento prima di proseguire.
