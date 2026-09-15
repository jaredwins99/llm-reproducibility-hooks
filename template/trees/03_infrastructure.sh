#!/usr/bin/env bash
# Tree 03: Infrastructure
# Determines where the project will run.

tree_03_walk() {
    forest_header "Infrastructure"

    if forest_confirm "Reproducible stack: pinned conda + renv + CmdStan, Dockerfile, make setup/all/check, git hooks, working principles?" "y"; then
        SELECTIONS[reproducible_stack]="yes"
    else
        SELECTIONS[reproducible_stack]="no"
    fi

    if forest_confirm "MLflow experiment tracking: local tracking store, tracked_run helper, make mlflow-ui?" "n"; then
        SELECTIONS[mlflow]="yes"
    else
        SELECTIONS[mlflow]="no"
    fi

    if forest_confirm "DVC data and pipeline versioning: dvc.yaml mirroring make, remote placeholder, make dvc-*?" "n"; then
        SELECTIONS[dvc]="yes"
    else
        SELECTIONS[dvc]="no"
    fi

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
