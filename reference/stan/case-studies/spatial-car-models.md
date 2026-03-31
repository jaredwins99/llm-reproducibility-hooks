> Source: https://mc-stan.org/learn-stan/case-studies/icar_stan.html

Spatial Models in Stan: Intrinsic Auto-Regressive Models for Areal Data
# Spatial Models in Stan: Intrinsic
Auto-Regressive Models for Areal Data

#### Mitzi Morris

- About conditional
autoregressive models
- Adding an ICAR
component to a Stan model
- Example:
disease mapping using the Besag York Mollié model
- BYM2:
improving the parameterization of the Besag, York, and Mollié
model
- Bigger
data: from 56 counties in Scotland to 1921 census tracts in New York
City
- Discussion
- Acknowledgements
- References
#### Update, August 2019


An expanded version of this case study is now available as: Bayesian
Hierarchical Spatial Models: Implementing the Besag York Mollié Model in
Stan Many thanks to my awesome co-authors:
- Katherine Wheeler-Martin
- Dan Simpson
- Stephen J. Mooney
- Andrew Gelman
- Charles DiMaggio

When areal data has a spatial structure such that observations from
neighboring regions exhibit higher correlation than distant regions,
this correlation can be accounted for using the class of spatial models
called “CAR” models (Conditional Auto-Regressive) introduced by Besag
(Besag 1974). Intrinsic Conditional Auto-Regressive (ICAR) models are a
subclass of CAR models. The Besag York Mollié (BYM) model is a lognormal
Poisson model which includes both an ICAR component for spatial
smoothing and an ordinary random-effects component for non-spatial
heterogeneity. This case study covers how to efficiently code these
models in Stan.

All models and data files are available in the Stan example-models
GitHub repo for Stan case studies: car-iar-poisson.
All commands should be run from the directory
stan-dev/example-models/knitr/car-iar-poisson.
## About conditional autoregressive models


CAR and ICAR models are used when areal data consists of a single
aggregated measure per areal unit, either a binary, count, or continuous
value. Areal units are volumes, more precisely, areal units partition a
multi-dimensional volume D into a finite number of sub-volumes with
well-defined boundaries. Areal data differs from point data, which
consists of measurements from a known set of geo-spatial points. For
point data, the relationship between points is a continuous, real-valued
distance measure which can be calculated automatically for any two
points on the map, allowing for the addition of new points to the map.
Given a set of areal units, there is no automatic procedure for adding a
new areal unit, thus models for areal data are non-generative with
respect to the areal regions.

For a set of \(N\) areal units, the
relationship between areal units is described by an \(N \times N\) adjacency matrix, which is
usually written \(A\) for adjacency, or
\(W\) for weights. For the binary
neighbor relationship, written \(i
\sim j\) where \(i \neq j\), the
entries in the adjacency matrix are \(1\) if regions \(n_i\) and \(n_j\) are neighbors and is otherwise \(0\). For CAR models, the neighbor
relationship is symmetric but not reflexive; if \(i \sim j\) then \(j \sim i\), but a region is not its own
neighbor.
### Conditional Autoregressive (CAR) Models


Given a set of observations taken at \(N\) different areal units of a region,
spatial interactions between a pair of units \(n_i\) and \(n_j\) can be modelled conditionally as a
spatial random variable \(\mathbf{\phi}\), which is an \(n\)-length vector \(\mathbf{\phi} = ({\phi}_1, \ldots,
{\phi}_n)^T\).

In the full conditional distribution, each \({\phi}_i\) is conditional on the sum of the
weighted values of its neighbors (\(w_{ij}\,\phi_j\)) and has unknown variance
\[\phi_i \mid \phi_j, j \neq i, \sim
\mathrm{N} \left( \sum_{j = 1}^n w_{ij} \phi_j, {\sigma}^2
\right).\]

Specification of the global, or joint distribution via the local
specification of the conditional distributions of the individual random
variables defines a Gaussian Markov random field (GMRF). Besag (1974)
proved that the corresponding joint specification of \(\phi\) is a multivariate normal random
variable centered at \(0\). The
variance of \(\phi\) is specified as a
precision matrix \(Q\) which is simply
the inverse of the covariance matrix \(\Sigma\), i.e. \(\Sigma = Q^{-1}\) so that \[\phi \sim \mathrm{N}(0, Q^{-1}).\]

In order for the standard multivariate normal random variable \(\phi\) to have a proper joint probability
density, the precision matrix \(Q\)
must be symmetric and positive definite. This is accomplished by
constructing the precision matrix \(Q\)
from the adjacency matrix \(W\):

\[ Q = [D_{\tau}(I - \alpha B)]
\]

where
- \(W\) is the \(n \times n\) adjacency matrix where entries
\(\{i,i\}\) are zero and the
off-diagonal elements are \(1\) if
regions \(i\) and \(j\) are neighbors and \(0\) otherwise.
- \(D\) is the \(n \times n\) diagonal matrix where entries
\(\{i,i\}\) are the number of neighbors
of region \(i\) and the off-diagonal
entries are \(0\).
- \(D_{\tau} = \tau\, D\).
- \(\alpha\) controls the amount of
spatial correlation; \(\alpha = 0\)
implies spatial independence and \(\alpha =
1\) implies complete spatial correlation.
- \(B\) is the scaled adjacency
matrix \(D^{-1}W\).
- \(I\) is an \(n \times n\) identity matrix.

When \(\alpha\) is in the interval
(0,1), the precision matrix \(Q\) is
positive definite, thus the joint distribution \(\phi\) is proper.

Evaluation of \(\phi\) requires
computing the determinant of the precision matrix \(Q\), which is computationally expensive.
See the Stan case study Exact
sparse CAR models in Stan for ways to speed up computation.
### Intrinsic Conditional Auto-Regressive (ICAR) models


An Intrinsic Conditional Auto-Regressive (ICAR) model is a CAR model
where \(\alpha = 1\), that is, it
assumes complete spatial correlation between regions. (Spoiler alert:
this assumption is problematic, resulting in the the BYM model and
successors). The joint distribution of the ICAR model is derived from
the joint distribution for the CAR model as follows:
- since \(D_{\tau} = \tau D\) and
\(B = D^{-1}W\), the expression \([D_{\tau}(I - \alpha B)]\) simplifies to
\([{\tau}(D - \alpha W)]\).
- since \(\alpha = 1\), it is
omitted.

The resulting matrix \([\tau \, (D -
W)]\) is singular, thus the ICAR variate \(\phi\) is an improper prior distribution,
with joint distribution:

\[\phi \sim N(0, [\tau \, (D -
W)]^{-1}).\]

While this ICAR model is non-generating in that it cannot be used as
a model for the data, it can be used as a prior as part of a
hierarchical model, which is the role it plays in the BYM model.

The corresponding conditional distribution specification is:

\[ p \left( { \phi }_i \, \vert\, {\phi}_j
\, j \neq i, {{\tau}_i}^{-1} \right)
= \mathit{N} \left( \frac{\sum_{i \sim j} {\phi}_{i}}{d_{i,i}},
\frac{1}{d_{i,i} {\tau}_i} \right)\]

where \(d_{i,i}\) is the number of
neighbors for region \(n_i\). The
individual spatial random variable \({\phi}_i\) for region \(n_i\) which has a set of neighbors \(j \neq i\) whose cardinality is \(d_{i,i}\), is normally distributed with a
mean equal to the average of its neighbors. Its variance decreases as
the number of neighbors increases.

