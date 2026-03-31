#!/usr/bin/env bash
# forest.sh — Interactive prompt primitives for the decision tree wizard
# Part of The Forest framework
#
# All display output goes to /dev/tty so these functions work correctly
# when their stdout is captured with $().
# Return values go to stdout (captured by caller).

set -euo pipefail

# Colors
readonly FOREST_BOLD='\033[1m'
readonly FOREST_DIM='\033[2m'
readonly FOREST_GREEN='\033[0;32m'
readonly FOREST_YELLOW='\033[0;33m'
readonly FOREST_CYAN='\033[0;36m'
readonly FOREST_RED='\033[0;31m'
readonly FOREST_RESET='\033[0m'

# Print a styled header for a tree section
forest_header() {
    local title="$1"
    echo "" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_CYAN}══════════════════════════════════════${FOREST_RESET}" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_CYAN}  $title${FOREST_RESET}" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_CYAN}══════════════════════════════════════${FOREST_RESET}" >/dev/tty
    echo "" >/dev/tty
}

# Print a sub-header
forest_subheader() {
    local title="$1"
    echo "" >/dev/tty
    echo -e "${FOREST_BOLD}  $title${FOREST_RESET}" >/dev/tty
    echo -e "${FOREST_DIM}  ──────────────────────────────────${FOREST_RESET}" >/dev/tty
}

# Single-select prompt: returns the selected value on stdout
# Usage: result=$(forest_select_one "prompt" "option1:label1" "option2:label2" ...)
# Format: "value:Display Label"
forest_select_one() {
    local prompt="$1"
    shift
    local -a options=("$@")

    echo -e "  ${FOREST_BOLD}$prompt${FOREST_RESET}" >/dev/tty
    echo "" >/dev/tty

    local i=1
    for opt in "${options[@]}"; do
        local label="${opt#*:}"
        echo -e "    ${FOREST_CYAN}${i})${FOREST_RESET} $label" >/dev/tty
        ((i++))
    done
    echo "" >/dev/tty

    while true; do
        echo -ne "  ${FOREST_YELLOW}Select [1-${#options[@]}]:${FOREST_RESET} " >/dev/tty
        read -r choice </dev/tty

        if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#options[@]} )); then
            local selected="${options[$((choice-1))]}"
            local value="${selected%%:*}"
            local label="${selected#*:}"
            echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} ${FOREST_DIM}$label${FOREST_RESET}" >/dev/tty
            echo "$value"  # This is the only stdout — captured by caller
            return 0
        fi
        echo -e "  ${FOREST_RED}Invalid choice. Please enter a number between 1 and ${#options[@]}.${FOREST_RESET}" >/dev/tty
    done
}

# Multi-select prompt: returns comma-separated values on stdout
# Usage: result=$(forest_select_many "prompt" "option1:label1" "option2:label2" ...)
forest_select_many() {
    local prompt="$1"
    shift
    local -a options=("$@")

    echo -e "  ${FOREST_BOLD}$prompt${FOREST_RESET}" >/dev/tty
    echo -e "  ${FOREST_DIM}(enter numbers separated by spaces, e.g. \"1 3 4\")${FOREST_RESET}" >/dev/tty
    echo "" >/dev/tty

    local i=1
    for opt in "${options[@]}"; do
        local label="${opt#*:}"
        echo -e "    ${FOREST_CYAN}${i})${FOREST_RESET} $label" >/dev/tty
        ((i++))
    done
    echo "" >/dev/tty

    while true; do
        echo -ne "  ${FOREST_YELLOW}Select [1-${#options[@]}]:${FOREST_RESET} " >/dev/tty
        read -r choices </dev/tty

        local -a selected_values=()
        local -a selected_labels=()
        local valid=true

        for choice in $choices; do
            if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#options[@]} )); then
                local selected="${options[$((choice-1))]}"
                selected_values+=("${selected%%:*}")
                selected_labels+=("${selected#*:}")
            else
                echo -e "  ${FOREST_RED}Invalid choice: $choice. Please enter numbers between 1 and ${#options[@]}.${FOREST_RESET}" >/dev/tty
                valid=false
                break
            fi
        done

        if [[ "$valid" == true ]] && (( ${#selected_values[@]} > 0 )); then
            for label in "${selected_labels[@]}"; do
                echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} ${FOREST_DIM}$label${FOREST_RESET}" >/dev/tty
            done
            local IFS=','
            echo "${selected_values[*]}"  # stdout — captured by caller
            return 0
        elif [[ "$valid" == true ]]; then
            echo -e "  ${FOREST_RED}Please select at least one option.${FOREST_RESET}" >/dev/tty
        fi
    done
}

# Yes/No confirmation prompt (no capture needed — uses return code)
# Usage: if forest_confirm "Do something?"; then ...; fi
# Default is yes unless second arg is "n"
forest_confirm() {
    local prompt="$1"
    local default="${2:-y}"

    local hint="Y/n"
    [[ "$default" == "n" ]] && hint="y/N"

    echo -ne "  ${FOREST_BOLD}$prompt${FOREST_RESET} ${FOREST_DIM}[$hint]:${FOREST_RESET} " >/dev/tty
    read -r answer </dev/tty

    answer="${answer:-$default}"
    answer="${answer,,}"  # lowercase

    [[ "$answer" == "y" || "$answer" == "yes" ]]
}

# Free text input with default
# Usage: result=$(forest_input "prompt" "default_value")
forest_input() {
    local prompt="$1"
    local default="${2:-}"

    if [[ -n "$default" ]]; then
        echo -ne "  ${FOREST_BOLD}$prompt${FOREST_RESET} ${FOREST_DIM}[$default]:${FOREST_RESET} " >/dev/tty
    else
        echo -ne "  ${FOREST_BOLD}$prompt:${FOREST_RESET} " >/dev/tty
    fi

    read -r answer </dev/tty
    answer="${answer:-$default}"
    echo "$answer"  # stdout — captured by caller
}

# Print summary of selections (display only — goes to tty)
forest_summary() {
    echo "" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_GREEN}══════════════════════════════════════${FOREST_RESET}" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_GREEN}  Summary of Selections${FOREST_RESET}" >/dev/tty
    echo -e "${FOREST_BOLD}${FOREST_GREEN}══════════════════════════════════════${FOREST_RESET}" >/dev/tty
    echo "" >/dev/tty

    for key in $(echo "${!SELECTIONS[@]}" | tr ' ' '\n' | sort); do
        local value="${SELECTIONS[$key]}"
        echo -e "  ${FOREST_CYAN}$key${FOREST_RESET}: $value" >/dev/tty
    done
    echo "" >/dev/tty
}
