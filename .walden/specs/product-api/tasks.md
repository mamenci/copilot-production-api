---
walden_schema_version: v1alpha1
status: approved
approved_at: 2026-11-09T08:51:55Z
last_modified: 2026-11-09T08:51:55Z
approved_fingerprint: sha256:c123decdd449b4e13f0e1b02f5b764322e803369fa76825186a71a09808c0649
source_design_approved_at: 2026-11-09T08:33:15Z
source_design_fingerprint: sha256:f3b75552d34830dd5e3c952bfab866c221626d7307cf8064705b966cbffad21f
---

# Implementation Plan

- [x] 1. Preparare ambiente e scheletro del progetto
  - Requirements: `C1`, `C3`, `C4`
  - Design: Architecture
  - Verification:
    - command: ["sh", "-c", "python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements-dev.txt && .venv/bin/python -c 'import fastapi, pydantic, httpx2, pytest, ruff; print(\"ENV_OK\")'"]
      expect_output: "ENV_OK"
      covers: ["C1", "C4"]
    - command: ["sh", "-c", "test -f main.py && test -f models.py && test -f service.py && test -d tests && echo LAYOUT_OK"]
      expect_output: "LAYOUT_OK"
      covers: ["C3"]
  - Note: creare `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `.gitignore`, i tre moduli e `tests/`.

- [x] 2. Creazione ed elenco prodotti
  - [x] 2.1 Modelli e servizio per creazione ed elenco
    - Requirements: `R1.AC2`, `R1.AC3`, `R2.AC2`
    - Design: Architecture, Verification Plan
    - Verification:
      - command: [".venv/bin/python", "-m", "pytest", "tests/test_service.py", "-v", "-k", "create or list"]
        expect_output: "passed"
        covers: ["R1.AC2", "R1.AC3", "R2.AC2"]
  - [x] 2.2 Endpoint POST e GET
    - Requirements: `R1.AC1`, `R2.AC1`, `R2.AC2`
    - Design: Architecture, Verification Plan
    - Verification:
      - command: [".venv/bin/python", "-m", "pytest", "tests/test_api.py", "-v", "-k", "create or list"]
        expect_output: "passed"
        covers: ["R1.AC1", "R2.AC1", "R2.AC2"]

- [x] 3. Aggiornamento parziale
  - [x] 3.1 Logica di aggiornamento nel servizio
    - Requirements: `R3.AC2`, `R3.AC3`
    - Design: Architecture, Failure Modes And Tradeoffs
    - Verification:
      - command: [".venv/bin/python", "-m", "pytest", "tests/test_service.py", "-v", "-k", "update"]
        expect_output: "passed"
        covers: ["R3.AC2", "R3.AC3"]
  - [x] 3.2 Endpoint PATCH con 404
    - Requirements: `R3.AC1`, `R3.AC3`
    - Design: Architecture
    - Verification:
      - command: [".venv/bin/python", "-m", "pytest", "tests/test_api.py", "-v", "-k", "update"]
        expect_output: "passed"
        covers: ["R3.AC1", "R3.AC3"]

- [x] 4. Validazione e integrità del catalogo
  - Requirements: `R4.AC1`, `R4.AC2`, `R4.AC3`, `R4.AC4`, `R4.AC5`, `R4.AC6`, `NFR1`
  - Design: Failure Modes And Tradeoffs, Verification Plan
  - Verification:
    - command: [".venv/bin/python", "-m", "pytest", "tests/test_api.py", "tests/test_service.py", "-v", "-k", "invalid or unchanged"]
      expect_output: "passed"
      covers: ["R4.AC1", "R4.AC2", "R4.AC3", "R4.AC4", "R4.AC5", "R4.AC6", "NFR1"]

- [x] 5. Revisione, refactoring e controlli finali
  - Requirements: `C3`, `C4`
  - Design: Simplicity And Elegance Review, Verification Plan
  - Verification:
    - command: [".venv/bin/python", "-m", "pytest", "tests/test_api.py", "tests/test_service.py", "-v"]
      expect_output: "passed"
      covers: ["R1.AC1", "R2.AC1", "R3.AC1"]
    - command: [".venv/bin/python", "-m", "ruff", "check", "main.py", "models.py", "service.py", "tests"]
      expect_output: "All checks passed"
      covers: ["C4"]
    - command: [".venv/bin/python", "-m", "ruff", "format", "--check", "main.py", "models.py", "service.py", "tests"]
      expect_output: "already formatted"
      covers: ["C4"]
