> Source: https://mc-stan.org/learn-stan/case-studies/golf.html

Model building and expansion for golf putting
# Model building and expansion for golf
putting

#### Andrew Gelman

#### 24 Sep 2019


The following graph shows data from professional golfers on the
proportion of successful putts as a function of distance from the hole.
Unsurprisingly, the probability of making the shot declines as a
function of distance:


The error bars associated with each point \(j\) in the above graph are simple classical
standard deviations, \(\sqrt{\hat{p}_j(1-\hat{p}_j)/n_j}\), where
\(\hat{p}_j=y_j/n_j\) is the success
rate for putts taken at distance \(x_j\).
### Logistic regression


Can we model the probability of success in golf putting as a function
of distance from the hole? Given usual statistical practice, the natural
starting point would be logistic regression:

\[
y_j\sim\mbox{binomial}(n_j, \mbox{logit}^{-1}(a + bx_j)),
\mbox{ for } j=1,\dots, J.
\] In Stan, this is:
```
data {
  int J;
  array[J] int n;
  vector[J] x;
  array[J] int y;
}
parameters {
  real a;
  real b;
}
model {
  y ~ binomial_logit(n, a + b * x);
}
```


The code in the above model block is (implicitly) vectorized, so that
it is mathematically equivalent to modeling each data point,
y[i] ~ binomial_logit(n[i], a + b*x[i]). The vectorized
code is more compact (no need to write a loop, or to include the
subscripts) and faster (because of more efficient gradient
evaluations).

We fit the model to the data:
```
golf_data <- list(x=x, y=y, n=n, J=J)
fit_logistic <- stan("golf_logistic.stan", data=golf_data)
a_sim <- extract(fit_logistic)$a
b_sim <- extract(fit_logistic)$b
```


And here is the result:
```
Inference for Stan model: anon_model.
4 chains, each with iter=2000; warmup=1000; thin=1; 
post-warmup draws per chain=1000, total post-warmup draws=4000.

   mean se_mean   sd   25%   50%   75% n_eff Rhat
a  2.23       0 0.06  2.20  2.23  2.27  1346    1
b -0.26       0 0.01 -0.26 -0.26 -0.25  1369    1

Samples were drawn using NUTS(diag_e) at Tue Sep 12 13:17:49 2023.
For each parameter, n_eff is a crude measure of effective sample size,
and Rhat is the potential scale reduction factor on split chains (at 
convergence, Rhat=1).
```


Going through the columns of the above table: Stan has computed the
posterior means \(\pm\) standard
deviations of \(a\) and \(b\) to be 2.23 \(\pm\) 0.06 and -0.26 \(\pm\) 0.01, respectively. The Monte Carlo
standard error of the mean of each of these parameters is 0 (to two
decimal places), indicating that the simulations have run long enough to
estimate the posterior means precisely. The posterior quantiles give a
sense of the uncertainty in the parameters, with 50% posterior intervals
of [2.20, 2.27] and [-0.26, -0.25] for \(a\) and \(b\), respectively. Finally, the values of
\(\widehat{R}\) near 1 tell us that the
simulations from Stan’s four simulated chains have mixed well. (We have
more sophisticated convergence diagnostics, and also we recommend
checking the fit using simulated data, as discussed in the Bayesian
Workflow Using Stan book, but checking that \(\widehat{R}\) is near 1 is a good
start.)

The following graph shows the fit plotted along with the data:


The black line shows the fit corresponding to the posterior median
estimates of the parameters \(a\) and
\(b\); the green lines show 10 draws
from the posterior distribution.

In this example, posterior uncertainties in the fits are small, and
for simplicity we will just plot point estimates based on posterior
median parameter estimates for the remaining models. Our focus here is
on the sequence of models that we fit, not so much on uncertainty in
particular model fits.
### Modeling from first principles


As an alternative to logistic regression, we shall build a model from
first principles and fit it to the data.

The graph below shows a simplified sketch of a golf shot. The dotted
line represents the angle within which the ball of radius \(r\) must be hit so that it falls within the
hole of radius \(R\). This threshold
angle is \(\sin^{-1}((R-r)/x)\). The
graph, which is not to scale, is intended to illustrate the geometry of
the ball needing to go into the hole.


