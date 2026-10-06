# NEXUS-BTC: Network–Entity eXplainable Unified Surveillance for Bitcoin
# Air-Gapped Forensic Platform Makefile

SHELL := /bin/bash
PYTHON := .venv/bin/python
PIP := .venv/bin/pip
NPM := npm

.PHONY: help install build test test-offline serve dev clean scenario

help:
	@echo "NEXUS-BTC Build & Orchestration Commands:"
	@echo "  make install       - Create virtualenv, install Python and Frontend dependencies"
	@echo "  make build         - Compile production offline React frontend bundle"
	@echo "  make test          - Run full pytest test suite across backend and e2e"
	@echo "  make test-offline  - Execute complete air-gapped 10-step offline verification"
	@echo "  make serve         - Launch backend and serve embedded frontend (default port 8000)"
	@echo "  make dev           - Run frontend Vite dev server concurrently with backend"
	@echo "  make scenario      - Generate synthetic adversarial laundering topologies"
	@echo "  make clean         - Remove cache artifacts, databases, and build outputs"

install:
	@echo "[*] Initializing local virtual environment..."
	python3 -m venv .venv
	@echo "[*] Installing Python dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt
	@echo "[*] Installing Frontend dependencies..."
	cd frontend && $(NPM) install

build:
	@echo "[*] Building local air-gapped frontend bundle..."
	cd frontend && $(NPM) run build

test:
	@echo "[*] Running comprehensive automated test suite..."
	PYTHONPATH=backend $(PYTHON) -m pytest backend/tests tests -v

test-offline:
	@echo "[*] Executing air-gapped offline test suite..."
	bash scripts/offline_test.sh

serve:
	@echo "[*] Starting NEXUS-BTC on http://127.0.0.1:8000..."
	PYTHONPATH=backend:. $(PYTHON) -m nexus serve --host 127.0.0.1 --port 8000

scenario:
	@echo "[*] Generating synthetic forensic scenario..."
	PYTHONPATH=backend:. $(PYTHON) -m nexus scenario PEELING_CHAIN

clean:
	@echo "[*] Cleaning temporary files and caches..."
	rm -rf backend/.pytest_cache tests/.pytest_cache frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f data/nexus_forensics.db* data/normalized/quarantine/*.json
