#!/usr/bin/env bash
# tool_mlflow — optional experiment tracking with MLflow, for any project type.
# A local SQLite tracking store in mlruns/ (or a server via
# MLFLOW_TRACKING_URI), a tracked_run helper that tags each run with the git
# commit and hashes of the pinned environment files, and make mlflow-* targets.
#
# New project:      init.sh (answer yes to "MLflow")
# Existing project: template/apply.sh --module tool_mlflow --output-dir <dir>

MODULE_NAME="tool_mlflow"
MODULE_DESCRIPTION="MLflow: tracking store in mlruns/, tracked_run helper, make mlflow-ui / mlflow-server"
ACTIVATE_WHEN=("mlflow=yes")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")

post_install() {
    env_add_conda_package mlflow
    echo "  tool_mlflow: runs are stored in mlruns/; browse them with 'make mlflow-ui'"
}