The next step is to model human error. We assume that the golfer is
attempting to hit the ball completely straight but that many small
factors interfere with this goal, so that the actual angle follows a
normal distribution centered at 0 with some standard deviation \(\sigma\).


The probability the ball goes in the hole is then the probability
that the angle is less than the threshold; that is, \(\mbox{Pr}\left(|\mbox{angle}| <
\sin^{-1}((R-r)/x)\right) =
2\Phi\left(\frac{\sin^{-1}((R-r)/x)}{\sigma}\right) - 1\), where
\(\Phi\) is the cumulative normal
distribution function. The only unknown parameter in this model is \(\sigma\), the standard deviation of the
distribution of shot angles. Stan (and, for that matter, R) computes
trigonometry using angles in radians, so at the end of our calculations
we will need to multiply by \(180/\pi\)
to convert to degrees, which are more interpretable by humans.

Our model then has two parts: \[\begin{align}
y_j &\sim \mbox{binomial}(n_j, p_j)\\
p_j &= 2\Phi\left(\frac{\sin^{-1}((R-r)/x_j)}{\sigma}\right) - 1 ,
\mbox{ for } j=1,\dots, J.
\end{align}\] Here is a graph showing the curve for some
potential values of the parameter \(\sigma\).


The highest curve on the graph corresponds to \(\sigma=0.5^\circ\): if golfers could
control the angles of their putts to an accuracy of approximately half a
degree, they would have a very high probability of success, making over
80% of their ten-foot putts, over 50% of their fifteen-foot putts, and
so on. At the other extreme, the lowest plotted curve corresponds to
\(\sigma=20^\circ\): if your putts
could be off as high as 20 degrees, then you would be highly inaccurate,
missing more than half of your two-foot putts. When fitting the model in
Stan, the program moves around the space of \(\sigma\), sampling from the posterior
distribution.

We now write the Stan model in preparation to estimating \(\sigma\):
```
data {
  int J;
  array[J] int n;
  vector[J] x;
  array[J] int y;
  real r;
  real R;
}
transformed data {
  vector[J] threshold_angle = asin((R - r) ./ x);
}
parameters {
  real<lower=0> sigma;
}
model {
  vector[J] p = 2 * Phi(threshold_angle / sigma) - 1;
  y ~ binomial(n, p);
}
generated quantities {
  real sigma_degrees = sigma * 180 / pi();
}
```


In the transformed data block above, the ./ in the
calculation of p corresponds to componentwise division in this
vectorized computation.

The data \(J,n,x,y\) have already
been set up; we just need to define \(r\) and \(R\) (the golf ball and hole have diameters
1.68 and 4.25 inches, respectively), and run the Stan model:
```
r <- (1.68/2)/12
R <- (4.25/2)/12
golf_data <- c(golf_data, r=r, R=R)
fit_trig <- stan("golf_angle.stan", data=golf_data)
sigma_sim <- extract(fit_trig)$sigma
sigma_degrees_sim <- extract(fit_trig)$sigma_degrees
```


Here is the result:
```
Inference for Stan model: anon_model.
4 chains, each with iter=2000; warmup=1000; thin=1; 
post-warmup draws per chain=1000, total post-warmup draws=4000.

              mean se_mean   sd  25%  50%  75% n_eff Rhat
sigma         0.03       0 0.00 0.03 0.03 0.03  1352    1
sigma_degrees 1.53       0 0.02 1.51 1.53 1.54  1352    1

Samples were drawn using NUTS(diag_e) at Tue Sep 12 13:18:35 2023.
For each parameter, n_eff is a crude measure of effective sample size,
and Rhat is the potential scale reduction factor on split chains (at 
convergence, Rhat=1).
```


