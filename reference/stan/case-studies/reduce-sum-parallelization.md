> Source: https://mc-stan.org/learn-stan/case-studies/reduce_sum_tutorial.html

Reduce Sum: A Minimal Example
# Reduce Sum: A Minimal Example

#### 2 Dec 2020


This introduction to reduce_sum copies directly from Richard McElreath’s Multithreading and Map-Reduce in Stan 2.18.0: A Minimal Example.
## Introduction


Note: This has been rewritten to use unnormalized distribution functions ( _lupdf˙/˙_lupmf) which requires Cmdstan 2.25 or newer.

Cmdstan 2.23 introduced reduce_sum, a new way to parallelize the execution of a single Stan chain across multiple cores. This is in addition to the already existing map_rect utility, and introduces a number of features that make it easier to use parallelism:
- More flexible argument interface, avoiding the packing and unpacking that is necessary with map_rect.
- Partitions data for parallelization automatically (this is done manually in map_rect).
- Is easier to use.

This tutorial will highlight these new features and demonstrate how to use reduce_sum on a simple logistic regression using cmdstanr.
## Overview


Modifying a Stan model for use with reduce_sum has three steps.
- 

Identify the portion of the model that you want to parallelize. reduce_sum is design specifically for speeding up log likelihood evaluations that are composed of a number of conditionally independent terms that can be computed in parallel then added together.
- 

Write a partial sum function that can compute a given number of terms in that sum. Pass this function (and other necessary arguments) to a call to reduce_sum.
- 

Configure your compiler to enable multithreading. Then compile and sample as usual.

To demonstrate this process, we’ll first build a model first without reduce_sum, identify the part to be parallelized, and then work out how to use reduce_sum to parallelize it.
## Prepping the data


