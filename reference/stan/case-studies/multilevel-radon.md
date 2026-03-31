> Source: https://mc-stan.org/learn-stan/case-studies/radon_cmdstanpy_plotnine.html

radon
# Multilevel regression modeling with CmdStanPy and plotnine¶

### Table of Contents

- Case study: home radon measurement
- Notebook setup
- Radon dataset:  home radon measurements, per-county soil uranium levels
- Plotting basics with plotnine
- Best Practice: preliminary data analysis
- Best Practice: start with a simple model
- Linear regression in Stan
- Fitting Models in CmdStanPy
- Extracting fit information
- Visualizing model estimates with plotnine
- Best Practice: posterior predictive checks
- Multilevel Regression
- Modeling the regression intercept term
- Visualizations
- Posterior predictive checks
- Discussion
- References and Resources
- Acknowledgement and thanks!
- Appendix A: Linear regression review (chapters 2 and 3 of Gelman and Hill)
- Appendix B:  Data preparation using pandas.

This notebook is a short introduction to multilevel regression modeling
using Stan and the CmdStanPy interface.
It shows how to integrate CmdStanPy into the data analysis workflow: how to instantiate
the Stan model, fit it to data, access and validate the inference engine outputs,
and use the results for downstream analysis and prediction.

A secondary goal is to demonstrate best practices of Bayesian Data Analysis.
Before coding up a model and trying to fit it to the data it is critical to
establish both the analysis goals and the sizes, shapes, and tendencies of
the available data.
Once the model is running, we can use posterior predictive checks to assess
whether or not the model is properly specified.
Both of these activities rely primarily on data visualization.
This notebook uses the plotnine package,
an Python implementation of a grammar of graphics
based on ggplot2.
## Case study: home radon measurement¶


The data and models for this notebook are taken from chapter 12 of the book
Data Analysis Using Regression and Multilevel/Hierarchical Models
by Andrew Gelman and Jennifer Hill, Cambridge Press, 2007.
In this chapter they use a multilevel regression model to analyze data
taken from a national survey of home radon levels in the US done by the EPA in the early 1990s.

The goal of the radon study is to provide reasonable estimates
of home radon levels in each of the approximately 3000 counties in the United States.
Radon gas is a product of the slow decay of uranium into lead.  Due to local differences in geology, the level of exposure to radon gas differs from place to place. A common source is uranium-containing minerals in the ground, and therefore it accumulates in subterranean areas such as basements.

Image from https://www.health.state.mn.us/communities/environment/air/radon/index.html
### Notebook setup¶


In addition to CmdStanPy and plotnine,
we will be using both numpy and pandas.In [1]:
```
# import all libraries used in this notebook
import os
import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel

# plotting libs
import matplotlib.pyplot as plt
import plotnine as p9

# suppress plotnine warnings
import warnings
warnings.filterwarnings('ignore')

# setup plotnine look and feel
p9.theme_set(
  p9.theme_grey() + 
  p9.theme(text=p9.element_text(size=10),
        plot_title=p9.element_text(size=14),
        axis_title_x=p9.element_text(size=12),
        axis_title_y=p9.element_text(size=12),
        axis_text_x=p9.element_text(size=8),
        axis_text_y=p9.element_text(size=8)
       )
)
xlabels_90 = p9.theme(axis_text_x = p9.element_text(angle=90, hjust=1))

```
In [2]:
```
# keep notebook outputs clean - demos only
import logging
logging.getLogger('cmdstanpy').setLevel(logging.CRITICAL)

```

### Radon dataset:  home radon measurements, per-county soil uranium levels¶


The data comes from EPA surveys at the state and national level carried out in the 1990s.
It is available from the Gelman and Hill ARM website, together with the R scripts used to produce the examples in the book.

Raw data

The study data is in two separate files: one for the radon home survey, one for county soil uranium levels.
These are distributed as
srrs2.dat
and 
cty.dat
respectively.
For this notebook, we have downloaded and renamed them:
- 

data/raw_radon.csv - home radon measurements, and the floor on which the measurement was taken,  "0" for basement,  "1" for ground floor.
- 

data/raw_uranium.csv -county level measurements of soil uranium levels in parts per million.

There are a total of 120K home radon measurements from 3000 US counties.
The per-county measurements follow the population density; there are few or no measurements
for sparsely populated counties, i.e. rural counties and correspondingly more for metropolitan counties.

Processed data

Our analysis will use both the home radon data measurements and the county level data.

We need to extract and combine that subset of the information in these tables into the dataset required for this analysis.
The essential pre-processing steps are
- 

Cross-index the county-level data and the home-level data.
- 

Put home radon and soil uranium on the log scale, following Gelman and Hill, chapter 4, section 12.
- 

Restrict the dataset to Minnesota.

See Appendix B for the full set of pre-processing operations.

The results are in two files
- data/mn_radon.csv contains the individual home radon measurements.
- data/mn_counties.csv contains county-level data.In [3]:
```
mn_radon = pd.read_csv(os.path.join('data','mn_radon.csv'))
print(f'number of houses: {len(mn_radon)}')
mn_radon.head(7)


number of houses: 919

```
Out[3]:floorcountylog_radonlog_uraniumcounty_id01AITKIN0.788457-0.689048110AITKIN0.788457-0.689048120AITKIN1.064711-0.689048130AITKIN0.000000-0.689048140ANOKA1.131402-0.847313250ANOKA0.916291-0.847313260ANOKA0.405465-0.8473132In [4]:
```
mn_counties = pd.read_csv(os.path.join('data','mn_uranium.csv'))
print(f'number of counties: {len(mn_counties)}')
mn_counties.head(3)


number of counties: 85

```
Out[4]:countylog_uraniumcounty_idhomes0AITKIN-0.689048141ANOKA-0.8473132522BECKER-0.11345933

Best Practice:  avoid meaningless precision

The precision of an estimate is inversely proportional to square root of the amount of data.
For the Minnesota data, only 2 decimal places is warrented.
To change the default print behavoir for pandas DataFrames, we use the pandas global option display.precision.In [5]:
```
pd.set_option('display.precision', 2)

```

### Plotting basics with plotnine¶


For plotting we use the plotnine package, which
is a Python implementation of a grammar of graphics based on the R ggplot2 package.
The grammar allows users to compose plots from one or more layers.
A good resource is Data Visualization with Plotnine,
a Python translation of R for Data Science.

A grammar of graphics defines a plot in terms of:
- A dataset in the form of a pandas.DataFrame.
- A set of mappings from dataset variables to graph elements called "aesthetics".
- A coordinate system, default Cartesian, x,y axes, where x is on the horizontal and y is on the vertical axis.
- A facet specification based on a categorical variable which results in per-category subplots, default None.
- One or more layers, each layer takes as arguments:
- a dataset and aesthetic mapping - by default, the plot dataset and mappings are used
- one geometric object ("geom") - the geometric building blocks of the plot, e.g., point, line, polygon.
- one statistical transformation ("stat"), default "identity"
- one position adjustment, default "identity"

A plot layer is based on a geom, or a stat paired with a geom.
As a first example, we create a plot which contains a single layer which is a 
plotnine geom_histogram.
We provide the minimum plot specification:  the geom, data, and mapping.In [6]:
```
p9.ggplot(data=mn_radon, mapping=p9.aes(x='log_radon')) + p9.geom_histogram()

```
Out[6]:
```
<ggplot: (8771573607283)>
```


Each layer works off a dataset and mapping which can be specified either
as arguments to the plotnine.ggplot object,
as in the above example, or as arguments to the geom object.
An alternative way to create the same plot is:
```
p9.ggplot() + p9.geom_histogram(data=mn_radon, mapping=p9.aes(x='log_radon'))

```


