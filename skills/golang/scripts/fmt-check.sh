#!/usr/bin/env bash
# ABOUTME: Verify Go code formatting without modifying files
# ABOUTME: Returns non-zero exit code if any files need formatting

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_error() { echo -e "${RED}ERROR: $1${NC}" >&2; }
log_success() { echo -e "${GREEN}$1${NC}"; }
log_info() { echo -e "${BLUE}$1${NC}"; }

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [PATHS...]

Verify Go code formatting without modifying files.

OPTIONS:
    -h, --help      Show this help message
    -d, --diff      Show diff of formatting changes
    -f, --fix       Fix formatting (runs gofmt -w)
    -s, --simplify  Apply simplification rules (gofmt -s)

PATHS:
    Directories or files to check (default: .)

EXAMPLES:
    $(basename "$0")                # Check all Go files
    $(basename "$0") ./pkg          # Check specific directory
    $(basename "$0") --diff         # Show what would change
    $(basename "$0") --fix          # Fix formatting issues

EOF
}

# Parse arguments
SHOW_DIFF=false
FIX=false
SIMPLIFY=false
PATHS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -d|--diff)
            SHOW_DIFF=true
            shift
            ;;
        -f|--fix)
            FIX=true
            shift
            ;;
        -s|--simplify)
            SIMPLIFY=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            PATHS+=("$1")
            shift
            ;;
    esac
done

# Default paths
if [[ ${#PATHS[@]} -eq 0 ]]; then
    PATHS=(".")
fi

# Check for go command
if ! command -v gofmt &> /dev/null; then
    log_error "gofmt is not available; ensure Go is installed"
    exit 1
fi

# Build gofmt flags
FMT_FLAGS=()
if [[ "${SIMPLIFY}" == "true" ]]; then
    FMT_FLAGS+=(-s)
fi

# Fix mode
if [[ "${FIX}" == "true" ]]; then
    log_info "Fixing formatting..."
    for path in "${PATHS[@]}"; do
        if [[ -d "${path}" ]]; then
            find "${path}" -name "*.go" -type f -exec gofmt "${FMT_FLAGS[@]}" -w {} \;
        elif [[ -f "${path}" ]]; then
            gofmt "${FMT_FLAGS[@]}" -w "${path}"
        fi
    done
    log_success "Formatting fixed"
    exit 0
fi

# Check mode
log_info "Checking Go formatting..."

UNFORMATTED=""
for path in "${PATHS[@]}"; do
    if [[ -d "${path}" ]]; then
        # Find all Go files and check each
        while IFS= read -r -d '' file; do
            OUTPUT=$(gofmt "${FMT_FLAGS[@]}" -l "${file}")
            if [[ -n "${OUTPUT}" ]]; then
                UNFORMATTED="${UNFORMATTED}${OUTPUT}"$'\n'
            fi
        done < <(find "${path}" -name "*.go" -type f -print0)
    elif [[ -f "${path}" ]]; then
        OUTPUT=$(gofmt "${FMT_FLAGS[@]}" -l "${path}")
        if [[ -n "${OUTPUT}" ]]; then
            UNFORMATTED="${UNFORMATTED}${OUTPUT}"$'\n'
        fi
    fi
done

if [[ -n "${UNFORMATTED}" ]]; then
    log_error "Files need formatting:"
    echo "${UNFORMATTED}"

    if [[ "${SHOW_DIFF}" == "true" ]]; then
        echo ""
        log_info "Diff of required changes:"
        echo "---"
        for file in ${UNFORMATTED}; do
            if [[ -f "${file}" ]]; then
                echo "# ${file}"
                gofmt "${FMT_FLAGS[@]}" -d "${file}"
                echo ""
            fi
        done
    fi

    echo ""
    echo "Run to fix: gofmt -w <file>"
    echo "Or use:     $(basename "$0") --fix"
    exit 1
fi

log_success "All files are properly formatted"
