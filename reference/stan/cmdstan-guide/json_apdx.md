# JSON Format for CmdStan

## Overview

CmdStan accepts JSON format for input data used by both model data and parameters. Data is read during model construction, while parameters initialize the sampler and optimizer.

## Creating JSON Files

While you can manually create JSON files following the guidelines below, the CmdStanR interface provides a more convenient method through the `write_stan_json()` function.

## JSON Syntax Summary

JSON is defined by the ECMA-404 standard and must be in Unicode format. JSON consists of:

**Structural tokens:** `{}`, `[]`, `;`, `,`

**Literal tokens (lowercase only):** `true`, `false`, `null`

**Primitive values:** Literals, strings, or numbers

**Strings:** Unicode characters in double quotes with backslash escape support

**Numbers:** Decimal or scientific notation (e.g., `17`, `17.2`, `-17.2e8`)

**Special floating-point values:**
- Positive infinity: `"Inf"`, `"Infinity"`, or `Infinity`
- Negative infinity: `"-Inf"`, `"-Infinity"`, or `-Infinity`
- Not-a-number: `"NaN"` or `NaN`

**Complex scalars:** Two-element array `[real, imaginary]` (e.g., `[2.3, -1.83]` for 2.3 - 1.83i)

**Arrays:** Ordered, comma-separated values in square brackets

**Vectors and row vectors:** Arrays of elements

**Complex vectors:** Arrays of two-element arrays

**Matrices:** Arrays of row vectors

**Complex matrices:** Arrays of complex row vectors

**Tuples:** Nested JSON objects with numbered string keys (e.g., `{"1": 1.5, "2": 3.4}`)

**Name-value pairs:** String, colon, then value

**JSON objects:** Comma-separated name-value pairs in curly brackets

## Stan Data Types in JSON Notation

A Stan JSON input file contains a single JSON object with zero or more name-value pairs, equivalent to a Python dictionary.

**Example Bernoulli data:**
```json
{ "N" : 10, "y" : [0,1,0,0,0,0,0,0,0,1] }
```

Multi-dimensional arrays and matrices use row-major order.

**Example multi-dimensional array:**
```json
{ "d1" : 2,
  "d2" : 3,
  "d3" : 4,
  "ar" : [[[0,1,2,3], [4,5,6,7], [8,9,10,11]],
          [[12,13,14,15], [16,17,18,19], [20,21,22,23]]]
}
```

JSON whitespace is ignored for readability.

## Data Type Encoding Table

| Stan Declaration | JSON Encoding |
|---|---|
| `int i` | `"i": 17` |
| `real a` | `"a" : 17` or `"a" : 17.2` or `"a" : "NaN"` or `"a" : "+inf"` or `"a" : "-inf"` |
| `complex z` | `"z": [1, -2.3]` |
| `array[5] int` | `"a" : [1, 2, 3, 4, 5]` |
| `array[5] real a` | `"a" : [ 1, 2, 3.3, "NaN", 5 ]` |
| `array[2] complex b` | `"b" : [[1, -2.3], [4.9, 0]]` |
| `vector[5] a` | `"a" : [1, 2, 3.3, "NaN", 5]` |
| `row_vector[5] a` | `"a" : [1, 2, 3.3, "NaN", 5]` |
| `matrix[2, 3] a` | `"a" : [[ 1, 2, 3 ], [ 4, 5, 6]]` |
| `complex_vector[2] c` | `"c" : [[-1.2, 3.3], [4.8, 1.9], [2.3, 0]]` |
| `complex_row_vector[2] c` | `"c" : [[-1.2, 3.3], [4.8, 1.9], [2.3, 0]]` |
| `complex_matrix[2, 3] d` | `"d" : [[[1, 1], [2, 2], [3, 3]], [4, 4], [5, 5], [6, 6]]]` |
| `tuple(real, array[2] int) t` | `"t" : { "1": 1.4, "2": [1, 2]}` |

## Empty Arrays in JSON

JSON cannot distinguish between multi-dimensional arrays where any dimension equals zero. All such cases share the representation `[ ]`.

**Example Stan data block:**
```stan
data {
  int d;
  array[d] int ar_1d;
  array[d, d] int ar_2d;
  array[d, d, d] int ar_3d;
}
```

**When d = 1** (single values):
```json
{ "ar_d1" : [7],
  "ar_d2" : [[8]],
  "ar_d3" : [[[9]]]
}
```

**When d = 0** (empty arrays):
```json
{ "d" : 0,
  "ar_d1" : [ ],
  "ar_d2" : [ ],
  "ar_d3" : [ ]
}
```