In this example, the only aesthetic is "x" - the position of data along the x-axis;
the y axis are the values of the histogram bins.
Different geoms require different mappings. 
Were this a plot such as a scatterplot, mapping for value "y" would be required as well.
Other common mappings are:
- "shape" - of points
- "linetype"
- "color" - color of lines and outlines
- "fill" - color inside shapes
- "size"

All of these can be mapped to features of the data, so that a single plot layer
can express many aspects of the dataset.
To see how this works, we add information to the histogram by using aesthetics
"color" and "fill" to factor radon measurements by floor.In [7]:
```
# overlay histograms
(p9.ggplot(data=mn_radon, mapping=p9.aes(x='log_radon', color='factor(floor)', fill='factor(floor)'))
    + p9.geom_histogram(alpha=0.7, binwidth=0.2)
    + p9.scale_color_manual(['darkgreen','darkblue'])
    + p9.scale_fill_manual(['orange','violet'])
    + p9.theme(figure_size=(6,4))
)

```
Out[7]:
```
<ggplot: (8771625035457)>
```


In analyzing and plotting the data, the county name is a categorical value.
We update the mn_radon dataframe accordingly.In [8]:
```
# use home radon data county name as a categorical variable
mn_radon['county'] = (mn_radon['county'].astype('category', copy=False))

```

## Best Practice: preliminary data analysis¶


A sometimes overlooked issue when doing model criticism and model comparison is the fact that we are evaluating the fit of the model to the data.  The size and shape of the data informs our choice of model.  Finally, the data collected is not always the data expected.  Therefore we start with plots and summaries of the raw data.

First questions: amount of data, variable of interest

How much data is there for Minnesota?In [9]:
```
print(f'number of houses: {len(mn_radon)}')
print(f'number of counties: {len(mn_counties)}')


number of houses: 919
number of counties: 85

```


The goal of our analysis is to estimate home radon levels; therefore the outcome variable of interest is log_radon.
We use the pandas.DataFrame.describe function to get summary statistics over the observed outcome log_radon.In [10]:
```
print(f'log_radon summary statistics\n{mn_radon["log_radon"].describe()}')


log_radon summary statistics
count    919.00
mean       1.22
std        0.85
min       -2.30
25%        0.64
50%        1.28
75%        1.79
max        3.88
Name: log_radon, dtype: float64

```


Relationship between radon and floor

As the radon pathways diagram shows, radon comes from the soil, therefore the floor level on which the measurement was taken should be a good predictor of the observed radon level. This is coded as "0" for basement and "1" for ground floor level.  Most of the observations in the survey were taken on the basement level.In [11]:
```
pct_1 = round((mn_radon.floor.sum() / len(mn_radon) * 100))
pct_0= round(100 - pct_1)
print(f'floor 0: {pct_0}%\nfloor 1: {pct_1}%')


floor 0: 83%
floor 1: 17%

```


Plotting the histogram of raw counts of number of observations by floor clearly shows the differing amount of per-floor data, but the trend in log radon levels is unclear.In [12]:
```
# overlay histograms
(p9.ggplot(data=mn_radon, mapping=p9.aes(x='log_radon', color='factor(floor)', fill='factor(floor)'))
    + p9.geom_histogram(alpha=0.7, binwidth=0.2)
    + p9.scale_color_manual(['darkgreen','blue'], name='floor')
    + p9.scale_fill_manual(['orange','violet'], name='floor')
    + p9.xlab("log radon levels")
    + p9.theme(figure_size=(6,4))
)

```
Out[12]:
```
<ggplot: (8771608679855)>
```


The plotnine stat_density
shows per-floor trends, but obscures the difference in amounts of observations.
This is an example of a layer constructed from a plotnine stat paired with a geom.In [13]:
```
(p9.ggplot(data=mn_radon, mapping=p9.aes(x='log_radon', color='factor(floor)'))
    + p9.stat_density(geom='line')
    + p9.scale_color_manual(['darkorange','purple'], name='floor')
    + p9.xlab("log radon levels")
    + p9.theme(figure_size=(6,4))
)

```
Out[13]:
```
<ggplot: (8771608678229)>
```


The plotnine geom_point plots two variables as (x, y) points.
A scatterplot of points (floor, log_radon) will only have 2 distinct x-axis values:  0 and 1.
The plotnine geom_jitter adds jitter to the (x, y) points,
which reduces the amount of overplotting and therefore allows for a better visualization of the amount of data being plotted.
Therefore we use the latter to visualize the differences between the the radon measurements by floor.

Because log_radon is the outcome variable of interest for this example, whenever possible, we plot it on the y axis.In [14]:
```
plot_radon_floor = (p9.ggplot(data=mn_radon, mapping=p9.aes(x='floor', y='log_radon')) 
    + p9.geom_jitter(width=0.1, alpha=0.5, fill='orange', color='darkred')
    + p9.scale_x_continuous(breaks=range(0,2), minor_breaks=[])
    + p9.ggtitle("Radon measurements by floor")
    + p9.theme(figure_size=(4,4))
)
plot_radon_floor

```
Out[14]:
```
<ggplot: (8771531305870)>
```


County-level information

Because the most home radon measurements were taken at the basement floor level and because most of the counties have relatively few home measurements taken, there are many counties where all measurements are from the basement floor.In [15]:
```
print(f'Number of counties: {mn_radon.county.nunique()}')
print(f'Counties with measurements from floor 0: {mn_radon[mn_radon["floor"]==0]["county"].nunique()}')
print(f'Counties with measurements from floor 1: {mn_radon[mn_radon["floor"]==1]["county"].nunique()}')


Number of counties: 85
Counties with measurements from floor 0: 85
Counties with measurements from floor 1: 60

```


At the county level we have many home radon measurements from the relatively few counties with metropolitan areas, and very few home radon measurements from the rest.
A basic way to see this distribution of homes per county is a histogram.In [16]:
```
(p9.ggplot()
    + p9.geom_histogram(data=mn_counties, mapping=p9.aes(x='homes'), bins=40)
    + p9.xlab("homes per county")
    + p9.ylab("counties per bin")
    + p9.theme(figure_size=(12,4))
)

```
Out[16]:
```
<ggplot: (8771625057524)>
```


Sort order: observations per county, ascending

The amount of data per county directly affects the precision of our estimates; we sort these counties accordingly.In [17]:
```
obs_asc = mn_counties.sort_values(by='homes').reset_index(drop=True).county.values
mn_radon['county'] = mn_radon['county'].cat.reorder_categories(obs_asc)

```


Boxplot visualizations

Another way to visualize the amount and spread of data per county is by using a
plotnine.geom_boxplot
to generate a box_and_whiskers plot for each set of per-county radon measurements.
The box encloses the central 25% - 75% quantiles; this is the 
interquartile range (IQR).
The the whiskers extend to the values which are a distance of 1.5 the IQR, and values beyond that are plotted as points - these are the outliers.

Setting the width of the box to be proportional to the square root of the number of observations
shows amount of data per county, as well as its spread.
Because the counties are ordered by number of observations, the width of the boxes increases from left to right.In [18]:
```
(p9.ggplot(data=mn_radon, mapping=p9.aes(x='county',y='log_radon'))
    + p9.geom_boxplot(width=2, varwidth=True, outlier_alpha=0.4)
    + p9.scale_x_discrete(expand=(0,3))
    + p9.ggtitle("Counties ordered by number of observations per county")
    + p9.ylab("range of home radon measurements")
    + xlabels_90
    + p9.theme(figure_size=(20,6))
)

```
Out[18]:
```
<ggplot: (8771573709993)>
```


Relationship between home radon and county-level soil uranium

