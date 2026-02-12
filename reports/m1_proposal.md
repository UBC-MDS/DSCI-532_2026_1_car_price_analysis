## Section 1: Motivation and Purpose

**Our role:** Data scientist consultancy firm  
**Target audience:** Car buyers

Purchasing a car is one of the largest financial decisions most people make, yet the automotive market is complex — prices vary significantly based on brand, body type, fuel type, engine specifications, and manufacturing origin. Buyers often struggle to assess whether a vehicle is fairly priced relative to comparable options, or to understand which features drive price differences.

To address this, we propose building an interactive dashboard that allows car buyers to explore pricing patterns across different vehicle attributes. The app will visualize how factors such as brand, fuel type, body type, and engine performance relate to price, enabling buyers to compare vehicles, identify good-value segments, and make more informed purchasing decisions.
## Section 2: Description of the Data

We will be visualizing a dataset of 300 vehicles from the global automotive market. Each vehicle has 16 associated variables describing:

- **Vehicle identity and brand:** `Car_ID`, `Brand` (10 brands including Toyota, BMW, Tesla, Ford, etc.), `Manufacturing_Country` (6 countries: USA, Germany, Japan, South Korea, China, UK)
- **Vehicle specifications:** `Body_Type` (SUV, Sedan, Coupe, Hatchback, Pickup), `Fuel_Type` (Petrol, Diesel, Hybrid, Electric), `Transmission` (Manual, Automatic), `Engine_CC` (1,001–4,994), `Horsepower` (100–550)
- **Performance and value metrics:** `Mileage_km_per_l` (fuel efficiency), `Price_USD` (~$5,000–$100,000, mean ~$50,000), `Efficiency_Score`, `HP_per_CC` (power density)
- **Age-related features:** `Manufacture_Year` (2005–2025), `Car_Age`, `Age_Category` (New, Recent, Moderate, Old)
- **Derived price segment:** `Price_Category` (Budget, Mid-Range, Premium, Luxury)

Variables like `Brand`, `Body_Type`, and `Fuel_Type` allow buyers to compare pricing across vehicle segments. `Horsepower`, `Mileage_km_per_l`, and `Efficiency_Score` help assess performance-to-value tradeoffs. `Car_Age` and `Price_Category` enable filtering to match budget constraints, while `Manufacturing_Country` supports buyers who have origin preferences.
## Section 3: Research Questions & Usage Scenarios

User Story 1: As a luxury car buyer, I want to explore which brands and vehicle characteristics that consistently fall into the highest price segment in order to choose a premium status vehicle that matches my expectations.

User Story 2: As an environmentally conscious Uber driver, I want to compare hybrid vehicles with standard fuel vehicles in terms of pricing and performance efficiency in order to understand the true cost premium of greener technology while ensuring reliability, maximizing passenger capacity, and keeping operating costs low.

User Story 3: As an automotive market analyst, I want to study how engineering efficiency and vehicle age together influence pricing across segments in order to determine whether buyers pay more for newer, more optimized cars.

## Section 4: Exploratory Data Analysis

The first plot shows what type of fuel is the most efficient. Efficiency score is the normalized fuel efficiency of the vehicle. Our user may prioritize fuel efficiency when purchasing a car as any expense/running costs will eat into the revenue as an environmentally concious Uber/Lyft driver. The second plot shows the relationship between the price category and the efficiency score. This is important to understand as it may be the case that more expensive cars are more fuel efficient, which may be a factor in the user's decision making process when purchasing a car for ridesharing purposes. A high upfront cost may be justified if the car is more fuel efficient and thus has lower running costs, which may be more important to the user than the initial purchase price.

You may find this analysis in [notebooks/eda_analysis.ipynb](../notebooks/eda_analysis.ipynb).



## Section 5: App Sketch & Description


![Sketch](../img/Sketch.png)



The sketch illustrates a single page dashboard that enables comparison between hybrid and standard fuel vehicles across price category, efficiency, body type, and engine size.
It is designed for an environmentally conscious Uber driver to compare hybrid vehicles with standard fuel vehicles. The landing area at the top left provides a short title and  at the top right it includes a legend indicating fuel type (Hybrid vs Fuel), which is consistently encoded by color across all charts.

A filter panel on the left allows users to narrow the dataset while preserving the hybrid vs. fuel comparison. Filters include engine size, price category, performance efficiency, and body type.

The main chart visualizes vehicle distribution across price categories, split by fuel type, to highlight the cost premium of greener technology. Three supporting charts provide complementary insights: average performance efficiency (efficiency_score) by fuel type, Passenger capacity distribution (body type) by fuel type to assess ride suitability, and a scatter plot of engine size  vs. performance efficiency (efficiency_score) to reveal performance trade offs. Users can hover over chart elements to see tooltips with exact values (counts, averages, and points).
