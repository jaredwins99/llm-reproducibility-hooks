## DVC (data and pipeline versioning)

`dvc.yaml` mirrors the make pipeline: each stage runs `make step M=...` or
`make pipeline-r PIPELINE_R=...` for one entry of `project.mk`, in the same
order. Change the pipeline in `project.mk` first, then `make dvc-stages` and
`make dvc-check`. Never put a command in `dvc.yaml` that make does not run.

- `make dvc-init` — once per repository; adds `DVC_REMOTE` as the default remote
- `make dvc-repro` / `make dvc-status` / `make dvc-dag`
- `make dvc-push` / `make dvc-pull` — versioned data to and from the remote