At the county-level, we have information on the soil uranium level.  We plot the number of observations by soil uranium.  The points on the x-axis line up with the histogram bars on the above plot, but instead of histogram bars, we have a series of points showing the different log_uranium levels.In [19]:
```
(p9.ggplot(data=mn_counties, mapping=p9.aes(x='homes', y='log_uranium'))
    + p9.geom_point(fill='orange', color='darkred')
    + p9.geom_text(data=mn_counties[mn_counties['homes']>25],
                   mapping=p9.aes(label='county'),
                   size=8, nudge_x=4, nudge_y=0.1)
    + p9.xlab("observations per county") + p9.ylab("county soil log_uranium")
    + p9.theme(figure_size=(12,4))
)

```
Out[19]:
```
<ggplot: (8771625099171)>
```


We plot the relationship between soil uranium level and the home radon measurement.
We use plotnine's facet_grid to get side-by-side per-floor plots.
Because the soil uranium level measurement is the same for all homes in a county, for counties with many houses, i.e., metropolitan areas, the plot shows distinct vertical bands.

Comparing the information in two side-by-side plots is difficult.  We have established that there are fewer measurements taken on the ground floor than on the basement level.   But we can't see whether or not the home radon measurements are consistently lower when taken on the ground floor.In [20]:
```
(p9.ggplot(data=mn_radon, mapping=p9.aes(x='log_uranium', y='log_radon'))
     + p9.geom_point(alpha=0.9, fill='orange', color='darkred')
     + p9.facet_grid(facets='~ floor', labeller='label_both')
     + p9.xlab("county-level soil log_uranium") + p9.ylab("home log_radon") 
     + p9.theme(figure_size=(12,4))
)

```
Out[20]:
```
<ggplot: (8771573693413)>
```


Alternatively, we can use color to indicate floor, basement orange, ground floor purple, and add jitter to overplot the data.  Taken together, it's not clear whether or not the blue dots are generally lower than the orange ones.In [21]:
```
(p9.ggplot()
    + p9.geom_jitter(data=mn_radon[mn_radon['floor']==0],
                    mapping=p9.aes(x='log_uranium', y='log_radon'), 
                    width=0.01, alpha=0.7, fill='orange', color='darkred')
    + p9.geom_jitter(data=mn_radon[mn_radon['floor']==1],
                    mapping=p9.aes(x='log_uranium', y='log_radon'), 
                    width=0.01, alpha=0.7, fill='purple', color='darkblue')
    + p9.xlab("county-level soil log_uranium")
    + p9.ylab("home log_radon")
    + p9.theme(figure_size=(8,4))
)

```
Out[21]:
```
<ggplot: (8771540349456)>
```


To see whether or not the soil uranium level might be a good predictor of the home radon measurements,
we can repeat the above boxplot, this time ordering the counties on the x-axis by
the per-county activity levels, ordered by uranium level per county, descending.

Given the sparse data, the resulting plot is inconclusive.In [22]:
```
uranium_desc = mn_counties.sort_values(by='log_uranium', ascending=False).reset_index()

(p9.ggplot(data=mn_radon, mapping=p9.aes(x='county',y='log_radon'))
    + p9.geom_boxplot(width=2, varwidth=True, outlier_alpha=0.4)
    + p9.scale_x_discrete(limits=uranium_desc['county'], expand=(0,1))
    + p9.ggtitle("Counties ordered by soil uranium high (left) to low (right)")
    + p9.ylab("range of home radon measurements")
    + xlabels_90
    + p9.theme(figure_size=(20,6))
)

```
Out[22]:
```
<ggplot: (8771531337186)>
```


Preliminary Data Analysis Findings
- 

83% of the data are measurements taken on the basement level.
- 

70% of the counties (60 out of 85) have observations from both floors 0 and 1, the remaining 30% only have observations from floor 0 (basement).
- 

For most counties, there are fewer than 10 observations; 8 counties in metropolitan areas account for over half of the observations.
- 

The counties with the highest soil uranium levels do not have a lot of observations per county.
- 

Within each county, the range of radon measurements is very wide.
## Best Practice: start with a simple model¶


Starting from a simple model ensures that there is a good baseline
against which to measure performance.

Two regular linear regression models

For this case study, 
the baseline model is a regular (non-multilevel) linear regression model,
see Appendix A,
where the outcome y is the home log radon level and the predictor x is the floor
on which the measurement was taken.
We consider two possible models:   complete pooling and no-pooling.

The complete pooling model estimates a single intercept term for the regression.

$
\mathrm{log\_radon}_i = \alpha \, + {\beta}\,\mathrm{floor}_i + {\epsilon}_i
$

The no pooling model estimates a per-county intercept term.
The intercept term $\alpha$ is a vector of size $\mathrm{J}$, the number of counties.

$
\mathrm{log\_radon}_i = \alpha_{j[i]} \, + {\beta}\,\mathrm{floor}_i + {\epsilon}_i \ \ \ \
$
where $j = 1 \ldots 85$.

Gelman and Hill use the notation $\alpha_{j[i]}$ to denote the element of $j$ corresponding to observation $i$,
arguing that this notation better reflects the structure of the data.

Because the floors are coded
$\mathrm{floor}_{\mathrm{basement}} = 0$,  $\mathrm{floor}_{\mathrm{ground}} = 1$,
for basement measurements, the observed outcome $\mathrm{log\_radon}$ is just
the intercept term plus measurement error.

We can use plotnine.geom.geom_smooth(method="lm")
to visualize both the complete pooling and no pooling-models.
This adds a layer with the mean regression line, and grey margins which indicate the amount of variance.

For the complete pooling model, we add this geom to the saved plot plot_radon_floor.In [23]:
```
p1 = (plot_radon_floor
      +  p9.geom_smooth(method='lm')
      +  p9.ggtitle("regression log_radon on floor, all counties")
     )      
p1

```
Out[23]:
```
<ggplot: (8771625059545)>
```


For the no-pooling model, we facet the radon by floor plot.
When combined with geom_smooth, every facet has its own regression model.
As noted above, most of the measurements are taken at the basement level and there are 25 counties without any measurements taken on floor 1. For these counties, in the faceted plot the geom_smooth trend line is absent; i.e., we cannot estimate the slope of the regression line. For counties with measurements on both floors, in a few cases, e.g., Todd and Carlton counties, the regression line between floor 0 and 1 has a positive slope, which a) goes against the estimate from the complete pooling model, and b) goes against what we know about how radon enters the home.In [24]:
```
(p9.ggplot(data=mn_radon, mapping=p9.aes('floor', 'log_radon'))
     + p9.geom_jitter(width=0.05)
     + p9.geom_smooth(method='lm')
     + p9.facet_wrap('county')
     + p9.ggtitle("per-county regression log_radon on floor, counties ordered by observations, ascending")
     + p9.scale_x_continuous(breaks=range(0,2), minor_breaks=[])
     + p9.scales.ylim(-3, 4)  # same limits as complete pooling
     + p9.theme(figure_size=(18,20))
)

```
Out[24]:
```
<ggplot: (8771591108985)>
```

## Linear regression in Stan¶


The complete-pooling model corresponds to the simplest linear regression model in the
Stan User's Guide.
This model is in file radon_cp.stan.
It adds the following to the model in the Stan User's Guide:
- 

All model parameters have weakly informative priors.
- 

The generated quantities program block is used to generate a new sample y_rep, which is $\widetilde{y}$, yet to be observed data.
By using the model parameter estimates with Stan's random number generator probability functions
we generate a new dataset which captures both sampler error and estimation error; see the User's Guide
chapter on Posterior Predictive Sampling for details.
In the next section we show how to use y_rep to test model correctness.

The complete-pooling model doesn't use county information.
If there is no real difference between the radon levels observed across the different counties,
this is model will provide useful estimates.
```
data {
  int<lower=1> N;
  vector[N] x;
  vector[N] y;
}
parameters {
  real alpha;
  real beta;
  real<lower=0> sigma;
}
model {
  y ~ normal(alpha + beta * x, sigma);
  alpha ~ normal(0, 10);
  beta ~ normal(0, 10);
  sigma ~ normal(0, 10);
}
generated quantities {
  array[N] real y_rep = normal_rng(alpha + beta * x, sigma);
}

```