Let’s consider a simple logistic regression. We’ll use a reasonably large amount of data, the football red card data set from the recent crowdsourced data analysis project (https://psyarxiv.com/qkwst/). This data table contains 146,028 player-referee dyads. For each dyad, the table records the total number of red cards the referee assigned to the player over the observed number of games.

RedcardData.csv is provided in the repository here. Load the data in R, and let’s take a look at the distribution of red cards:
```
d <- read.csv("RedcardData.csv", stringsAsFactors = FALSE)
table(d$redCards)

## 
##      0      1      2 
## 144219   1784     25
```


The vast majority of dyads have zero red cards. Only 25 dyads show 2 red cards. These counts are our inference target.

The motivating hypothesis behind these data is that referees are biased against darker skinned players. So we’re going to try to predict these counts using the skin color ratings of each player. Not all players actually received skin color ratings in these data, so let’s reduce down to dyads with ratings:
```
d2 <- d[!is.na(d$rater1),]
redcard_data <- list(n_redcards = d2$redCards, n_games = d2$games, rating = d2$rater1)
redcard_data$N <- nrow(d2)
```


This leaves us with 124,621 dyads to predict.

At this point, you are thinking: “But there are repeat observations on players and referees! You need some cluster variables in there in order to build a proper multilevel model!” You are right. But let’s start simple. Keep your partial pooling on idle for the moment.
## Making the model


A Stan model for this problem is just a simple logistic (binomial) GLM. I’ll assume you know Stan well enough already that I can just plop the code down here. Save this code as logistic0.stan where you saved RedcardData.csv (we’ll assume this is your current working directory):
```
data {
  int<lower=0> N;
  int<lower=0> n_redcards[N];
  int<lower=0> n_games[N];
  vector[N] rating;
}
parameters {
  vector[2] beta;
}
model {
  beta[1] ~ normal(0, 10);
  beta[2] ~ normal(0, 1);

  n_redcards ~ binomial_logit(n_games, beta[1] + beta[2] * rating);
}
```

## Building and Running the Basic Model


To install cmdstanr, follow the directions here: https://mc-stan.org/cmdstanr/

To build the model in cmdstanr run:
```
logistic0 <- cmdstan_model("logistic0.stan")

## Model executable is up to date!
```


To sample from the model run:
```
time0 = system.time(fit0 <- logistic0$sample(redcard_data,
                                             chains = 4,
                                             parallel_chains = 4,
                                             refresh = 1000))

## Running MCMC with 4 parallel chains...
## 
## Chain 1 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 2 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 3 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 4 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 4 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 4 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 1 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 1 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 3 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 3 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 2 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 2 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 1 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 1 finished in 163.9 seconds.
## Chain 4 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 4 finished in 167.2 seconds.
## Chain 3 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 3 finished in 167.5 seconds.
## Chain 2 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 2 finished in 168.7 seconds.
## 
## All 4 chains finished successfully.
## Mean chain execution time: 166.8 seconds.
## Total execution time: 168.7 seconds.

time0

##    user  system elapsed 
## 582.427  86.830 169.233
```


Note: Older versions of cmdstanr use num_cores, cores, and num_chains instead of parallel_chains, threads_per_chain, and chains. If you get an error, updatecmdstanr.

In this case, we’ll compute four chains running in parallel on four cores. This computer has eight cores though, and we’ll see how we can make use of those other cores later. The elapsed time is the time that we would have recorded if we were timing this process with a stop-watch, so that is the one relevant to understanding performance here (system time is time spent on system functions like I/O, and user time is for parallel calculations).
## Rewriting the Model to Enable Multithreading


The key to porting this calculation to reduce_sum, is recognizing that the statement:
```
n_redcards ~ binomial_logit(n_games, beta[1] + beta[2] * rating);
```


can be rewritten as:
```
for(n in 1:N) {
  target += binomial_logit_lupmf(n_redcards[n] | n_games[n], beta[1] + beta[2] * rating[n])
}
```


Now it is clear that the calculation is the sum (up to a proportionality constant) of a number of conditionally independent Bernoulli log probability statements. Whenever we need to calculate a large sum where each term is independent of all others and associativity holds, then reduce_sum is useful.

To use reduce_sum, a function must be written that can be used to compute arbitrary sections of this sum.

Note we are using binomial_logit_lupmf instead of binomial_logit_lpmf. This is because we only need this likelihood term up to a proportionality constant for MCMC to work and for some distributions this can make code run noticeably faster. There is a catch though: Stan only allows _lupmf in the model block or in user-defined probability distribution functions. Thus, for us to use binomial_logit_lupmf the, function we write for reduce_sum must be a user-defined probability distribution function (which means it must be suffixed with _lpdf or _lpmf).

If the difference in the performance of normalized and unnormalized functions is not relevant for your application, you can call your reduce_sum function whatever you like.

Using the reducer interface defined in Reduce-Sum:
```
functions {
  real partial_sum_lpmf(int[] slice_n_redcards,
                        int start, int end,
                        int[] n_games,
                        vector rating,
                        vector beta) {
    return binomial_logit_lupmf(slice_n_redcards |
                                n_games[start:end],
                                beta[1] + beta[2] * rating[start:end]);
  }
}
```


The likelihood statement in the model can now be written:
```
target += partial_sum_lupmf(n_redcards, 1, N, n_games, rating, beta); // Sum terms 1 to N in the likelihood
```


Note that we’re calling partial_sum_lupmf even though we defined the function partial_sum_lpmf. partial_sum_lupmf is implicitly defined when we write partial_sum_lpmf and is a special version of the function that will signify to all the _lupmf calls inside it that it is okay to drop constants. If we call partial_sum_lpmf, the binomial_logit_lupmf function call will not drop constants (and hence be slower).

Equivalently this partial sum could be broken into two pieces and written like:
```
int M = N / 2;
target += partial_sum_lupmf(n_redcards[1:M], 1, M, n_games, rating, beta) // Sum terms 1 to M
target += partial_sum_lupmf(n_redcards[(M + 1):N], M + 1, N, n_games, rating, beta); // Sum terms M + 1 to N
```


By passing partial_sum_lupmf to reduce_sum, we tell Stan to automatically break up these calculations and do them in parallel.

Notice the difference in how n_redcards is split in half (to reflect which terms of the sum are being accumulated) and the rest of the arguments (n_games, x, and beta) are left alone. This distinction is important and more fully described in the User’s Guide section on Reduce-sum.

Given the partial sum function, reduce_sum can be used to automatically parallelize the likelihood:
```
int grainsize = 1;
target += reduce_sum(partial_sum_lupmf, n_redcards, grainsize,
                     n_games, rating, beta);
```


reduce_sum automatically breaks the sum into roughly grainsize sized pieces and computes them in parallel. grainsize = 1 specifies that the grainsize should be estimated automatically (grainsize should be left at 1 unless specific tests are done to pick a different one).

Again, if we passed partial_sum_lpmf to reduce_sum instead of partial_sum_lupmf we would not take advantage of the performance benefits of using bernoulli_logit_lupmf.

Making grainsize data (this makes it convenient to experiment with), the final model is:
```
functions {
  real partial_sum_lpmf(int[] slice_n_redcards,
                        int start, int end,
                        int[] n_games,
                        vector rating,
                        vector beta) {
    return binomial_logit_lupmf(slice_n_redcards |
                               n_games[start:end],
                               beta[1] + beta[2] * rating[start:end]);
  }
}
data {
  int<lower=0> N;
  int<lower=0> n_redcards[N];
  int<lower=0> n_games[N];
  vector[N] rating;
  int<lower=1> grainsize;
}
parameters {
  vector[2] beta;
}
model {

  beta[1] ~ normal(0, 10);
  beta[2] ~ normal(0, 1);

  target += reduce_sum(partial_sum_lupmf, n_redcards, grainsize,
                       n_games, rating, beta);
}
```


Save this as logistic1.stan.
## Running the Multithreaded Model


Compile this model with threading support:
```
logistic1 <- cmdstan_model("logistic1.stan", cpp_options = list(stan_threads = TRUE))

## Model executable is up to date!
```


Note: If you get an error Error in self$compile(...) : unused argument (cpp_options = list(stan_threads = TRUE)), update your cmdstanr to the latest version (the threading interface was changed in May 2020, shortly after this tutorial was originally published).

The computer I’m on has 8 cores and we want to make use of all of them. Running 4 chains in parallel gives us 2 threads per chain (which makes full use of all 8 cores on the processor). The within-chain parallelism is generally less efficient as compared to running chains in parallel, but if greater single-chain speedups are desired, then the user can choose to run fewer chains (i.e. 2 chains in parallel with 4 threads each).

Run and time the model with:
```
redcard_data$grainsize <- 1
time1 = system.time(fit1 <- logistic1$sample(redcard_data,
                                             chains = 4,
                                             parallel_chains = 4,
                                             threads_per_chain = 2,
                                             refresh = 1000))

## Running MCMC with 4 parallel chains, with 2 thread(s) per chain...
## 
## Chain 1 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 2 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 3 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 4 Iteration:    1 / 2000 [  0%]  (Warmup) 
## Chain 2 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 2 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 1 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 1 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 4 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 4 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 3 Iteration: 1000 / 2000 [ 50%]  (Warmup) 
## Chain 3 Iteration: 1001 / 2000 [ 50%]  (Sampling) 
## Chain 2 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 2 finished in 58.3 seconds.
## Chain 1 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 1 finished in 61.1 seconds.
## Chain 4 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 4 finished in 63.1 seconds.
## Chain 3 Iteration: 2000 / 2000 [100%]  (Sampling) 
## Chain 3 finished in 64.7 seconds.
## 
## All 4 chains finished successfully.
## Mean chain execution time: 61.8 seconds.
## Total execution time: 64.8 seconds.

time1

##    user  system elapsed 
## 494.100   0.430  64.919
```


Note: Older versions of cmdstanr use num_cores, cores, and num_chains instead of parallel_chains, threads_per_chain, and chains. If you get an error, updatecmdstanr.

Again, elapsed time is the time recorded as if by a stopwatch. Computing the ratios of the two times gives a speedup on eight cores of:
```
time0[["elapsed"]] / time1[["elapsed"]]

## [1] 2.606833
```


This model was particularly easy to parallelize because a lot of the arguments are data (and do not need to be autodiffed). It is possible to get a speedup over two even though we are only doubling the computational resources because of the way reduce_sum breaks up work and uses CPU cache more efficiently. If a model has a large number of arguments that are either defined in the parameters block, transformed parameters block, or model block, or do not do very much computation inside the reduce function, or does not get lucky with caching, the speedup will be much more limited.

We can always get speedup in terms of effective sample size per time by running multiple chains in parallel on different cores. reduce_sum is not a replacement for that, and it is still important to run multiple chains to check diagnostics. reduce_sum is a tool for speeding up single chain calculations, which can be useful for model development and on computers with large numbers of cores.

We can do a quick check that these two methods are mixing with the posterior package (https://github.com/stan-dev/posterior). When parallelizing a model is a good thing to do to make sure something is not breaking:
```
library(posterior)

## This is posterior version 0.1.2

summarise_draws(bind_draws(fit0$draws(), fit1$draws(), along = "chain"))

## # A tibble: 3 x 10
##   variable     mean   median     sd    mad       q5      q95  rhat ess_bulk
##   <chr>       <dbl>    <dbl>  <dbl>  <dbl>    <dbl>    <dbl> <dbl>    <dbl>
## 1 lp__     -1.03e+4 -1.03e+4 0.979  0.741  -1.03e+4 -1.03e+4  1.00    3574.
## 2 beta[1]  -5.53e+0 -5.53e+0 0.0337 0.0339 -5.59e+0 -5.48e+0  1.00    2669.
## 3 beta[2]   2.89e-1  2.89e-1 0.0819 0.0806  1.53e-1  4.21e-1  1.00    2674.
## # … with 1 more variable: ess_tail <dbl>
```


Ignoring lp__ (remember the change to bernoulli_logit_lpmf means the likelihoods between the two models are only proportional up to a constant), the Rhats are less than 1.01, so our basic convergence checks pass. Unless something strange is going on, we probably parallelized our model correctly!
## More Information


For a more detailed description of how reduce_sum works, see the User’s Manual. For a more complete description of the interface, see the Function Reference.
