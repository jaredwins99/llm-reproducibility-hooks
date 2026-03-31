# Mathematical Functions - Stan Functions Reference

## Overview

This appendix defines several mathematical functions used throughout the Stan manual.

## Beta Function

The beta function, B(a, b), computes the normalizing constant for the beta distribution, defined for a > 0 and b > 0:

**Definition:**
B(a,b) = integral_0^1 u^(a-1) (1-u)^(b-1) du = Gamma(a)*Gamma(b)/Gamma(a+b)

where Gamma(x) is the Gamma function.

## Incomplete Beta Function

The incomplete beta function, B(x; a, b), is defined for x in [0, 1] and a, b >= 0 where a + b != 0:

**Definition:**
B(x; a, b) = integral_0^x u^(a-1) (1-u)^(b-1) du

When x = 1, the incomplete beta function equals the beta function: B(1; a, b) = B(a, b).

**Regularized Form:**
The regularized incomplete beta function divides by the beta function:

I_x(a, b) = B(x; a, b)/B(a, b)

## Gamma Function

The gamma function, Gamma(x), generalizes the factorial to continuous variables:

**For positive integers n:**
Gamma(n+1) = n!

**General definition for positive numbers and non-integer negative numbers:**
Gamma(x) = integral_0^inf u^(x-1) exp(-u) du

## Digamma Function

The digamma function Psi is the derivative of the log Gamma function:

**Definition:**
Psi(u) = d/du log Gamma(u) = (1/Gamma(u)) * d/du Gamma(u)
