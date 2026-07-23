.PHONY: help install dev test lint run validate docker up down clean

help:
	@echo "Targets:"
	@echo "  install   Install the package"
	@echo "  dev       Install with development extras"
	@echo "  test      Run the test suite"
	@echo "  lint      Run ruff"
	@echo "  run       Run the honeypot with the local config"
	@echo "  validate  Validate the local config"
	@echo "  docker    Build the container image"
	@echo "  up        Start the full stack (compose)"
	@echo "  down      Stop the stack"
	@echo "  clean     Remove build artefacts and caches"

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

run:
	sentinels run --config config/sentinels.yml

validate:
	sentinels validate --config config/sentinels.yml

docker:
	docker build -t sentinels:latest .

up:
	docker compose up -d --build

down:
	docker compose down

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
