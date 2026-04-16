#!/usr/bin/env bash
# Tree 05: Data Sensitivity
# Determines data classification and security controls.

tree_05_walk() {
    forest_header "Data Sensitivity"

    local sensitivity
    sensitivity=$(forest_select_many "How sensitive is your data?" \
        "public:Public / open data" \
        "internal:Internal / proprietary" \
        "regulated:Regulated (PII, HIPAA, etc.)")

    [[ -z "$sensitivity" ]] && return 0
    SELECTIONS[data_sensitivity]="$sensitivity"

    local has_regulated=false
    local has_restricted=false

    local IFS=','
    for level in $sensitivity; do
        case "$level" in
            regulated)
                has_regulated=true
                has_restricted=true
                ;;
            internal)
                has_restricted=true
                ;;
        esac
    done

    if [[ "$has_regulated" == true ]]; then
        forest_subheader "Regulation"
        local reg_type
        reg_type=$(forest_select_one "What regulation applies?" \
            "hipaa:HIPAA" \
            "gdpr:GDPR" \
            "sox:SOX" \
            "other:Other")
        SELECTIONS[regulated_type]="$reg_type"
    fi

    if [[ "$has_restricted" == true ]]; then
        forest_subheader "Security Controls"

        if forest_confirm "Disable AI tooling (Claude, Copilot, etc.)?" "n"; then
            SELECTIONS[ai_tooling]="disabled"
        else
            SELECTIONS[ai_tooling]="enabled"
        fi

        if forest_confirm "Disable telemetry everywhere?" "n"; then
            SELECTIONS[telemetry]="disabled"
        else
            SELECTIONS[telemetry]="enabled"
        fi
    fi
}
