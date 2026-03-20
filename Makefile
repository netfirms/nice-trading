# --- Nice Trading Platform Makefile ---

.PHONY: help install build run-api run-go-worker up down logs test clean db-shell

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
	@echo "Docker Orchestration:"
	@echo "  make up              Start all containers (detached)"
	@echo "  make down            Stop and remove all containers"
	@echo "  make build           Rebuild Docker images"
	@echo "  make logs            Follow all container logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove binaries, pyc, and temp files"
	@echo "  make db-shell        Enter PostgreSQL console"

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

# --- Docker ---

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

# --- Utility ---

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f workers/golang/orderbook-worker-go
	@echo "✨ Workspace cleaned."

db-shell:
	docker-compose exec postgres psql -U postgres -d trading_bot