The no-pooling model is in file radon_np.stan.
It differs from the complete pooling model in that
- The input data includes the number of counties J and a vector of county ids for each observation.
- The intercept parameter alpha is coded as a vector of size J.
```
data {
  int<lower=1> N;  // observations
  int<lower=1> J;  // counties
  array[N] int<lower=1, upper=J> county;
  vector[N] x;     // floor
  vector[N] y;     // radon
}
parameters {
  vector[J] alpha;
  real beta;
  real<lower=0> sigma;
}
model {
  y ~ normal(alpha[county] + beta * x, sigma);  
  alpha ~ normal(0, 10);
  beta ~ normal(0, 10);
  sigma ~ normal(0, 10);
}
generated quantities {
  array[N] real y_rep = normal_rng(alpha[county] + beta * x, sigma);
}

```


Stan Programming Language:  Multiple Indexes

The no-pooling model uses Stan's multiple indexing syntax to specify the likelihood of y and to compute y_rep
```
y ~ normal(alpha[county] + beta * x, sigma);

```

- vector alpha has size J
- integer array county is size N
- the values of county are between 1 and J, inclusive, therefore county is a valid set of indexes into alpha
- the expression alpha[county] is a vector of size N
- the expression alpha[county] + beta * x is a vector of size N

This satisfies the size constraints on the arguments to the vectorized normal distribution function.

Best Practice:  Use File Naming Conventions

In this case study
- suffix "cp" stands for "complete pooling"
- suffix "np" stands for "no pooling"
- suffix "pp" stands for "partial pooling"
### Fitting Models in CmdStanPy¶


We create CmdStanModel objects for both the complete-pooling and no-pooling models.In [25]:
```
complete_pooling_model = CmdStanModel(stan_file=os.path.join('stan', 'radon_cp.stan'))
no_pooling_model = CmdStanModel(stan_file=os.path.join('stan', 'radon_np.stan'))

```


We assemble a Python dictionary which contains the definitions of the data block variables.In [26]:
```
radon_data = {"N": len(mn_radon), 
              "x": mn_radon.floor.astype(float), 
              "y": mn_radon.log_radon,
              "J":85, 
              "county" : mn_radon.county_id}

```


We call the model's sample
method which runs Stan's NUTS-HMC sampler.In [27]:
```
complete_pooling_fit = complete_pooling_model.sample(data=radon_data, show_progress=False)


16:19:05 - cmdstanpy - INFO - CmdStan start processing
16:19:05 - cmdstanpy - INFO - Chain [1] start processing
16:19:05 - cmdstanpy - INFO - Chain [2] start processing
16:19:05 - cmdstanpy - INFO - Chain [3] start processing
16:19:05 - cmdstanpy - INFO - Chain [4] start processing
16:19:06 - cmdstanpy - INFO - Chain [1] done processing
16:19:06 - cmdstanpy - INFO - Chain [2] done processing
16:19:06 - cmdstanpy - INFO - Chain [3] done processing
16:19:06 - cmdstanpy - INFO - Chain [4] done processing
16:19:06 - cmdstanpy - WARNING - Non-fatal error during sampling:
Exception: normal_lpdf: Scale parameter is 0, but must be positive! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_cp.stan', line 12, column 2 to column 38)
Exception: normal_lpdf: Scale parameter is 0, but must be positive! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_cp.stan', line 12, column 2 to column 38)
Consider re-running with show_console=True if the above output is unclear!

```
In [28]:
```
no_pooling_fit = no_pooling_model.sample(data=radon_data, show_progress=False)


16:19:06 - cmdstanpy - INFO - CmdStan start processing
16:19:06 - cmdstanpy - INFO - Chain [1] start processing
16:19:06 - cmdstanpy - INFO - Chain [2] start processing
16:19:06 - cmdstanpy - INFO - Chain [3] start processing
16:19:06 - cmdstanpy - INFO - Chain [4] start processing
16:19:07 - cmdstanpy - INFO - Chain [2] done processing
16:19:07 - cmdstanpy - INFO - Chain [3] done processing
16:19:07 - cmdstanpy - INFO - Chain [1] done processing
16:19:07 - cmdstanpy - INFO - Chain [4] done processing

```

### Extracting fit information¶


The sample method returns a CmdStanMCMC object which
provides methods to summarize and diagnose the model fit and accessor methods to access the entire sample or individual items.
Accessor functions allow the user
to access the sample in whatever data format is needed for further analysis.

The sample can be treated as a collection of named, structured variables
- 

methods stan_variable and stan_variables return a numpy.ndarray and a Python dictionary of numpy.ndarray objects, respectively, whose structure corresponds to the Stan variable.
- 

method draws_xr returns an xarray.Dataset of all Stan variables.

The sample can be extracted in tabular format, either as
- 

method draws returns a numpy.ndarray over all columns in the output CSV file.
- 

method draws_pd returns a pandas.DataFrame over all columns in the output CSV file.  The argument vars can be used to restrict this to specified variables or columns.

Extracting model estimates as pandas.DataFrame

We use the draws_pd method to access the sample draws for variables alpha, beta, and sigma.
The draws across all chains are flattened into a single dimension.
In this example, the output 3-D array of 4 chains of 1000 draws over 3 variables which becomes
a 2-D array of 4000 draws of 3 variables.

There are two reasons why we use the draws_pd method here:
- pandas provides many useful statistical functions.
- plotnine is designed to work with pandas DataFrames.In [29]:
```
pool_pd = complete_pooling_fit.draws_pd(vars=['alpha', 'beta', 'sigma'])
print(f'sample draws shape:  {pool_pd.shape}')
pool_pd.head(3)


sample draws shape:  (4000, 3)

```
Out[29]:alphabetasigma01.32-0.580.8011.35-0.610.8421.32-0.680.81In [30]:
```
pool_stats = pool_pd.describe()
pool_stats.round(2)

```
Out[30]:alphabetasigmacount4000.004000.004000.00mean1.33-0.610.82std0.030.070.02min1.22-0.870.7625%1.31-0.660.8150%1.33-0.610.8275%1.35-0.560.84max1.43-0.330.90

Another, more computationally expensive way to get these summary statistics is to call the CmdStanMCMC.summary method.
This returns a pandas.DataFrame of summary statistics for total joint log probability lp__ and all model variables,
plus diagnostic statistics on the
effective sample size
and R_hat, the potential scale reduction factor.In [31]:
```
complete_pooling_fit.summary().round(2)[1:4]

```
Out[31]:MeanMCSEStdDev5%50%95%N_EffN_Eff/sR_hatalpha1.330.00.031.281.331.382840.001750.931.0beta-0.610.00.07-0.73-0.61-0.492874.221772.021.0sigma0.820.00.020.790.820.863778.412329.471.0

Extracting model estimates as structured variables

To see the difference in the estimates of the intercept term alpha for the
complete-pooling (single intercept) and the no-pooling models,
i.e. to compare the estimates for a single intercept term
and a vector of per-county intercept terms,
we use the accessor method stan_variable which returns these
estimates as numpy.ndarray objects.

