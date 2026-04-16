#!/usr/bin/env bash
MODULE_NAME="lang_r"
MODULE_DESCRIPTION="R language support"
ACTIVATE_WHEN=("languages~=r")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name" "project_description" "author_name")
