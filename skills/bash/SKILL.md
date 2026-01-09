---
name: bash
description: >-
  Guide for writing production-quality bash scripts following modern idiomatic practices.
  Enforces set -euo pipefail, [[ ]] conditionals, ${var} syntax, ShellCheck compliance.
  Triggers on "bash script", "shell script", ".sh file", "write a script", "automation script",
  "bash function", "shellcheck", "bash template", "pre-commit hook", "deploy script",
  "build script", "install script", "setup script", "bash error handling", "bash arrays",
  "bash loop", "bash conditional", "parse arguments", "getopts", "bash logging",
  "#!/bin/bash", "source script", "dot script", "shell function".
  PROACTIVE: MUST invoke when writing ANY .sh file or pre-commit hook.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# ABOUTME: Bash scripting skill for production-quality scripts with Bash 4.x+
# ABOUTME: Emphasizes safety, readability, maintainability, and mandatory ShellCheck compliance

# Bash Scripting Skill

## Overview

This skill generates production-quality bash scripts following modern idiomatic practices for Bash 4.x+, emphasizing safety, readability, maintainability, and mandatory ShellCheck compliance.

## When to Use Bash

**IMPORTANT**: Use bash only for **small tactical scripting**:

- Quick automation tasks (< 200 lines)
- Build/deployment scripts
- System administration tasks
- Glue code between other tools
- One-off data processing

**Do NOT use bash for**:

- Complex business logic (use Python, Go, etc.)
- Applications requiring data structures beyond arrays
- Anything requiring robust error handling with recovery
- Long-running services or daemons
- Code that needs unit testing coverage

If the script exceeds ~200 lines or requires complex logic, consider rewriting in Python or Go.

## 🔄 RESUMED SESSION CHECKPOINT

**When a session is resumed from context compaction, verify Bash scripting state:**

```
┌─────────────────────────────────────────────────────────────┐
│  SESSION RESUMED - BASH SKILL VERIFICATION                  │
│                                                             │
│  Before continuing Bash script implementation:              │
│                                                             │
│  1. Was I in the middle of writing Bash scripts?            │
│     → Check summary for "script", "shell", ".sh"            │
│                                                             │
│  2. Did I follow all Bash skill guidelines?                 │
│     → set -euo pipefail at top                              │
│     → [[ ]] conditionals (not [ ])                          │
│     → ${var} syntax with quotes                             │
│     → ABOUTME headers on new files                          │
│                                                             │
│  3. Check script quality before continuing:                 │
│     → Run: shellcheck <script>.sh                           │
│                                                             │
│  If implementation was in progress:                         │
│  → Review the partial script for completeness               │
│  → Ensure all variables are quoted                          │
│  → Verify ShellCheck passes with no warnings                │
└─────────────────────────────────────────────────────────────┘
```

## Target Environment

- **Bash Version**: 4.0+ (released 2009)
- **ShellCheck**: All scripts must pass without warnings
- **POSIX Compliance**: Not required; leverage Bash-specific features

## Core Principles

### 1. Safety Headers

Every script starts with strict error handling:

```bash
#!/bin/bash
# set -n   # Uncomment for syntax check only (dry run)
# set -x   # Uncomment for execution tracing (debugging)
set -euo pipefail

# -e: Exit immediately if a command exits with non-zero status
# -u: Treat unset variables as an error
# -o pipefail: Return value of pipeline is the value of the last command to exit with non-zero status
```

### 2. Modern Bash Syntax Standards

**Conditionals**

- Always use `[[ ]]` for test expressions (never `[ ]` or `test`)
- Supports pattern matching, regex, and prevents word splitting

```bash
if [[ "${var}" =~ ^[0-9]+$ ]]; then
    echo "Variable is numeric"
fi
```

**Variable Expansion**

- Always use `${var}` syntax (never `$var` alone)
- Always quote expansions: `"${var}"`

```bash
# Good
echo "Value: ${config_path}"
echo "Array: ${my_array[@]}"

# Bad (ShellCheck will flag these)
echo "Value: $config_path"
echo "Value: ${config_path}"  # Unquoted
```

**Command Substitution**

- Always use `$(command)` (never backticks)

```bash
current_date=$(date +"%Y-%m-%d")
file_count=$(find . -type f | wc -l)
```