The joint distribution, above, rewrites to the pairwise
difference formulation:

\[ p(\phi | \tau) \propto {\tau}^{\frac{n
- NC}{2}} \exp \left\{ {- \frac{\tau}{2}} \sum_{i \sim j}{({\phi}_i -
{\phi}_j)}^2 \right\} \]

where \(NC\) is the number of
components in the graph over all areal subregions defined by the spatial
proximity matrix; \(NC == 1\) when the
areal graph is fully connected, i.e., every subregion can be reached
from every other subregion via a sequence of neighbors.

From the pairwise difference formulation, we see that the joint
distribution is non-identifiable; adding any constant to all of the
elements of \(\phi\) leaves the joint
distribution unchanged. Adding the constraint \(\sum_{i} {\phi}_i = 0\) resolves this
problem.
### Derivation of the Pairwise Difference Formula


The jump from the joint distribution to the pairwise difference
requires a little reasoning about the matrix \(D - W\) and a lot of algebra, which we
present here. As stated above, the notation \(i \sim j\) indicates that \(i\) and \(j\) are neighbors.

To compute with a unit multivariate Gaussian, we set \(\tau\) to 1 so that the joint distribution
for for vector-valued random variable \(\phi =
{[{\phi}_1, \ldots, {\phi}_n]}^T\) is:

\[\phi \sim N(0, [D -
W]^{-1}).\]

with probability density function:

\[ p(\phi) \propto {(2 \, \pi)}^{-{n / 2}}
\, {\begin{vmatrix} [D - W]^{-1} \end{vmatrix}}^{1/2} \exp \left(
-{\frac{1}{2}} {\phi}^T [D - W] \phi \right) \]

Terms \({(2 \, \pi)}^{-{n / 2}}\)
and \({\vert[D - W]^{-1} \vert}^{1/2}\)
are constants with respect to \(\phi\)
and can be dropped from the computation:

\[ p(\phi) \propto \exp \left(
-{\frac{1}{2}} {\phi}^T [D - W] \phi \right) \]

Stan computes on the log scale, so the log probability density
is:

\[
\begin{align}
\log p(\phi) &=  -{\frac{1}{2}} {\phi}^T [D - W] \phi + \mbox{const}
\\
&= -{\frac{1}{2}} \left( \sum_{i,j} {\phi}_i {[D - W]}_{i,j}
{\phi}_j \right) + \mbox{const} \\
&= -{\frac{1}{2}} \left( \sum_{i,j} {\phi}_i\,{\phi}_j D_{i,j} -
\sum_{i,j} {\phi}_i\,{\phi}_j W_{i,j} \right) + \mbox{const} \\
&= -{\frac{1}{2}} \left( \sum_{i} {{\phi}_i}^2\,D_{i,i} - \sum_{i
\sim j} 2\ {\phi}_i\,{\phi}_j \right) + \mbox{const} \\
&= -{\frac{1}{2}} \left( \sum_{i \sim j} ({{\phi}_i}^2 +
{{\phi}_j}^2) - \sum_{i \sim j} 2\ {\phi}_i\,{\phi}_j \right) +
\mbox{const} \\
&= -{\frac{1}{2}} \left( \sum_{i \sim j} {{\phi}_i}^2 - 2\
{\phi}_i\,{\phi}_j + {{\phi}_j}^2 \right) + \mbox{const} \\
&= -{\frac{1}{2}} \left( \sum_{i \sim j} {({\phi}_i - {\phi}_j)}^2
\right) + \mbox{const}
\end{align}
\]

Since \(D\) is the diagonal matrix
where \(D_{i,i}\) is the number of
neighbors and the off-diagonal entries have value \(0\). The expression \(\sum_{i,j} {\phi}_i\,{\phi}_j D_{i,j}\)
rewrites to terms \({{\phi}_i}^2\)
where the number of each \({\phi_i}\)
terms is given by \(D_{i,i}\). For each
pair of adjacent regions \(\{i,j\}\)
and \(\{j,i\}\), one \({\phi}^2\) term each is contributed, so we
can rewrite this in terms of \(i \sim
j\). Since \(W\) is the
adjacency matrix where \(w_{ii} = 0, w_{ij} =
1\) if \(i\) is a neighbor of
\(j\), and \(w_{ij}=0\) otherwise, the expression \(\sum_{i,j} {\phi}_i\,{\phi}_j W_{i,j}\)
rewrite to terms \(2 \, {\phi}_i
{\phi}_j\), since there are two entries in \(W\) for each pair of adjacent regions. When
both expressions are over \(i \sim j\),
we combine, rearrange, and reduce.

We check our work by a simple example using 4 regions \(\{a, b, c, d\}\) where \(a\) is adjacent to \(b\), \(b\)
is adjacent to \(c\), and \(c\) is adjacent to \(d\). The diagonal matrix \(D\)\[\begin{pmatrix}\ 1\ 0\ 0\ 0\ \\
\ 0\ 2\ 0\ 0\ \\
\ 0\ 0\ 2\ 0\ \\
\ 0\ 0\ 0\ 1\ \end{pmatrix}\] contributes terms \(a^2, b^2, b^2, c^2, c^2, d^2\). The
adjacency matrix \(W\)\[\begin{pmatrix}\ 0\ 1\ 0\ 0\ \\
\ 1\ 0\ 1\ 0\ \\
\ 0\ 1\ 0\ 1\ \\
\ 0\ 0\ 1\ 0\  \end{pmatrix}\] contributes terms \(ab, ba, bc, cb, cd, dc\). We group the
terms in \(D - W\) as follows: \((a^2 - 2ab + b^2), (b^2 - 2bc + c^2), (c^2 - 2cd +
d^2)\) which rewrites to \({(a - b)}^2,
{(b - c)}^2, {(c - d})^2\).

Note that while adjacency is symmetric, i.e., \(b\) is adjacent to \(a\) and \(c\) is adjacent to \(b\), the pairwise difference counts
pairs of neighbors, hence the name. Therefore, the
specification of the pairwise difference form includes the constraint on
the indices \(i\) and \(j\) for the summation that \(i < j\), as is done in Besag and
Kooperberg 1995.
## Adding an ICAR component to a Stan model


In this section we provide an efficient implementation of a simple
ICAR component in Stan. To check our work, we compute a spatial prior on
a small dataset.

The encoding of adjacency as entries of either \(0\) or \(1\) in an \(N
\times N\) adjacency matrix is equivalent to an undirected graph
with set of \(N\) nodes and a set of
edges, one edge per pair of non-zero entries \(\{i,j\}\) and \(\{j,i\}\). The cardinality of this edge set
is equal to the number of non-zero entries in either the upper or lower
triangular matrix.

For large values of \(N\), storing
and traversing a full \(N \times N\)
adjacency matrix is computationally expensive. As the adjacency matrix
for areal data is a sparse matrix whose triangular matrices are also
sparse, encoding the non-zero entries as an edge set requires less
storage. This is also the natural encoding for computing pairwise
differences \({({\phi}_i -
{\phi}_j)}^2\). Furthermore, the pairwise difference formulation
doesn’t use information about the nodes, only the edges, thus we don’t
even need to store the node set explicitly, we only need to store \(N\).

