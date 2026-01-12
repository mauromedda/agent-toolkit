#!/bin/bash
# ABOUTME: Status line for Claude Code displaying model, directory, branch, cost, and context
# ABOUTME: Receives JSON from stdin and formats output for the status line (right-aligned)

input=$(cat)

# Claude Code colors (ANSI true color)
ORANGE='\033[38;2;217;119;87m'   # Claude orange/coral
BLUE='\033[38;2;147;178;214m'    # Light blue
GREEN='\033[38;2;134;188;134m'   # Soft green
YELLOW='\033[38;2;229;192;123m'  # Soft yellow
CYAN='\033[38;2;139;191;191m'    # Soft cyan
DIM='\033[2m'                     # Dim
RESET='\033[0m'

# Icons
ICON_FOLDER="📁"
ICON_BRANCH="🌿"
ICON_MODEL="🍵"
ICON_COST="💰"
ICON_SESSION="🔗"

# Extract model, directory, and session ID
MODEL_DISPLAY=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // "."')
SESSION_ID=$(echo "$input" | jq -r '.session_id // "unknown"')
SESSION_ID_SHORT="${SESSION_ID:0:8}"

# Display path with ~ for home directory
DIR_DISPLAY="${CURRENT_DIR/#$HOME/~}"

# Display git branch if inside a repository
GIT_BRANCH=""
GIT_BRANCH_PLAIN=""
if git -C "$CURRENT_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)
    COMMIT_COUNT=$(git -C "$CURRENT_DIR" rev-list --count HEAD 2>/dev/null || echo "0")
    if [[ -n "$BRANCH" ]]; then
        GIT_BRANCH="  ${ICON_BRANCH} ${GREEN}${BRANCH}${RESET} ${DIM}(${COMMIT_COUNT})${RESET}"
        GIT_BRANCH_PLAIN="  ${BRANCH} (${COMMIT_COUNT})"
    fi
fi

# Extract session cost
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
COST_DISPLAY=""
COST_PLAIN=""
if [[ "$COST" != "0" && "$COST" != "null" ]]; then
    COST_FMT=$(printf '%.2f' "$COST")
    COST_DISPLAY="  ${ICON_COST} ${YELLOW}\$${COST_FMT}${RESET}"
    COST_PLAIN="  \$${COST_FMT}"
fi

# Extract context usage and generate progress bar
CTX_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
INPUT_TOKENS=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
CACHE_CREATE=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
CACHE_READ=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')

CTX_DISPLAY=""
CTX_PLAIN=""
if [[ "$CTX_SIZE" != "0" && "$CTX_SIZE" != "null" ]]; then
    CURRENT_TOKENS=$((INPUT_TOKENS + CACHE_CREATE + CACHE_READ))
    if [[ "$CURRENT_TOKENS" -gt 0 ]]; then
        PERCENT=$((CURRENT_TOKENS * 100 / CTX_SIZE))

        # Progress bar (10 blocks)
        BAR_WIDTH=10
        FILLED=$((PERCENT * BAR_WIDTH / 100))
        [[ "$FILLED" -gt "$BAR_WIDTH" ]] && FILLED=$BAR_WIDTH
        EMPTY=$((BAR_WIDTH - FILLED))

        # Choose color based on percentage
        if [[ "$PERCENT" -lt 50 ]]; then
            BAR_COLOR="$GREEN"
            ICON_CTX="🟢"
        elif [[ "$PERCENT" -lt 80 ]]; then
            BAR_COLOR="$YELLOW"
            ICON_CTX="🟡"
        else
            BAR_COLOR="$ORANGE"
            ICON_CTX="🔴"
        fi

        # Build progress bar
        BAR_FILLED=$(printf '█%.0s' $(seq 1 $FILLED 2>/dev/null) || true)
        BAR_EMPTY=$(printf '░%.0s' $(seq 1 $EMPTY 2>/dev/null) || true)

        CTX_DISPLAY="  ${ICON_CTX} ${BAR_COLOR}${BAR_FILLED}${DIM}${BAR_EMPTY}${RESET} ${CYAN}${PERCENT}%${RESET}"
        CTX_PLAIN="  ${BAR_FILLED}${BAR_EMPTY} ${PERCENT}%"
    fi
fi

# Build output
OUTPUT="${ICON_SESSION} ${DIM}${SESSION_ID}${RESET}  ${ICON_FOLDER} ${BLUE}${DIR_DISPLAY}${RESET}${GIT_BRANCH}  ${ICON_MODEL} ${ORANGE}${MODEL_DISPLAY}${RESET}${COST_DISPLAY}${CTX_DISPLAY}"
OUTPUT_PLAIN="${SESSION_ID}  ${DIR_DISPLAY}${GIT_BRANCH_PLAIN}  ${MODEL_DISPLAY}${COST_PLAIN}${CTX_PLAIN}"

# Calculate terminal width and padding for right-align
TERM_WIDTH=$(tput cols 2>/dev/null || echo 120)
# Account for emoji width (each emoji takes ~2 cells)
EMOJI_COUNT=5
[[ -n "$GIT_BRANCH" ]] && EMOJI_COUNT=$((EMOJI_COUNT + 1))
[[ -n "$COST_DISPLAY" ]] && EMOJI_COUNT=$((EMOJI_COUNT + 1))
[[ -n "$CTX_DISPLAY" ]] && EMOJI_COUNT=$((EMOJI_COUNT + 1))

TEXT_LEN=${#OUTPUT_PLAIN}
PADDING=$((TERM_WIDTH - TEXT_LEN - EMOJI_COUNT))
[[ "$PADDING" -lt 0 ]] && PADDING=0

# Output with left padding
printf "%${PADDING}s" ""
echo -e "$OUTPUT"
