from functools import partial
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import page_navbar

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "global_cars_enhanced.csv"
data = pd.read_csv(DATA_PATH)
brand_choices = ["All"] + sorted(data["Brand"].unique().tolist())
body_type_choices = ["All"] + sorted(data["Body_Type"].unique().tolist())
fuel_type_choices = ["All"] + sorted(data["Fuel_Type"].unique().tolist())
price_min = int(data["Price_USD"].min())
price_max = int(data["Price_USD"].max())

ui.page_opts(
    title="Car Prices",
    page_fn=partial(page_navbar, id="page"),
)

with ui.nav_panel("Overview"):
    ui.h2("Overview")

    with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
        with ui.card():
            ui.card_header("Project focus")
            ui.p("Explore car pricing patterns across brands and countries.")
            ui.tags.ul(
                ui.tags.li("Target (regression): Price_USD"),
                ui.tags.li("Label (classification): Price_Category"),
            )

        with ui.card():
            ui.card_header("Dataset quick stats")
            ui.tags.ul(
                ui.tags.li("Records: 300"),
                ui.tags.li("Brands: 10"),
                ui.tags.li("Countries: 6"),
                ui.tags.li("Years: 2005–2025"),
                ui.tags.li("Price range: $5,000–$120,000"),
            )
with ui.nav_panel("EDA"):
    ui.h2("EDA")

    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_selectize("input_brand", "Brand", choices=brand_choices, selected="All")
            ui.input_selectize("input_body_type", "Body Type", choices=body_type_choices, selected="All")
            ui.input_slider(
                "input_price_range",
                "Price range (USD)",
                min=price_min,
                max=price_max,
                value=(price_min, price_max),
                pre="$",
            )
            ui.input_selectize("input_fuel_type", "Fuel Type", choices=fuel_type_choices, selected="All")

        @reactive.calc
        def filtered_df():
            df = data.copy()

            if input.input_brand() != "All":
                df = df[df["Brand"] == input.input_brand()]

            if input.input_body_type() != "All":
                df = df[df["Body_Type"] == input.input_body_type()]

            price_low, price_high = input.input_price_range()
            df = df[(df["Price_USD"] >= price_low) & (df["Price_USD"] <= price_high)]

            if input.input_fuel_type() != "All":
                df = df[df["Fuel_Type"] == input.input_fuel_type()]

            return df[["Brand", "Body_Type", "Price_USD", "Fuel_Type"]]

        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
            with ui.card():
                ui.card_header("Average Price by Fuel Type")

                @render.plot
                def fuel_eff_plot():
                    df = filtered_df().groupby("Fuel_Type", as_index=False)["Price_USD"].mean()
                    fig, ax = plt.subplots()

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
                        ax.axis("off")
                        return fig

                    ax.bar(df["Fuel_Type"], df["Price_USD"])
                    ax.set_xlabel("Fuel Type")
                    ax.set_ylabel("Average Price (USD)")
                    ax.set_title("Average Price by Fuel Type")
                    fig.tight_layout()
                    return fig

            with ui.card():
                ui.card_header("Plot 2")
                ui.p("Placeholder: plot title")

        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
            with ui.card():
                ui.card_header("Plot 3")
                ui.p("Placeholder: plot title")

            with ui.card():
                ui.card_header("Plot 4")
                ui.p("Placeholder: plot title")