Like pandas, numpy provides statistics routines.  We use these to plot the mean of the estimate of alpha from the complete-pooling model and the central 50% interval of the elements of vector alpha, the per-county estimates from the no-pooling model.In [32]:
```
complete_pool_alpha_mean = complete_pooling_fit.stan_variable('alpha').mean()

no_pool_alpha = no_pooling_fit.stan_variable('alpha')
no_pool_alpha_mean = np.mean(no_pool_alpha, axis=0)  # axis=0 uses all rows, i.e., per-column mean
no_pool_alpha_lower = np.quantile(no_pool_alpha, 0.16, axis=0)
no_pool_alpha_upper = np.quantile(no_pool_alpha, 0.84, axis=0)
no_pool_alpha_pd = pd.DataFrame(data={
    "mean": no_pool_alpha_mean,
    "upper": no_pool_alpha_upper, 
    "lower": no_pool_alpha_lower, 
    "county":mn_counties['county']
})
no_pool_alpha_pd.head(3)

```
Out[32]:meanupperlowercounty00.851.240.47AITKIN10.880.980.77ANOKA21.511.941.09BECKER
### Visualizing model estimates with plotnine¶


To check that the Stan model's estimates are in line with the geom_smooth(method='lm')  results shown above,
we create the same plot from the fitted model.
We need to overlay the jittered plot of the data with a trend line showing
the mean estimated log radon level for floor 0 and 1.
To do this, we plug the estimates of alpha and beta into
the equation $y = \alpha + \beta \, x$
- when x $= 0$, y $=$ alpha
- when x $= 1$, y $=$ alpha + beta.

Then we add a trend line to the plot which connects this pair of (x, y) points.
In plotnine, there are two ways to do this
- plotnine.geoms.geom_line draws a line through a set of connected points
- plotnine.stats.stat_function superimposes a function on a plot.

We use the stats.stat_function to draw the mean trend line and the geoms.geom_line function to plot
a random sample of draws from the posterior.In [33]:
```
f1 = pool_pd.alpha + pool_pd.beta  # y coord at floor 1 
f0 = pd.Series(pool_pd.alpha.values)  # y coord at floor 0

# 
sz = 100
ys = pd.concat([f0, f1], axis=1)
ys = ys.sample(sz).reset_index(drop=True)

# add sample regression lines to plot_radon_floor (from earlier section)
p2 = plot_radon_floor
for i in range(sz):
    p2 = p2 + p9.geom_line(data=ys.T, mapping=p9.aes(x=[0,1], y=ys.loc[i]),
                           inherit_aes=False, color='grey', alpha=0.06)

# add central regression line
p2 = p2 + p9.stat_function(mapping=p9.aes(x=1),
    fun=lambda x: pool_stats.alpha['mean'] + pool_stats.beta['mean']*x,
    color='blue', size=1
)
p2

```
Out[33]:
```
<ggplot: (8771573864090)>
```


To compare the complete-pooling and no-pooling estimates of alpha we use the geoms.geom_line function to visualize the central 50% interval of the per-county estimates of alpha.
The x-axis shows the county labels, ordered by number of observations descending, and the y-axis shows the values of alpha.
We use a 
plotnine.geoms.geom_hline to add a horizontal line which is the mean value of alpha from the complete-pooling model.In [34]:
```
# get sort order
pop_asc = mn_counties.sort_values(by='homes').reset_index()

p_no_pool = (p9.ggplot(data=no_pool_alpha_pd)
 # Range strip
 + p9.geom_segment(
     mapping=p9.aes(x='county', xend='county', y='lower', yend='upper'),
     size=1.4, color='darkblue', alpha=0.5,
 )
 + p9.geom_point(mapping=p9.aes(x='county', y='mean'))
 + p9.geom_hline(yintercept=complete_pool_alpha_mean, color='darkorange', size=1.5)
 + p9.scale_x_discrete(limits=pop_asc['county'])
 + p9.ggtitle("No pooling model estimates for alpha (basement log_radon level)")
 + p9.xlab("observations per county") + p9.ylab("central 67% interval")
 + xlabels_90
 + p9.theme(figure_size=(20,6)) 
)
p_no_pool

```
Out[34]:
```
<ggplot: (8771591724575)>
```


This shows the problems with the complete-pooling and no-pooling models; for the latter, the small number of observations result in very wide estimates.
## Best Practice: posterior predictive checks¶


Posterior predictive checks are the unit tests of probabilistic programming
```
                                        Ben Goodrich
```


Posterior predictive checks tests how well the fitted model captures basic features of the data.

In the generated quantities block we generate a new sample of "replicated data",
by convention called y_rep by using the estimated model parameters as arguments to
Stan's PRNG distribution functions.
If a model captures the data well, summary statistics such as sample mean and standard deviation,
should have similar values in the original and replicated data sets.
See the Stan Users Guide for further details.

For the no-pooling model, the likelihood statement is
```
y ~ normal(alpha[county] + beta * x, sigma);

```


The posterior predictive check is
```
array[N] real y_rep = normal_rng(alpha[county] + beta * x, sigma);

```


To see how this works, we again use the draws_pd method with argument vars='y_rep'.In [35]:
```
y_rep_pp = no_pooling_fit.draws_pd(vars='y_rep')
y_rep_pp.shape

```
Out[35]:
```
(4000, 919)
```


Next, we estimate the per-county median value for each of the 85 counties.In [36]:
```
# for each of the 85 counties, estimate the median y_rep
stat_median = []
for i in range(1,86):
    idxs = mn_radon.index[mn_radon['county_id'] == i].tolist()
    stat_median.append(np.median(y_rep_pp.iloc[:, idxs].to_numpy().flatten()))

```


We create a plot which combines  a boxplot layer and a layer of per-county median point estimates.
For counties with a large number of observations, the median of y and y_rep are quite close.In [37]:
```
np_ppc_median = (p9.ggplot()
  + p9.geom_boxplot(data=mn_radon,
                    mapping=p9.aes(x='county',y='log_radon'),
                    color='orange', fatten=3, alpha=0.7, outlier_alpha=0.3)
  + p9.geom_point(mapping=p9.aes(x=mn_counties.county, y=stat_median), color='purple')
  + p9.scale_x_discrete(limits=pop_asc['county'], expand=(0,1))
  + p9.ggtitle("No-pooling model, posterior predictive checks: median estimates for alpha")
  + p9.xlab("observations per county")                
  + xlabels_90
  + p9.theme(figure_size=(16,6))
)
np_ppc_median

```
Out[37]:
```
<ggplot: (8771591493036)>
```


Another visualization is to plot the distribution of the actual data against a random sample of replicates.
We plot 2% of the data - 80 replicates out of 4000.In [38]:
```
# get a random sample of the draws
sz = 80
y_rep = no_pooling_fit.draws_pd(vars='y_rep')

# each column is a replicate of the data, using estimates of alpha, beta
y_rep_sample = y_rep.sample(sz).reset_index(drop=True).T

# plot actual distribution of the data against predicted new data
np_ppc = p9.ggplot()
for i in range(sz):
    np_ppc = np_ppc + p9.stat_density(mapping=p9.aes(x=y_rep_sample[i]), geom='line', color='lightblue', alpha=0.4)
np_ppc = (np_ppc 
          + p9.stat_density(data=mn_radon, mapping=p9.aes(x='log_radon'), geom='line', color='darkblue', size=1.1)
          + p9.ggtitle("No-pooling model, posterior predictive checks: density of y, y_rep")
          + p9.xlab("log radon levels") + p9.ylab("density") + p9.scales.xlim(-3,6)
          + p9.theme(figure_size=(6,4))
         )
np_ppc

```
Out[38]:
```
<ggplot: (8771591769826)>
```


The replicated densities are more diffuse, wider at the base, not lining up with the peak.
## Multilevel Regression¶


Multilevel regression models the dependency structures in the data
in addition to the relation between outcome and predictors.
If the data has a hierarchical structure, all levels of the hierarchy may be modeled
and all of the data is used to estimate all parameters jointly.

