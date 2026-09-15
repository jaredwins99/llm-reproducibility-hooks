#!/usr/bin/env bash
# tool_dvc — optional data and pipeline versioning with DVC, for any project
# type. dvc.yaml mirrors the make pipeline (each stage calls make), so the
# Makefile stays the single orchestrator and DVC adds caching and data versions.
#
# New project:      init.sh (answer yes to "DVC")
# Existing project: template/apply.sh --module tool_dvc --output-dir <dir>

MODULE_NAME="tool_dvc"
MODULE_DESCRIPTION="DVC: dvc.yaml mirroring the make pipeline, remote placeholder, make dvc-* targets"
ACTIVATE_WHEN=("dvc=yes")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")

post_install() {
    env_add_conda_package dvc
    if [[ -f project.mk ]] && ! grep -q '^DVC_REMOTE' project.mk; then
        project_mk_add_line ""
        project_mk_add_line "# DVC (tool_dvc). make pin-conda keeps dvc, which no code imports; make dvc-init"
        project_mk_add_line "# adds DVC_REMOTE (s3://bucket/path, gs://..., /mnt/share/...) as the default remote."
        project_mk_add_line "PIN_ARGS        += --extra dvc"
        project_mk_add_line "DVC_REMOTE      ="
    fi
    _dvc_precommit
    if [[ -d .git && ! -d .dvc ]] && command -v dvc >/dev/null; then
        dvc init -q && echo "  tool_dvc: dvc init done"
    else
        echo "  tool_dvc: run 'make dvc-init' once the repository is under git"
    fi
}

_dvc_precommit() {
    local config=.pre-commit-config.yaml
    grep -q 'id: dvc-check' "$config" 2>/dev/null && return
    [[ -f "$config" ]] || echo "repos:" > "$config"
    { echo ""; cat "$(dirname "${BASH_SOURCE[0]}")/stack/pre-commit-hooks.yaml"; } >> "$config"
}
