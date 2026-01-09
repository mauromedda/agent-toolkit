# ABOUTME: Minimal Makefile template with safety headers, help system, and logging
# ABOUTME: Extend with domain-specific targets; include modular .mk files as needed

# ==============================================================================
# SAFETY SETTINGS
# ==============================================================================
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.DEFAULT_GOAL := help

# ==============================================================================
# VARIABLES
# ==============================================================================
PROJECT_NAME ?= myproject

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# ==============================================================================
# LOGGING MACROS
# ==============================================================================
define log_info
	@printf "$(CYAN)[INFO]$(NC) %s\n" "$(1)"
endef

define log_success
	@printf "$(GREEN)[OK]$(NC) %s\n" "$(1)"
endef

define log_warn
	@printf "$(YELLOW)[WARN]$(NC) %s\n" "$(1)"
endef

define log_error
	@printf "$(RED)[ERROR]$(NC) %s\n" "$(1)"
endef

define log_step
	@printf "$(BOLD)>>> %s$(NC)\n" "$(1)"
endef

# ==============================================================================
# TARGETS
# ==============================================================================

##@ General
.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BOLD)$(PROJECT_NAME)$(NC)\n\nUsage:\n  make $(CYAN)<target>$(NC)\n"} \
		/^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BOLD)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
.PHONY: build
build: ## Build the project
	$(call log_step,Building $(PROJECT_NAME))
	@echo "Add your build commands here"
	$(call log_success,Build completed)

.PHONY: test
test: ## Run tests
	$(call log_step,Running tests)
	@echo "Add your test commands here"
	$(call log_success,Tests passed)

.PHONY: lint
lint: ## Run linters
	$(call log_step,Running linters)
	@echo "Add your lint commands here"
	$(call log_success,Linting passed)

##@ Cleanup
.PHONY: clean
clean: ## Clean build artifacts
	$(call log_step,Cleaning build artifacts)
	@rm -rf build/ dist/ *.egg-info/
	$(call log_success,Clean completed)
