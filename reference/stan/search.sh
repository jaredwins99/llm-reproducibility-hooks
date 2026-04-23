#!/usr/bin/env bash
# Fast Stan reference search — class-prioritized
# Usage: bash reference/stan/search.sh "divergent transitions"
# Usage: bash reference/stan/search.sh --from-file model.stan
#
# Search priority:
#   Class 1 (official docs) → Class 2 (case studies, packages) → Class 3 (forum)
# When Class 3 contradicts Class 1, Class 1 wins.

set -euo pipefail

STAN_REF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_LINES=5
MAX_PER_CLASS=20

# ———————————————————————————————————
#       Class definitions
# ———————————————————————————————————
# Class 1: Official reference (always search first)
CLASS1_DIRS=(
    "$STAN_REF/users-guide"
    "$STAN_REF/reference-manual"
    "$STAN_REF/functions-reference"
    "$STAN_REF/cmdstan-guide"
    "$STAN_REF/cmdstanr"
    "$STAN_REF/cmdstanpy"
)

# Class 1b: Official example models (complete .stan files from stan-dev/example-models)
CLASS1B_DIRS=(
    "$STAN_REF/example-models"
)

# Class 2: Case studies & supporting packages
CLASS2_DIRS=(
    "$STAN_REF/case-studies"
    "$STAN_REF/math-library"
    "$STAN_REF/compiler"
    "$STAN_REF/bayesplot"
    "$STAN_REF/loo"
    "$STAN_REF/posterior"
)

# Class 3: Community knowledge (verify against Class 1)
CLASS3_DIRS=(
    "$STAN_REF/forum"
)

usage() {
    echo "Usage: $0 <query>                      Search by keyword(s)"
    echo "       $0 --list <query>               List matching files only (no content)"
    echo "       $0 --read <query>               Show full file content for top matches"
    echo "       $0 --from-file <.stan file>     Extract concepts from Stan code and search"
    echo "       $0 --class <1|1b|2|3> <query>   Search only a specific class"
}

# ———————————————————————————————————
#       Extract concepts from Stan code
# ———————————————————————————————————
extract_concepts() {
    local file="$1"

    # Distribution names
    grep -oE '[a-z_]+\s*\(' "$file" 2>/dev/null | sed 's/\s*($//' | sort -u

    # Stan keywords
    grep -oiE 'target\s*\+=|log_sum_exp|reduce_sum|map_rect|ode_rk45|ode_bdf|integrate_1d|algebra_solver|gp_exp_quad|cholesky|multi_normal|ordered|simplex|positive_ordered|unit_vector' "$file" 2>/dev/null | sort -u

    # Block names
    grep -oE '^(data|parameters|transformed parameters|model|generated quantities|functions)\s*\{' "$file" 2>/dev/null | sed 's/\s*{$//' | sort -u

    # Modeling patterns
    grep -oiE 'hierarchical|mixture|time.series|survival|censored|truncat|missing|latent|gaussian.process|changepoint|measurement.error|zero.inflat|hurdle|poststratif|cross.valid' "$file" 2>/dev/null | sort -u
}