**Arithmetic**

- Use `(( ))` for arithmetic operations

```bash
(( count++ ))
(( total = value1 + value2 ))
if (( count > 10 )); then
    echo "Count exceeded threshold"
fi
```

### 3. Error Handling Patterns

**Pattern 1: Complex Commands (need output and status)**

Use this when you need to capture command output and check the return code separately:

```bash
output=$(complex_command --with args 2>&1)
rc=$?
if [[ ${rc} -ne 0 ]]; then
    log_error "complex_command failed with status ${rc}"
    log_error "Output: ${output}"
    return "${EXIT_FAILURE}"
fi
```

**Pattern 2: Simple Commands (status check only)**

Use this for straightforward command execution where output isn't needed:

```bash
if ! simple_command --with args; then
    log_error "simple_command failed"
    return "${EXIT_FAILURE}"
fi

# Or for very simple checks
simple_command || die "Failed to execute simple_command"
```

**When to use each:**

- Use `rc=$?` when you need the output of the command AND need to handle errors
- Use `if ! command` when you only care about success/failure
- The `if ! (($?))` pattern is NOT recommended; use `if ! command` instead

### 4. Standard Script Template

```bash
#!/bin/bash
# set -n   # Uncomment for syntax check only (dry run)
# set -x   # Uncomment for execution tracing (debugging)
#
# File: script_name.sh
# Author: Mauro Medda
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
    [Detailed description of what the script does and its purpose]

OPTIONS:
    -h, --help              Show this help message and exit
    -v, --verbose           Enable verbose/debug output
    -V, --version           Show version information
    -c, --config FILE       Use alternate configuration file
                            Default: ${CONFIG_FILE}
    -n, --dry-run           Perform a dry run without making changes

ARGUMENTS:
    ARG1                    Description of first argument
    ARG2                    Description of second argument (optional)

EXAMPLES:
    # Basic usage
    ${SCRIPT_NAME} input.txt

    # With verbose output
    ${SCRIPT_NAME} --verbose input.txt

    # Using custom config
    ${SCRIPT_NAME} -c /path/to/config input.txt

EXIT CODES:
    0    Success
    1    General failure
    2    Usage error (invalid arguments)

ENVIRONMENT VARIABLES:
    CONFIG_FILE             Override default config file location
    DEBUG                   Enable debug mode (same as --verbose)

AUTHOR:
    Mauro Medda

EOF
}

version() {
    echo "${SCRIPT_NAME} version ${VERSION}"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
check_dependencies() {
    local -a required_commands=("jq" "curl" "awk")
    local missing=false

    for cmd in "${required_commands[@]}"; do
        if ! command -v "${cmd}" &> /dev/null; then
            log_error "Required command not found: ${cmd}"
            missing=true
        fi
    done

    if [[ "${missing}" == true ]]; then
        die "Missing required dependencies. Please install them and try again."
    fi
}

validate_file() {
    local -r filepath="${1}"

    if [[ ! -f "${filepath}" ]]; then
        die "File not found: ${filepath}"
    fi

    if [[ ! -r "${filepath}" ]]; then
        die "File not readable: ${filepath}"
    fi
}

validate_directory() {
    local -r dirpath="${1}"

    if [[ ! -d "${dirpath}" ]]; then
        die "Directory not found: ${dirpath}"
    fi

    if [[ ! -x "${dirpath}" ]]; then
        die "Directory not accessible: ${dirpath}"
    fi
}

# ============================================================================
# CLEANUP AND SIGNAL HANDLING
# ============================================================================
cleanup() {
    local -ri exit_code=$?

    log_debug "Cleanup function called with exit code: ${exit_code}"

    # Remove temporary files
    if [[ -n "${TEMP_DIR:-}" ]] && [[ -d "${TEMP_DIR}" ]]; then
        log_debug "Removing temporary directory: ${TEMP_DIR}"
        rm -rf "${TEMP_DIR}"
    fi

    exit "${exit_code}"
}

# Set up signal handlers
trap cleanup EXIT
trap 'die "Script interrupted by user"' INT TERM

# ============================================================================
# CORE BUSINESS LOGIC FUNCTIONS
# ============================================================================
process_input() {
    local -r input="${1}"

    log_info "Processing input: ${input}"

    if [[ -z "${input}" ]]; then
        die "Input cannot be empty"
    fi

    # Example: Complex command with output capture
    output=$(process_command "${input}" 2>&1)
    rc=$?
    if [[ ${rc} -ne 0 ]]; then
        log_error "Failed to process input: ${input}"
        log_error "Command output: ${output}"
        return "${EXIT_FAILURE}"
    fi

    log_debug "Process output: ${output}"

    # Example: Simple command check
    if ! validate_output "${output}"; then
        die "Output validation failed"
    fi

    return "${EXIT_SUCCESS}"
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
                log_debug "Verbose mode enabled"
                shift
                ;;
            -c|--config)
                if [[ -z "${2:-}" ]]; then
                    die "Option ${1} requires an argument"
                fi
                CONFIG_FILE="${2}"
                shift 2
                ;;
            -n|--dry-run)
                DRY_RUN=true
                log_info "Dry run mode enabled"
                shift
                ;;
            -*)
                die "Unknown option: ${1}. Use --help for usage information."
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

    local -r input_arg="${POSITIONAL_ARGS[0]}"

    validate_file "${input_arg}"
    process_input "${input_arg}"

    log_info "Script completed successfully"
    return "${EXIT_SUCCESS}"
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "${@}"
fi
```

