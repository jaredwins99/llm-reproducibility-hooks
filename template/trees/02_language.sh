#!/usr/bin/env bash
# Tree 02: Language
# Determines programming languages and their package managers.

tree_02_walk() {
    forest_header "Language"

    local languages
    languages=$(forest_select_many "What languages will this project use?" \
        "python:Python" \
        "r:R")

    [[ -z "$languages" ]] && return 0
    SELECTIONS[languages]="$languages"

    local IFS=','
    for lang in $languages; do
        case "$lang" in
            python)
                forest_subheader "Python Environment"
                local mgr
                mgr=$(forest_select_one "Package manager?" \
                    "uv:uv (recommended)" \
                    "conda:conda")
                SELECTIONS[python_env_manager]="$mgr"
                ;;
            r)
                # renv + rig is the default; no sub-question needed
                SELECTIONS[r_env_manager]="renv"
                ;;
        esac
    done
}