For this dataset, houses are nested within counties.
An ordinary regression can either model all counties as being identical, the complete pooling model,
or all counties as being different, the no-pooling model.
In the no-pooling model, the resulting estimates for counties with sparse data
were too diffuse.
A multi-level regression accounts for the observed variation across counties
by modeling the counties as being drawn from
a common distribution, whose parameters are estimated jointly by the model.
This allows for partial pooling of information.
When there is very little variation across counties, the multi-level model approaches the complete-pooling model,
at the other extreme, when the amount of variation is very large, it approaches the no-pooling model

A simple linear regression model with a single predictor
estimates two parameters:  the intercept and slope of the regression line.
In a multilevel model, either or both of these parameters can be modeled.
As the number of regression predictors increases, the modeling choices increase.
### Modeling the regression intercept term¶


A first multilevel version of the radon model extends the no-pooling model
by putting a distribution on the intercept term

$
\alpha_j \sim \mathrm{N}(\mu_\alpha,\, {\sigma_\alpha}^2),\ \ \ \ \mathrm{for}\ \ j\, = 1, \ldots, \mathrm{J}
$

In combination with the likelihood, the partial-pooling model is

$
y_i = \alpha_{j[i]} \, + {\beta}\,x_i + {\epsilon}_i \\
\alpha_j \sim \mathrm{N}(\mu_\alpha,\, {\sigma_\alpha}^2),\ \ \ \ \mathrm{for}\ \ j\, = 1, \ldots, \mathrm{J}
$

All parameters are also estimated jointly by the model.
This model provides partial pooling of information;
it pulls the estimates of $\alpha_j$ towards the mean level $\mu_\alpha$, to a greater or lesser degree.
Partial pooling is a soft constraint whose effect depends on the amount of group-level variance $\sigma_\alpha$.
As the variance increases, the amount of pooling decreases so that when
$\sigma_\alpha \rightarrow \inf$ there is no pooling; and when $\sigma_\alpha \rightarrow 0$ there is complete-pooling.
```
data {
  int<lower=1> N;  // observations
  int<lower=1> J;  // counties
  array[N] int<lower=1, upper=J> county;
  vector[N] x;
  vector[N] y;
}
parameters {
  real mu_alpha;
  real<lower=0> sigma_alpha;
  vector<offset=mu_alpha, multiplier=sigma_alpha>[J] alpha;  // non-centered parameterization
  real beta;
  real<lower=0> sigma;
}
model {
  y ~ normal(alpha[county] + beta * x, sigma);  
  alpha ~ normal(mu_alpha, sigma_alpha); // partial-pooling
  beta ~ normal(0, 10);
  sigma ~ normal(0, 10);
  mu_alpha ~ normal(0, 10);
  sigma_alpha ~ normal(0, 10);
}
generated quantities {
  array[N] real y_rep = normal_rng(alpha[county] + beta * x, sigma);
}

```
In [39]:
```
partial_pooling_alpha_model = CmdStanModel(stan_file=os.path.join('stan', 'radon_pp_alpha.stan'))

```
In [40]:
```
partial_pooling_alpha_fit = partial_pooling_alpha_model.sample(data=radon_data, show_progress=False)
partial_pooling_alpha_fit.summary().round(2).head(10)


16:19:28 - cmdstanpy - INFO - CmdStan start processing
16:19:28 - cmdstanpy - INFO - Chain [1] start processing
16:19:28 - cmdstanpy - INFO - Chain [2] start processing
16:19:28 - cmdstanpy - INFO - Chain [3] start processing
16:19:28 - cmdstanpy - INFO - Chain [4] start processing
16:19:29 - cmdstanpy - INFO - Chain [1] done processing
16:19:29 - cmdstanpy - INFO - Chain [2] done processing
16:19:29 - cmdstanpy - INFO - Chain [3] done processing
16:19:30 - cmdstanpy - INFO - Chain [4] done processing
16:19:30 - cmdstanpy - WARNING - Non-fatal error during sampling:
Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
	Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
Exception: offset_multiplier_constrain: multiplier is 0, but must be positive finite! (in '/Users/mitzi/github/stan-dev/example-models/jupyter/radon/stan/radon_pp_alpha.stan', line 11, column 2 to column 59)
Consider re-running with show_console=True if the above output is unclear!

```
Out[40]:MeanMCSEStdDev5%50%95%N_EffN_Eff/sR_hatlp__-246.180.319.25-262.06-245.92-231.25901.00330.041.0mu_alpha1.460.000.051.381.461.552379.49871.611.0sigma_alpha0.330.000.050.260.330.411500.24549.541.0alpha[1]1.190.000.260.741.191.627863.332880.341.0alpha[2]0.930.000.100.770.931.096276.732299.171.0alpha[3]1.480.000.261.061.481.918023.512939.021.0alpha[4]1.510.000.221.141.501.878997.973295.961.0alpha[5]1.440.000.251.021.441.878071.052956.431.0alpha[6]1.480.000.261.051.481.928957.863281.271.0alpha[7]1.860.000.171.571.852.158237.523017.411.0
### Visualizations¶


To visualize the results, we plot the central 50% of the estimates for alpha, as we did for the no-pooling model above. 
We use the stan_variable method to compute the mean and central 50% interval of the elements of vector alpha.In [41]:
```
part_pool_mu_alpha = partial_pooling_alpha_fit.stan_variable('mu_alpha').mean()
part_pool_alpha = partial_pooling_alpha_fit.stan_variable('alpha')
part_pool_alpha_mean = np.mean(part_pool_alpha, axis=0)
part_pool_alpha_lower = np.quantile(part_pool_alpha, 0.16, axis=0)
part_pool_alpha_upper = np.quantile(part_pool_alpha, 0.84, axis=0)
part_pool_alpha_pd = pd.DataFrame(
    data={
        "mean": part_pool_alpha_mean,
        "upper": part_pool_alpha_upper, 
        "lower": part_pool_alpha_lower, 
        "county":mn_counties['county']
    }
)

```


We plot the per-county estimates of alpha just as we did above, and we keep the y-axis on the same scale
as for the no-pooling model; which were in range $(0, 3.5)$ (roughly).   This shows how the hierarchical pools information
among the intercept terms and helps shrink the variance of the estimates.In [42]:
```
# visualize
p_partial_pool_intercept = (p9.ggplot(data=part_pool_alpha_pd)
 # Range strip
 + p9.geom_segment(
     mapping=p9.aes(x='county', xend='county', y='lower', yend='upper'),
     size=1.7, color='blue', alpha=0.7,
 )
 + p9.geom_point(mapping=p9.aes(x='county', y='mean'))
 + p9.geom_hline(yintercept=part_pool_mu_alpha, color='darkblue', size=1)
 + p9.scale_x_discrete(limits=pop_asc['county']) + p9.scales.ylim(0,3.5)
 + p9.ggtitle("multilevel varying intercept model estimates for alpha (basement log_radon level)")
 + p9.xlab("ordered by observations per county") + p9.ylab("central 67% interval")
 + xlabels_90
 + p9.theme(figure_size=(20,6)) 
)
p_partial_pool_intercept

```
Out[42]:
```
<ggplot: (8771573842981)>
```


To compare the no-pooling and partial pooling model estimates of alpha directly, we overlay the above plot with the estimated from the no-pooling model in orange.In [43]:
```
(p_partial_pool_intercept
    + p9.geom_segment(data=no_pool_alpha_pd,
         mapping=p9.aes(x='county', xend='county', y='lower', yend='upper'),
         size=1.4, color='orange', alpha=0.6,
     )
     + p9.geom_hline(yintercept=complete_pool_alpha_mean, color='darkorange', size=1)
)

```
Out[43]:
```
<ggplot: (8771573711529)>
```


Another visualization is to plot the multilevel model estimates with the boxplots of the raw data.In [44]:
```
(p_partial_pool_intercept
 + p9.geom_boxplot(data=mn_radon, mapping=p9.aes(x='county',y='log_radon'), 
                   color='orange', alpha=0.4, outlier_alpha=0.3)
)

```
Out[44]:
```
<ggplot: (8771591521133)>
```

