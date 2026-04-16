#!/usr/bin/env bash
# _always module — files included in every project

MODULE_NAME="_always"
MODULE_DESCRIPTION="Base project scaffolding included in every project"

# Always activated (handled specially by resolver)
ACTIVATE_WHEN=()
DEPENDS_ON=()
CONFLICTS_WITH=()

REQUIRED_VARS=(
    "project_name"
    "project_description"
    "author_name"
)