## Advanced Patterns

### Working with Arrays

**Indexed Arrays (Bash 4+)**

```bash
# Declaration
declare -a files=()
declare -a -r readonly_array=("item1" "item2")

# Population
files+=("file1.txt")
files+=("file2.txt")

# Iteration
for file in "${files[@]}"; do
    echo "Processing: ${file}"
done

# Length
echo "Array has ${#files[@]} elements"

# Slicing
echo "First two: ${files[@]:0:2}"
```

**Associative Arrays (Bash 4+)**

```bash
# Declaration
declare -A config=()

# Population
config["host"]="localhost"
config["port"]="8080"

# Access
echo "Host: ${config[host]}"

# Iteration
for key in "${!config[@]}"; do
    echo "${key} = ${config[${key}]}"
done

# Check if key exists
if [[ -v config[host] ]]; then
    echo "Host is configured"
fi
```

### String Manipulation (Bash 4+)

```bash
# Lowercase/Uppercase (Bash 4+)
declare -l lowercase_var="HELLO"  # Stores as "hello"
declare -u uppercase_var="hello"  # Stores as "HELLO"

# Parameter expansion
text="hello world"
echo "${text^}"      # Hello world (capitalize first)
echo "${text^^}"     # HELLO WORLD (all uppercase)
echo "${text,}"      # hello world (lowercase first)
echo "${text,,}"     # hello world (all lowercase)

# Pattern replacement
filename="test.tar.gz"
echo "${filename%.gz}"        # test.tar (remove shortest match from end)
echo "${filename%%.gz}"       # test.tar (remove longest match from end)
echo "${filename#test.}"      # tar.gz (remove shortest match from start)
echo "${filename##*.}"        # gz (remove longest match from start)
echo "${filename/test/demo}"  # demo.tar.gz (replace first match)
echo "${filename//t/T}"       # TesT.Tar.gz (replace all matches)
```

### Advanced Error Handling

**Custom Exit Codes**

```bash
declare -ri ERR_FILE_NOT_FOUND=10
declare -ri ERR_PERMISSION_DENIED=11
declare -ri ERR_NETWORK_FAILURE=12

handle_error() {
    local -r error_code="${1}"
    local -r error_msg="${2}"

    log_error "${error_msg}"

    case "${error_code}" in
        "${ERR_FILE_NOT_FOUND}")
            log_error "File not found. Check path and try again."
            ;;
        "${ERR_PERMISSION_DENIED}")
            log_error "Permission denied. Run with appropriate privileges."
            ;;
        "${ERR_NETWORK_FAILURE}")
            log_error "Network error. Check connectivity and retry."
            ;;
    esac

    exit "${error_code}"
}
```

**Error Stack Traces**

