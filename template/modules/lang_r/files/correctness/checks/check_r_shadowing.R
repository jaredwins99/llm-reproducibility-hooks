# Same-call shadowing in R: a data-masking call that creates a column and then reads the name again.
#
#   Rscript check_r_shadowing.R [FILE or DIR ...]
#
# (tools/ in a repro_stack project, correctness/checks/ in a lang_r one; the file is the same in both.)
#
# Inside tibble(), mutate(), summarise() and the other data-masking calls, each argument sees the columns the
# arguments before it created. When a column takes the name of a variable or argument of the code around the
# call, a later argument that reads the name gets the column, not the variable:
#
#   draws <- fit$draws("mu_gamma", format = "matrix")
#   tibble(draws = nrow(draws), finite = all(is.finite(draws)))   # finite tests the row count
#
# This reports each such read, at the line of the read. Two forms are not reported, because the column and
# the variable are then the same value or the reader has said which is meant:
#
#   x = x              a column that copies the variable of its own name
#   .data$x, .env$x    a read that names the column or the variable
#
# A column meant to replace the variable for the rest of the call is allowed by a comment containing
# "shadow-ok" on the line that creates it or on the line that reads it. Exits 1 when anything is reported.

VERBS <- c("tibble", "tribble", "data.frame", "mutate", "transmute", "summarise", "summarize", "reframe")
PACKAGES <- c("", "tibble", "dplyr", "base")
ALLOW <- "shadow-ok"

children_of <- function(pd, id) pd[pd$parent == id, , drop = FALSE]

descendants <- function(pd, id) {
  found <- integer()
  frontier <- id
  while (length(frontier)) {
    frontier <- pd$id[pd$parent %in% frontier]
    found <- c(found, frontier)
  }
  pd[pd$id %in% found, , drop = FALSE]
}

ancestors <- function(pd, id) {
  parents <- pd$parent
  names(parents) <- pd$id
  chain <- integer()
  at <- parents[[as.character(id)]]
  while (!is.na(at) && at > 0) {
    chain <- c(chain, at)
    at <- parents[[as.character(at)]]
  }
  chain
}

# every function definition's formals, by the id of the expression that defines it
functions_in <- function(pd) {
  ids <- pd$parent[pd$token == "FUNCTION"]
  stats::setNames(lapply(ids, function(id) {
    kids <- children_of(pd, id)
    kids$text[kids$token == "SYMBOL_FORMALS"]
  }), ids)
}

# each assignment of a plain name: the name, the function it happens in (0 outside any), and whether a
# function is what it assigns
assignments_in <- function(pd, scopes) {
  arrows <- pd[pd$token %in% c("LEFT_ASSIGN", "EQ_ASSIGN", "RIGHT_ASSIGN"), , drop = FALSE]
  rows <- lapply(seq_len(nrow(arrows)), function(k) {
    kids <- children_of(pd, arrows$parent[[k]])
    kids <- kids[order(kids$line1, kids$col1), , drop = FALSE]
    exprs <- kids[kids$token == "expr", , drop = FALSE]
    if (nrow(exprs) != 2) return(NULL)
    target <- if (arrows$token[[k]] == "RIGHT_ASSIGN") exprs[2, ] else exprs[1, ]
    value <- if (arrows$token[[k]] == "RIGHT_ASSIGN") exprs[1, ] else exprs[2, ]
    inner <- children_of(pd, target$id)
    if (nrow(inner) != 1 || inner$token != "SYMBOL") return(NULL)
    around <- intersect(ancestors(pd, arrows$parent[[k]]), as.integer(names(scopes)))
    data.frame(name = inner$text, scope = if (length(around)) around[[1]] else 0L,
               is_function = any(children_of(pd, value$id)$token == "FUNCTION"))
  })
  do.call(rbind, c(list(data.frame(name = character(), scope = integer(), is_function = logical())), rows))
}

# the names a call's code can see as variables: every enclosing function's formals and locals, and the
# file's own variables (not its functions)
outer_names <- function(pd, call_id, scopes, assigned) {
  around <- intersect(ancestors(pd, call_id), as.integer(names(scopes)))
  unique(c(unlist(scopes[as.character(around)], use.names = FALSE),
           assigned$name[assigned$scope %in% around],
           assigned$name[assigned$scope == 0 & !assigned$is_function]))
}

# a data-masking call's arguments in order: each one's name ("" when unnamed), its value's expression id,
# and the line its name is on
arguments_of <- function(pd, call_id) {
  kids <- children_of(pd, call_id)
  kids <- kids[order(kids$line1, kids$col1), , drop = FALSE]
  out <- list()
  pending <- NULL
  for (k in seq_len(nrow(kids))[-1]) {
    token <- kids$token[[k]]
    if (token == "SYMBOL_SUB") pending <- kids[k, ]
    if (token == "expr") {
      out[[length(out) + 1]] <- data.frame(name = if (is.null(pending)) "" else pending$text,
                                           value = kids$id[[k]],
                                           line = if (is.null(pending)) kids$line1[[k]] else pending$line1)
      pending <- NULL
    }
  }
  do.call(rbind, c(list(data.frame(name = character(), value = integer(), line = integer())), out))
}