In Stan, we create two parallel integer arrays node1 and
node2 which store edge information, together with integer
values N, the number of nodes, and N_edges,
the number of edges. These two arrays are (implicitly) indexed by the
ordinal value of node \(i\) in the
graph, thus we don’t need to store the list of node ids. These are
declared in the data block of a Stan program as follows:
```
data {
  int<lower=0> N;
  int<lower=0> N_edges;
  array[N_edges] int<lower=1, upper=N> node1; // node1[i] adjacent to node2[i]
  array[N_edges] int<lower=1, upper=N> node2; // and node1[i] < node2[i]
```


Stan’s multiple indexing feature allows multiple indexes to be
provided for containers (i.e., arrays, vectors, and matrices) in a
single index position on that container, where the multiple indexes are
either an array of integer values or range bounds. Using the entries in
arrays node1 and node2 as multiple indexes, we
compute the pairwise differences \({\phi}_i -
{\phi}_j\) as:
```
phi[node1] - phi[node2]       // multi-indexing and vectorization!

```


The log probability density of \(\phi\) is: \[-{\frac{1}{2}} \left( \sum_{i \sim j} {({\phi}_i
- {\phi}_j)}^2 \right) + \mbox{const}\] Since Stan computes up to
a proportion, the constant term drops out.

As noted above, \(\phi\) is
non-identifiable; adding any constant to all of the elements of \(\phi\) leaves the distribution unchanged.
Therefore we must add the constraint \(\sum_{i} {\phi}_i = 0\). This can be
implemented as a hard sum-to-zero constraint by declaring an parameter
vector of length \(N - 1\) with a
corresponding transformed parameter vector of length \(N\) whose n-th element is negation of the
sum of the parameter vector. Another option is to set up a soft
sum-to-zero constraint using a prior on \({\phi}\) which tightly constrains the mean
of \({\phi}\) to be within some epsilon
of zero. Having explored both options, we found that Stan’s HMC sampler
runs faster on models which have a soft sum-to-zero constraint.

The following program fragment shows the Stan parameter and model
block to compute the spatial effects vector \({\phi}\). The Stan function
dot_self computes the dot product of a vector with itself,
i.e., it computes the quantity \({({\phi}_i -
{\phi}_j)}^2\):
```
parameters {
  vector[N] phi;
}
model {
  target += -0.5 * dot_self(phi[node1] - phi[node2]);
  
  // soft sum-to-zero constraint on phi,
  // equivalent to mean(phi) ~ normal(0,0.01)
  sum(phi) ~ normal(0, 0.01 * N);
}
```

### Model Validation: an ICAR Prior for the Counties of Scotland


To check our work, we build a simple Stan model which takes in the
neighborhood structure of the counties of Scotland and use it to compute
the spatial ICAR prior. We then compare our results against those
obtained by running an equivalent BUGS model which calls the
WinBUGS/GeoBUGS function car.normal.

The Stan program is in the file simple_iar.stan.
It consists of just the statements discussed in the preceding
section:
```
writeLines(readLines('simple_iar.stan'))

data {
  int<lower=0> N;
  int<lower=0> N_edges;
  array[N_edges] int<lower=1, upper=N> node1; // node1[i] adjacent to node2[i]
  array[N_edges] int<lower=1, upper=N> node2; // and node1[i] < node2[i]
}
parameters {
  vector[N] phi;
}
model {
  target += -0.5 * dot_self(phi[node1] - phi[node2]);
  
  // soft sum-to-zero constraint on phi,
  // equivalent to mean(phi) ~ normal(0,0.01)
  sum(phi) ~ normal(0, 0.01 * N);
}
```


The data comes from the Scotland lip cancer dataset originally
presented by Clayton and Kaldor 1987, but here we use the version of the
data downloaded from Brad Carlin’s
software page, file named “Lipsbrad.odc”, which is an OpenBUGS data
format file containing a WinBUGS model, data, and inits. We’ve edited
the data into file scotland_data.R.
It defines a list named data with the following fields:
- y: the observed lip cancer case counts on a per-county
basis
- x: an area-specific continuous covariate that
represents the proportion of the population employed in agriculture,
fishing, or forestry (AFF)
- E: the expected number of cases, used as an
offset,
- adj: a list of region ids for adjacent regions
- num: a list of the number of neighbors for each
region

Elements adj and num describe the
neighborhood structure of the counties in Scotland. We have written a
helper function mungeCARdata4stan
which can transform the fields data$adj and
data$num into a list structure with fields N,
N_edges, node1, and node2 which
correspond to the inputs required by the Stan model.

The script fit_simple_iar_stan.R
compiles and runs the model on the Scotland data. To check that this
model recovers the spatial relationships, we compare the Stan results to
those obtained by fitting the same data to the equivalent BUGS model
which is in the file simple_iar.txt.
We use the R R2OpenBugs
package to this model via OpenBUGS, which requires that we wrap the BUGS
model in a function statement for R:
```
writeLines(readLines('simple_iar.txt'))

simple_iar <- function() {
  phi[1:N]~car.normal(adj[],weights[],num[],1)
}
```

The following description of the car.normal
function and arguments is taken from the GeoBUGS manual:


The intrinsic Gaussian CAR prior distribution is specified using the
distribution car.normal for the vector of random variables
S = ( S1, ….., SN ) where: S[1:N] ~ car.normal(adj[], weights[], num[],
tau)

The parameters to this function are:
- adj[]: A vector listing the ID numbers of the adjacent areas for
each area.
- weights[] : A vector the same length as adj[] giving unnormalized
weights associated with each pair of areas.
- num[] : A vector of length N (the total number of areas) giving the
number of neighbors for each area.
- tau: A scalar argument representing the precision (inverse variance)
parameter. ()

The first 3 arguments must be entered as data (it is currently not
possible to allow the weights to be unknown); the final variable tau is
usually treated as unknown and so is assigned a prior distribution.

The script fit_simple_iar_bugs.R
compiles and runs the model on the Scotland data.

We fit both models running 2 chains for a total of 10,000 iterations
of which 9000 are warmup/burnin which results in a sample of 2000 draws.
We use RStan to print the posterior summary statistics for the fit
object returned by ROpenBugs.

Below we compare the results for the first 10 elements of \({\phi}\): The RStan output column “se_mean”
reports the Monte Carlo standard error, which reflects the uncertainty
from the simulation.
```
                 mean   se_mean  sd    2.5%  97.5%  n_eff Rhat
(stan) phi[1]   0.000   0.037 0.806  -1.548  1.630   473 1.004
(bugs) phi[1]  -0.009   0.017 0.769  -1.559  1.524  1900 1.000

(stan) phi[2]   0.029   0.042 1.012  -1.930  2.055   572 1.005
(bugs) phi[2]   0.005   0.022 0.994  -1.979  1.912  1900 1.000

(stan) phi[3]   0.005   0.068 1.369  -2.833  2.593   409 1.000
(bugs) phi[3]   0.007   0.032 1.398  -2.730  2.645  1950 1.000

(stan) phi[4]   0.015   0.041 0.959  -1.895  1.899   552 1.000
(bugs) phi[4]   0.005   0.021 0.918  -1.748  1.838  1900 1.003

(stan) phi[5]  -0.001   0.039 0.788  -1.581  1.557   413 1.003
(bugs) phi[5]   0.005   0.018 0.792  -1.509  1.568  1900 1.001

(stan) phi[6]  -0.033   0.081 1.657  -3.348  3.219   421 1.000
(bugs) phi[6]  -0.002   0.038 1.693  -3.281  3.183  1977 1.000

(stan) phi[7]  -0.005   0.036 0.757  -1.455  1.444   453 1.008
(bugs) phi[7]  -0.003   0.016 0.734  -1.397  1.476  1900 0.999

(stan) phi[8]  -0.022   0.085 1.916  -3.873  3.584   513 1.000
(bugs) phi[8]   0.024   0.045 1.986  -3.794  3.860  1958 0.999

(stan) phi[9]  -0.006   0.026 0.595  -1.185  1.199   529 1.005
(bugs) phi[9]   0.016   0.013 0.596  -1.108  1.157  1900 0.999

(stan) phi[10]  -0.002  0.039 0.853  -1.691  1.727   480 1.006
(bugs) phi[10]   0.018  0.018 0.822  -1.595  1.580  2000 0.999

```


