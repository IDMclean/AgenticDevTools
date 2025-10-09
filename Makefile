# Makefile for project standards and validation

.PHONY: all build build-protocol install format lint analyze-protocol decompile-protocol

# ==============================================================================
# Main Targets
# ==============================================================================
all: build

build: build-protocol
	@echo "--> Build complete."

# ==============================================================================
# Protocol Compilation & Management
# ==============================================================================
build-protocol:
	@echo "--> Compiling AGENTS.md from protocol sources..."
	@python3 tooling/protocol_compiler.py

analyze-protocol:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make analyze-protocol file=<path_to_agents_md>"; \
		exit 1; \
	fi
	@echo "--> Analyzing protocol file: $(file)..."
	@python3 tooling/protocol_analyzer.py $(file)

decompile-protocol:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make decompile-protocol file=<path_to_agents_md> [out=<output_dir>]"; \
		exit 1; \
	fi
	@out_dir=${out:-protocols_decomposed}; \
	echo "--> Decompiling $(file) into directory: $$out_dir..."; \
	@python3 tooling/protocol_decompiler.py $(file) --output-dir $$out_dir

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