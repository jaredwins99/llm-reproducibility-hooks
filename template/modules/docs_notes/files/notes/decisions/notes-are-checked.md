---
kind: decision
title: Notes declare what they cover, an index is generated, and findings re-run their evidence
covers: correctness/checks/check_notes.py, correctness/hooks/notes-gate.sh
---
Reasoning that lives only in a head or a chat log is re-derived or
contradicted. Notes hold it, and the check keeps them honest: a note that
covers a file that no longer exists, a source file no note covers, one file
decided by two notes, or a finding whose evidence no longer shows its claim
each fail rather than waiting to mislead.

The scope is declared in notes/coverage.ini, not written into the checker, so
adding a directory or a language cannot leave it unchecked. The index is
generated from what the notes declare.

Rejected: a hand-maintained index, which drifts silently; and a scope
hardcoded in the checker, which is how code slips outside the check.