```bash
error_exit() {
    local -r msg="${1}"
    local -r line="${2}"
    local -r func="${3}"

    log_error "Error in function '${func}' at line ${line}: ${msg}"
    log_error "Call stack:"

    local -i frame=0
    while caller ${frame}; do
        (( frame++ ))
    done

    exit "${EXIT_FAILURE}"
}

# Usage in script
trap 'error_exit "Command failed" "${LINENO}" "${FUNCNAME[0]}"' ERR
```

### Parallel Processing (Bash 4+)

```bash
process_files_parallel() {
    local -r -a files=("${@}")
    local -r max_jobs=4
    local -i job_count=0

    for file in "${files[@]}"; do
        process_single_file "${file}" &

        (( job_count++ ))

        if (( job_count >= max_jobs )); then
            wait -n
            (( job_count-- ))
        fi
    done

    wait
    log_info "All parallel processing complete"
}
```

### Temporary File Management

```bash
setup_temp_directory() {
    TEMP_DIR=$(mktemp -d -t "$(basename "${0}").XXXXXXXXXX")
    readonly TEMP_DIR

    log_debug "Created temporary directory: ${TEMP_DIR}"
}

create_temp_file() {
    local -r prefix="${1:-temp}"
    local temp_file

    temp_file=$(mktemp "${TEMP_DIR}/${prefix}.XXXXXXXXXX")
    echo "${temp_file}"
}
```

### Progress Indicators

```bash
show_progress() {
    local -r current="${1}"
    local -r total="${2}"
    local -r task="${3:-Processing}"

    local -i percent=$(( (current * 100) / total ))
    local -i bar_length=50
    local -i filled=$(( (current * bar_length) / total ))

    printf "\r%s: [" "${task}"
    printf "%${filled}s" '' | tr ' ' '='
    printf "%$((bar_length - filled))s" '' | tr ' ' ' '
    printf "] %d%% (%d/%d)" "${percent}" "${current}" "${total}"

    if (( current == total )); then
        echo ""
    fi
}
```

### Input Validation Functions

```bash
is_integer() {
    local -r value="${1}"
    [[ "${value}" =~ ^-?[0-9]+$ ]]
}

is_positive_integer() {
    local -r value="${1}"
    [[ "${value}" =~ ^[0-9]+$ ]] && (( value > 0 ))
}

is_valid_email() {
    local -r email="${1}"
    [[ "${email}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
}

is_valid_ip() {
    local -r ip="${1}"
    local -a octets

    IFS='.' read -r -a octets <<< "${ip}"

    [[ ${#octets[@]} -eq 4 ]] || return 1

    for octet in "${octets[@]}"; do
        [[ "${octet}" =~ ^[0-9]+$ ]] || return 1
        (( octet >= 0 && octet <= 255 )) || return 1
    done

    return 0
}

is_valid_url() {
    local -r url="${1}"
    [[ "${url}" =~ ^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$ ]]
}
```

## ShellCheck Compliance

### Mandatory Checks

All scripts must pass ShellCheck with zero warnings. Address issues in order of severity:

**Common ShellCheck Warnings and Fixes**

1. **SC2086: Double quote to prevent globbing and word splitting**

   ```bash
   # Bad
   rm $file

   # Good
   rm "${file}"
   ```

2. **SC2155: Declare and assign separately to avoid masking return values**

   ```bash
   # Bad
   local result=$(command)

   # Good
   local result
   result=$(command)
   ```

3. **SC2034: Variable appears unused**

   ```bash
   # If variable is used elsewhere, tell ShellCheck:
   # shellcheck disable=SC2034
   local unused_var="value"

   # Or use it:
   : "${unused_var}"  # Prevents error on 'set -u'
   ```

4. **SC1090: Can't follow non-constant source**

   ```bash
   # shellcheck source=/dev/null
   source "${CONFIG_FILE}"
   ```

5. **SC2046: Quote to prevent word splitting**

   ```bash
   # Bad
   files=$(find . -name "*.txt")
   for file in $files; do

   # Good
   while IFS= read -r file; do
       echo "${file}"
   done < <(find . -name "*.txt")
   ```

### Running ShellCheck

```bash
# Check single file
shellcheck script.sh

# Check with specific shell
shellcheck -s bash script.sh

# Check all scripts in directory
find . -name "*.sh" -exec shellcheck {} +

# Output in different formats
shellcheck -f json script.sh
shellcheck -f gcc script.sh  # GCC-style output for editors
```

