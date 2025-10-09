# Makefile for project standards and validation

.PHONY: all build build-protocol install format lint

# ==============================================================================
# Main Targets
# ==============================================================================
all: build

build: build-protocol
	@echo "--> Build complete."

# ==============================================================================
# Protocol Compilation
# ==============================================================================
build-protocol:
	@echo "--> Compiling AGENTS.md from protocol sources..."
	@python3 tooling/protocol_compiler.py

# ==============================================================================
# Dependency Management
# ==============================================================================
install:
	@echo "--> Installing dependencies from requirements.txt..."
	@pip install -r requirements.txt

# ==============================================================================
# Code Quality & Formatting
# ==============================================================================
format:
	@echo "--> Formatting Python code with black..."
	@black .

lint:
	@echo "--> Linting Python code with flake8..."
	@flake8 .