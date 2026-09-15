# === MLflow: experiment tracking (tool_mlflow) ===
# src/<package>/tracking.py records runs in MLFLOW_DIR (SQLite store plus
# artifacts) unless MLFLOW_TRACKING_URI points at a server.
MLFLOW         ?= $$( [ -x "$(ENV_PREFIX)/bin/mlflow" ] && echo "$(ENV_PREFIX)/bin/mlflow" || echo mlflow )
MLFLOW_DIR     ?= mlruns
MLFLOW_BACKEND ?= sqlite:///$(MLFLOW_DIR)/mlflow.db
MLFLOW_HOST    ?= 127.0.0.1
MLFLOW_PORT    ?= 5000

mlflow-ui: ## MLflow: browse the local runs (MLFLOW_HOST, MLFLOW_PORT)
	@mkdir -p $(MLFLOW_DIR)
	$(MLFLOW) ui --backend-store-uri $(MLFLOW_BACKEND) --host $(MLFLOW_HOST) --port $(MLFLOW_PORT)

mlflow-server: ## MLflow: tracking server; point runs at it with MLFLOW_TRACKING_URI=http://host:port
	@mkdir -p $(MLFLOW_DIR)/artifacts
	$(MLFLOW) server --backend-store-uri $(MLFLOW_BACKEND) --artifacts-destination $(MLFLOW_DIR)/artifacts \
		--host $(MLFLOW_HOST) --port $(MLFLOW_PORT)
