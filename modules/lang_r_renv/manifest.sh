#!/usr/bin/env bash
MODULE_NAME="lang_r_renv"
MODULE_DESCRIPTION="R renv environment manager"
ACTIVATE_WHEN=("r_env_manager=renv")
DEPENDS_ON=("lang_r")
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