### Posterior predictive checks¶
In [45]:
```
y_rep_pp = partial_pooling_alpha_fit.draws_pd(vars='y_rep')

# compute per-county medians, means
pp_stat_median = []
for i in range(1,86):
    idxs = mn_radon.index[mn_radon['county_id'] == i].tolist()
    pp_stat_median.append(np.median(y_rep_pp.iloc[:, idxs].to_numpy().flatten()))

# plot medians from sample against boxplot y
(p9.ggplot()
  + p9.geom_boxplot(data=mn_radon,
                    mapping=p9.aes(x='county',y='log_radon'), 
                    color='orange', fatten=2, alpha=0.7, outlier_alpha=0.3)
  + p9.geom_point(mapping=p9.aes(x=mn_counties.county, y=pp_stat_median), color='purple')
  + p9.scale_x_discrete(limits=pop_asc['county'])
  + p9.ggtitle("Partial-pooling model, posterior predictive checks: median estimates for alpha")
  + xlabels_90
  + p9.theme(figure_size=(16,6))
)

```
Out[45]:
```
<ggplot: (8771591473116)>
```


There is no discernible difference between the results for this model and the no-pooling model; both models are well-specified.

The PPC density plots are also similar.In [46]:
```
# each column is a replicate of the data, using estimates of alpha, beta
y_rep_pp_sample = y_rep_pp.sample(sz).reset_index(drop=True).T

# plot actual distribution of the data against predicted new data
pp_ppc = p9.ggplot()
for i in range(sz):
    pp_ppc = pp_ppc + p9.stat_density(mapping=p9.aes(x=y_rep_pp_sample[i]),
                                      geom='line', color='lightblue', alpha=0.4)
pp_ppc = (pp_ppc 
          + p9.stat_density(data=mn_radon, mapping=p9.aes(x='log_radon'),
                            geom='line', color='darkblue', size=1.1)
          + p9.ggtitle("Partial-pooling model, posterior predictive checks: density for y, y_rep")
          + p9.xlab("log radon levels") + p9.ylab("density") + p9.scales.xlim(-3, 6)
          + p9.theme(figure_size=(6,4))
         )
pp_ppc

```
Out[46]:
```
<ggplot: (8771524138572)>
```


We can use the patchworklib package to display these plots side by side.
For the partial pooling model, the densities of the replicates in light blue better approximate the density plot of the raw data.In [47]:
```
# combine multiple plots
import patchworklib as pw  # ignore warning about seaborn
from plotnine.data import *

g1 = pw.load_ggplot(pp_ppc)
g1.savefig(quick=True)
g2 = pw.load_ggplot(np_ppc)
g2.savefig(quick=True)
p12 = (g1 | g2)

p12.savefig(quick=True)


No module named 'seaborn'

```
Out[47]:
## Discussion¶


In CmdStanPy, fitting a model to data is straightforward.
- 

Instantiate a CmdStanModel object
- 

Assemble a data dictionary or JSON file which contains definitions for all data variables declared in the model's data block.
- 

Run one of the available inference methods:
- sample to do exact Bayesian estimation
- variational to do approximate Bayesian estimation
- optimize to do penalized maximum likelihood estimation
- 

Extract the estimates for parameters and quantities of interest.  CmdStanPy's accessor functions make it easy to get the outputs in whatever data format is appropriate for downstream analysis.

Fitting the model to the data is just one component of the analysis.
The bulk of the code in this notebook is devoted to visualizing both the raw data and the model estimates;
data visualization drives both the model specification process and the model testing process.
With the plotnine package we can create multi-layer plots which overly the raw data with the model estimates
and predictions or multi-layer plots which demonstrate the behaviors of different models.
These activities play a central role in developing trustworthy data analysis pipelines:
- 

Plotting the raw or simulated data before modeling informs the model design process
- 

Plotting prior and posterior predictive checks drives testing
- 

Plotting model estimates and predictions drives documentation and dissemination of results.

In this notebook we work through the multilevel regression model from Gelman and Hill, chapter 12,
restricting our analysis to just the data from the state of Minnesota.
Even if we weren't writing this up as part of an introduction to multi-level modeling,
that is, if we were tasked with this analysis qua analysis, we would proceed similarly -
starting with a very simple model.
There are many possible next steps:
- Expanding the analysis to other states or the entire US.
- Expanding the model to use the county-level soil uranium level measurements
- as a varying-intercept / varying-slope model (Chapter 12)
- as a spatial-effects model
## References and Resources¶


This notebook is based on Chris Fonnesbeck's excellent A Primer on Bayesian Multilevel Modeling using PyStan, which was developed as part of a Stan workshop  for biomedical statisticians at Vanderbilt University.

Stan Tutorials YouTube Playlist Maggie Lieu - a series of introductory videos on Bayesian modeling with Stan

Stan User's Guide

Visualization in Bayesian workflow
Jonah Gabry, Daniel Simpson, Aki Vehtari, Michael Betancourt, and Andrew Gelman, 2019

Designing for interactive exploratory data analysis requires theories of graphical inference Jessica Hullman and Andrew Gelman, 2021

Data analysis using regression and multilevel/hierarchical models Andrew Gelman and Jennifer Hill, 2007

Statistical rethinking by Richard McElreath -
an intro-stats/linear models course taught from a Bayesian perspective.
- GitHub page
- Course page

Making Plots With plotnine - plotnine tutorial notebook.

Papers by Price and Gelman on the radon data and multilevel models:

Centralized analysis of local data, with dollars and lives on the line: Lessons from the home radon experience. Phillip N. Price and Andrew Gelman, 2015

Analysis of local decisions using hierarchical modeling, applied to home radon measurement and remediation (with discussion) Phillip N. Price and Andrew Gelman, 1999
## Acknowledgement and thanks!¶

- Bob Carpenter
- Chris Fonnesbeck
- Jonah Gabry
- Andrew Gelman
- Reshama Shaikh
- Brian Ward


## Appendix A: Linear regression review (chapters 2 and 3 of Gelman and Hill)¶


Linear regression models the relationship between a scalar response and one or more prediexplanatory variables.


A simple linear regression where the observed data (red) are assumed to be
the result of random deviations (green) from an underlying relationship (blue)
between the dependent variable (y) and an independent variable (x).
The model fits the data by finding the linear function (a non-vertical straight line)
which minimizes the distance between "$y_i$ at offset $x_i$   and the line at offset $x_i$.

$y_i = \alpha \, + \beta\,x_i + {\epsilon}_i$
- $\alpha$ is the intercept, the offset from zero on the x-axis
- $\beta$ is the slope, the multiplier applied to x.
- ${\epsilon}_i$ is the error term, assuming independent errors drawn from a normal distribution with mean $0$, standard deviation $\sigma$.

In a simple linear regression, there is only a single predictor.  In an ordinary linear regression,
there are many predictors, i.e., the model fits a vector of coefficients $\beta$ to the vector
of independent variables $X$.

Interpretation

In Chapter 3, Gelman and Hill write:

Linear regression is a method that summarizes how the average values of a numerical outcome variable vary over subpopulations defined by linear functions of predictors. ... Regression can be used to predict an outcome given a linear function of these predictors, and regression coefficients can be thought of as comparisons across predicted values or as comparisons among averages in the data.

Linear regression:  two ways to write the model

The goal of inference is to learn from incomplete or imperfect data.
In the simple linear regression model, the error term $\epsilon$ accounts for imperfect measurements of the data.

$
y_i = \alpha \, + {\beta}\,x_i + {\epsilon}_i
$
where the errors ${\epsilon}_i$ have independent normal distributions with mean $0$ and standard deviation $\sigma$.

An equivalent representation is