The model has a single parameter, \(\sigma\). From the output, we find that
Stan has computed the posterior mean of \(\sigma\) to be 0.03. Multiplying this by
\(180/\pi\), this comes to 1.53
degrees. The Monte Carlo standard error of the mean is 0 (to two decimal
places), indicating that the simulations have run long enough to
estimate the posterior mean precisely. The posterior standard deviation
is calculated at 0.02 degrees, indicating that \(\sigma\) itself has been estimated with
high precision, which makes sense given the large number of data points
and the simplicity of the model. The precise posterior distribution of
\(\sigma\) can also be seen from the
narrow range of the posterior quantiles. Finally, \(\widehat{R}\) is near 1, telling us that
the simulations from Stan’s four simulated chains have mixed well.

We next plot the data and the fitted model (here using the posterior
median of \(\sigma\) but in this case
the uncertainty is so narrow that any reasonable posterior summary would
give essentially the same result), along with the logistic regression
fitted earlier:


The custom nonlinear model fits the data much better. This is not to
say that the model is perfect—any experience of golf will reveal that
the angle is not the only factor determining whether the ball goes in
the hole—but it seems like a useful start, and it is good to know that
we can fit nonlinear models by just coding them up in Stan.
### Testing the fitted model on new data


Recently a local business school professor and golfer, Mark Broadie,
came by my office with tons of new data. For simplicity we’ll just look
here at the summary data, probabilities of the ball going into the hole
for shots up to 75 feet from the hole. The graph below shows these new
data (in red), along with our earlier dataset (in blue) and the
already-fit geometry-based model from before, extending to the range of
the new data.


Comparing the two datasets in the range 0-20 feet, the success rate
is similar for longer putts but is much higher than before for the short
putts. This could be a measurement issue, if the distances to the hole
are only approximate for the old data, and it could also be that golfers
are better than they used to be.

Beyond 20 feet, the empirical success rates become lower than would
be predicted by the old model. These are much more difficult attempts,
even after accounting for the increased angular precision required as
distance goes up.
### A new model accounting for how hard the ball is
hit


To get the ball in the hole, the angle isn’t the only thing you need
to control; you also need to hit the ball just hard enough.

Mark Broadie added this to our model by introducing another parameter
corresponding to the golfer’s control over distance. Supposing \(u\) is the distance that golfer’s shot
would travel if there were no hole, Broadie assumes that the putt will
go in if (a) the angle allows the ball to go over the hole, and (b)
\(u\) is in the range \([x,x+3]\). That is the ball must be hit
hard enough to reach the whole but not go too far. Factor (a) is what we
have considered earlier; we must now add factor (b).

The following sketch, which is not to scale, illustrates the need for
the distance as angle as well as the angle of the shot to be in some
range, in this case the gray zone which represents the trajectories for
which the ball would reach the hole and stay in it.


Broadie supposes that a golfer will aim to hit the ball one foot past
the hole but with a multiplicative error in the shot’s potential
distance, so that \(u = (x+1)\cdot (1 +
\mbox{error})\), where the error has a normal distribution with
mean 0 and standard deviation \(\sigma_{\rm
distance}\). This new parameter \(\sigma_{\rm distance}\) represents the
uncertainty in the shot’s relative distance. In statistics notation,
this model is, \[u \sim \mbox{normal}\,(x+1,
(x+1)\,\sigma_{\rm distance}),\] and the distance is acceptable
if \(u\in [x, x+3]\), an event that has
probability \(\Phi\left(\frac{2}{(x+1)\,\sigma_{\rm
distance}}\right) - \Phi\left(\frac{-1}{(x+1)\,\sigma_{\rm
distance}}\right)\).

