# Copulas

Copulas provide a flexible way to model multivariate distributions by separating the marginal cumulative distribution functions from the dependence structure. This chapter introduces copulas in Stan, focusing on implementation techniques and practical examples. This chapter was derived from Brynjolfur Gauti Gudrunar Jonsson's "A gentle introduction: the Gaussian copula".

## What Are Copulas?

According to Sklar's theorem (Sklar 1959), any multivariate distribution can be expressed in terms of its marginals and a copula that captures the dependence structure. Copulas are functions that join univariate marginal cumulative distribution functions to form multivariate distributions.

For a multivariate random variable **X** = [X1 ... Xd]^T with marginal cumulative distribution functions Fi, the joint cumulative distribution function can be written as:

F_X(x) = C(F1(x1), ..., Fd(xd)) = Pr[X1 <= x1, ..., Xd <= xd]

where C is the copula function, F_X is the joint cumulative distribution function, and Fi are the marginal cumulative distribution functions. The copula function C must be a joint cumulative distribution function over the unit hypercube [0, 1]^D.

## General Structure of Copula Models in Stan

This section describes the general structure of copula models in Stan. The next sections will provide specific examples of copula implementations, but first, let's understand the general pattern that separates the marginal distributions from the dependence structure.

The log density of a multivariate distribution using a copula can be written as:

log h(x) = log c(u1, ..., ud | alpha) + Σ_{i=1}^D log fi(xi | beta_i)

where:

- ui = Fi(xi | beta_i) are the probability integral transforms of the data
- log c(u1, ..., ud | alpha) is the log density of the copula
- Σ_{i=1}^D log fi(xi | beta_i) is the sum of the log densities of the marginals
- alpha represents the parameters describing the parametric form of the copula
- beta_i represents the parameters describing the parametric form of the i-th marginal distribution

The implementation of copulas in Stan has two key requirements:

1. Both the probability density functions and cumulative distribution functions of the marginal distributions must be available
2. A function that computes the log density of the copula for the transformed data must be implemented

Most copula implementations in Stan follow a three-step process:

1. **Accumulate marginal log likelihoods**: Calculate and add the log density of each marginal distribution to the target log density
2. **Transform to uniform variables**: Apply the marginal CDFs to transform the data to uniform variables on the unit interval
3. **Calculate copula density**: Compute the log density of the copula based on these uniform variables and add it to the target log density

This process is reflected in the general form of the log density shown above, where the first term represents the copula density and the second term represents the sum of marginal log densities.

In a way, we are always modeling with copulas, as the independence assumption can be viewed as a special case using the independence copula, where log c(u) = 0, resulting in the familiar sum of marginal log densities. This perspective highlights that traditional independent modeling is just a specific case within the broader copula framework.

Most parametric copula families include independence as a special case, either as a subset of their parameter space (e.g., when correlation parameters are zero) or as a limit when parameters approach specific values (e.g., when the dependence parameter approaches zero in Archimedean copulas).

## Gaussian Copula Example

The Gaussian copula is constructed using the multivariate normal distribution. For a D-dimensional random vector **X** with marginals Fi, the log Gaussian copula density is given by:

log c(u) = -1/2 log |Omega| - 1/2 z^T (Omega^{-1} - I) z
         = -1/2 log |Omega| - 1/2 z^T Omega^{-1} z + 1/2 z^T z
         = log N(z | 0, Omega) - log N(z | 0, I)

where z = [Phi^{-1}(u1), ..., Phi^{-1}(ud)]^T are the inverse normal CDF transforms of the uniform marginals, Omega is the correlation matrix, and I is the identity matrix. The joint log density is then:

log h(x) = log c(F1(x1), ..., Fd(xd)) + Σ_{i=1}^D log fi(xi)

Following the three-step process for implementing copulas in Stan:

1. **Accumulate marginal log likelihoods**: The exponential log densities are added to the target in the line `target += exponential_lpdf(y[n] | lambda)`
2. **Transform to uniform variables**: The exponential CDF transforms the data to uniform variables: `exponential_cdf(y[n, d] | lambda[d])`
3. **Calculate copula density**: The transformed variables are converted to normal scale using `inv_Phi` and the multivariate normal log density is computed: `z ~ multi_normal_cholesky(zeros, L_Omega)`

The following example demonstrates a Gaussian copula with exponential marginal distributions. Note that while the copula is Gaussian, the marginals are exponential.

```stan
data {
  int<lower=0> N;  // number of observations
  int<lower=0> D;  // number of dimensions
  vector<lower=0>[D] y[N];  // data
}

transformed data {
  vector[D] zeros = rep_vector(0, D);
}

parameters {
  // Parameters for exponential marginal distributions
  vector<lower=0>[D] lambda;  // rate parameters

  // Correlation matrix for Gaussian copula
  cholesky_factor_corr[D] L_Omega;
}

model {
  // Priors
  lambda ~ gamma(2, 1);  // prior for rate parameters
  L_Omega ~ lkj_corr_cholesky(2);

  // Likelihood using Gaussian copula with exponential marginals
  for (n in 1:N) {
    // Add exponential log density to target
    target += exponential_lpdf(y[n] | lambda);

    vector[D] z;
    for (d in 1:D) {
      // Transform to uniform using exponential CDF
      real u_d = exponential_cdf(y[n, d] | lambda[d]);

      // Transform to standard normal
      z[d] = inv_Phi(u_d);
    }
    // Multivariate normal log density with correlation matrix
    z ~ multi_normal_cholesky(zeros, L_Omega);
  }
}

generated quantities {
  // Optional: Recover correlation matrix from Cholesky factor
  matrix[D, D] Omega = multiply_lower_tri_self_transpose(L_Omega);
}
```