$
y_i ∼ \mathrm{N}(\alpha + \beta\,\mathrm{X}_i,\, \sigma^2), \ \ \ \mathrm{for}\ i=1, ..., n
$

The corresponding Stan statement is
```
y ~ normal(alpha + beta * x, sigma);

```


Stan provides vectorized versions of all univariate probability distrions.
This statement is far more efficient than using a for loop over all $x_i$ and $y_i$ pairs.

Simple linear regression model in Stan

The simple linear regression with a single predictor and a slope and intercept coefficient and normally distributed noise is the first model discussed in the Stan User's Guide Regression Models chapter.
```
data {
  int<lower=0> N;
  vector[N] x;
  vector[N] y;
}
parameters {
  real alpha;
  real beta;
  real<lower=0> sigma;
}
model {
  y ~ normal(alpha + beta * x, sigma);
}

```


This model is the minimal possible model.
It consists of three named program blocks:
the data and parameters are declared in the respectively named data and parameters block;
the model block specifies the likelihood, i.e., the probability of the data given the model.
Because no priors are specified on the model parameters, they are given the default prior
distribution, which is uniform from  $-\infty$ to $+\infty$.


## Appendix B:  Data preparation using pandas.¶


The steps required to convert the CSV files from the Gelman and Hill ARM website
into the data structures used in this analysis:
- Merge the county-level soil uranium level measurement into the home radon data.
- Put both outcome and predictors on the log scale, following Gelman and Hill, chapter 4, section 12.
- Restrict the dataset to Minnesota.
- Aggregate county-level information

Pandas objects contain structured arrays which are labeled by
Index objects.
A Series object 
manages 1-D arrays and a DataFrame
is a 2-D size-mutable, table, allowing for heterogenous columns.
These index labels are used to perform database-like select, join, and group-by operations.
However, sometimes we need to access just the data, not the index labels.
Most data is backed by an NumPy ndarray.
The array property
returns the underlying numpy.ndarray of the Index or Series object.

Extract relevant columns from CSV as pandas DataFrame

We leverage the pandas.read_csv function
to extract the information we need from the raw CSV files with the following non-default arguments
- parameter usecols allows us to extract just the relevant columns for this analysis.
- parameter skipinitialspace strips out initial whitespace from the data.

Once instantiated, we call the convert_dtypes method on the newly instantiated DataFrame so that we can do merge and join operations on all columns.In [48]:
```
df_radon = pd.read_csv(os.path.join('data','raw_radon.csv'),
    usecols=['state', 'stfips', 'floor', 'activity', 'county', 'cntyfips'],
    skipinitialspace=True,    # CSV file has spaces after delimiter, ignore them
).convert_dtypes()
print(f'Total records: {len(df_radon)}')
df_radon.head(3)


Total records: 12777

```
Out[48]:statestfipsflooractivitycntyfipscounty0AZ410.31APACHE1AZ490.61APACHE2AZ410.51APACHEIn [49]:
```
df_uranium = pd.read_csv(os.path.join('data','raw_uranium.csv'),
                        usecols=['stfips', 'ctfips', 'st', 'cty', 'Uppm'],
                        skipinitialspace=True,
                        ).drop_duplicates().convert_dtypes()
df_uranium.head(3)

```
Out[49]:stfipsctfipsstctyUppm011ALAUTAUGA1.78113ALBALDWIN1.38215ALBARBOUR2.1

Combine datasets

FIPS code are numbers which uniquely identify geographic areas. Both datasets have codes for the state and county ids, but these need to be combined to get a national-level county FIPS code.   In order to do a database-style join on the two tables, we need to
- add a common key to both tables
- add the county-level soil uranium levels to the radon survey via the DataFrame.merge method.In [50]:
```
df_radon['fips'] = df_radon.stfips*1000 + df_radon.cntyfips
df_uranium['fips'] = df_uranium.stfips*1000 + df_uranium.ctfips

df_radon = df_radon.merge(df_uranium[['fips', 'Uppm']], on='fips')
df_radon.head(3)

```
Out[50]:statestfipsflooractivitycntyfipscountyfipsUppm0AZ410.31APACHE40012.261AZ490.61APACHE40012.262AZ410.51APACHE40012.26

Put data on log scale

Following Gelman and Hill chapter 4, section 4, we work with data on the log scale,
for two reasons
- the outcome variable log_radon is always positive.
- it provides modeling flexibility.

We know from geology that both radon measurements and soil uranium levels are always greater than zero,
however a few radon measurements in the EPA dataset are 0.
In order to be able to work with these measurements on the log scale, we replace 0 with 0.1,
which corresponds to a low radon level (following Gelman and Hill).In [51]:
```
df_radon['radon'] = df_radon.activity.apply(lambda x: x if x > 0. else 0.1)
df_radon['log_radon'] = np.log(df_radon['radon'])

df_radon['uranium'] = df_radon.Uppm.apply(lambda x: x if x > 0. else 0.1)
df_radon['log_uranium'] = np.log(df_radon['uranium'])
df_radon.head(3)

```
Out[51]:statestfipsflooractivitycntyfipscountyfipsUppmradonlog_radonuraniumlog_uranium0AZ410.31APACHE40012.260.3-1.202.260.821AZ490.61APACHE40012.260.6-0.512.260.822AZ410.51APACHE40012.260.5-0.692.260.82

Cleanup

Remove the columns which contain redundant information.In [52]:
```
df_radon.drop(columns=['stfips', 'activity', 'cntyfips', 'Uppm', 'fips', 'radon', 'uranium'], inplace=True)

```


Restrict dataset to Minnesota

In order to work with just the data from Minnesota, we use a 
use a conditional expression to filter specific rows of a dataframe, combined with operation reset_index(drop=True) so that the rows are indexed starting from 0.In [53]:
```
mn_radon = df_radon[df_radon['state']=='MN'].reset_index(drop=True)
mn_radon.drop(columns=['state'], inplace=True)
mn_radon.head(3)

```
Out[53]:floorcountylog_radonlog_uranium01AITKIN0.79-0.6910AITKIN0.79-0.6920AITKIN1.06-0.69

Add 1-based index code for MN counties

The data inputs to a Stan model include a 1-based county index for each observation.
In order to do this we need to first get a sorted list of county names and then convert these to category code.In [54]:
```
mn_radon['county'] = (mn_radon['county'].astype('category', copy=False))
mn_radon['county_id'] = mn_radon.county.cat.codes + 1  ## Stan indexes from 1
mn_radon[:5]

```
Out[54]:floorcountylog_radonlog_uraniumcounty_id01AITKIN0.79-0.69110AITKIN0.79-0.69120AITKIN1.06-0.69130AITKIN0.00-0.69140ANOKA1.13-0.852

Create auxiliary dataset of per-county information

County-level information includes the number of observations taken in that county as well as the soil uranium level.
In order to easily visualize this information using plotnine, we create a secondary pandas.Dataframe object with per-county level information.

The value_counts method returns a Series containing counts of unique values,
We add these to the county-level dataframe.In [55]:
```
mn_uranium = mn_radon.iloc[mn_radon.county.drop_duplicates().index].reset_index(drop=True)
mn_uranium['homes'] = mn_radon.value_counts(subset='county', sort=False).array
mn_uranium.drop(columns=['floor', 'log_radon'], inplace=True)
mn_uranium[:5]

```
Out[55]:countylog_uraniumcounty_idhomes0AITKIN-0.69141ANOKA-0.852522BECKER-0.11333BELTRAMI-0.59474BENTON-0.1454

Save as CSV files

These files are already part of this notebook, therefore calls to the  pandas.to_csv method have been commented out.In [56]:
```
# uncomment as needed
# mn_radon.to_csv(r'mn_radon.csv', index=False)
# mn_uranium.to_csv(r'mn_uranium.csv', index=False)

```