Putting these together, the probability a shot goes in becomes, \(\left(2\Phi\left(\frac{\sin^{-1}((R-r)/x)}{\sigma_{\rm
angle}}\right) - 1\right)\left(\Phi\left(\frac{2}{(x+1)\,\sigma_{\rm
distance}}\right) - \Phi\left(\frac{-1}{(x+1)\,\sigma_{\rm
distance}}\right)\right)\), where we have renamed the parameter
\(\sigma\) from our earlier model to
\(\sigma_{\rm angle}\) to distinguish
it from the new \(\sigma_{\rm
distance}\) parameter. We write the new model in Stan, giving it
the name golf_angle_distance_2.stan to convey that it is
the second model in a series, and that it accounts both for angle and
distance:
```
data {
  int J;
  array[J] int n;
  vector[J] x;
  array[J] int y;
  real r;
  real R;
  real overshot;
  real distance_tolerance;
}
transformed data {
  vector[J] threshold_angle = asin((R - r) ./ x);
}
parameters {
  real<lower=0> sigma_angle;
  real<lower=0> sigma_distance;
}
model {
  vector[J] p_angle = 2 * Phi(threshold_angle / sigma_angle) - 1;
  vector[J] p_distance = Phi((distance_tolerance - overshot)
                             ./ ((x + overshot) * sigma_distance))
                         - Phi((-overshot)
                               ./ ((x + overshot) * sigma_distance));
  vector[J] p = p_angle .* p_distance;
  y ~ binomial(n, p);
  [sigma_angle, sigma_distance] ~ normal(0, 1);
}
generated quantities {
  real sigma_degrees = sigma_angle * 180 / pi();
}
```


Here we have defined overshot and
distance_tolerance as data, which Broadie has specified as
1 and 3 feet, respectively. We might wonder why if the distance range is
3 feet, the overshot is not 1.5 feet. One reason could be that it is
riskier to hit the ball too hard than too soft. In addition we assigned
weakly informative half-normal(0,1) priors on the scale parameters,
\(\sigma_{\rm angle}\) and \(\sigma_{\rm distance}\), which are required
in this case to keep the computations stable.
### Fitting the new model to data


We fit the model to the new dataset.
```
Warning: There were 1755 divergent transitions after warmup. See
https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
to find out why this is a problem and how to eliminate them.

Warning: There were 1 chains where the estimated Bayesian Fraction of Missing Information was low. See
https://mc-stan.org/misc/warnings.html#bfmi-low

Warning: Examine the pairs() plot to diagnose sampling problems

Warning: The largest R-hat is 2.77, indicating chains have not mixed.
Running the chains for more iterations may help. See
https://mc-stan.org/misc/warnings.html#r-hat

Warning: Bulk Effective Samples Size (ESS) is too low, indicating posterior means and medians may be unreliable.
Running the chains for more iterations may help. See
https://mc-stan.org/misc/warnings.html#bulk-ess

Warning: Tail Effective Samples Size (ESS) is too low, indicating posterior variances and tail quantiles may be unreliable.
Running the chains for more iterations may help. See
https://mc-stan.org/misc/warnings.html#tail-ess
```


There is poor convergence, and we need to figure out what is going on
here. (Problems with computation often indicate underlying problems with
the model being fit. That’s the folk theorem of statistical
computing.)
```
Inference for Stan model: anon_model.
4 chains, each with iter=2000; warmup=1000; thin=1; 
post-warmup draws per chain=1000, total post-warmup draws=4000.

               mean se_mean   sd  25%  50%  75% n_eff  Rhat
sigma_angle    0.03    0.01 0.02 0.01 0.03 0.05     2 62.24
sigma_distance 0.11    0.02 0.02 0.09 0.10 0.14     2  7.89
sigma_degrees  1.75    0.69 0.98 0.76 1.84 2.73     2 62.24

Samples were drawn using NUTS(diag_e) at Tue Sep 12 13:19:31 2023.
For each parameter, n_eff is a crude measure of effective sample size,
and Rhat is the potential scale reduction factor on split chains (at 
convergence, Rhat=1).
```


To understand what is happening, we graph the new data and the fitted
model, accepting that this “fit,” based as it is on poorly-mixing
chains, is only provisional:


There are problems with the fit in the middle of the range of \(x\). We suspect this is a problem with the
binomial error model, as it tries harder to fit points where the counts
are higher. Look at how closely the fitted curve hugs the data at the
very lowest values of \(x\).

Here are the first few rows of the data:
```
print(golf_new[1:5,])

     x      n      y
1 0.28  45198  45183
2 0.97 183020 182899
3 1.93 169503 168594
4 2.92 113094 108953
5 3.93  73855  64740
```


With such large values of \(n_j\),
the binomial likelihood enforces an extremely close fit at these first
few points, and that drives the entire fit of the model.

