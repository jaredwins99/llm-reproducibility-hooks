# Bounded Discrete Distributions - Stan Functions Reference

## Overview

"Bounded discrete probability functions have support on {0, ..., N} for some upper bound N."

## Binomial Distribution

### Probability Mass Function
The binomial distribution with N trials and success probability theta is:
Binomial(n|N,theta) = C(N,n) theta^n (1-theta)^{N-n}

### Log Probability Mass Function
log Binomial(n|N,theta) = log Gamma(N+1) - log Gamma(n+1) - log Gamma(N-n+1) + n*log(theta) + (N-n)*log(1-theta)

### Gradient
d/d(theta) log Binomial(n|N,theta) = n/theta - (N-n)/(1-theta)

### Distribution Statement
`n ~ binomial(N, theta)`

### Stan Functions
- `real binomial_lpmf(ints n | ints N, reals theta)` - Log PMF (available since 2.12)
- `real binomial_lupmf(ints n | ints N, reals theta)` - Log PMF dropping constants (available since 2.25)
- `real binomial_cdf(ints n | ints N, reals theta)` - CDF (available since 2.0)
- `real binomial_lcdf(ints n | ints N, reals theta)` - Log CDF (available since 2.12)
- `real binomial_lccdf(ints n | ints N, reals theta)` - Log complementary CDF (available since 2.12)
- `R binomial_rng(ints N, reals theta)` - Random variate generation (available since 2.18)

---

## Binomial Distribution, Logit Parameterization

### Probability Mass Function
BinomialLogit(n|N,alpha) = C(N,n) (logit^{-1}(alpha))^n (1-logit^{-1}(alpha))^{N-n}

### Distribution Statement
`n ~ binomial_logit(N, alpha)`

### Stan Functions
- `real binomial_logit_lpmf(ints n | ints N, reals alpha)` - Log PMF (available since 2.12)
- `real binomial_logit_lupmf(ints n | ints N, reals alpha)` - Log PMF dropping constants (available since 2.25)

---

## Binomial-Logit Generalized Linear Model (Logistic Regression)

### Probability Mass Function
For N trials with linear predictor, the probability of success is inv_logit(alpha + x*beta).

### Distribution Statement
`n ~ binomial_logit_glm(N, x, alpha, beta)`

### Stan Functions
Multiple overloads available:
- `real binomial_logit_glm_lpmf(int n | int N, matrix x, real alpha, vector beta)`
- `real binomial_logit_glm_lupmf(int n | int N, matrix x, real alpha, vector beta)`
- `real binomial_logit_glm_lpmf(int n | int N, matrix x, vector alpha, vector beta)`
- `real binomial_logit_glm_lupmf(int n | int N, matrix x, vector alpha, vector beta)`
- `real binomial_logit_glm_lpmf(array[] int n | array[] int N, row_vector x, real alpha, vector beta)`
- `real binomial_logit_glm_lupmf(array[] int n | array[] int N, row_vector x, real alpha, vector beta)`
- `real binomial_logit_glm_lpmf(array[] int n | array[] int N, row_vector x, vector alpha, vector beta)`
- `real binomial_logit_glm_lupmf(array[] int n | array[] int N, row_vector x, vector alpha, vector beta)`
- `real binomial_logit_glm_lpmf(array[] int n | array[] int N, matrix x, real alpha, vector beta)`
- `real binomial_logit_glm_lupmf(array[] int n | array[] int N, matrix x, real alpha, vector beta)`
- `real binomial_logit_glm_lpmf(array[] int n | array[] int N, matrix x, vector alpha, vector beta)`
- `real binomial_logit_glm_lupmf(array[] int n | array[] int N, matrix x, vector alpha, vector beta)`

All available since version 2.34.

---

## Beta-Binomial Distribution

### Probability Mass Function
BetaBinomial(n|N,alpha,beta) = C(N,n) B(n+alpha, N-n+beta) / B(alpha,beta)

where the beta function is: B(u,v) = Gamma(u)*Gamma(v) / Gamma(u+v)

### Distribution Statement
`n ~ beta_binomial(N, alpha, beta)`

### Stan Functions
- `real beta_binomial_lpmf(ints n | ints N, reals alpha, reals beta)` - Log PMF (available since 2.12)
- `real beta_binomial_lupmf(ints n | ints N, reals alpha, reals beta)` - Log PMF dropping constants (available since 2.25)
- `real beta_binomial_cdf(ints n | ints N, reals alpha, reals beta)` - CDF (available since 2.0)
- `real beta_binomial_lcdf(ints n | ints N, reals alpha, reals beta)` - Log CDF (available since 2.12)
- `real beta_binomial_lccdf(ints n | ints N, reals alpha, reals beta)` - Log complementary CDF (available since 2.12)
- `R beta_binomial_rng(ints N, reals alpha, reals beta)` - Random variate generation (available since 2.18)

---

## Hypergeometric Distribution

### Probability Mass Function
For a in N, b in N, and N in {0,...,a+b}:
Hypergeometric(n|N,a,b) = C(a,n)*C(b,N-n) / C(a+b,N)

### Distribution Statement
`n ~ hypergeometric(N, a, b)`

### Stan Functions
- `real hypergeometric_lpmf(int n | int N, int a, int b)` - Log PMF (available since 2.12)
- `real hypergeometric_lupmf(int n | int N, int a, int b)` - Log PMF dropping constants (available since 2.25)
- `int hypergeometric_rng(int N, int a, int b)` - Random variate generation (available since 2.18)

---

## Categorical Distribution

