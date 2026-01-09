#!/bin/bash
# ABOUTME: Makefile validation script with hybrid checkmake + custom pattern checks
# ABOUTME: Validates safety headers, help target, .PHONY declarations, forbidden patterns
#
# File: validate_makefile.sh
# Author: Mauro Medda
# Created: 2025-01-08
# Purpose: Validate Makefile quality and compliance with make skill standards

set -euo pipefail

# ============================================================================
# GLOBAL VARIABLES AND CONSTANTS
# ============================================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly VERSION="1.0.0"

# Exit codes
declare -ri EXIT_SUCCESS=0
declare -ri EXIT_FAILURE=1
declare -ri EXIT_USAGE=2

# Validation state
declare -i ERRORS=0
declare -i WARNINGS=0

# Colors
readonly CYAN='\033[0;36m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================
log_info() {
    printf "${CYAN}[INFO]${NC} %s\n" "${*}" >&2
}

log_success() {
    printf "${GREEN}[OK]${NC} %s\n" "${*}" >&2
}

log_warn() {
    printf "${YELLOW}[WARN]${NC} %s\n" "${*}" >&2
    (( WARNINGS++ )) || true
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "${*}" >&2
    (( ERRORS++ )) || true
}

# ============================================================================
# HELP DOCUMENTATION
# ============================================================================
help() {
    cat <<EOF
${SCRIPT_NAME} v${VERSION}

USAGE:
    ${SCRIPT_NAME} [OPTIONS] [MAKEFILE]

DESCRIPTION:
    Validates Makefile quality and compliance with make skill standards.
    Uses checkmake if available, plus custom pattern checks.

OPTIONS:
    -h, --help      Show this help message
    -V, --version   Show version information
    -v, --verbose   Enable verbose output
    -s, --strict    Treat warnings as errors

ARGUMENTS:
    MAKEFILE        Path to Makefile (default: ./Makefile)

CHECKS PERFORMED:
    - Safety headers (SHELL, .SHELLFLAGS, .DELETE_ON_ERROR)
    - Help target exists with ## documentation
    - .PHONY declarations present
    - No forbidden patterns (complex shell logic, bare rm, etc.)
    - checkmake linter (if installed)

EXAMPLES:
    ${SCRIPT_NAME}                    # Validate ./Makefile
    ${SCRIPT_NAME} make/docker.mk     # Validate specific file
    ${SCRIPT_NAME} -s Makefile        # Strict mode

EXIT CODES:
    0    All checks passed
    1    Validation errors found
    2    Usage error

EOF
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================
check_safety_headers() {
    local -r makefile="${1}"

    log_info "Checking safety headers..."

    # Check for SHELL definition
    if ! grep -qE '^SHELL\s*:?=' "${makefile}"; then
        log_warn "Missing SHELL definition (recommended: SHELL := bash)"
    fi

    # Check for .SHELLFLAGS
    if ! grep -qE '^\.SHELLFLAGS\s*:?=' "${makefile}"; then
        log_warn "Missing .SHELLFLAGS (recommended: .SHELLFLAGS := -eu -o pipefail -c)"
    fi

    # Check for .DELETE_ON_ERROR
    if ! grep -qE '^\.DELETE_ON_ERROR:' "${makefile}"; then
        log_warn "Missing .DELETE_ON_ERROR directive"
    fi
}

check_help_target() {
    local -r makefile="${1}"

    log_info "Checking help target..."

    # Check for help target
    if ! grep -qE '^help:' "${makefile}"; then
        log_error "Missing help target"
        return
    fi

    # Check for ## documentation comments
    if ! grep -qE '^[a-zA-Z_-]+:.*##' "${makefile}"; then
        log_warn "No targets have ## documentation comments"
    fi

    # Check for .DEFAULT_GOAL := help
    if ! grep -qE '^\.DEFAULT_GOAL\s*:?=\s*help' "${makefile}"; then
        log_warn "Missing .DEFAULT_GOAL := help"
    fi
}

check_phony_declarations() {
    local -r makefile="${1}"

    log_info "Checking .PHONY declarations..."

    # Check if any .PHONY declarations exist
    if ! grep -qE '^\.PHONY:' "${makefile}"; then
        log_error "No .PHONY declarations found"
        return
    fi

    # Extract targets that look like they should be phony (no file output)
    local -a potential_phony
    potential_phony=($(grep -oE '^[a-zA-Z_][a-zA-Z0-9_-]*:' "${makefile}" | tr -d ':' | sort -u))

    # Extract declared phony targets
    local -a declared_phony
    declared_phony=($(grep -E '^\.PHONY:' "${makefile}" | sed 's/\.PHONY://g' | tr ' ' '\n' | sort -u))

    # Common phony target names that should be declared
    local -a common_phony=("help" "all" "clean" "test" "build" "install" "deploy" "lint" "format")

    for target in "${common_phony[@]}"; do
        if grep -qE "^${target}:" "${makefile}"; then
            if ! printf '%s\n' "${declared_phony[@]}" | grep -qE "^${target}$"; then
                log_warn "Target '${target}' should be declared .PHONY"
            fi
        fi
    done
}

check_forbidden_patterns() {
    local -r makefile="${1}"

    log_info "Checking for forbidden patterns..."

    # Check for bare rm (should use rm -f or rm -rf)
    # Uses word boundary to catch rm anywhere in the command
    if grep -nE $'^\t[^#]*\\brm[[:space:]]+[^-]' "${makefile}" 2>/dev/null; then
        log_warn "Found bare 'rm' without -f flag (use rm -f or rm -rf)"
    fi

    # Check for spaces instead of tabs in recipes
    # Look for lines that start with 4 spaces followed by a command character
    # Exclude continuation lines (previous line ends with \)
    local -i space_issues=0
    while IFS= read -r line_num; do
        # Get the previous line to check for continuation
        local prev_line
        prev_line=$(sed -n "$((line_num - 1))p" "${makefile}" 2>/dev/null || echo "")
        if [[ ! "${prev_line}" =~ \\$ ]]; then
            (( space_issues++ )) || true
            if (( space_issues <= 3 )); then
                grep -n '' "${makefile}" | sed -n "${line_num}p"
            fi
        fi
    done < <(grep -nE '^    [a-zA-Z@$]' "${makefile}" 2>/dev/null | cut -d: -f1)
    if (( space_issues > 0 )); then
        log_error "Found ${space_issues} line(s) with spaces instead of tabs in recipe"
    fi

    # Check for complex shell logic that should be in a script
    if grep -cE $'^\t.*if \[|^\t.*for .* in|^\t.*while ' "${makefile}" 2>/dev/null | grep -qvE '^0$'; then
        local -i complex_count
        complex_count=$(grep -cE $'^\t.*if \[|^\t.*for .* in|^\t.*while ' "${makefile}" 2>/dev/null || echo 0)
        if (( complex_count > 3 )); then
            log_warn "Found ${complex_count} instances of complex shell logic; consider moving to scripts"
        fi
    fi

    # Check for recursive make without $(MAKE)
    if grep -nE $'^\t[^#]*make [^$]' "${makefile}" 2>/dev/null; then
        log_warn "Found 'make' call without \$(MAKE); use \$(MAKE) for recursive make"
    fi
}

run_checkmake() {
    local -r makefile="${1}"

    if ! command -v checkmake &>/dev/null; then
        log_info "checkmake not installed; skipping linter checks"
        log_info "Install with: go install github.com/mrtazz/checkmake/cmd/checkmake@latest"
        return
    fi

    log_info "Running checkmake linter..."

    local output
    if output=$(checkmake "${makefile}" 2>&1); then
        log_success "checkmake passed"
    else
        log_warn "checkmake found issues:"
        echo "${output}" | head -20 >&2
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    local makefile="Makefile"
    local verbose=false
    local strict=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "${1}" in
            -h|--help)
                help
                exit "${EXIT_SUCCESS}"
                ;;
            -V|--version)
                echo "${SCRIPT_NAME} version ${VERSION}"
                exit "${EXIT_SUCCESS}"
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -s|--strict)
                strict=true
                shift
                ;;
            -*)
                log_error "Unknown option: ${1}"
                help
                exit "${EXIT_USAGE}"
                ;;
            *)
                makefile="${1}"
                shift
                ;;
        esac
    done

    # Validate file exists
    if [[ ! -f "${makefile}" ]]; then
        log_error "File not found: ${makefile}"
        exit "${EXIT_FAILURE}"
    fi

    log_info "Validating: ${makefile}"
    echo ""

    # Run all checks
    check_safety_headers "${makefile}"
    check_help_target "${makefile}"
    check_phony_declarations "${makefile}"
    check_forbidden_patterns "${makefile}"
    run_checkmake "${makefile}"

    # Summary
    echo ""
    if (( ERRORS > 0 )); then
        log_error "Validation failed: ${ERRORS} error(s), ${WARNINGS} warning(s)"
        exit "${EXIT_FAILURE}"
    elif (( WARNINGS > 0 )); then
        if [[ "${strict}" == true ]]; then
            log_error "Validation failed (strict mode): ${WARNINGS} warning(s)"
            exit "${EXIT_FAILURE}"
        else
            log_warn "Validation passed with ${WARNINGS} warning(s)"
            exit "${EXIT_SUCCESS}"
        fi
    else
        log_success "Validation passed: no errors or warnings"
        exit "${EXIT_SUCCESS}"
    fi
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "${@}"
fi