As both simulations are within se_mean of one another, we conclude
that they have both converged to the same posterior distribution. From
this we conclude that the Stan model correctly implements the ICAR model
as specified above.
## Example: disease mapping using the Besag York Mollié model


Adding a CAR spatially structured error term to a multi-level GLM
provides spatial smoothing of the resulting estimates. The lognormal
Poisson model proposed in Besag York Mollié 1991 is used for count data
in biostatistics and epidemiology. It includes both an ICAR component
for spatial smoothing and an ordinary random-effects component for
non-spatial heterogeneity.

Implementations of this model are available via R, BUGS, and JAGS as
well as INLA (Integrated Nested Laplace Approximation) which is a fast
alternative to MCMC, (INLA trades speed and scalability for accuracy,
per the “no free lunch” principle). Banerjee Carlin and Gelfand 2003,
section 5.4, presents the details of this model and its difficulties,
together with a WinBUGS implementation which they use to fit the
Scottish lip cancer dataset from Clayton and Kaldor 1987.

Using the notation of Banerjee et al., the Besag York Mollié model
is: \[
Y_i \, \vert \, \psi_i \sim Poisson ( E_i \, e^{\psi_i}),
\] for \(i \in 1:N\), where
\[
\psi = x \beta + \theta + \phi
\] and
- 

\(x\) is the matrix of
explanatory spatial covariates such that \(x_i\) is the vector of covariates for areal
unit \(i\). The coefficients \(\beta\) are called “fixed
effects.”
- 

\(\theta\) is an ordinary
random-effects components for non-spatial heterogeneity.
- 

\(\phi\) is an ICAR spatial
component.

The pairwise difference formulation of the ICAR spatial component
\(\phi\) is non-identifiable. Adding
the constraint that \(\phi\) must sum
to zero centers it, allowing the model to fit both the fixed-effect
intercept term as well as \(\phi\) and
\(\theta\).

The convolution of the random effects components \(\phi\) and \(\theta\) is difficult to fit without strong
constraints on one of the two components, as either component can
account for most or all of the individual-level variance. Without any
hyperpriors on \(\phi\) and \(\theta\) the sampler will be forced to
explore many extreme posterior probability distributions; the sampler
will go very slowly or fail to fit the data altogether. The example
model used to fit the Scotland lip cancer dataset in Banerjee Carlin and
Gelfand 2003 uses gamma hyperpriors on the precision parameters \({\tau}_{\phi}\) and \({\tau}_{\theta}\), see discussion of “CAR
models and their difficulties”, section 5.4. The precision of \(\phi\), tau_phi is given the
hyperprior gamma(1, 1) while the precision of \(\theta\) is given the hyperprior
gamma(3.2761, 1.81). This is intended to make a “fair”
prior which places equal emphasis on both spatial and non-spatial
variance, based on the formula from Bernardinelli et al. (1995):

\[ \textit{sd} ({\theta}_i) =
\frac{1}{\sqrt{\tau}_{\phi}} \approx \frac{1}{0.7 \sqrt{ \bar m
{\tau}_{\theta}}} \approx \textit{sd}({\phi}_i) \]

We use these same hyperpriors for the precision of the random effects
when implementing this model in Stan. These particular values allows the
model to fit the Scotland data. However, the assumptions underlying the
use of this choice of hyperpriors and the actual values used for the
gamma hyperprior on tau_theta depend on \(\bar m\), which is the average number of
neighbors across all regions in the dataset, which means that they are
dependent on the dataset being analyzed and must be reevaluated for each
new dataset accordingly.
### A Stan Implementation of the BYM Model


A Stan model which implements the BYM model for the Scotland dataset,
i.e., univariate data plus offset, is in the file bym_predictor_plus_offset.stan.
```
writeLines(readLines('bym_predictor_plus_offset.stan'))

// use for Scotland dataset
data {
  int<lower=0> N;
  int<lower=0> N_edges;
  array[N_edges] int<lower=1, upper=N> node1; // node1[i] adjacent to node2[i]
  array[N_edges] int<lower=1, upper=N> node2; // and node1[i] < node2[i]
  
  array[N] int<lower=0> y; // count outcomes
  vector[N] x; // predictor
  vector<lower=0>[N] E; // exposure
}
transformed data {
  vector[N] log_E = log(E);
}
parameters {
  real beta0; // intercept
  real beta1; // slope
  
  real<lower=0> tau_theta; // precision of heterogeneous effects
  real<lower=0> tau_phi; // precision of spatial effects
  
  vector[N] theta; // heterogeneous effects
  vector[N] phi; // spatial effects
}
transformed parameters {
  real<lower=0> sigma_theta = inv(sqrt(tau_theta)); // convert precision to sigma
  real<lower=0> sigma_phi = inv(sqrt(tau_phi)); // convert precision to sigma
}
model {
  y ~ poisson_log(log_E + beta0 + beta1 * x + phi * sigma_phi
                  + theta * sigma_theta);
  
  // NOTE:  no prior on phi_raw, it is used to construct phi
  // the following computes the prior on phi on the unit scale with sd = 1
  target += -0.5 * dot_self(phi[node1] - phi[node2]);
  // soft sum-to-zero constraint on phi)
  sum(phi) ~ normal(0, 0.001 * N); // equivalent to mean(phi) ~ normal(0,0.001)
  
  beta0 ~ normal(0, 5);
  beta1 ~ normal(0, 5);
  theta ~ normal(0, 1);
  tau_theta ~ gamma(3.2761, 1.81); // Carlin WinBUGS priors
  tau_phi ~ gamma(1, 1); // Carlin WinBUGS priors
}
generated quantities {
  vector[N] mu = exp(log_E + beta0 + beta1 * x + phi * sigma_phi
                     + theta * sigma_theta);
}
```


This model builds on the model in file
simple_iar.stan:
- the data block has declarations for the outcome, covariate data, and
exposure data for the Poisson regression.
- a transformed data block is used to put the exposure data on the log
scale
- the set of model parameters now includes the parameters
beta0 and beta1 for the fixed effects slope
and intercept terms, vector theta for ordinary random
effects, and vector phi for spatial random effects, and
precision parameters tau_theta and tau_phi
(following Banerjee et al).
- we use the non-centered parameterization for both the ordinary and
spatial random effects.
- in the model block we put priors on all parameters excepting
phi_std_raw.
### Fitting the Model to the Scotland Lip Cancer Dataset