To fix this problem we took the data model, \(y_j \sim \mbox{binomial}(n_j, p_j)\), and
added an independent error term to each observation. There is no easy
way to add error directly to the binomial distribution—we could replace
it with its overdispersed generalization, the beta-binomial, but this
would not be appropriate here because the variance for each data point
\(i\) would still be roughly
proportional to the sample size \(n_j\), and our whole point here is to get
away from this assumption and allow for model misspecification—so
instead we first approximate the binomial data distribution by a normal
and then add independent variance; thus: \[y_j/n_j \sim \mbox{normal}\left(p_j,
\sqrt{p_j(1-p_j)/n_j + \sigma_y^2}\right),\] To write this in
Stan there are some complications:
- 

\(y\) and \(n\) are integer variables, which we convert
to vectors so that we can multiply and divide them.
- 

To perform componentwise multiplication or division using
vectors, you need to use .* or ./ so that San
knows not to try to perform vector/matrix multiplication and division.
Stan is opposite from R in this way: Stan defaults to vector/matrix
operations and has to be told otherwise, whereas R defaults to
componentwise operations, and vector/matrix multiplication in R is
indicated using the %*% operator.

We implement these via the following new code in the transformed data
block:
```
  vector[J] raw_proportions = to_vector(y) ./ to_vector(n);
```


And then in the model block:
```
  raw_proportions ~ normal(p, sqrt(p .* (1-p) ./ to_vector(n) + sigma_y^2));
```


To complete the model we add \(\sigma_y\) to the parameters block and
assign it a weakly informative half-normal(0,1) prior distribution.
Here’s the new Stan program:
```
data {
  int J;
  array[J] int n;
  vector[J] x;
  array[J] int y;
  real r;
  real R;
  real overshot;
  real distance_tolerance;
}
transformed data {
  vector[J] threshold_angle = asin((R - r) ./ x);
  vector[J] raw_proportions = to_vector(y) ./ to_vector(n);
}
parameters {
  real<lower=0> sigma_angle;
  real<lower=0> sigma_distance;
  real<lower=0> sigma_y;
}
model {
  vector[J] p_angle = 2 * Phi(threshold_angle / sigma_angle) - 1;
  vector[J] p_distance = Phi((distance_tolerance - overshot)
                             ./ ((x + overshot) * sigma_distance))
                         - Phi((-overshot)
                               ./ ((x + overshot) * sigma_distance));
  vector[J] p = p_angle .* p_distance;
  raw_proportions ~ normal(p,
                           sqrt(p .* (1 - p) ./ to_vector(n) + sigma_y ^ 2));
  [sigma_angle, sigma_distance, sigma_y] ~ normal(0, 1);
}
generated quantities {
  real sigma_degrees = sigma_angle * 180 / pi();
}
```


We now fit this model to the data:
```
Inference for Stan model: anon_model.
4 chains, each with iter=2000; warmup=1000; thin=1; 
post-warmup draws per chain=1000, total post-warmup draws=4000.

                mean se_mean    sd   25%   50%   75% n_eff  Rhat
sigma_angle    0.018       0 0.000 0.018 0.018 0.018  1582 1.000
sigma_distance 0.080       0 0.001 0.079 0.080 0.081  1574 1.001
sigma_y        0.003       0 0.001 0.003 0.003 0.003  1689 1.001
sigma_degrees  1.020       0 0.006 1.016 1.020 1.024  1582 1.000

Samples were drawn using NUTS(diag_e) at Tue Sep 12 13:20:24 2023.
For each parameter, n_eff is a crude measure of effective sample size,
and Rhat is the potential scale reduction factor on split chains (at 
convergence, Rhat=1).
```


The new parameter estimates are:
- 

\(\sigma_{\rm angle}\) is
estimated at 0.02, which when corresponds to \(\sigma_{\rm degrees}=\) 1.0. According to
the fitted model, there is a standard deviation of 1.0 degree in the
angles of putts taken by pro golfers. The estimate of \(\sigma_{\rm angle}\) has decreased compared
to the earlier model that only had angular errors. This makes sense: now
that distance errors have been included in the model, there is no need
to explain so many of the missed shots using errors in angle.
- 

