# Sparse and Ragged Data Structures

## Overview

Stan does not directly support either sparse or ragged data structures, though both can be accommodated with some programming effort. The material covers two distinct approaches for handling non-standard data organization patterns.

## Sparse Data Structures

The sparse data approach converts matrix-like representations into database-style formats. Rather than maintaining a full J×K array where many entries are undefined, developers instead create three parallel arrays:
- Index array for first dimension (jj)
- Index array for second dimension (kk)
- Value array (y)

This proves particularly useful for Item Response Theory (IRT) models where not every student answers every question. The documentation provides an example with J=3 students and K=4 questions, showing how to restructure incomplete response data.

The sparse method requires iterating through N defined observations rather than iterating through all possible positions. Both the dense and sparse formulations "produce exactly the same log posterior density" when no values are missing.

## Ragged Data Structures

Ragged arrays have rows of different lengths. The solution combines:
- A single vector holding all values sequentially
- A separate integer array recording the size of each group

For example, three groups with 3, 2, and 4 observations respectively concatenate into one vector, with a sizes array [3, 2, 4] tracking boundaries.

The documentation recommends using the `segment()` function for slicing operations, as this "allows for efficient vectorization" despite modest copy overhead.
