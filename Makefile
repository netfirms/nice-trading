# --- Nice Trading Platform Makefile ---

# Detection logic for Podman/Docker
SHELL := /bin/zsh
PATH := /usr/local/bin:$(PATH)

# Use absolute paths if found in /usr/local/bin, otherwise fallback to command -v
PODMAN := $(shell ls /usr/local/bin/podman 2>/dev/null || command -v podman 2>/dev/null)
DOCKER := $(shell ls /usr/local/bin/docker 2>/dev/null || command -v docker 2>/dev/null)

ifeq ($(PODMAN),)
    COMPOSE := docker-compose
    CONTAINER_ENGINE := docker
else
    # If podman is found, prefer podman-compose
    COMPOSE := $(shell ls /usr/local/bin/podman-compose 2>/dev/null || command -v podman-compose 2>/dev/null)
    ifeq ($(COMPOSE),)
        COMPOSE := podman compose
    endif
    CONTAINER_ENGINE := podman
endif

.PHONY: help install build run-api run-go-worker up down logs test clean db-shell podman-init

# Default target: show help
help:
	@echo "Nice Trading Platform - Operational Commands"
	@echo "-------------------------------------------"
	@echo "Local Development:"
	@echo "  make install         Install Python and Go dependencies"
	@echo "  make run-api         Run FastAPI management dashboard"
	@echo "  make run-go-worker   Run Go-based orderbook worker"
	@echo "  make test            Run pytest suite"
	@echo ""
	@echo "Container Orchestration ($(CONTAINER_ENGINE)):"
	@echo "  make up              Start all containers (detached)"
	@echo "  make down            Stop and remove all containers"
	@echo "  make build           Rebuild images"
	@echo "  make logs            Follow all container logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove binaries, pyc, and temp files"
	@echo "  make db-shell        Enter PostgreSQL console"
	@echo "  make podman-init     (Podman Only) Start the podman machine"

# --- Local Development ---

install:
	pip install -r requirements.txt
	cd workers/golang && go mod download

run-api:
	uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

run-go-worker:
	cd workers/golang && go run main.go

test:
	pytest tests/

# --- Container Management ---

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

podman-init:
	@if [ -n "$(PODMAN)" ]; then \
		echo "🚀 Starting Podman machine..."; \
		podman machine start || echo "⚠️ Podman machine might already be running or needs 'podman machine init'"; \
	else \
		echo "❌ Podman not found on this system."; \
	fi

# --- Utility ---

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f workers/golang/orderbook-worker-go
	@echo "✨ Workspace cleaned."

db-shell:
	$(COMPOSE) exec postgres psql -U postgres -d trading_bot
