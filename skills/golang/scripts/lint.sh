#!/usr/bin/env bash
# ABOUTME: Wrapper script for golangci-lint with project configuration
# ABOUTME: Installs golangci-lint if missing and runs with sensible defaults

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
readonly GOLANGCI_LINT_VERSION="v1.62.0"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_error() { echo -e "${RED}ERROR: $1${NC}" >&2; }
log_success() { echo -e "${GREEN}$1${NC}"; }
log_warn() { echo -e "${YELLOW}$1${NC}"; }
log_info() { echo -e "${BLUE}$1${NC}"; }

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [PACKAGES...]

Run golangci-lint with project configuration.

OPTIONS:
    -h, --help          Show this help message
    -i, --install       Install golangci-lint if not present
    -f, --fix           Auto-fix issues where possible
    -v, --verbose       Verbose output
    --new               Only check new code (since last commit)
    --config FILE       Use custom config file

PACKAGES:
    Go packages to lint (default: ./...)

EXAMPLES:
    $(basename "$0")                    # Lint all packages
    $(basename "$0") ./pkg/...          # Lint specific package
    $(basename "$0") --fix              # Auto-fix issues
    $(basename "$0") --new              # Only check new code

EOF
}

install_golangci_lint() {
    log_info "Installing golangci-lint ${GOLANGCI_LINT_VERSION}..."
    if ! go install "github.com/golangci/golangci-lint/cmd/golangci-lint@${GOLANGCI_LINT_VERSION}"; then
        log_error "Failed to install golangci-lint"
        exit 1
    fi
    log_success "golangci-lint installed successfully"
}

# Parse arguments
INSTALL=false
FIX=false
VERBOSE=false
NEW_ONLY=false
CONFIG=""
PACKAGES=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -f|--fix)
            FIX=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --new)
            NEW_ONLY=true
            shift
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

# Default packages
if [[ ${#PACKAGES[@]} -eq 0 ]]; then
    PACKAGES=("./...")
fi

# Check for golangci-lint
if ! command -v golangci-lint &> /dev/null; then
    if [[ "${INSTALL}" == "true" ]]; then
        install_golangci_lint
    else
        log_error "golangci-lint is not installed"
        echo "Run with --install to install, or manually:"
        echo "  go install github.com/golangci/golangci-lint/cmd/golangci-lint@${GOLANGCI_LINT_VERSION}"
        exit 1
    fi
fi

# Build command
CMD=(golangci-lint run)

# Determine config file
if [[ -n "${CONFIG}" ]]; then
    CMD+=(--config "${CONFIG}")
elif [[ -f ".golangci.yml" ]]; then
    # Use project config if exists
    :
elif [[ -f ".golangci.yaml" ]]; then
    :
elif [[ -f "${SKILL_DIR}/resources/.golangci.yml" ]]; then
    CMD+=(--config "${SKILL_DIR}/resources/.golangci.yml")
fi

# Add flags
if [[ "${FIX}" == "true" ]]; then
    CMD+=(--fix)
fi

if [[ "${VERBOSE}" == "true" ]]; then
    CMD+=(-v)
fi

if [[ "${NEW_ONLY}" == "true" ]]; then
    CMD+=(--new-from-rev=HEAD~1)
fi

# Add packages
CMD+=("${PACKAGES[@]}")

# Show command if verbose
if [[ "${VERBOSE}" == "true" ]]; then
    log_info "Running: ${CMD[*]}"
fi

# Run linter
if "${CMD[@]}"; then
    log_success "Linting passed!"
else
    exit_code=$?
    log_error "Linting failed"
    exit ${exit_code}
fi