# ———————————————————————————————————
#       Search a set of directories
# ———————————————————————————————————
search_class() {
    local class_label="$1"
    local pattern="$2"
    shift 2
    local -a dirs=("$@")

    # Filter to dirs that exist
    local -a existing=()
    for d in "${dirs[@]}"; do
        [[ -d "$d" ]] && existing+=("$d")
    done
    (( ${#existing[@]} == 0 )) && return 0

    local results
    results=$(grep -riEc "$pattern" "${existing[@]}" 2>/dev/null | grep -v ':0$' | sort -t: -k2 -rn | head -5 || true)

    [[ -z "$results" ]] && return 0

    echo "[$class_label]"
    while IFS=: read -r file count; do
        [[ -z "$file" ]] && continue
        local relpath="${file#$STAN_REF/}"
        echo "  --- $relpath ($count matches) ---"
        grep -niE "$pattern" "$file" -C "$CONTEXT_LINES" 2>/dev/null | head -"$MAX_PER_CLASS" | sed 's/^/  /'
        echo ""
    done <<< "$results"
}

# ———————————————————————————————————
#       List-only search (filenames + match counts)
# ———————————————————————————————————
list_class() {
    local class_label="$1"
    local pattern="$2"
    local max_files="${3:-10}"
    shift 3
    local -a dirs=("$@")

    local -a existing=()
    for d in "${dirs[@]}"; do
        [[ -d "$d" ]] && existing+=("$d")
    done
    (( ${#existing[@]} == 0 )) && return 0

    local results
    results=$(grep -riEc "$pattern" "${existing[@]}" 2>/dev/null | grep -v ':0$' | sort -t: -k2 -rn | head -"$max_files" || true)

    [[ -z "$results" ]] && return 0

    echo "[$class_label]"
    while IFS=: read -r file count; do
        [[ -z "$file" ]] && continue
        local relpath="${file#$STAN_REF/}"
        local lines
        lines=$(wc -l < "$file")
        echo "  $relpath ($count matches, ${lines}L)"
    done <<< "$results"
    echo ""
}

# ———————————————————————————————————
#       Read mode — show full content of top matches
# ———————————————————————————————————
read_top_matches() {
    local pattern="$1"
    shift
    local -a all_dirs=("$@")

    local -a existing=()
    for d in "${all_dirs[@]}"; do
        [[ -d "$d" ]] && existing+=("$d")
    done
    (( ${#existing[@]} == 0 )) && return 0

    local results
    results=$(grep -riEc "$pattern" "${existing[@]}" 2>/dev/null | grep -v ':0$' | sort -t: -k2 -rn | head -3 || true)

    [[ -z "$results" ]] && return 0

    while IFS=: read -r file count; do
        [[ -z "$file" ]] && continue
        local relpath="${file#$STAN_REF/}"
        local lines
        lines=$(wc -l < "$file")
        echo "=== $relpath ($count matches, ${lines}L) ==="
        if (( lines <= 200 )); then
            cat "$file"
        else
            grep -niE "$pattern" "$file" -C "$CONTEXT_LINES" 2>/dev/null | head -60
        fi
        echo ""
        echo "---"
        echo ""
    done <<< "$results"
}

# ———————————————————————————————————
#       Main search function
# ———————————————————————————————————
search_refs() {
    local query="$1"
    local pattern
    pattern=$(echo "$query" | tr ' ' '|')

    echo "=== Stan Reference: '$query' ==="
    echo "=== Version: 2.38 | Priority: Class 1 → 2 → 3 ==="
    echo ""

    search_class "CLASS 1 — Official Docs" "$pattern" "${CLASS1_DIRS[@]}"
    search_class "CLASS 1b — Example Models (stan-dev/example-models @ 2025-04-30)" "$pattern" "${CLASS1B_DIRS[@]}"
    search_class "CLASS 2 — Case Studies & Packages" "$pattern" "${CLASS2_DIRS[@]}"
    search_class "CLASS 3 — Community (verify against Class 1)" "$pattern" "${CLASS3_DIRS[@]}"
}

# ———————————————————————————————————
#       CLI
# ———————————————————————————————————
if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

if [[ "$1" == "--list" ]]; then
    shift
    query="$*"
    pattern=$(echo "$query" | tr ' ' '|')

    echo "=== Stan Reference: '$query' (file list) ==="
    echo ""
    list_class "CLASS 1 — Official Docs" "$pattern" 5 "${CLASS1_DIRS[@]}"
    list_class "CLASS 1b — Example Models" "$pattern" 10 "${CLASS1B_DIRS[@]}"
    list_class "CLASS 2 — Case Studies & Packages" "$pattern" 5 "${CLASS2_DIRS[@]}"
    list_class "CLASS 3 — Community" "$pattern" 3 "${CLASS3_DIRS[@]}"
    echo "Tip: use 'Read' tool on any file above, or --read for top 3 full files"

elif [[ "$1" == "--read" ]]; then
    shift
    query="$*"
    pattern=$(echo "$query" | tr ' ' '|')

    echo "=== Stan Reference: '$query' (full content, top 3) ==="
    echo ""
    # Combine all dirs, search across all, return top 3 full files
    local_all_dirs=("${CLASS1_DIRS[@]}" "${CLASS1B_DIRS[@]}" "${CLASS2_DIRS[@]}" "${CLASS3_DIRS[@]}")
    read_top_matches "$pattern" "${local_all_dirs[@]}"

elif [[ "$1" == "--from-file" ]]; then
    if [[ $# -lt 2 || ! -f "$2" ]]; then
        echo "ERROR: provide a .stan file" >&2
        exit 1
    fi

    concepts=$(extract_concepts "$2")
    if [[ -z "$concepts" ]]; then
        echo "No Stan concepts found in $2"
        exit 0
    fi

    echo "Extracted concepts: $(echo "$concepts" | tr '\n' ', ')"
    echo ""

    seen=""
    while IFS= read -r concept; do
        [[ -z "$concept" ]] && continue
        if echo "$seen" | grep -qF "$concept"; then continue; fi
        seen+="$concept "
        search_refs "$concept"
    done <<< "$concepts"

elif [[ "$1" == "--class" ]]; then
    class="$2"
    shift 2
    query="$*"
    pattern=$(echo "$query" | tr ' ' '|')

    case "$class" in
        1) search_class "CLASS 1" "$pattern" "${CLASS1_DIRS[@]}" ;;
        1b) search_class "CLASS 1b — Example Models" "$pattern" "${CLASS1B_DIRS[@]}" ;;
        2) search_class "CLASS 2" "$pattern" "${CLASS2_DIRS[@]}" ;;
        3) search_class "CLASS 3" "$pattern" "${CLASS3_DIRS[@]}" ;;
        *) echo "ERROR: class must be 1, 1b, 2, or 3" >&2; exit 1 ;;
    esac
else
    search_refs "$*"
fi
