# Write renv.lock for exactly the packages the R code uses.
#
#   Rscript tools/snapshot_renv.R R
#
# Packages are the union of what renv finds referenced in the given
# directories and the Depends, Imports and Suggests fields of every
# DESCRIPTION file under them (packages attached from a character vector,
# such as library(pkg, character.only = TRUE), are only visible there).
# The lockfile pins those packages and their recursive dependencies at the
# versions installed in the active library. Base and recommended packages
# are not recorded.

args <- commandArgs(trailingOnly = TRUE)
dirs <- if (length(args)) args else "R"

if (!requireNamespace("renv", quietly = TRUE)) {
  stop("renv is not installed; run: Rscript -e 'install.packages(\"renv\")'")
}

description_packages <- function(path) {
  fields <- read.dcf(path, fields = c("Depends", "Imports", "Suggests"))
  entries <- unlist(strsplit(paste(stats::na.omit(as.vector(fields)), collapse = ","), ","))
  names <- trimws(sub("\\(.*$", "", entries))
  names[nzchar(names) & names != "R"]
}

descriptions <- unlist(lapply(dirs, list.files, pattern = "^DESCRIPTION$",
                              recursive = TRUE, full.names = TRUE))
referenced <- unique(renv::dependencies(dirs, quiet = TRUE)$Package)
declared <- unique(unlist(lapply(descriptions, description_packages)))

base <- rownames(installed.packages(priority = "base"))
# RENV_SNAPSHOT_EXCLUDE: comma-separated packages to leave out even though the
# code mentions them (for example a Suggests entry whose presence changes how
# the tests run).
excluded <- trimws(strsplit(Sys.getenv("RENV_SNAPSHOT_EXCLUDE"), ",")[[1]])
packages <- sort(setdiff(union(referenced, declared), c(base, "renv", excluded)))
if (length(excluded)) cat("excluded on request:", paste(excluded, collapse = " "), "\n")
missing <- packages[!vapply(packages, function(p) nzchar(system.file(package = p)), logical(1))]
if (length(missing)) {
  stop("not installed, so they cannot be pinned: ", paste(missing, collapse = ", "))
}

# Repositories recorded in the lockfile: Posit Package Manager for CRAN, so
# restore gets prebuilt Linux binaries, plus any other repository a pinned
# package was installed from (for example stan-dev's r-universe for cmdstanr).
db <- installed.packages(fields = "Repository")
closure <- unique(c(packages, unlist(tools::package_dependencies(
  packages, db = db, which = c("Depends", "Imports", "LinkingTo"), recursive = TRUE))))
extra <- unique(stats::na.omit(db[rownames(db) %in% closure, "Repository"]))
extra <- extra[grepl("^https?://", extra)]
cran <- Sys.getenv("RENV_SNAPSHOT_CRAN", "https://packagemanager.posit.co/cran/latest")
options(repos = c(CRAN = cran, stats::setNames(extra, sub("^https?://([^.]+).*$", "\\1", extra))))
cat("repositories:", paste(getOption("repos"), collapse = " "), "\n")

cat("pinning", length(packages), "packages and their dependencies:\n ",
    paste(packages, collapse = " "), "\n")
renv::snapshot(packages = c("renv", packages), prompt = FALSE, force = TRUE)
