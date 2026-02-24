# Hybrid vs Fuel Vehicle Comparison Dashboard

This project presents an interactive dashboard designed to help environmentally conscious Uber drivers compare hybrid and standard fuel vehicles. Using vehicle data from Kaggle, the dashboard enables comparison across price categories, performance efficiency, body type, and engine size. The goal is to support informed decision making around the true cost premium and suitability of greener vehicle technologies.

## Dashboard Links

- **Stable (main):** [Car Price Analysis Dashboard](https://019c91d1-3afa-d970-b785-26d650f700b7.share.connect.posit.cloud/)
- **Preview (dev):** [Development Preview](https://019c91db-1353-42dc-c59a-fb96e3babc9f.share.connect.posit.cloud)

## How to set up and run the dashboard
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