### Probability Mass Functions
For N-simplex theta and y in {1,...,N}:
Categorical(y|theta) = theta_y

For log-odds parameterization:
CategoricalLogit(y|beta) = Categorical(y|softmax(beta))

### Distribution Statements
- `y ~ categorical(theta)`
- `y ~ categorical_logit(beta)`

### Stan Functions
- `real categorical_lpmf(ints y | vector theta)` - Log PMF (available since 2.12)
- `real categorical_lupmf(ints y | vector theta)` - Log PMF dropping constants (available since 2.25)
- `real categorical_logit_lpmf(ints y | vector beta)` - Log PMF with logit parameterization (available since 2.12)
- `real categorical_logit_lupmf(ints y | vector beta)` - Log PMF with logit dropping constants (available since 2.25)
- `int categorical_rng(vector theta)` - Random variate generation (available since 2.0)
- `int categorical_logit_rng(vector beta)` - Random variate generation with logit (available since 2.16)

---

## Categorical Logit Generalized Linear Model (Softmax Regression)

### Distribution Statement
`y ~ categorical_logit_glm(x, alpha, beta)`

### Stan Functions
Multiple overloads available:
- `real categorical_logit_glm_lpmf(int y | row_vector x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lupmf(int y | row_vector x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lpmf(int y | matrix x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lupmf(int y | matrix x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lpmf(array[] int y | row_vector x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lupmf(array[] int y | row_vector x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lpmf(array[] int y | matrix x, vector alpha, matrix beta)`
- `real categorical_logit_glm_lupmf(array[] int y | matrix x, vector alpha, matrix beta)`

Available since version 2.23 (lupmf since 2.25).

---

## Discrete Range Distribution

### Probability Mass Function
For bounds l <= u and y in {l,...,u}:
DiscreteRange(y|l,u) = 1/(u-l+1)

### Distribution Statement
`y ~ discrete_range(l, u)`

### Stan Functions
- `real discrete_range_lpmf(ints y | ints l, ints u)` - Log PMF (available since 2.26)
- `real discrete_range_lupmf(ints y | ints l, ints u)` - Log PMF dropping constants (available since 2.26)
- `real discrete_range_cdf(ints y | ints l, ints u)` - CDF (available since 2.26)
- `real discrete_range_lcdf(ints y | ints l, ints u)` - Log CDF (available since 2.26)
- `real discrete_range_lccdf(ints y | ints l, ints u)` - Log complementary CDF (available since 2.26)
- `ints discrete_range_rng(ints l, ints u)` - Random variate generation (available since 2.26)

---

## Ordered Logistic Distribution

### Probability Mass Function
For K > 2, ordered cutpoints c, and eta in R:
- OrderedLogistic(k=1|eta,c) = 1 - logit^{-1}(eta - c_1)
- OrderedLogistic(1<k<K|eta,c) = logit^{-1}(eta - c_{k-1}) - logit^{-1}(eta - c_k)
- OrderedLogistic(k=K|eta,c) = logit^{-1}(eta - c_{K-1})

### Distribution Statement
`k ~ ordered_logistic(eta, c)`

### Stan Functions
- `real ordered_logistic_lpmf(ints k | vector eta, vectors c)` - Log PMF (available since 2.18)
- `real ordered_logistic_lupmf(ints k | vector eta, vectors c)` - Log PMF dropping constants (available since 2.25)
- `int ordered_logistic_rng(real eta, vector c)` - Random variate generation (available since 2.0)

---

## Ordered Logistic Generalized Linear Model (Ordinal Regression)

### Distribution Statement
`y ~ ordered_logistic_glm(x, beta, c)`

### Stan Functions
Multiple overloads available:
- `real ordered_logistic_glm_lpmf(int y | row_vector x, vector beta, vector c)`
- `real ordered_logistic_glm_lupmf(int y | row_vector x, vector beta, vector c)`
- `real ordered_logistic_glm_lpmf(int y | matrix x, vector beta, vector c)`
- `real ordered_logistic_glm_lupmf(int y | matrix x, vector beta, vector c)`
- `real ordered_logistic_glm_lpmf(array[] int y | row_vector x, vector beta, vector c)`
- `real ordered_logistic_glm_lupmf(array[] int y | row_vector x, vector beta, vector c)`
- `real ordered_logistic_glm_lpmf(array[] int y | matrix x, vector beta, vector c)`
- `real ordered_logistic_glm_lupmf(array[] int y | matrix x, vector beta, vector c)`

Available since version 2.23 (lupmf since 2.25).

---

## Ordered Probit Distribution

### Probability Mass Function
For K > 2, ordered cutpoints c, and eta in R:
- OrderedProbit(k=1|eta,c) = 1 - Phi(eta - c_1)
- OrderedProbit(1<k<K|eta,c) = Phi(eta - c_{k-1}) - Phi(eta - c_k)
- OrderedProbit(k=K|eta,c) = Phi(eta - c_{K-1})

### Distribution Statement
`k ~ ordered_probit(eta, c)`

### Stan Functions
- `real ordered_probit_lpmf(ints k | vector eta, vectors c)` - Log PMF (available since 2.18)
- `real ordered_probit_lupmf(ints k | vector eta, vectors c)` - Log PMF dropping constants (available since 2.25)
- `real ordered_probit_lpmf(ints k | real eta, vectors c)` - Log PMF scalar eta (available since 2.19)
- `real ordered_probit_lupmf(ints k | real eta, vectors c)` - Log PMF scalar eta dropping constants (available since 2.19)
- `int ordered_probit_rng(real eta, vector c)` - Random variate generation (available since 2.18)