To test this model with real data, we ran it on the version of the
Scotland Lip Cancer dataset in file scotland_data.R,
described in the previous section. The R script fit_scotland_bym.R
fits the model to the data.
```
library(devtools)
if(!require(cmdstanr)){
  devtools::install_github("stan-dev/cmdstanr", dependencies=c("Depends", "Imports"))
}
library(cmdstanr)   
options(digits=3)

source("mungeCARdata4stan.R")  
source("scotland_data.R")
y = data$y;
x = 0.1 * data$x;
E = data$E;

nbs = mungeCARdata4stan(data$adj, data$num);
N = nbs$N;
node1 = nbs$node1;
node2 = nbs$node2;
N_edges = nbs$N_edges;

data = list(N=N,
            N_edges=N_edges,
            node1=node1,
            node2=node2,
            y=y,
            x=x,
            E=E);

bym_model = cmdstan_model("bym_predictor_plus_offset.stan");

bym_scot_stanfit = bym_model$sample(
         data = data,
         parallel_chains = 4,
     refresh=0);

Running MCMC with 4 parallel chains...

Chain 1 finished in 4.8 seconds.
Chain 2 finished in 4.8 seconds.
Chain 3 finished in 4.8 seconds.
Chain 4 finished in 4.7 seconds.

All 4 chains finished successfully.
Mean chain execution time: 4.8 seconds.
Total execution time: 4.9 seconds.

bym_scot_stanfit$summary(variables = c("lp__", "beta0", "beta1",
                                       "sigma_phi", "tau_phi",
                                       "sigma_theta", "tau_theta",
                                       "mu[5]","phi[5]","theta[5]"));

# A tibble: 10 × 10
   variable       mean  median     sd    mad      q5      q95  rhat ess_bulk
   <chr>         <num>   <num>  <num>  <num>   <num>    <num> <num>    <num>
 1 lp__        756.    756.    8.43   8.42   742.    770.      1.00    1010.
 2 beta0        -0.284  -0.285 0.163  0.156   -0.560  -0.0147  1.00    1346.
 3 beta1         0.419   0.417 0.163  0.162    0.151   0.689   1.00    1431.
 4 sigma_phi     0.669   0.656 0.135  0.133    0.477   0.914   1.00     965.
 5 tau_phi       2.51    2.33  1.02   0.924    1.20    4.39    1.00     965.
 6 sigma_theta   0.478   0.472 0.0672 0.0670   0.379   0.598   1.00    2620.
 7 tau_theta     4.64    4.48  1.29   1.25     2.80    6.97    1.00    2620.
 8 mu[5]        14.1    13.8   3.43   3.26     9.06   20.3     1.00    4760.
 9 phi[5]        1.27    1.26  0.459  0.452    0.538   2.05    1.00    1781.
10 theta[5]      0.411   0.406 0.701  0.707   -0.736   1.56    1.00    3732.
# ℹ 1 more variable: ess_tail <num>
```


The priors on all parameters match the priors on the corresponding
WinBUGS model in the file “Lipsbrad.odc”. To check this model, we use
OpenBUGS and R package R2OpenBugs to fit the WinBUGS version. We have
edited the WinBUGS program so that the variable names match the names
used in the Stan model, also we have changed the parameterization of the
heterogenous random effects component theta to the
non-centered parameterization. Our version of the WinBUGS model is in
file bym_bugs.txt.
The R script fit_scotland_bugs.R
uses OpenBUGS to fit this model.
```
options(digits=2);
sims[1:10, 1:7];
```


WinBUGS and Stan produce compatible estimates of the parameters and
quantities of interest for this model when run on the Scotland dataset.
For this model, the fit is achieved by careful choice of the
hyperpriors, in particular, the choice of the gamma hyperprior on
tau_theta which depends on \(\bar
m\), the average number of neighbors across all regions in the
dataset. These values may not work so well for data with a different
spatial structure.
## BYM2: improving the parameterization of the Besag, York, and Mollié
model


Although the previous section shows that Stan can comfortably fit
disease mapping models, there are some difficulties with the standard
parameterization of the BYM model. In particular, it’s quite challenging
to set sensible priors on the precisions of the structured and
unstructured random effects. While the recommendations of Bernardinelli
et al. (1995) are ok, it’s better to re-state the model in an equivalent
way that removes the problem. To some extent, this is a Bayesian version
of Gelman’s famous “Folk Theorem”: if it’s hard to set priors, then you
model is probably wrong!

In the discussion of disease risk mapping in the original BYM paper,
the spatial and non-spatial random effects are added to the Poisson
model to account for over-dispersion (called “extra-Poisson variation”),
not modelled by the Poisson variates. The use of two components is
motivated by the concern that the the observed variance isn’t fully
explained by the spatial structure of the data. Fitting a model which
includes an ordinary random effects component \(\theta\) as well as a spatial ICAR
component \(\phi\) is difficult because
either component can account for most or all of the individual-level
variance. Riebler et al 2016 provides an excellent summary of the
underlying problem as well as a survey of the subsequent refinements to
the parameterization and choice of priors for this model.

The BYM2 model was proposed by Riebler et al 2016, following Simpson
2014. Like the BYM model, it includes two random effects components, and
like the alternative Leroux (1999) model, it places a single precision
(scale) parameter on the combined components, and a mixing parameter for
the amount of spatial/non-spatial variation. The combined random effects
component for the BYM2 model are written as:

\[\theta + \phi = \sigma
(\sqrt{1-\rho}\theta^* + \sqrt{\rho}\phi^* ),\] where
- \(\sigma\geq 0\) is the
overall standard deviation
- \(\rho \in [0,1]\) models how much
of the variance comes from the spatially structured effect and how much
comes from the spatially unstructured effect
- \(\theta^* \sim N(0,I)\) is the
unstructured random effect with fixed standard deviation \(1\)
- \(\phi^*\) is the ICAR model scaled
so \(\operatorname{Var}(\phi_i) \approx
1\)

In order for \(\sigma\) to
legitimately be the standard deviation of the random effect, it is
critical that, for each \(i\), \(\operatorname{Var}(\theta_i) \approx
\operatorname{Var}(\phi_i) \approx 1\). This is not
automatic for ICAR models, where every component of \(\theta\) will have a different variance.
Riebler et al. (2016) recommend scaling the model so the geometric mean
of these variances is 1. For the elements of \(\phi^*\), this scaling factor is computed
from the adjacency matrix using the R-INLA package’s function
inla.scale.model. With this re-parameterization, it is now
easy to set priors. Following Riebler et al, we recommend:
- A standard prior on the standard deviation such as a half-normal, a
half-t or an exponential.
- A beta(1/2,1/2) prior on \(\rho\).

Riebler et al. also propose a more sophisticated prior on \(\rho\) which accounts for the fact that the
two random effects are different “sizes”. For more information about
this re-parameterization, see Riebler et al. (2016), Dean et al. (2001),
and Wakefield (2007).

