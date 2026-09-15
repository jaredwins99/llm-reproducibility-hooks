# Activate the project's renv library once it has been restored (make setup).
# Until then R starts on the user library, so a fresh clone still opens; the
# message says how to get the pinned packages. Rscript --vanilla skips this file.
local({
  library_path <- Sys.getenv("RENV_PATHS_LIBRARY", file.path("renv", "library"))
  installed <- c(Sys.glob(file.path(library_path, "*", "*", "*", "DESCRIPTION")),
                 Sys.glob(file.path(library_path, "*", "*", "*", "*", "DESCRIPTION")))
  restored <- any(basename(dirname(installed)) != "renv")
  if (file.exists(file.path("renv", "activate.R")) && restored) {
    source(file.path("renv", "activate.R"))
  } else if (interactive()) {
    message("renv library not restored; run `make renv` for the pinned R packages")
  }
})
