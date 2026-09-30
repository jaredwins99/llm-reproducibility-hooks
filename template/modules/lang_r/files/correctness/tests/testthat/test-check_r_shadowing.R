# Tests for correctness/checks/check_r_shadowing.R: a column a data-masking call creates, read again by a later
# argument where a variable of the same name was meant. From the project root:
#   Rscript -e 'testthat::test_file("correctness/tests/testthat/test-check_r_shadowing.R")'

checker <- Filter(file.exists, c(file.path("correctness", "checks", "check_r_shadowing.R"),
                                 file.path("tools", "check_r_shadowing.R"),
                                 file.path("..", "..", "checks", "check_r_shadowing.R")))[[1]]

run_check <- function(body) {
  file <- tempfile(fileext = ".R")
  writeLines(body, file)
  out <- suppressWarnings(system2(file.path(R.home("bin"), "Rscript"), c("--no-save", "--no-restore", checker, file),
                                  stdout = TRUE, stderr = TRUE))
  status <- attr(out, "status")
  list(status = if (is.null(status)) 0L else status, report = paste(out, collapse = "\n"), file = file)
}

test_that("a column read where the variable of its name was meant is reported at the read", {
  found <- run_check(c(
    "check <- function(fit) {",
    "  draws <- fit$draws()",
    "  tibble(draws = nrow(draws),",
    "         finite = all(is.finite(draws)))",
    "}"))
  expect_equal(found$status, 1L)
  expect_match(found$report, paste0(basename(found$file), ":4:"), fixed = TRUE)
  expect_match(found$report, "column 'draws' on line 3", fixed = TRUE)
})

test_that("code outside any function is checked against the script's variables", {
  found <- run_check(c("draws <- read(file)", "summary <- tibble(draws = nrow(draws), finite = all(is.finite(draws)))"))
  expect_equal(found$status, 1L)
})

test_that("a copy, an explicit .data$ or .env$, a local function's call and a marked line are not reported", {
  found <- run_check(c(
    "metrics <- function(x, share) {",
    "  mae <- mean(abs(x))",
    "  correlation <- function(a, b) stats::cor(a, b)",
    "  tibble(x = x, x2 = 2 * x, mae = mae, rel = mae / 2,",
    "         correlation = correlation(x, x), again = correlation(x, x))",
    "  mutate(frame, share = share * 2, doubled = .data$share, given = .env$share)",
    "  mutate(frame, eligible = share > 0, # shadow-ok: runnable reads the row's column",
    "         runnable = eligible)",
    "}"))
  expect_equal(found$status, 0L)
})

test_that("a column that names no variable of the code around it is the ordinary idiom", {
  found <- run_check("f <- function(frame) summarise(frame, mean = mean(value), mean_exp = exp(mean))")
  expect_equal(found$status, 0L)
})
