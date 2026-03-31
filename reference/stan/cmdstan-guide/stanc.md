# `stanc`: Translating Stan to C++

## Overview

The Stan compiler program translates Stan code to C++ implementation. CmdStan includes the `stanc` binary in its `bin` directory. As of version 2.22, the compiler is written in OCaml and called "stanc3," with source code available at https://github.com/stan-dev/stanc3.

## Creating the `stanc` Binary

Before use, build the binary via makefile:

**Mac/Linux:**
```
make bin/stanc
```

**Windows:**
```
make bin/stanc.exe
```

This is also completed as part of `make build`.

## Using the Stan Compiler

The compiler converts Stan programs to C++ and reports syntax errors with location details.

### Direct Compilation Example

**Mac/Linux:**
```
cd <cmdstan-home>
bin/stanc --o=bernoulli.hpp examples/bernoulli/bernoulli.stan
```

**Windows:**
```
cd <cmdstan-home>
bin/stanc.exe --o=bernoulli.hpp examples/bernoulli/bernoulli.stan
```

### Naming Requirements

"The base name of the Stan program file determines the name of the C++ model class. Because this name is the name of a C++ class, it must start with an alphabetic character (`a--z` or `A--Z`) and contain only alphanumeric characters (`a--z`, `A--Z`, and `0--9`) and underscores (`_`)" and should avoid C++ reserved keywords.

Output goes to the specified file (`bernoulli.hpp`).

## Building via GNU Make

**Mac/Linux:**
```
make examples/bernoulli/bernoulli
```

**Windows:**
```
make examples/bernoulli/bernoulli.exe
```

The makefile translates Stan to C++, then compiles and links the resulting code.

### Custom Compiler Flags

Override default stanc arguments using the `STANCFLAGS` variable:

```
make STANCFLAGS="--include-paths=~/foo" examples/bernoulli/bernoulli
```

See [stanc arguments documentation](https://mc-stan.org/docs/stan-users-guide/using-stanc.html#stanc-args) for available options.
