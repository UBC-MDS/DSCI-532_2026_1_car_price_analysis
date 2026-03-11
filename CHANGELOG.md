## [0.4.0]

### Changed
- Refactored charts/app to use Altair for improved interactivity compared to Matplotlib static plots.

## [0.3.0]

### Added
- AI Assistant tab powered by `querychat`.
- AI driven dataframe filtering with table output and data download option.
- Additional visualizations that respond to AI filtered results.
- Multi select filtering support for dashboard controls.
- Default dashboard view shows data filtered for relevant user story.
- Filters are now shown as cards with clear labels and consistent styling.

### Changed
- Improved dashboard UI/UX with a consistent theme and visual hierarchy.
- Added navigation header background to better separate page sections.
- Standardized chart sizing and layout across the dashboard.
- Moved scatter plot legends outside of plots to improve readability.
- Added value labels above bar charts for easier interpretation.
- Improved price formatting using comma-separated USD values.

### Fixed
- Inconsistent plot sizing between chart panels.
- Redundant chart titles between card headers and plot titles.

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
