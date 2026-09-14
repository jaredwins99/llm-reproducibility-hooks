#!/usr/bin/env bash
MODULE_NAME="style_pipelines"
MODULE_DESCRIPTION="Pandas pipeline style: chained transforms, no inline comments, reported shapes"
ACTIVATE_WHEN=("project_types~=dataset_pipeline_batch" "project_types~=dataset_pipeline_streaming" "project_types~=dataset_oneoff")
DEPENDS_ON=("lang_python")
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
