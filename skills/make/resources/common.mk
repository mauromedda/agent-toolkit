# ABOUTME: Reusable Makefile library with shared variables, colors, logging, and utility macros
# ABOUTME: Include in project Makefiles with: include path/to/common.mk

# ==============================================================================
# SAFETY SETTINGS (include once at top level)
# ==============================================================================
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# ==============================================================================
# PATH RESOLUTION
# ==============================================================================
# Directory containing this common.mk file
COMMON_MK_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Project root (assumes common.mk is in make/ subdirectory)
# Override in consuming Makefile if structure differs
PROJECT_ROOT ?= $(abspath $(COMMON_MK_DIR)/..)

# ==============================================================================
# ENVIRONMENT
# ==============================================================================
# Docker BuildKit for better builds
export DOCKER_BUILDKIT := 1
export COMPOSE_DOCKER_CLI_BUILD := 1

# Timestamp for backups and logs
TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

# Git information (with fallbacks)
GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
GIT_DIRTY := $(shell git diff --quiet 2>/dev/null || echo "-dirty")

# ==============================================================================
# COLORS (ANSI escape codes)
# ==============================================================================
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
BOLD := \033[1m
DIM := \033[2m
NC := \033[0m

# ==============================================================================
# LOGGING MACROS
# ==============================================================================
# Usage: $(call log_info,Your message here)

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
	@printf "\n$(BOLD)>>> %s$(NC)\n" "$(1)"
endef

define log_debug
	@printf "$(DIM)[DEBUG] %s$(NC)\n" "$(1)"
endef

# ==============================================================================
# UTILITY MACROS
# ==============================================================================

# Check if a command exists
# Usage: $(call check_cmd,docker)
define check_cmd
	@command -v $(1) >/dev/null 2>&1 || { \
		printf "$(RED)[ERROR]$(NC) Required command not found: $(1)\n"; \
		exit 1; \
	}
endef

# Ensure a directory exists
# Usage: $(call ensure_dir,build/output)
define ensure_dir
	@mkdir -p $(1)
endef

# Confirm a dangerous action
# Usage: $(call confirm,Are you sure you want to delete everything?)
define confirm
	@read -p "$(1) [y/N] " ans && [ "$${ans:-N}" = "y" ] || { echo "Aborted."; exit 1; }
endef

# Print a separator line
define separator
	@printf "$(DIM)%s$(NC)\n" "────────────────────────────────────────────────────────────"
endef

# ==============================================================================
# DEPENDENCY CHECK TARGET
# ==============================================================================
# Common dependencies - extend in consuming Makefile
REQUIRED_COMMANDS ?= git

.PHONY: deps-check
deps-check: ## Check required dependencies
	$(call log_step,Checking dependencies)
	@for cmd in $(REQUIRED_COMMANDS); do \
		if command -v $$cmd >/dev/null 2>&1; then \
			printf "  $(GREEN)✓$(NC) $$cmd\n"; \
		else \
			printf "  $(RED)✗$(NC) $$cmd (not found)\n"; \
			exit 1; \
		fi; \
	done
	$(call log_success,All dependencies satisfied)

# ==============================================================================
# HELP SYSTEM
# ==============================================================================
# Self-documenting help using ## comments
# Usage in targets: target: ## Description of what this target does
# Usage for sections: ##@ Section Name

.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(CYAN)<target>$(NC)\n"} \
		/^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BOLD)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# ==============================================================================
# VERSION INFO TARGET
# ==============================================================================
.PHONY: version
version: ## Show version information
	@printf "$(BOLD)Version Info$(NC)\n"
	@printf "  Git SHA:    %s%s\n" "$(GIT_SHA)" "$(GIT_DIRTY)"
	@printf "  Branch:     %s\n" "$(GIT_BRANCH)"
	@printf "  Timestamp:  %s\n" "$(TIMESTAMP)"