## Testing Bash Scripts

**Testing is MANDATORY for scripts exceeding 100 lines.**

For smaller scripts (< 100 lines), testing is optional but recommended for complex logic.

### Basic Test Framework (bats-core)

```bash
#!/usr/bin/env bats
# test_script.bats

setup() {
    export TEST_DIR="$(mktemp -d)"
    export PATH="${BATS_TEST_DIRNAME}:${PATH}"
}

teardown() {
    rm -rf "${TEST_DIR}"
}

@test "script shows help with --help" {
    run script.sh --help
    [ "${status}" -eq 0 ]
    [[ "${output}" =~ "USAGE:" ]]
}

@test "script fails with invalid argument" {
    run script.sh --invalid
    [ "${status}" -ne 0 ]
    [[ "${output}" =~ "Unknown option" ]]
}

@test "script processes valid input" {
    echo "test data" > "${TEST_DIR}/input.txt"
    run script.sh "${TEST_DIR}/input.txt"
    [ "${status}" -eq 0 ]
}
```

## Performance Considerations

### Avoiding Subprocess Spawning

```bash
# Bad: Spawns external process
lines=$(cat file.txt | wc -l)

# Good: Use built-in
lines=0
while IFS= read -r line; do
    (( lines++ ))
done < file.txt

# Best: Use mapfile (Bash 4+)
mapfile -t lines < file.txt
echo "Line count: ${#lines[@]}"
```

### Efficient String Building

```bash
# Bad: Repeated concatenation
result=""
for i in {1..1000}; do
    result="${result}${i}\n"
done

# Good: Use array then join
results=()
for i in {1..1000}; do
    results+=("${i}")
done
result=$(IFS=$'\n'; echo "${results[*]}")
```

## Documentation Standards

### Inline Documentation

```bash
# Brief: One-line description of function purpose
# Arguments:
#   $1 - Description of first parameter (required)
#   $2 - Description of second parameter (optional, default: "value")
# Returns:
#   0 - Success
#   1 - Failure reason
# Outputs:
#   Writes processed data to stdout
#   Writes errors to stderr
# Example:
#   process_data "input.txt" "output.txt"
process_data() {
    local -r input="${1}"
    local -r output="${2:-/dev/stdout}"

    # Implementation
}
```

## Security Best Practices

1. **Never use `eval`** - Find alternatives using arrays or proper quoting
2. **Sanitize inputs** - Validate and sanitize all external input
3. **Use absolute paths** - Especially for system commands
4. **Avoid storing secrets** - Use environment variables or secret management
5. **Check file permissions** - Before reading sensitive files
6. **Use `readonly`** - For constants and immutable variables

```bash
readonly ALLOWED_COMMANDS=("ls" "cat" "grep")

execute_safe_command() {
    local -r cmd="${1}"

    local allowed=false
    for allowed_cmd in "${ALLOWED_COMMANDS[@]}"; do
        if [[ "${cmd}" == "${allowed_cmd}" ]]; then
            allowed=true
            break
        fi
    done

    if [[ "${allowed}" == false ]]; then
        die "Command not allowed: ${cmd}"
    fi

    command -v "${cmd}" &> /dev/null || die "Command not found: ${cmd}"
    "$(command -v "${cmd}")" "${@:2}"
}
```

## Checklist

Before considering a bash script complete, verify:

- [ ] ShellCheck passes with zero warnings
- [ ] Uses `set -euo pipefail` at the top
- [ ] All variables use `${var}` syntax and are quoted
- [ ] Uses `[[ ]]` for all conditionals
- [ ] Uses `$(command)` for command substitution
- [ ] Includes comprehensive `help()` function
- [ ] Has proper error handling (die/log functions)
- [ ] Uses appropriate error handling pattern (rc=$? or if !)
- [ ] Has cleanup trap for temporary resources
- [ ] Follows the standard script structure
- [ ] Variables are properly scoped (local/readonly)
- [ ] Has meaningful logging at appropriate levels
- [ ] Validates all inputs and arguments
- [ ] Checks for required dependencies
- [ ] Includes usage examples in help text
- [ ] Functions have single responsibility
- [ ] Exit codes are meaningful and documented
- [ ] **If > 100 lines**: Has bats tests

## Additional Resources

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/)
