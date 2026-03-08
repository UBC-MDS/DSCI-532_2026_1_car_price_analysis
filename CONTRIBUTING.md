# Contributing

Contributions of all kinds are welcome here, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Module Ownership

The following ownership rules apply to files in `src/`:


| File / Area              | Owner                                           | Notes                                   |
| ------------------------ | ----------------------------------------------- | --------------------------------------- |
| `src/data_processing.py` | @tanav2202                                      | Data loading, filtering, constants      |
| `src/charts.py`          | @tanav2202 @Eric-Wong97 @quandothoang @limorwin | Chart/figure generation functions       |
| `src/app.py` (AI tab)    | @Eric-Wong97 @quandothoang                      | AI Assistant tab, querychat integration |
| `src/app.py` (general)   | @tanav2202 @Eric-Wong97 @quandothoang @limorwin | Overview, EDA tab, layout, wiring       |


Coordinate with the owner when making significant changes to their modules.

## Branch Naming Conventions

Use the following prefixes for branch names:

- `feat/` — New features (e.g. `feat/currency-selector`)
- `fix/` — Bug fixes (e.g. `fix/price-filter-bug`)
- `docs/` — Documentation only (e.g. `docs/contributing-update`)
- `refactor/` — Code refactoring (e.g. `refactor/modularize-app`)

## Pull Request Rules

1. **No self-merges** — Authors must not merge their own PRs.
2. **Review required** — At least one reviewer approval is required before merging any code-bearing PR.
3. **Link to issues** — Use `Closes #X` (or `Fixes #X`) in the PR description body to link the PR to the relevant issue(s).
4. **Design note** — Every PR description must include a brief design note explaining the approach, trade-offs, or rationale for the changes.

### Report Bugs

Report bugs at [https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis/issues](https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis/issues) .

**If you are reporting a bug, please follow the template guidelines. The more
detailed your report, the easier and thus faster we can help you.**

### Fix Bugs

Look through the GitHub issues for bugs. When you decide to work onan issue, please assign yourself to it and add a comment that you'll be working on that,  
too. 

### Write Documentation

We could always use more documentation, whether as part of the official
documentation, in docstrings, or even on the web in blog posts, articles, and such.
Just [open an issue](https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis/issues)
to let us know what you will be working on so that we can provide you with guidance.

### Submit Feedback

The best way to send feedback is to file an issue at
[https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis/issues](https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis/issues) . If your feedback fits the format of one of
the issue templates, please use that. Remember that this is a volunteer-driven
project and everybody has limited time.

## Get Started!

Ready to contribute? Here's how to set it up for local development.

1. Fork the [https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis](https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis) repository on GitHub.
2. Clone your fork locally (*if you want to work locally*)
  ```shell
    git clone git@github.com:UBC-MDS/DSCI-532_2026_1_car_price_analysis.git
  ```
3. Create a branch for local development using the default branch (typically `main`) as a starting point. Use `feat/` or `fix/` as a prefix for your branch name.
  ```shell
    git checkout main
    git checkout -b feat-name-of-your-feature
  ```
    Now you can make your changes locally.
4. Commit your changes and push your branch to GitHub. Please use [semantic
  commit messages]([https://www.conventionalcommits.org/](https://www.conventionalcommits.org/)).
5. Open the link displayed in the message when pushing your new branch in order
  to submit a pull request.

### Pull Request Guidelines

Before you submit a pull request, please check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your
  new functionality into a function with a docstring.
3. Your pull request will automatically be checked by the full test suite.
  It needs to pass all of them before it can be considered for merging.
4. Include `Closes #X` in the description to link to the issue.
5. Include a brief design note in the PR description.

