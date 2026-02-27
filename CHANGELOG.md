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
