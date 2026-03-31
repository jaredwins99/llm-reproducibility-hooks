# Void Functions - Stan Functions Reference

## Overview

Stan supports special statements for printing and signaling program issues. These constructs—`print`, `reject`, and `fatal_error`—accept variable numbers of arguments and can handle string literals, distinguishing them from regular functions. They operate through side effects and don't affect the log density function.

## Print Statement

**Signature:** `void print(T1 x1,..., TN xN)`

The print function outputs values to the standard output stream without affecting model probability calculations. Arguments are printed consecutively without spaces, with a newline character appended at the end. It accepts any built-in numerical types or double-quoted character strings.

**Available since:** 2.1

## Reject Statement

**Signature:** `void reject(T1 x1,..., TN xN)`

The reject statement terminates the current iteration by throwing an internal exception, with behavior dependent on the algorithmic context. It accepts the same argument types as print and outputs values identically (no spaces between items, newline at end). The iteration is rejected and error messages are displayed.

**Available since:** 2.18

## Fatal Error Statement

**Signature:** `void fatal_error(T1 x1,..., TN xN)`

This statement prints specified values and immediately terminates the entire algorithm by throwing an internal exception. Unlike reject, it represents an unrecoverable error condition. Arguments display without spacing between items, with a newline appended. Use only when algorithm termination is necessary.

**Available since:** 2.35
