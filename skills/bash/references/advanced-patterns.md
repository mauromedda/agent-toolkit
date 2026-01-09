# ABOUTME: Advanced bash patterns for arrays, strings, error handling, parallelism
# ABOUTME: Reference for complex scripting scenarios

# Advanced Bash Patterns

## Arrays

### Indexed Arrays (Bash 4+)

```bash
declare -a files=()
files+=("file1.txt")
files+=("file2.txt")

for file in "${files[@]}"; do
    echo "Processing: ${file}"
done

echo "Count: ${#files[@]}"
echo "First two: ${files[@]:0:2}"
```

### Associative Arrays (Bash 4+)

```bash
declare -A config=()
config["host"]="localhost"
config["port"]="8080"

for key in "${!config[@]}"; do
    echo "${key} = ${config[${key}]}"
done

# Check if key exists
if [[ -v config[host] ]]; then
    echo "Host is configured"
fi
```

## String Manipulation

```bash
# Case conversion (Bash 4+)
declare -l lowercase_var="HELLO"  # Stores as "hello"
declare -u uppercase_var="hello"  # Stores as "HELLO"

text="hello world"
echo "${text^}"      # Hello world (capitalize first)
echo "${text^^}"     # HELLO WORLD (all uppercase)

# Pattern replacement
filename="test.tar.gz"
echo "${filename%.gz}"        # test.tar (remove from end)
echo "${filename#test.}"      # tar.gz (remove from start)
echo "${filename/test/demo}"  # demo.tar.gz (replace first)
echo "${filename//t/T}"       # TesT.Tar.gz (replace all)
```

## Advanced Error Handling

### Custom Exit Codes

```bash
declare -ri ERR_FILE_NOT_FOUND=10
declare -ri ERR_PERMISSION_DENIED=11
declare -ri ERR_NETWORK_FAILURE=12

handle_error() {
    local -r error_code="${1}"
    local -r error_msg="${2}"

    log_error "${error_msg}"
    case "${error_code}" in
        "${ERR_FILE_NOT_FOUND}") log_error "Check path and try again." ;;
        "${ERR_PERMISSION_DENIED}") log_error "Run with appropriate privileges." ;;
        "${ERR_NETWORK_FAILURE}") log_error "Check connectivity and retry." ;;
    esac
    exit "${error_code}"
}
```

### Error Stack Traces

```bash
error_exit() {
    local -r msg="${1}"
    local -r line="${2}"
    local -r func="${3}"

    log_error "Error in '${func}' at line ${line}: ${msg}"
    local -i frame=0
    while caller ${frame}; do
        (( frame++ ))
    done
    exit "${EXIT_FAILURE}"
}

trap 'error_exit "Command failed" "${LINENO}" "${FUNCNAME[0]}"' ERR
```

## Parallel Processing

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
}
```

## Temporary File Management

```bash
setup_temp_directory() {
    TEMP_DIR=$(mktemp -d -t "$(basename "${0}").XXXXXXXXXX")
    readonly TEMP_DIR
}

create_temp_file() {
    local -r prefix="${1:-temp}"
    mktemp "${TEMP_DIR}/${prefix}.XXXXXXXXXX"
}
```

## Progress Indicators

```bash
show_progress() {
    local -r current="${1}"
    local -r total="${2}"
    local -r task="${3:-Processing}"

    local -i percent=$(( (current * 100) / total ))
    local -i filled=$(( (current * 50) / total ))

    printf "\r%s: [%-50s] %d%%" "${task}" \
        "$(printf '%*s' "${filled}" '' | tr ' ' '=')" "${percent}"
    (( current == total )) && echo ""
}
```

## Input Validation

```bash
is_integer() {
    [[ "${1}" =~ ^-?[0-9]+$ ]]
}

is_positive_integer() {
    [[ "${1}" =~ ^[0-9]+$ ]] && (( ${1} > 0 ))
}

is_valid_email() {
    [[ "${1}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
}

is_valid_ip() {
    local -a octets
    IFS='.' read -r -a octets <<< "${1}"
    [[ ${#octets[@]} -eq 4 ]] || return 1
    for octet in "${octets[@]}"; do
        [[ "${octet}" =~ ^[0-9]+$ ]] || return 1
        (( octet >= 0 && octet <= 255 )) || return 1
    done
}
```

## Performance Tips

### Avoid Subprocess Spawning

```bash
# Bad: spawns external process
lines=$(cat file.txt | wc -l)

# Good: use mapfile (Bash 4+)
mapfile -t lines < file.txt
echo "Count: ${#lines[@]}"
```

### Efficient String Building

```bash
# Bad: repeated concatenation
result=""
for i in {1..1000}; do
    result="${result}${i}\n"
done

# Good: use array then join
results=()
for i in {1..1000}; do
    results+=("${i}")
done
result=$(IFS=$'\n'; echo "${results[*]}")
```

## Testing with bats-core

```bash
#!/usr/bin/env bats

setup() {
    export TEST_DIR="$(mktemp -d)"
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
}
```
