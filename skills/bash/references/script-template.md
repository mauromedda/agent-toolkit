# ABOUTME: Full production bash script template with all sections
# ABOUTME: Copy and customize for new scripts

# Bash Script Template

## Standard Template

```bash
#!/bin/bash
# set -n   # Uncomment for syntax check only (dry run)
# set -x   # Uncomment for execution tracing (debugging)
#
# File: script_name.sh
# Author: [Your Name]
# Created: YYYY-MM-DD
# Revision: YYYY-MM-DD
# Purpose: [Brief one-line description]
# Usage: See help() function below

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

# Default configuration
declare CONFIG_FILE="${CONFIG_FILE:-${SCRIPT_DIR}/.config}"
declare VERBOSE=false
declare DRY_RUN=false

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================
load_config() {
    if [[ -f "${CONFIG_FILE}" ]]; then
        log_info "Loading configuration from: ${CONFIG_FILE}"
        # shellcheck source=/dev/null
        source "${CONFIG_FILE}"
    else
        log_debug "No configuration file found at: ${CONFIG_FILE}"
    fi
}

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================
log_debug() {
    if [[ "${VERBOSE}" == true ]]; then
        echo "[DEBUG] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
    fi
}

log_info() {
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

log_warn() {
    echo "[WARN] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

log_error() {
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

die() {
    log_error "${*}"
    exit "${EXIT_FAILURE}"
}

# ============================================================================
# HELP DOCUMENTATION
# ============================================================================
help() {
    cat <<EOF
${SCRIPT_NAME} v${VERSION}

USAGE:
    ${SCRIPT_NAME} [OPTIONS] ARGUMENTS

DESCRIPTION:
    [Detailed description of what the script does]

OPTIONS:
    -h, --help              Show this help message and exit
    -v, --verbose           Enable verbose/debug output
    -V, --version           Show version information
    -c, --config FILE       Use alternate configuration file
    -n, --dry-run           Perform a dry run without making changes

ARGUMENTS:
    ARG1                    Description of first argument

EXAMPLES:
    ${SCRIPT_NAME} input.txt
    ${SCRIPT_NAME} --verbose input.txt

EXIT CODES:
    0    Success
    1    General failure
    2    Usage error

EOF
}

version() {
    echo "${SCRIPT_NAME} version ${VERSION}"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
check_dependencies() {
    local -a required_commands=("jq" "curl")
    local missing=false

    for cmd in "${required_commands[@]}"; do
        if ! command -v "${cmd}" &> /dev/null; then
            log_error "Required command not found: ${cmd}"
            missing=true
        fi
    done

    if [[ "${missing}" == true ]]; then
        die "Missing required dependencies."
    fi
}

validate_file() {
    local -r filepath="${1}"
    [[ -f "${filepath}" ]] || die "File not found: ${filepath}"
    [[ -r "${filepath}" ]] || die "File not readable: ${filepath}"
}

# ============================================================================
# CLEANUP AND SIGNAL HANDLING
# ============================================================================
cleanup() {
    local -ri exit_code=$?
    log_debug "Cleanup called with exit code: ${exit_code}"

    if [[ -n "${TEMP_DIR:-}" ]] && [[ -d "${TEMP_DIR}" ]]; then
        rm -rf "${TEMP_DIR}"
    fi

    exit "${exit_code}"
}

trap cleanup EXIT
trap 'die "Script interrupted"' INT TERM

# ============================================================================
# CORE BUSINESS LOGIC
# ============================================================================
process_input() {
    local -r input="${1}"
    log_info "Processing: ${input}"
    # Implementation here
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================
parse_arguments() {
    if [[ $# -eq 0 ]]; then
        help
        exit "${EXIT_USAGE}"
    fi

    while [[ $# -gt 0 ]]; do
        case "${1}" in
            -h|--help)
                help
                exit "${EXIT_SUCCESS}"
                ;;
            -V|--version)
                version
                exit "${EXIT_SUCCESS}"
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--config)
                [[ -z "${2:-}" ]] && die "Option ${1} requires an argument"
                CONFIG_FILE="${2}"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -*)
                die "Unknown option: ${1}"
                ;;
            *)
                break
                ;;
        esac
    done

    export -a POSITIONAL_ARGS=("${@}")
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    log_info "Starting ${SCRIPT_NAME} v${VERSION}"

    parse_arguments "${@}"
    load_config
    check_dependencies

    if [[ ${#POSITIONAL_ARGS[@]} -lt 1 ]]; then
        log_error "Missing required arguments"
        help
        exit "${EXIT_USAGE}"
    fi

    validate_file "${POSITIONAL_ARGS[0]}"
    process_input "${POSITIONAL_ARGS[0]}"

    log_info "Completed successfully"
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "${@}"
fi
```