The Stan code for this model can be found at bym2.stan
```
writeLines(readLines('bym2.stan'))

data {
  int<lower=0> N;
  int<lower=0> N_edges;
  array[N_edges] int<lower=1, upper=N> node1; // node1[i] adjacent to node2[i]
  array[N_edges] int<lower=1, upper=N> node2; // and node1[i] < node2[i]
  
  array[N] int<lower=0> y; // count outcomes
  vector<lower=0>[N] E; // exposure
  int<lower=1> K; // num covariates
  matrix[N, K] x; // design matrix
  
  real<lower=0> scaling_factor; // scales the variance of the spatial effects
}
transformed data {
  vector[N] log_E = log(E);
}
parameters {
  real beta0; // intercept
  vector[K] betas; // covariates
  
  real<lower=0> sigma; // overall standard deviation
  real<lower=0, upper=1> rho; // proportion unstructured vs. spatially structured variance
  
  vector[N] theta; // heterogeneous effects
  vector[N] phi; // spatial effects
}
transformed parameters {
  vector[N] convolved_re;
  // variance of each component should be approximately equal to 1
  convolved_re = sqrt(1 - rho) * theta + sqrt(rho / scaling_factor) * phi;
}
model {
  y ~ poisson_log(log_E + beta0 + x * betas + convolved_re * sigma); // co-variates
  
  // This is the prior for phi! (up to proportionality)
  target += -0.5 * dot_self(phi[node1] - phi[node2]);
  // soft sum-to-zero constraint on phi
  sum(phi) ~ normal(0, 0.001 * N); // equivalent to mean(phi) ~ normal(0,0.001)
  
  beta0 ~ normal(0.0, 1.0);
  betas ~ normal(0.0, 1.0);
  theta ~ normal(0.0, 1.0);
  sigma ~ normal(0, 1.0);
  rho ~ beta(0.5, 0.5);
}
generated quantities {
  real logit_rho = log(rho / (1.0 - rho));
  vector[N] eta = log_E + beta0 + x * betas + convolved_re * sigma; // co-variates
  vector[N] mu = exp(eta);
}
```


To test this model with real data, we ran it on the version of the
Scotland Lip Cancer dataset in file scotland_data.R,
described in the previous section. The R script fit_scotland.R
fits the model to the data. This code includes details on how to compute
the scaling factor using the INLA library.
```
library(devtools)
if(!require(cmdstanr)){
  devtools::install_github("stan-dev/cmdstanr", dependencies=c("Depends", "Imports"))
}
if(!require(INLA)){
install.packages("INLA",repos=c(getOption("repos"),INLA="https://inla.r-inla-download.org/R/stable"), dep=TRUE)
}
library(cmdstanr)   
library(INLA)

source("mungeCARdata4stan.R")  
source("scotland_data.R")
y = data$y;
x = 0.1 * data$x;
E = data$E;
K = 1;

nbs = mungeCARdata4stan(data$adj, data$num);
N = nbs$N;
node1 = nbs$node1;
node2 = nbs$node2;
N_edges = nbs$N_edges;

#Build the adjacency matrix using INLA library functions
adj.matrix = sparseMatrix(i=nbs$node1,j=nbs$node2,x=1,symmetric=TRUE)
#The ICAR precision matrix (note! This is singular)
Q=  Diagonal(nbs$N, rowSums(adj.matrix)) - adj.matrix
#Add a small jitter to the diagonal for numerical stability (optional but recommended)
Q_pert = Q + Diagonal(nbs$N) * max(diag(Q)) * sqrt(.Machine$double.eps)

# Compute the diagonal elements of the covariance matrix subject to the 
# constraint that the entries of the ICAR sum to zero.
#See the inla.qinv function help for further details.
Q_inv = inla.qinv(Q_pert, constr=list(A = matrix(1,1,nbs$N),e=0))

#Compute the geometric mean of the variances, which are on the diagonal of Q.inv
scaling_factor = exp(mean(log(diag(Q_inv))))

data = list(N=N,
            N_edges=N_edges,
            node1=node1,
            node2=node2,
            y=y,
            x=x,
            E=E,
            scaling_factor=scaling_factor);

bym2_model = cmdstan_model("bym2_predictor_plus_offset.stan");

bym2_scot_stanfit = bym2_model$sample(
                                   data=data,
                                   parallel_chains=4,
                   refresh=0);

Running MCMC with 4 parallel chains...

Chain 3 finished in 4.7 seconds.
Chain 1 finished in 4.8 seconds.
Chain 2 finished in 4.8 seconds.
Chain 4 finished in 4.8 seconds.

All 4 chains finished successfully.
Mean chain execution time: 4.8 seconds.
Total execution time: 4.9 seconds.

bym2_scot_stanfit$summary(variables = c("beta0", "beta1",
                                       "sigma", "rho",
                                       "mu[5]","phi[5]","theta[5]"))

# A tibble: 7 × 10
  variable   mean median     sd    mad     q5      q95  rhat ess_bulk ess_tail
  <chr>     <num>  <num>  <num>  <num>  <num>    <num> <num>    <num>    <num>
1 beta0    -0.217 -0.217 0.129  0.129  -0.431 -0.00570  1.00    1927.    2288.
2 beta1     0.365  0.367 0.134  0.133   0.143  0.583    1.00    2065.    2633.
3 sigma     0.514  0.506 0.0885 0.0863  0.383  0.675    1.00     739.    1341.
4 rho       0.878  0.935 0.144  0.0891  0.572  1.00     1.00     686.    1354.
5 mu[5]    13.8   13.5   3.13   3.01    9.14  19.4      1.00    5079.    3161.
6 phi[5]    1.43   1.41  0.406  0.401   0.789  2.14     1.00    1255.    1820.
7 theta[5]  0.170  0.177 0.959  0.944  -1.41   1.75     1.00    7680.    2894.
```


To see how this re-parameterization affects the fit, we reprint the
above results, showing only the parameters and generated quantities
shared by these two models:
```
bym_scot_stanfit$summary(variables = c("beta0", "beta1", "mu[5]"));

# A tibble: 3 × 10
  variable   mean median    sd   mad     q5     q95  rhat ess_bulk ess_tail
  <chr>     <num>  <num> <num> <num>  <num>   <num> <num>    <num>    <num>
1 beta0    -0.283 -0.284 0.164 0.160 -0.548 -0.0164  1.00    1653.    2312.
2 beta1     0.420  0.420 0.163 0.162  0.150  0.682   1.00    1573.    2372.
3 mu[5]    14.1   13.8   3.39  3.27   9.14  20.2     1.00    4131.    2873.
```


As a further check, we compare the results of using Stan
implementation of the BYM2 model to fit the Scotland lip cancer dataset
with the results obtained by using INLA’s implementation of the BYM2
model. The script to run INLA using package R-INLA is in file fit_scotland_inla_bym2.R.
After fitting the model, we print the values for the fixed effects
parameters, i.e., the slope and intercept terms beta0 and
beta1:
```
> inla_bym2$summary.fixed
                  mean        sd 0.025quant   0.5quant 0.975quant       mode          kld
(Intercept) -0.2215948 0.1265029 -0.4711830 -0.2215091 0.02705429 -0.2214959 1.472228e-08
x            0.3706808 0.1320332  0.1054408  0.3725290 0.62566048  0.3762751 4.162445e-09
```

## Bigger data: from 56 counties in Scotland to 1921 census tracts in
New York City


To demonstrate the scalability of using Stan to compute a spatial
ICAR component, we use data taken from the published study: Small-area
spatiotemporal analysis of pedestrian and bicyclist injuries in New York
City. This dataset was compiled from all reported traffic accidents
involving a car and either a pedestrian or bicyclist in New York City
between 2001 and 2009, localized to the census tract level. We are using
just the 2001 data for total population per census tract and total
number of accidents. Although there are 2168 total census tracts in New
York City, we only have data for 1929 regions, 8 of which aren’t
properly connected to other regions and are therefore omitted for the
sake of simplicity.

