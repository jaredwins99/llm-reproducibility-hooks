# === R targets ===
lint: ## Run lintr
	Rscript -e 'lintr::lint_dir("src/R/")'

format: ## Run styler
	Rscript -e 'styler::style_dir("src/R/")'

test: ## Run testthat
	Rscript -e 'devtools::test()'

test-coverage: ## Run tests with coverage
	Rscript -e 'covr::package_coverage()'

pipeline-targets: ## Run pipeline via targets (skips unchanged steps)
	Rscript -e 'targets::tar_make()'

pipeline-viz: ## Visualize targets dependency graph
	Rscript -e 'targets::tar_visnetwork()'
