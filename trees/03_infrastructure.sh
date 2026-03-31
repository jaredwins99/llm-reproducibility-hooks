#!/usr/bin/env bash
# Tree 03: Infrastructure
# Determines where the project will run.

tree_03_walk() {
    forest_header "Infrastructure"

    local infra
    infra=$(forest_select_many "Where will this project run?" \
        "local:Local machine only" \
        "cloud:Cloud provider" \
        "hpc:HPC / compute cluster")

    [[ -z "$infra" ]] && return 0
    SELECTIONS[infrastructure]="$infra"

    local IFS=','
    for target in $infra; do
        case "$target" in
            cloud)
                forest_subheader "Cloud Providers"
                local providers
                providers=$(forest_select_many "Which cloud provider(s)?" \
                    "aws:AWS" \
                    "gcp:GCP" \
                    "azure:Azure")
                SELECTIONS[cloud_providers]="$providers"
                ;;
        esac
    done
}