The traffic accident data is in the file R dumpfile
nyc_subset.data.R. It contains a list of the 1921 census
tracts IDs used in this study (nyc_tractIDs), the count of
injuries per tract in 2001 (events_2001), and the 2001
population per census tract (pop_2001).
```
load("nyc_subset.data.R");
plot(log(pop_2001),events_2001,xlab="log(population)",ylab="observed events", pch=20);
```


The Stan program is in the file bym2_offset_only.stan.
This program implements the BYM model for a Poisson regression with no
covariates, only an offset term.

Spatial information is in a set of files in directory
nycTracts10. The spatial information for the census tracts
is obtained via the R maptools and spdep
packages. We use these packages to create an nb object
which is a list of all neighbors for each census tract. Each list entry
is itself a list containing the relative index of the neighboring
regions. We have written a set of R helper functions nb_data_funs.R.
The function nb2graph takes an nb object as
input and returns a list containing the input data objects
N, N_edges, node1, and
node2. The function scale_nb_components takes
an nb object as input and returns a vector of scaling
factors for all graph components. For this case study, we are working
with a fully connected neighborhood graph, therefore this function
returns a vector of length 1.

The script fit_nyc_bym2.R
fits the BYM2 Stan model to the 2001 NYC traffic accident data and saves
the resulting stanfit object as an R dumpfile.
```
library(maptools);
library(spdep);
library(rgdal)
library(cmdstanr);

load("nyc_subset.data.R");

nyc_shp<-readOGR("nycTracts10", layer="nycTracts10");

OGR data source with driver: ESRI Shapefile 
Source: "/Users/mitzi/github/stan-dev/example-models/knitr/car-iar-poisson/nycTracts10", layer: "nycTracts10"
with 2168 features
It has 14 fields
Integer64 fields read as strings:  ALAND10 AWATER10 

geoids <- nyc_shp$GEOID10 %in% nyc_tractIDs;
nyc_subset_shp <- nyc_shp[geoids,];
nyc_subset_shp <- nyc_subset_shp[order(nyc_subset_shp$GEOID10),];
nb_nyc_subset = poly2nb(nyc_subset_shp);

y = events_2001
E = pop_2001;
## set pop > 0 so we can use log(pop) as offset
E[E < 10] = 10;

source("nb_data_funs.R");
nbs=nb2graph(nb_nyc_subset);
N = nbs$N;
node1 = nbs$node1;
node2 = nbs$node2;
N_edges = nbs$N_edges;
scaling_factor = scale_nb_components(nb_nyc_subset)[1];

data = list(N=N,
            N_edges=N_edges,
            node1=node1,
            node2=node2,
            y=y,
            E=E,
            scaling_factor=scaling_factor);

bym2_model = cmdstan_model("bym2_offset_only.stan");
bym2_fit = bym2_model$sample(data=data, parallel_chains=4, refresh=0);

Running MCMC with 4 parallel chains...

Chain 4 finished in 53.0 seconds.
Chain 2 finished in 53.1 seconds.
Chain 3 finished in 53.9 seconds.
Chain 1 finished in 54.2 seconds.

All 4 chains finished successfully.
Mean chain execution time: 53.5 seconds.
Total execution time: 54.3 seconds.

bym2_fit$summary(
             variables = c(
                 "beta0", "rho", "sigma",
                 "mu[1]", "mu[2]", "mu[3]", "mu[500]", "mu[1000]", "mu[1500]", "mu[1900]",
                 "phi[1]", "phi[2]", "phi[3]", "phi[500]", "phi[1000]", "phi[1500]", "phi[1900]",
                 "theta[1]", "theta[2]", "theta[3]", "theta[500]", "theta[1000]", "theta[1500]", "theta[1900]"));

# A tibble: 24 × 10
   variable   mean median     sd    mad     q5    q95  rhat ess_bulk ess_tail
   <chr>     <num>  <num>  <num>  <num>  <num>  <num> <num>    <num>    <num>
 1 beta0    -6.61  -6.61  0.0232 0.0239 -6.65  -6.57   1.00    2614.    3069.
 2 rho       0.540  0.542 0.0400 0.0408  0.472  0.602  1.01     274.     712.
 3 sigma     1.18   1.18  0.0335 0.0338  1.13   1.24   1.01     401.     941.
 4 mu[1]     1.43   1.21  0.966  0.816   0.334  3.31   1.00    7798.    2934.
 5 mu[2]     1.62   1.39  1.02   0.853   0.445  3.56   1.00    8974.    3177.
 6 mu[3]     0.903  0.738 0.641  0.482   0.211  2.14   1.00    7406.    3457.
 7 mu[500]  21.5   21.1   4.45   4.35   14.6   29.3    1.00    4258.    2706.
 8 mu[1000]  1.71   1.48  1.03   0.872   0.513  3.68   1.00    7397.    3172.
 9 mu[1500]  2.22   1.98  1.20   1.06    0.716  4.53   1.00    7807.    3246.
10 mu[1900]  1.00   0.794 0.757  0.559   0.214  2.46   1.00    5466.    3132.
# ℹ 14 more rows

save(bym2_fit, file="nyc_bym2_fit.data.R");
```


The Rhat values indicate good convergences, and the n_eff numbers,
while low for rho and sigma, are
sufficient.
### Visual comparisons of data and model fits


We use maptools, ggplot2 and related
packages to visualize the data and the model fits for a simple Poisson
GLM, a Poisson GLM with a simple random effects component, a Poisson GLM
with just an ICAR spatial smoothing component, and the BYM2 model.
#### New York City data


The data subset that we are using for this case study is limited to
1921 out of a total of 2168 census tract regions. To see the neighbor
relations between these census tracts we use the maptools,
spdep, ggplot2, and ggmap
packages to overlay the neighborhood graph on top of the Google Maps
terrain map for New York city:


Included among the census tracts for which there is accident data are
several large parks and cemetaries, among them Central Park, and
Prospect Park and Greenwood Cemetary in Brooklyn. In the following zoom
of the above neighborhood map we’re drawn a circle around Prospect
Park:


In the following plot, the left panel shows the 2001 log population
per census tract and the right panel shows the raw number of 2001
events.


While parks are low-population areas, they have a high number of
recorded events. To see this, we again zoom in on Brooklyn:


Note that Greenwood Cemetary, the large tract slightly below (SE) of
Prospect Park is both unpopulated and uneventful.
#### Baseline model: a simple Poisson GLM


First we strip out the spatial and random effects components from the
BYM2 model and simply fit a Poisson GLM to this data. The Stan model
is:
```
writeLines(readLines('pois.stan'))

data {
  int<lower=0> N;
  array[N] int<lower=0> y; // count outcomes
  vector<lower=0>[N] E; // exposure
}
transformed data {
  vector[N] log_E = log(E);
}
parameters {
  real beta0; // intercept
}
model {
  y ~ poisson_log(log_E + beta0); // intercept only, no covariates
  beta0 ~ normal(0.0, 2.5);
}
generated quantities {
  vector[N] eta = log_E + beta0;
  vector[N] mu = exp(eta);
}
```


The script fit_nyc_pois.R
compiles and runs the model.

We show side-by-side plots for the raw number of events (left panel)
and Poisson fit (right panel) for all boroughs and just Brooklyn:


#### Adding a vector of random effects (heterogeneous variation
only)


