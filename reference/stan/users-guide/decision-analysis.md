# Decision Analysis

## Overview

Decision analysis addresses making choices under uncertainty. The foundational concept involves selecting actions that maximize expected utility. As the Stan documentation explains, "the so-called 'Bayes optimal' decision is the one that maximizes expected utility (or equivalently, minimizes expected loss)."

## Four-Step Framework

The methodology follows these steps:

1. **Define outcomes and decisions**: Establish sets X (possible outcomes) and D (possible decisions)

2. **Specify conditional probability**: Create a probability distribution p(x|d) representing outcomes given decisions

3. **Create utility function**: Map outcomes to real-valued utilities U: X → ℝ

4. **Optimize**: Select decision d* that achieves "arg max_d E[U(x)|d]"

## Practical Example: Commute Mode Selection

The documentation illustrates these principles using a transportation choice scenario where a commuter evaluates four modes: walking, biking, public transit, and taxi.

**Outcomes** consist of paired cost and time measurements. **Models** employ lognormal distributions for both commute duration and expense across each mode, with parameters estimated from 200 prior observations.

**Utility function** assumes linear preferences: U(c,t) = -(c + 25·t), where time carries $25/hour valuation.

## Implementation in Stan

The Stan program includes:
- Utility function definition
- Parameter declarations for distribution means and scales
- Sampling statements following the lognormal model
- Generated quantities block computing utilities for each decision option

Expected utility calculations emerge from posterior means across multiple MCMC samples, properly integrating over parameter uncertainty.

## Continuous Decisions

For non-discrete choices (investment amounts, exercise duration), Stan functions as an optimizer interface, computing expected utility given specified continuous parameters while external optimization tools identify optima.
