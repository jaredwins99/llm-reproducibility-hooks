# Stan Discourse Forum Reference Index

Main forum: https://discourse.mc-stan.org/

## Forum Categories

| Category | URL |
|----------|-----|
| General | https://discourse.mc-stan.org/c/general/24 |
| Modeling | https://discourse.mc-stan.org/c/modeling/9 |
| Interfaces | https://discourse.mc-stan.org/c/interfaces/5 |
| CmdStan | https://discourse.mc-stan.org/c/interfaces/cmdstan/28 |
| brms | https://discourse.mc-stan.org/c/interfaces/brms/36 |
| Developers | https://discourse.mc-stan.org/c/stan-dev/10 |
| Announcements | https://discourse.mc-stan.org/c/announce/32 |

---

## Troubleshooting Topics by Category

### Common Modeling Mistakes

- [Divergent transitions -- a primer](https://discourse.mc-stan.org/t/divergent-transitions-a-primer/17099) -- Comprehensive guide to understanding and resolving divergences
  - Local file: [divergent_transitions_primer.md](divergent_transitions_primer.md)
- [Text for warning message](https://discourse.mc-stan.org/t/text-for-warning-message/16928) -- Discussion of what Stan warnings mean and how to respond
  - Local file: [warning_messages_explained.md](warning_messages_explained.md)

### Divergent Transitions

- [Divergent transitions -- a primer](https://discourse.mc-stan.org/t/divergent-transitions-a-primer/17099) -- The go-to reference for understanding divergences
  - Local file: [divergent_transitions_primer.md](divergent_transitions_primer.md)
- [Best way to identify pathologies from divergent transitions (step-by-step workflow)](https://discourse.mc-stan.org/t/best-way-to-identify-pathologies-from-divergent-transitions-general-step-by-step-workflow/4358) -- Visual and automated diagnostic techniques
  - Local file: [diagnosing_pathologies_workflow.md](diagnosing_pathologies_workflow.md)
- [Divergent transitions and model averaging issues](https://discourse.mc-stan.org/t/divergent-transitions-and-model-averaging-issues/33348)
- [Divergent transitions after warmup](https://discourse.mc-stan.org/t/divergent-transitions-after-warmup/34179)
- [Help with my divergent transitions, part 999](https://discourse.mc-stan.org/t/help-with-my-divergent-transitions-part-999/22228)

### Prior Choice

- [Prior Choice Recommendations wiki](https://discourse.mc-stan.org/t/prior-choice-recommendations-wiki/11580) -- Links to the canonical GitHub wiki
  - Local file: [prior_choice_recommendations.md](prior_choice_recommendations.md)
- [Suggestion for Prior Choice Recommendations wiki](https://discourse.mc-stan.org/t/suggestion-for-prior-choice-recommendations-wiki/11584) -- Discussion of variability parameter priors
- [Prior recommendation for scale parameters in hierarchical models](https://discourse.mc-stan.org/t/prior-recommendation-for-scale-parameters-in-hierarchical-models-too-strong/2927)
- [Prior Choice for Beta Binomial Dispersion](https://discourse.mc-stan.org/t/prior-choice-for-beta-binomial-dispersion/24562)
- GitHub wiki (canonical): https://github.com/stan-dev/stan/wiki/Prior-Choice-Recommendations

### Reparameterization Tips

- [General guidelines to aid model reparametrization](https://discourse.mc-stan.org/t/are-there-any-general-guidelines-to-aid-model-reparametrization/40788) -- Core principles and approaches
  - Local file: [reparameterization_guidelines.md](reparameterization_guidelines.md)
- [Non-centered parameterization for non-hierarchical parameters](https://discourse.mc-stan.org/t/non-centered-parameterization-for-non-hierarchical-parameters/22133)
- [What does non-centered parameterization actually do? (brms)](https://discourse.mc-stan.org/t/what-does-non-centered-parameterization-actually-do-how-to-interpret-model-brms/22266)
- [Non-centered reparameterization for truncated normal](https://discourse.mc-stan.org/t/non-centered-reparameterization-for-truncated-normal-distribution/19024)
- [Placing priors with QR reparameterization (regression)](https://discourse.mc-stan.org/t/placing-priors-with-qr-reparametrization-regression/1756)
- [When to use reparameterization in gamma regression](https://discourse.mc-stan.org/t/when-to-use-reparameterization-in-gamma-regression/38465)
- [Updated non-centered parametrization with offset and multiplier](https://discourse.mc-stan.org/t/updated-non-centered-parametrization-with-offset-and-multiplier/13601)
- [Centered vs non-centered model, different loglikelihoods](https://discourse.mc-stan.org/t/centered-vs-non-centered-model-different-loglikelihoods/35053)

### Performance / Efficiency

- [How to speed up sampling in RStan](https://discourse.mc-stan.org/t/how-to-speed-up-sampling-in-rstan/16822) -- Hierarchical model optimization case study
  - Local file: [performance_optimization.md](performance_optimization.md)
- [How to improve model sampling speed (high-dimension data)](https://discourse.mc-stan.org/t/how-to-improve-model-sampling-speed-when-applied-to-high-dimension-data/40005) -- Vectorization, reduce_sum, compilation flags
- [How to speed up my Stan code and sampling in RStan](https://discourse.mc-stan.org/t/how-to-speed-up-my-stan-code-and-sampling-in-rstan/22756)
- [CmdStan cluster sampling speed](https://discourse.mc-stan.org/t/cmdstan-cluster-sampling-speed/38443)
- [CmdStanR sampling very slow compared to RStan](https://discourse.mc-stan.org/t/cmdstanr-sampling-very-slow-compared-to-rstan/37590)

### Interface-Specific Issues

#### CmdStan / CmdStanR / CmdStanPy
- Local file: [cmdstan_common_issues.md](cmdstan_common_issues.md)
- [CmdStan category](https://discourse.mc-stan.org/c/interfaces/cmdstan/28)
- [Installation of CmdStanR macOS](https://discourse.mc-stan.org/t/installation-of-cmdstanr-macos-tahoe/40997)
- [Cannot install CmdStanR on fresh macOS + RStudio](https://discourse.mc-stan.org/t/cannot-install-cmdstanr-on-freshly-installed-macos-rstudio/26736)
- [CmdStanPy recompiles models and fails](https://discourse.mc-stan.org/t/cmdstanpy-recompiles-models-and-fails-on-some-systems/40172)
- [Running Stan on GPU with OpenCL on WSL](https://discourse.mc-stan.org/t/running-stan-on-the-gpu-with-opencl-on-wsl-seeking-assistance/36149)

#### RStan
- [How to speed up sampling in RStan](https://discourse.mc-stan.org/t/how-to-speed-up-sampling-in-rstan/16822)

#### PyStan
- [Interfaces category](https://discourse.mc-stan.org/c/interfaces/5) -- General interface discussions including PyStan

#### brms
- [brms category](https://discourse.mc-stan.org/c/interfaces/brms/36)
- [Non-centered to centered parameterization in brms](https://discourse.mc-stan.org/t/brms-non-centered-to-centered-parameterization/32932)
- [Understanding reparameterization of nonlinear hierarchical models with brms](https://discourse.mc-stan.org/t/understanding-reparameterization-of-nonlinear-hierarchical-models-with-brms/20258)

---

## Local Reference Files

| File | Description |
|------|-------------|
| [divergent_transitions_primer.md](divergent_transitions_primer.md) | 13-step guide to diagnosing and resolving divergent transitions |
| [diagnosing_pathologies_workflow.md](diagnosing_pathologies_workflow.md) | Step-by-step visual and automated diagnostic workflow |
| [prior_choice_recommendations.md](prior_choice_recommendations.md) | Prior selection advice for various parameter types |
| [reparameterization_guidelines.md](reparameterization_guidelines.md) | General principles and approaches for reparameterization |
| [performance_optimization.md](performance_optimization.md) | Sampling speed optimization strategies in priority order |
| [warning_messages_explained.md](warning_messages_explained.md) | What Stan warnings mean and how to respond |
| [cmdstan_common_issues.md](cmdstan_common_issues.md) | CmdStan/CmdStanR/CmdStanPy installation and runtime troubleshooting |
