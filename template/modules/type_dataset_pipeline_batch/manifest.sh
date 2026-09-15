#!/usr/bin/env bash
MODULE_NAME="type_dataset_pipeline_batch"
MODULE_DESCRIPTION="Batch data pipeline project type"
ACTIVATE_WHEN=("project_types~=dataset_pipeline_batch")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")

# With repro_stack, the pipeline order lives in project.mk.
post_install() {
    [[ -f project.mk ]] || return 0
    sed -i 's|^PIPELINE_PY[[:space:]]*=[[:space:]]*$|PIPELINE_PY     = scripts/01_extract.py scripts/02_transform.py scripts/03_load.py|' project.mk
}
