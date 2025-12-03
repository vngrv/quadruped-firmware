.PHONY: help install install-minimal install-dev run run-keyboard run-network run-vision clean test

PYTHON := python3
PIP := pip3
MAIN := main.py

help: ## Показать справку по командам
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install-minimal: ## Установить минимальные зависимости
	$(PIP) install -r requirements-minimal.txt

install: ## Установить все зависимости
	$(PIP) install -r requirements.txt

install-dev: install ## Установить зависимости для разработки
	$(PIP) install -r requirements-dev.txt

run: ## Запустить с контроллером по умолчанию (network_receiver)
	$(PYTHON) $(MAIN) --controller src.controllers.network_receiver

run-keyboard: ## Запустить с клавиатурным контроллером
	$(PYTHON) $(MAIN) --controller src.controllers.local_keyboard_controller

run-network: ## Запустить с сетевым контроллером
	$(PYTHON) $(MAIN) --controller src.controllers.network_receiver

run-vision: ## Запустить с контроллером компьютерного зрения
	$(PYTHON) $(MAIN) --controller src.controllers.object_tracker_controller

clean: ## Очистить кэш Python и временные файлы
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true

test: ## Запустить тесты
	@if [ -d "tests" ]; then pytest tests/ -v; else echo "tests/ not found"; fi

test-validators: ## Запустить тесты валидации
	@pytest tests/test_validators.py -v

test-coverage: ## Запустить тесты с покрытием
	@if [ -d "tests" ]; then pytest tests/ --cov=. --cov-report=html; else echo "tests/ not found"; fi

check: ## Проверить код линтерами
	@command -v pylint > /dev/null && pylint --disable=C,R src/ || echo "pylint not installed"

format: ## Форматировать код с помощью black
	@command -v black > /dev/null && black src/ || echo "black not installed, run: make install-dev"

