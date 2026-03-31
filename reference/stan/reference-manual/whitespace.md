# Stan Reference Manual: Whitespace

## Overview

This page from the Stan Reference Manual explains how whitespace is handled in the Stan programming language.

## Whitespace Characters

The documentation defines whitespace as consisting of four ASCII characters: the space (0x20), tab (0x09), carriage return (0x0D), and line feed (0x0A).

## Whitespace Neutrality

Stan treats all whitespace characters identically. There is no significance to indentation, to tabs, to carriage returns or line feeds, or to any vertical alignment of text. One or more whitespace characters of any type are treated identically by the parser.

## Whitespace Location

You can insert zero or more whitespace characters between symbols in Stan code -- around operators like `a * b`, before semicolons, around parentheses, and between function arguments. However, there is a critical restriction: identifiers and literals may not be separated by whitespace. This means you cannot write `10 000` instead of `10000` or `normal _ lpdf` instead of `normal_lpdf`.

This flexibility allows developers to format code readably while maintaining parsing consistency.
