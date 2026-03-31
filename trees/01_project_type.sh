#!/usr/bin/env bash
# Tree 01: Project Type
# Determines what the project produces and drills into sub-types.

tree_01_walk() {
    forest_header "Project Type"

    SELECTIONS[project_types]=""

    local top_types
    top_types=$(forest_select_many "What does this project produce?" \
        "dataset_report:Dataset, report, or dashboard" \
        "model_prediction:Model or prediction" \
        "service_application:Service or application" \
        "library:Reusable library or package")

    [[ -z "$top_types" ]] && return 0

    local combined=()
    local IFS=','
    for top in $top_types; do
        case "$top" in
            dataset_report)
                forest_subheader "Data Work"
                local sub
                sub=$(forest_select_one "What kind of data work?" \
                    "oneoff:One-off analysis" \
                    "pipeline_batch:Batch pipeline" \
                    "pipeline_streaming:Streaming pipeline")
                combined+=("dataset_${sub}")
                ;;
            model_prediction)
                forest_subheader "Model Type"
                local sub
                sub=$(forest_select_one "What kind of model?" \
                    "classical:Classical statistics" \
                    "ml:Machine learning" \
                    "llm_app:LLM application" \
                    "optimization:Optimization")
                combined+=("model_${sub}")
                ;;
            service_application)
                forest_subheader "Service Type"
                local sub
                sub=$(forest_select_one "What kind of service?" \
                    "api:API / backend" \
                    "web:Web frontend" \
                    "fullstack:Full-stack application" \
                    "cli:CLI tool")
                combined+=("service_${sub}")
                ;;
            library)
                combined+=("library")
                ;;
        esac
    done

    # Join combined array with commas
    local result=""
    for item in "${combined[@]}"; do
        [[ -n "$result" ]] && result+=","
        result+="$item"
    done
    SELECTIONS[project_types]="$result"
}