Adding an ordinary random effects component allows us to fit the
model nicely. The Stan model is:
```
writeLines(readLines('pois_re.stan'))

data {
  int<lower=0> N;
  array[N] int<lower=0> y; // count outcomes
  vector<lower=0>[N] E; // exposure
}
transformed data {
  vector[N] log_E = log(E);
}
parameters {
  real beta0; // intercept
  vector[N] theta; // heterogeneous random effects
  real<lower=0> sigma; // non-centered re variance 
}
model {
  y ~ poisson_log(log_E + beta0 + theta * sigma);
  beta0 ~ normal(0.0, 2.5);
  theta ~ normal(0, 1);
  sigma ~ normal(0, 5);
}
generated quantities {
  vector[N] eta = log_E + beta0 + theta * sigma;
  vector[N] mu = exp(eta);
}
```


The script fit_nyc_pois_re.R
compiles and runs the model. The side-by-side plots of raw number of
events (left panel) and the fitted model (right panel) are almost
identical:


#### Adding an ICAR component (spatial smoothing only)


We add an ICAR component to the Poisson regression:
```
writeLines(readLines('pois_icar.stan'))

functions {
  real icar_normal_lpdf(vector phi, int N, array[] int node1,
                        array[] int node2) {
    return -0.5 * dot_self(phi[node1] - phi[node2]);
  }
}
data {
  int<lower=0> N;
  int<lower=0> N_edges;
  array[N_edges] int<lower=1, upper=N> node1; // node1[i] adjacent to node2[i]
  array[N_edges] int<lower=1, upper=N> node2; // and node1[i] < node2[i]
  
  array[N] int<lower=0> y; // count outcomes
  vector<lower=0>[N] x; // coefficient
  vector<lower=0>[N] E; // exposure
}
transformed data {
  vector[N] log_E = log(E);
}
parameters {
  real beta0; // intercept
  real beta1; // slope
  real<lower=0> sigma; // overall standard deviation
  vector[N] phi; // spatial effects
}
model {
  y ~ poisson_log(log_E + beta0 + beta1 * x + phi * sigma);
  beta0 ~ normal(0.0, 1.0);
  beta1 ~ normal(0.0, 1.0);
  sigma ~ normal(0.0, 1.0);
  phi ~ icar_normal(N, node1, node2);
  // soft sum-to-zero constraint on phi
  // more efficient than mean(phi) ~ normal(0, 0.001)
  sum(phi) ~ normal(0, 0.001 * N);
}
generated quantities {
  vector[N] eta = log_E + beta0 + beta1 * x + phi * sigma;
  vector[N] mu = exp(eta);
}
```


The script fit_nyc_pois_icar.R
compiles and runs the model. The side-by-side plots of raw number of
events (left panel) and the fitted model (right panel) differ in a few
places, particularly Central and Prospect Parks. Because these parks
have many neighboring small-count regions, the fitted model brings the
event level down significantly. In the Brooklyn plot, in the NE (upper
right), a few medium-count tracts in the East New York/ Brownsville
areas are upweighted:


#### Visualizing the fitted BYM2 model for New York City and
Brooklyn


Finally, we plot the fitted BYM2 model for all boroughs and just
Brooklyn. In comparison with the previous plots, for the BYM2 model the
differences between the data and the fitted model are greater than for
the model pois_icar.stan and less than for the model
pois_re.stan.


## Discussion


In this case study we have shown how to efficiently encode and
compute an ICAR component. To efficiently store the neighborhood
structure, we encode the spatial adjacency matrix as an array of edges
of an undirected graph instead of using a large square matrix. The
pairwise difference for adjacent areal units can be expressed as a
single statement using the Stan’s multiple indexing feature and the math
library’s dot-self function which provides efficient
computation of the sum of squares. The improper nature of the ICAR
component means that it can only be used as a prior, not a likelihood.
In order to make the ICAR component identifiable, we use a sum-to-zero
constraint.

The BYM model convolves both a spatial ICAR component and a
heterogeneous random effects component. There are many variants of this
model which differ in the parameterization of these two components. This
model is difficult for an MCMC sampler to fit unless there are strong
hyperpriors on the scale of each component. Here we follow Riebler et al
2016 in choosing to use a mixing parameter rho and a
scaling factor which is derived from the structure of the neighborhood
graph, in order to determine the amount of spatial structure present in
the data.

The data subset that we are using for this case study is limited to
1921 out of a total of 2168 census tract regions. This subset is a few
column’s worth of data taken from a study which focussed on child
safety, and both the population and accident data had been stratified
into age brackets. Using just the total population and total number of
accidents provides very little information with which to fit a model.
But we’re not trying to come up with policy solutions, we’re trying to
get a feel for what the components of these models do, and from this
perspective, working with almost no data is ideal, because a few
anomalous situations, in particular, accidents which occur in parks,
provide good illustrations of how ICAR models provide spatial
smoothing.
## Acknowledgements


Daniel Simpson contributed the section “A better parameterization of
the Besag, York, and Mollié model”. Many thanks to Imad Ali, Michael
Betancourt, Bob Carpenter, Andrew Gelman, and Rob Trangucci for all
their help and encouragement, as well as to Miguel A. Martínez Beneito
and Paqui Corpas of FISABIO, Valencia Spain.

Funded in part by the National Institute of Child Health and Human
Development, grant number 1R01HD087460-01, Charles DiMaggio Principal
Investigator.
## References

### Literature

- 

Banerjee, Sudipto, Alan E. Gelfand, and Bradley P. Carlin.
“Hierarchical modeling and analysis for spatial data.” (2003).
- 

Bernardinelli, L., Clayton, D. and Montomoli, C. (1995). Bayesian
estimates of disease maps: How important are priors? Statistics in
Medicine 14 2411–2431.
- 

Besag, Julian. “Spatial interaction and the statistical analysis
of lattice systems.” Journal of the Royal Statistical Society. Series B
(Methodological) (1974): 192-236.
- 

Besag, Julian, and Charles Kooperberg. “On conditional and
intrinsic autoregression.” Biometrika (1995): 733-746.
- 

Besag, J., J. York, and A. Mollie. “Bayesian image restoration
with two applications in spatial statistics (with discussion) Ann Inst
Stat Math. 1991; 43: 1–59. doi: 10.1007.” BF00116466.[Cross
Ref].
- 

Dean, C. B., Ugarte, M. D. and Militino, A. F. (2001). Detecting
interaction between random region and fixed age effects in disease
mapping. Biometrics 57 197–202.
- 

Haran, Murali. “Gaussian random field models for spatial data.”
Handbook of Markov Chain Monte Carlo (2011): 449-478.
- 

Riebler, Andrea, Sigrunn H. Sørbye, Daniel Simpson, and Håvard
Rue. “An intuitive Bayesian spatial model for disease mapping that
accounts for scaling.” Statistical methods in medical research 25, no. 4
(2016): 1145-1165.
- 

Wakefield, J. (2007). Disease mapping and spatial regression with
count data. Biostatistics 8 158–183.
#### R Packages

- 

Statistics: CmdStanR,
R2OpenBugs,
OpenBUGS, R-INLA.
- 

Plots and supporting libraries: ggplot2, ggmap, dplyr, tidy
- 

Spatial Data: maptools, spdep, rgdal
### Licenses


Code: Copyright (2018-2023) Columbia
University. Released under the BSD 3-clause
license. 

Text: Copyright (2018-2023) Mitzi Morris.
Released under the the CC BY-NC 4.0
license. 
