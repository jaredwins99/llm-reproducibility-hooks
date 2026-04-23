#!/usr/bin/env bash
# UserPromptSubmit hook for the eval harness with_refs variant.
#
# Reads the user's prompt, extracts Stan-relevant keywords, runs search.sh for
# each, and emits the results to be injected into Claude's context before it
# starts working. "Hard" reference-forcing: Claude sees reference content
# before writing anything, no chance to skip.
#
# Exits 0 always (non-blocking).

set -euo pipefail

PAYLOAD=$(cat)
PROMPT=$(printf '%s' "$PAYLOAD" | python3 -c 'import json, sys; d = json.load(sys.stdin); print(d.get("prompt", ""))' || true)

[[ -z "$PROMPT" ]] && exit 0

# Only fire when the prompt is Stan-relevant.
if ! printf '%s' "$PROMPT" | grep -qiE 'stan|ingarch|poisson|bayesian|mcmc|hierarchical|multilevel|zero[- ]inflat|gaussian process|gp\b|posterior'; then
    exit 0
fi

SEARCH_SCRIPT="${CLAUDE_PROJECT_DIR:-$PWD}/reference/stan/search.sh"
if [[ ! -e "$SEARCH_SCRIPT" ]]; then
    exit 0  # refs not available
fi

# Build a concept list by matching the prompt against common Stan concepts.
# This is intentionally coarse — we just need queries that hit relevant files.
concepts=()
grep -qi 'zero[- ]inflat\|hurdle'             <<< "$PROMPT" && concepts+=("zero inflated hurdle")
grep -qi 'hierarchical\|multilevel'           <<< "$PROMPT" && concepts+=("hierarchical reparameterization non-centered")
grep -qi 'mixture\|latent'                    <<< "$PROMPT" && concepts+=("finite mixture log_sum_exp")
grep -qi 'gaussian process\|gp\b\|kernel'     <<< "$PROMPT" && concepts+=("gp_exp_quad_cov cholesky")
grep -qi 'poisson\|count'                     <<< "$PROMPT" && concepts+=("poisson_log poisson")
grep -qi 'time series\|ingarch\|arch\|garch\|ar\(p\)\|lag' <<< "$PROMPT" && concepts+=("time series autoregressive")
grep -qi 'ode\|differential equation'         <<< "$PROMPT" && concepts+=("ode_rk45 ode_bdf")
grep -qi 'survival\|censored\|hazard'         <<< "$PROMPT" && concepts+=("survival censored")
grep -qi 'spatial\|car\|icar'                 <<< "$PROMPT" && concepts+=("car icar spatial")
grep -qi 'divergen\|r.hat\|ess\|diagnostic'   <<< "$PROMPT" && concepts+=("divergent reparameterization")

# If nothing matched, dump a general-priors search as baseline.
[[ ${#concepts[@]} -eq 0 ]] && concepts+=("weakly informative priors")

cat <<'HEADER'
<reference-search>
The Stan reference library at `reference/stan/` (733 files: docs + 561 example models) contains authoritative material for this task. The hook below has pre-run searches for concepts matched in your prompt. Read the top-matched files before writing Stan code — do not work from memory.

HEADER

for c in "${concepts[@]}"; do
    echo "=== Search: \"$c\" ==="
    bash "$SEARCH_SCRIPT" --list "$c" 2>/dev/null | head -25 || true
    echo ""
done

cat <<'FOOTER'
You can run additional searches during your work:
  bash reference/stan/search.sh --list "concept"      # file menu
  bash reference/stan/search.sh --class 1b "concept"  # example-model files only
  bash reference/stan/search.sh --read "concept"      # top 3 full files

Read matching files with the Read tool before writing .stan code.
</reference-search>
FOOTER
