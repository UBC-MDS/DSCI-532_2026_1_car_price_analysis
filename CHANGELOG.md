## [0.4.0]

### Added
- Chart captions explaining Efficiency Score and scatter plot interpretation (addressing feedback #73 via #84).
- Example prompt suggestions in the Querychat interface with copyable span components (#76).
- Playwright tests verifying core dashboard behaviors.
- Unit tests for refactored chart logic functions.
- Parquet dataset stored in `data/processed/` for improved data loading architecture (#92).
- DuckDB + ibis integration enabling lazy filtering before data enters memory (#92).
- M4 Feedback Prioritization issue created and tracked to organize instructor, TA, and peer feedback (#83).

### Changed
- Refactored charts/app to use Altair for improved interactivity compared to Matplotlib static plots (#75).
- Improved Querychat interface with scrollable chat output to prevent layout distortion (addressing TA feedback via #81).
- Updated data pipeline to use Parquet + DuckDB queries instead of loading CSV directly (#92).
- Updated dependencies and environment configuration to support new architecture and testing tools.

### Fixed
- Querychat now handles missing or non-existent columns and returns helpful suggestions instead of failing (#85).

### Known Issues
- Scatter plots may still show limited visible trends depending on filter combinations due to dataset size.
- Querychat responses depend on external model availability and environment variables for API access.

### Release Highlight: Interactive Plot Filtering

The dashboard now supports interactive plot driven filtering, allowing users to click visual elements such as bars or points to dynamically filter the underlying dataset and update the rest of the dashboard. This improves exploratory analysis by enabling users to move seamlessly between visual summaries and filtered views of the data.

- **Option chosen:** D — Component click event interaction
- **PR:** #75
- **Why this option over the others:** Interactive filtering aligns directly with the exploratory goals of the dashboard and enhances the user's ability to investigate pricing patterns through visual interactions rather than only sidebar controls.
- **Feature prioritization issue link:** #70

### Collaboration
- **CONTRIBUTING.md:** Updated via PR #87 documenting M3 retrospective and M4 collaboration norms.
- **M3 retrospective:** The team improved documentation of decisions and clarified responsibilities for each milestone component.
- **M4:** Work was organized into scoped branches (advanced feature, data architecture, testing, documentation) with peer reviewed pull requests before merging.

### Reflection
The dashboard now provides a more robust exploration experience through interactive filtering, improved AI assistance, and clearer visual explanations. Migrating the data pipeline to Parquet + DuckDB introduces a scalable architecture that better reflects real-world dashboard deployments.

A key limitation remains the small dataset size, which restricts the strength of observable trends in some scatter plots. However, the addition of captions and improved chart explanations helps users interpret the results correctly.

**Trade-off:** Feedback items were prioritized based on usability impact. Layout stability, chart interpretation, and AI error handling were treated as critical, while deeper visual redesigns were considered non-critical.

The most impactful guidance came from the feedback review sessions and lectures on dashboard interactivity and reactive data pipelines, which informed both the interactive filtering feature and the move to database-backed filtering.







## [0.3.0]

### Added
- AI Assistant tab powered by `querychat`.
- AI driven dataframe filtering with table output and data download option.
- Additional visualizations that respond to AI filtered results.
- Multi select filtering support for dashboard controls.
- Default dashboard view shows data filtered for relevant user story.
- Filters are now shown as cards with clear labels and consistent styling.
- Currency selector (USD / CAD / EUR) in EDA sidebar with approximate conversion; prices and value boxes in Overview and EDA charts use selected currency and symbol.
- Modular structure: data logic, chart logic , app using Shiny `@render` / `@reactive`.
- Project docs: `CONTRIBUTING.md` (module ownership, branch naming, PR rules, reviewer rotation) and `CODEOWNERS` for review assignments.
- tests added for edge-case and correctness (empty DataFrame, nulls, type checks, filter correctness, `load_data`, `build_choices`, `build_defaults`, `filter_dataframe`, `compute_kpis`, `as_selection`, `selection_label`).
- smoke tests ensuring all EDA and AI chart functions return valid matplotlib Figure objects.

### Changed
- Improved dashboard UI/UX with a consistent theme and visual hierarchy.
- Added navigation header background to better separate page sections.
- Standardized chart sizing and layout across the dashboard.
- Moved scatter plot legends outside of plots to improve readability.
- Added value labels above bar charts for easier interpretation.
- Improved price formatting using comma-separated USD values (and currency-aware formatting when CAD/EUR selected).
- Overview “Dataset quick stats” made dynamic and currency-aware.

### Fixed
- Inconsistent plot sizing between chart panels.
- Redundant chart titles between card headers and plot titles.
- Fixes for publishing and running the app on Posit Connect.

### Known Issues
- Scatter plots currently use static matplotlib rendering and do not yet support hover tooltips.

### Reflection
- The addition of natural language filtering enables users to explore subsets of the dataset dynamically without relying only on manual filters.
- UI improvements were implemented to improve readability, layout consistency, and overall usability of the dashboard.
- The team also continued improving project structure and collaboration practices to support upcoming milestones.

## [0.2.0]

### Added
- Working Shiny dashboard prototype deployed to Posit Connect Cloud (stable main and auto updating dev preview).
- Sidebar filters for Brand, Body Type, Fuel Type, and Price range.
- Shared reactive filtering (`filtered_df`) across multiple outputs.
- KPI value boxes showing Vehicle Count and Average Price for the current selection.
- EDA visualizations including price summaries and efficiency/performance comparisons.

### Changed
- Updated dashboard layout from the M1 sketch to a multi panel EDA view with summary KPIs and chart cards.

### Fixed
- Improved empty filter state by displaying “No data for selected filters” messages in plots.

### Known Issues
- Color consistency across all fuel categories may be refined for accessibility in future milestones.

### Reflection
- Job Story 1 is implemented through dynamic filtering and brand level price summaries that allow users to identify higher priced vehicle segments.
- Job Story 2 (hybrid vs standard fuel comparison) is implemented through efficiency and price comparisons by fuel type.
- Job Story 3 was revised for M2 to focus on engineering characteristics, using engine size and horsepower scatter plots to analyze pricing and efficiency patterns. Vehicle age analysis is planned for M3.
- The reactive design centers on a shared filtered dataset powering multiple outputs, improving performance and maintainability.
