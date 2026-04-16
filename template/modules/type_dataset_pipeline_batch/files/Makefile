# === Pipeline targets ===
pipeline: ## Run full pipeline (sequential)
	python scripts/01_extract.py
	python scripts/02_transform.py
	python scripts/03_load.py

pipeline-step: ## Run single step (usage: make pipeline-step STEP=01_extract)
	python scripts/$(STEP).py

pipeline-dvc: ## Run pipeline via DVC (skips unchanged steps)
	dvc repro
