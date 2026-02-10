## Section 2: Description of the Data

We will be visualizing a dataset of 300 vehicles from the global automotive market. Each vehicle has 16 associated variables describing:

- **Vehicle identity and brand:** `Car_ID`, `Brand` (10 brands including Toyota, BMW, Tesla, Ford, etc.), `Manufacturing_Country` (6 countries: USA, Germany, Japan, South Korea, China, UK)
- **Vehicle specifications:** `Body_Type` (SUV, Sedan, Coupe, Hatchback, Pickup), `Fuel_Type` (Petrol, Diesel, Hybrid, Electric), `Transmission` (Manual, Automatic), `Engine_CC` (1,001–4,994), `Horsepower` (100–550)
- **Performance and value metrics:** `Mileage_km_per_l` (fuel efficiency), `Price_USD` (~$5,000–$100,000, mean ~$50,000), `Efficiency_Score`, `HP_per_CC` (power density)
- **Age-related features:** `Manufacture_Year` (2005–2025), `Car_Age`, `Age_Category` (New, Recent, Moderate, Old)
- **Derived price segment:** `Price_Category` (Budget, Mid-Range, Premium, Luxury)

Variables like `Brand`, `Body_Type`, and `Fuel_Type` allow buyers to compare pricing across vehicle segments. `Horsepower`, `Mileage_km_per_l`, and `Efficiency_Score` help assess performance-to-value tradeoffs. `Car_Age` and `Price_Category` enable filtering to match budget constraints, while `Manufacturing_Country` supports buyers who have origin preferences.