# the verb a call expression names, or NA
verb_of <- function(pd, call_id) {
  kids <- children_of(pd, call_id)
  kids <- kids[order(kids$line1, kids$col1), , drop = FALSE]
  if (!nrow(kids) || kids$token[[1]] != "expr") return(NA_character_)
  head <- children_of(pd, kids$id[[1]])
  fun <- head$text[head$token == "SYMBOL_FUNCTION_CALL"]
  package <- head$text[head$token == "SYMBOL_PACKAGE"]
  if (length(fun) != 1 || !fun %in% VERBS) return(NA_character_)
  if (!(if (length(package)) package else "") %in% PACKAGES) return(NA_character_)
  paste0(if (length(package)) paste0(package, "::") else "", fun)
}

# the places inside an argument's value that read `name` as a variable: a symbol standing alone, so not a
# call, not the right of $ or @, and not inside a function of the value that takes `name` as an argument
reads_of <- function(pd, value_id, name, scopes) {
  inside <- descendants(pd, value_id)
  symbols <- inside[inside$token == "SYMBOL" & inside$text == name, , drop = FALSE]
  alone <- vapply(symbols$parent, function(parent) nrow(children_of(pd, parent)) == 1, logical(1))
  bound <- vapply(symbols$id, function(id) {
    around <- intersect(ancestors(pd, id), intersect(inside$id, as.integer(names(scopes))))
    any(vapply(as.character(around), function(f) name %in% scopes[[f]], logical(1)))
  }, logical(1))
  symbols[alone & !bound, , drop = FALSE]
}

value_is_name <- function(pd, value_id, name) {
  inner <- children_of(pd, value_id)
  nrow(inner) == 1 && inner$token == "SYMBOL" && inner$text == name
}

allowed_lines <- function(pd) pd$line1[pd$token == "COMMENT" & grepl(ALLOW, pd$text, fixed = TRUE)]

check_file <- function(file) {
  exprs <- tryCatch(parse(file, keep.source = TRUE), error = function(e) e)
  if (inherits(exprs, "error")) return(sprintf("%s:0: does not parse: %s", file, conditionMessage(exprs)))
  pd <- utils::getParseData(exprs, includeText = TRUE)
  if (is.null(pd) || !nrow(pd)) return(character())
  scopes <- functions_in(pd)
  assigned <- assignments_in(pd, scopes)
  allowed <- allowed_lines(pd)
  calls <- unique(pd$parent[pd$token == "SYMBOL_FUNCTION_CALL"])
  calls <- unique(pd$parent[pd$id %in% calls])
  found <- character()
  for (call_id in calls) {
    verb <- verb_of(pd, call_id)
    if (is.na(verb)) next
    args <- arguments_of(pd, call_id)
    if (nrow(args) < 2) next
    outer <- outer_names(pd, call_id, scopes, assigned)
    for (k in seq_len(nrow(args) - 1)) {
      name <- args$name[[k]]
      if (!nzchar(name) || !name %in% outer || value_is_name(pd, args$value[[k]], name)) next
      for (j in (k + 1):nrow(args)) {
        if (identical(args$name[[j]], name)) break
        reads <- reads_of(pd, args$value[[j]], name, scopes)
        for (r in seq_len(nrow(reads))) {
          if (any(c(args$line[[k]], reads$line1[[r]]) %in% allowed)) next
          found <- c(found, sprintf(
            "%s:%d: %s() creates the column '%s' on line %d, and '%s' reads it where the variable '%s' may be meant",
            file, reads$line1[[r]], verb, name, args$line[[k]], if (nzchar(args$name[[j]])) args$name[[j]] else "an argument",
            name))
        }
      }
    }
  }
  unique(found)
}

main <- function(paths) {
  if (!length(paths)) paths <- "."
  files <- character()
  for (path in paths) {
    if (!file.exists(path)) {
      message("ERROR: ", path, " does not exist, so nothing in it was checked")
      quit(status = 2)
    }
    if (dir.exists(path)) {
      found <- list.files(path, pattern = "\\.[Rr]$", recursive = TRUE, full.names = TRUE)
      if (!length(found)) message("WARNING: ", path, " holds no R files; nothing in it was checked")
      files <- c(files, found)
    } else if (!grepl("\\.[Rr]$", path)) {
      message("WARNING: ", path, " is not an R file; the shadowing check does not read it")
    } else {
      files <- c(files, path)
    }
  }
  found <- unlist(lapply(files, check_file))
  if (length(found)) {
    writeLines(found, stderr())
    message(sprintf("\n%d same-call shadowing read(s); read the variable before the call, rename the column, ",
                    length(found)), "or mark a deliberate one with a shadow-ok comment")
    quit(status = 1)
  }
  invisible(0)
}

main(commandArgs(trailingOnly = TRUE))
