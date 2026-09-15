# === DVC: data and pipeline versioning (tool_dvc) ===
# dvc.yaml stages call make for one entry of PIPELINE_PY / PIPELINE_R each, so
# commands are defined once, in the make pipeline. DVC_REMOTE: see project.mk.
DVC        ?= $$( [ -x "$(ENV_PREFIX)/bin/dvc" ] && echo "$(ENV_PREFIX)/bin/dvc" || echo dvc )
DVC_REMOTE ?=
DVC_PY     ?= $(or $(PY),python3)

dvc-init: ## DVC: initialise once, then add DVC_REMOTE as the default remote
	@if [ ! -d .dvc ]; then $(DVC) init; fi
	@if [ -n "$(DVC_REMOTE)" ]; then $(DVC) remote add -d -f storage "$(DVC_REMOTE)"; \
	else echo "==> DVC_REMOTE unset; set it in project.mk or: make dvc-init DVC_REMOTE=s3://bucket/path"; fi

dvc-repro: ## DVC: run the stages whose inputs changed
	$(DVC) repro

dvc-status: ## DVC: show stages and data that are out of date
	$(DVC) status

dvc-dag: ## DVC: show the stage graph
	$(DVC) dag

dvc-push: ## DVC: upload cached data to the remote
	$(DVC) push

dvc-pull: ## DVC: fetch the versioned data from the remote
	$(DVC) pull

dvc-stages: ## DVC: print dvc.yaml stages generated from the make pipeline
	@$(DVC_PY) tools/dvc_stages.py --py "$(PIPELINE_PY)" --r "$(PIPELINE_R)"

dvc-check: ## DVC: fail when dvc.yaml and the make pipeline disagree
	@$(DVC_PY) tools/dvc_stages.py --check --py "$(PIPELINE_PY)" --r "$(PIPELINE_R)"

# Without repro_stack there is no `make step`; this one runs a script or module.
ifeq ($(wildcard repro.mk),)
step:
	PYTHONPATH=src python $(if $(filter %.py,$(M)),$(M),-m $(M))
endif
