from functools import partial
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from shiny.express import ui, render
from shiny.ui import page_navbar

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "global_cars_enhanced.csv"
data = pd.read_csv(DATA_PATH)

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

    with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
        with ui.card():
            ui.card_header("Average Efficiency Score by Fuel Type")

            @render.plot
            def fuel_eff_plot():
                df = data.groupby("Fuel_Type", as_index=False)["Efficiency_Score"].mean()
                fig, ax = plt.subplots()
                ax.bar(df["Fuel_Type"], df["Efficiency_Score"])
                ax.set_xlabel("Fuel Type")
                ax.set_ylabel("Average Efficiency Score")
                ax.set_title("Average Efficiency Score by Fuel Type")
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
