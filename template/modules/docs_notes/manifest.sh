#!/usr/bin/env bash
MODULE_NAME="docs_notes"
MODULE_DESCRIPTION="Decision notes that declare what they cover, an index generated from them, and findings whose evidence is re-run"
ACTIVATE_WHEN=("decision_notes=yes")
DEPENDS_ON=("lang_python")
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
