# === Pipeline targets ===
# Without repro_stack this is the orchestrator; with it, repro.mk runs the
# same scripts from PIPELINE_PY in project.mk (make all).
pipeline: ## Run full pipeline (sequential)
	PYTHONPATH=src python scripts/01_extract.py
	PYTHONPATH=src python scripts/02_transform.py
	PYTHONPATH=src python scripts/03_load.py

pipeline-step: ## Run single step (usage: make pipeline-step STEP=01_extract)
	PYTHONPATH=src python scripts/$(STEP).py
