# === R targets ===
# Language-suffixed recipes; lint, format, test and test-coverage (declared in
# the base Makefile) collect every language's target as a prerequisite.
lint: lint-r
format: format-r
test: test-r
test-coverage: test-coverage-r

lint-r: ## Run lintr
	Rscript -e 'lintr::lint_dir("src/R/")'

format-r: ## Run styler
	Rscript -e 'styler::style_dir("src/R/")'

test-r: ## Run testthat
	Rscript -e 'devtools::test()'

test-coverage-r: ## Run tests with coverage
	Rscript -e 'covr::package_coverage()'

pipeline-targets: ## Run pipeline via targets (skips unchanged steps)
	Rscript -e 'targets::tar_make()'

pipeline-viz: ## Visualize targets dependency graph
	Rscript -e 'targets::tar_visnetwork()'