\(\sigma_{\rm distance}\) is
estimated at 0.08. According to the fitted model, there is a standard
deviation of 8% in the errors of distance.
- 

\(\sigma_y\) is estimated at
0.003. The fitted model fits the aggregate data (success rate as a
function of distance) to an accuracy of 0.3 percentage points.

And now we graph:


We can go further and plot the residuals from this fit. First we
augment the Stan model to compute residuals in the generated quantities
block.

Then we compute the posterior means of the residuals, \(y_j/n_j - p_j\), then plot these
vs. distance:


The residuals are small (see the scale of the \(y\)-axis) and show no clear pattern,
suggesting not that the model is perfect but that there are no clear
ways to develop it further just given the current data.
### Problems with the model and potential
improvements


The error term in the above model is a hack. It’s useful to allow the
model not to fit the data perfectly, but it can’t be right to model
these systematic errors as being independent. In this case, though, it
doesn’t really matter, given how tiny these errors are: their estimated
standard deviation is less than one percentage point.

The model has two parameters that were fixed as data:
distance_tolerance, which was set to 3 (implying that the
ball will only fall into the hole if it is hit on a trajectory that
would go past the hole, but no more than 3 feet past) and
overshot, which was set to 1 (implying that the golfer will
aim 1 foot past the hole). In theory it would be possible to estimate
either or both these parameters from the data. In practice, no way. The
model already fits the data so well (as shown by the above graph) that
there’s clearly no more information available to estimate any additional
parameters. If we were to do so, the estimates would be highly noisy and
unstable (if their prior is weak) or highly dependent on the prior (if
an informative prior distribution is specified). Either way we don’t see
the advantage of this sort of fit.

Just for laughs, though, we constructed such a model and fit it, just
to see what would happen. We simply took our previous Stan program and
moved these two parameters from the data block to the parameters block
along with zero-boundary constraints:
```
  real<lower=0> overshot;
  real<lower=0> distance_tolerance;
```


And then in the model block we added weak priors centered at
Broadie’s guesses and with wide uncertainties:
```
  overshot ~ normal(1, 5);
  distance_tolerance ~ normal(3, 5);
```


Fitting this model to the data yields poor convergence and no real
gain beyond the simpler version already fit in which overshot and
distance_tolerance were set to fixed values.

The model is unrealistic in other ways, for example by assuming
distance error is strictly proportional to distance aimed, and assuming
independence of angular and distance errors. Presumably, angular error
is higher for longer putts. Again, though, we can’t really investigate
such things well using these data which are already such a good fit to
the simple two-parameter model we have already fit.

Players vary in ability and golf courses vary in difficulty. Given
more granular data, we should be able to fit a multilevel model allowing
parameters to vary by player, golf course, and weather conditions.
## Summary of fitted models


We have two datasets, golf and golf_new, to
which we fit several Stan models. First we fit
golf_logistic and golf_angle to the
golf dataset, then we fit golf_angle to the
golf_new dataset and see a problem, then we fit
golf_angle_distance_2 and
golf_angle_distance_3 to golf_new and finally
obtained a good fit, then we fit
golf_angle_distance_3_with_resids which was the same model
but also saving residuals. Finally, we fit
golf_angle_distance_4 to golf_new but we
didn’t display the fit, we just discussed it.
## References


Don Berry (1995). Statistics: A Bayesian Perspective. Duxbury Press.
The original golf dataset appears as an example in this book.

Mark Broadie (2018). Two simple putting models in golf. Linked from
https://statmodeling.stat.columbia.edu/2019/03/21/new-golf-putting-data-and-a-new-golf-putting-model/.
Here is the larger dataset and a document describing the model with
angular and distance errors.

Andrew Gelman and Deborah Nolan (2002). A probability model for golf
putting. Teaching Statistics 50, 151-153. Our first explanation of the
angular-error model.

All code in this document is licensed under BSD 3-clause license and all text licensed under CC-BY-NC 4.0