## Advantages of Copulas

Copulas offer several advantages in statistical modeling:

1. **Flexibility**: They allow combining any marginal distributions with various dependence structures. For example:
   - Modeling financial returns with heavy-tailed marginals and complex dependence structures
   - Combining different types of distributions (e.g., normal and gamma) in a single model
   - Capturing asymmetric dependencies between variables, such as in financial markets where joint negative returns are more common than joint positive returns due to macro-events affecting multiple stocks simultaneously, while positive returns tend to be more idiosyncratic
   - Modeling different types of tail dependence in different parts of the distribution

2. **Factorability**: The marginal distributions and dependence structure can be modeled separately, allowing for different prior knowledge about each component. This is similar to the common practice of factoring scale and correlation in multivariate normal priors.

   For example, when modeling the survival times of two components in a system, we can separately specify exponential or gamma marginal distributions based on historical failure data for each component, and a Gaussian copula (or asymmetrical Archimedean copula) capturing how the failure of one component affects the other, making it easier to incorporate prior knowledge about each aspect independently.

3. **Tail dependence**: Different copulas can capture different types of tail dependence, which is crucial in applications like risk management and extreme value analysis where joint extreme scenarios need to be quantified.

4. **Universal Framework**: In a way, we are always modeling with copulas, as the independence assumption can be viewed as a special case using the independence copula. This perspective highlights that traditional independent modeling is just a specific case within the broader copula framework.

## Common Pitfalls and Considerations

When implementing copulas in Stan, several considerations should be kept in mind:

1. **Computational efficiency**: The probability integral transform and inverse transform steps can be computationally intensive, especially for complex marginal distributions.

2. **Parameter identifiability**: Care must be taken to ensure that the parameters of the marginal distributions and the copula are identifiable.

3. **Model selection**: The choice of copula family should be guided by the specific dependence structure of the data. For example:
   - The Gaussian copula may underestimate the probability of joint extreme events in financial data
   - The Student-t copula, while offering tail dependence, maintains symmetric tail behavior that may not match all applications
   - Archimedean copulas can model asymmetric tail dependence but may be less flexible and harder to estimate in high dimensions

4. **Numerical stability**: The transformations between different scales (original, uniform, and normal/Student-t/calculations using Archimedean copulas) require careful implementation to maintain numerical stability.

5. **Symmetry considerations**: Many copula families exhibit strong symmetries that may not match the data:
   - **Radial symmetry**: Some copulas (like Gaussian and Student-t) treat positive and negative extremes equally, which may not match financial data where joint negative returns are more common than joint positive returns
   - **Exchangeability**: Some copulas are invariant under permutations of their arguments, which can lead to unintuitive results when combined with inhomogeneous marginals. For example, when modeling time-to-event scenarios with different marginal distributions (e.g., exponential distributions with different parameters), perfect dependence in the copula does not imply simultaneous events. Instead, one event triggers the other at a later time corresponding to the same quantile, which can lead to incorrect modeling of joint events.

6. **Tail dependence**: Understanding and choosing appropriate tail dependence is crucial:
   - The upper (lower) tail dependence coefficient lambda_u (lambda_l) is the probability that one variable is extremely large (small) given that another is extremely large (small).
   - Different copula families exhibit different tail dependence properties:
     - Some copulas (like Gaussian) have zero tail dependence
     - Others can model symmetric tail dependence (lambda_u = lambda_l)
     - Some can capture asymmetric tail dependence (lambda_u != lambda_l)
     - Certain copulas allow for tail dependence even with zero correlation
   - The choice of copula should be guided by the expected tail behavior in the application:
     - Financial data often requires modeling joint lower extreme events
     - Risk management applications may need asymmetric tail dependence
     - Some applications may require different tail behavior in different parts of the distribution

7. **High-dimensional modeling**: As dimensionality increases:
   - The number of dependence parameters grows
   - Some copula families become less flexible
   - Vine copulas or factor copulas may be more appropriate

## Common Copula Families

Several copula families are available for modeling different dependence structures in the correlation component:

- **Gaussian copula**: Based on the multivariate normal distribution, offering symmetric dependence
- **Student-t copula**: Based on the multivariate Student-t distribution, providing more flexibility in tail dependence than the Gaussian copula
- **Archimedean copulas**: A class of copulas defined through generator functions, including:
  - Clayton copula: Stronger lower tail dependence
  - Gumbel copula: Stronger upper tail dependence
  - Frank copula: Symmetric dependence
- **Vine copulas**: A flexible approach for modeling high-dimensional dependencies by decomposing the joint distribution into a series of bivariate copulas

## Further Reading/Viewing

- Jonsson's three part blog series, *Copulas in Stan*:
  - Part I: [If it bleeds, we can kill it](https://bggj.is/posts/stan-copulas-1/)
  - Part II: [A gentle introduction: the Gaussian copula](https://bggj.is/posts/gaussian-copula/)
  - Part III: [It was the best of tails, it was the worst of tails: The T-Copula](https://bggj.is/posts/t-copula/)
- Brynjolfur Gauti Gudrunar Jonsson's StanCon 2024 presentation, [Copulas in Stan: Modeling Spatial Dependence](https://www.youtube.com/watch?v=aHZ-rnepUNk)
- Sean Pinkney's *Helpful Stan functions*: [copula functions](https://spinkney.github.io/helpful_stan_functions/group__copula.html)

## References

Sklar, Abe. 1959. "Abe Sklar's 'FONCTIONS DE REPARTITION a n DIMENSIONS ET LEURS MARGES': The Original Document and an English Translation." Translated by Ben Van Vliet. *The Original Document and an English Translation (March 3, 2023)*. https://dx.doi.org/10.2139/ssrn.4198458
