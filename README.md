# Hybrid vs Fuel Vehicle Comparison Dashboard

This interactive Shiny dashboard helps environmentally conscious Uber drivers compare hybrid and standard fuel vehicles. It allows users to explore pricing, performance efficiency, engine size, horsepower, and brand trends to better understand the cost benefit tradeoff of greener vehicle technologies.

The dashboard supports informed decision making by enabling dynamic filtering and real time comparison across vehicle attributes.

## Dashboard Links

- **Stable (main):** [Car Price Analysis Dashboard](https://019c91d1-3afa-d970-b785-26d650f700b7.share.connect.posit.cloud/)
- **Preview (dev):** [Development Preview](https://019c91db-1353-42dc-c59a-fb96e3babc9f.share.connect.posit.cloud)

## Demo

![Dashboard Demo](img/demo.gif)

## Features

- Sidebar filters for Brand, Body Type, Fuel Type, and Price Range
- Reactive KPI value boxes (Vehicle Count and Average Price)
- Price comparisons by fuel type and brand
- Engine size vs. performance efficiency visualization
- Horsepower vs. price analysis
- Hybrid vs. standard fuel efficiency comparison

## How to set up and run the dashboard (For Contributors)
#### Clone the repo
```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_1_car_price_analysis.git
cd DSCI-532_2026_1_car_price_analysis
```
#### Set-up the conda environment 
```bash
conda env create -f environment.yml
conda activate car_price_analysis_env
```
#### Run the shiny app 
```bash
shiny run --reload src/app.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.
