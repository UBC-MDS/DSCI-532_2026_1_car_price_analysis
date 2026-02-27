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

FUEL_COLORS = {
    "Hybrid": "#1b6c6e",
    "Petrol": "#c0392b",
    "Diesel": "#e67e22",
    "Electric": "#2980b9",
}

GROUP_COLORS = {
    "Hybrid": "#1b6c6e",
    "Standard Fuel": "#c0392b",
}

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

            return df
        
        @reactive.calc
        def summary_kpis():
            df = filtered_df()
            count = int(len(df))
            avg_price = float(df["Price_USD"].mean()) if count > 0 else None
            return {"count": count, "avg_price": avg_price}
        
        # KPI value boxes
        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
            with ui.card():
                ui.card_header("Vehicles in selection")

                @render.ui
                def value_box_count():
                    k = summary_kpis()
                    return ui.value_box(
                        title="Vehicle Count",
                        value=f"{k['count']:,}",
                    )

            with ui.card():
                ui.card_header("Average price")

                @render.ui
                def value_box_avg_price():
                    k = summary_kpis()
                    value = "—" if k["avg_price"] is None else f"${k['avg_price']:,.0f}"
                    return ui.value_box(
                        title="Avg Price (USD)",
                        value=value,
                    )

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
                ui.card_header("Average Price by Brand")

                @render.plot
                def plot_brand_price():
                    df = filtered_df()

                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for selected filters.",
                                ha="center", va="center", transform=ax.transAxes)
                        ax.axis("off")
                        return fig

                    agg = (
                        df.groupby("Brand", as_index=False)["Price_USD"]
                        .mean()
                        .sort_values("Price_USD", ascending=False)
                    )

                    ax.bar(agg["Brand"], agg["Price_USD"])
                    ax.set_xlabel("Brand")
                    ax.set_ylabel("Average Price (USD)")
                    ax.set_title("Average Price by Brand")
                    ax.tick_params(axis="x", rotation=45)
                    ax.grid(True, axis="y", alpha=0.3)

                    fig.tight_layout()
                    return fig

        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
            with ui.card():
                ui.card_header("Engine Size vs. Performance Efficiency")

                @render.plot
                def scatter_engine_efficiency():
                    df = filtered_df()
                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for selected filters.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    for fuel, group in df.groupby("Fuel_Type"):
                        ax.scatter(
                            group["Engine_CC"],
                            group["Efficiency_Score"],
                            label=fuel,
                            color=FUEL_COLORS.get(fuel, "#999999"),
                            alpha=0.7,
                            edgecolors="white",
                            linewidth=0.5,
                            s=50,
                        )

                    ax.set_xlabel("Engine Size (CC)")
                    ax.set_ylabel("Performance Efficiency")
                    ax.set_title("Engine Size vs. Performance Efficiency")
                    ax.legend(title="Fuel Type", fontsize=8, title_fontsize=9)
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    return fig

            with ui.card():
                ui.card_header("Average Performance Efficiency by Fuel Type")

                @render.plot
                def bar_fuel_efficiency():
                    df = filtered_df()
                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for current filters.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    df = df.copy()
                    df["Fuel_Group"] = df["Fuel_Type"].apply(
                        lambda x: "Hybrid" if x == "Hybrid" else "Standard Fuel"
                    )
                    agg = df.groupby("Fuel_Group", as_index=False)["Efficiency_Score"].mean()

                    order = ["Hybrid", "Standard Fuel"]
                    agg["Fuel_Group"] = pd.Categorical(
                        agg["Fuel_Group"], categories=order, ordered=True
                    )
                    agg = agg.sort_values("Fuel_Group")

                    bars = ax.bar(
                        agg["Fuel_Group"],
                        agg["Efficiency_Score"],
                        color=[GROUP_COLORS[g] for g in agg["Fuel_Group"]],
                        width=0.5,
                        edgecolor="white",
                    )

                    for bar in bars:
                        height = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            height + 0.01,
                            f"{height:.2f}",
                            ha="center", va="bottom", fontsize=10, fontweight="bold",
                        )

                    ax.set_ylabel("Avg Performance Efficiency")
                    ax.set_title("Average Performance Efficiency by Fuel Type")
                    ax.set_ylim(0, 1)
                    ax.grid(True, axis="y", alpha=0.3)
                    fig.tight_layout()
                    return fig
        
            with ui.card():
                ui.card_header("Horsepower vs Price")

                @render.plot
                def plot_hp_price():
                    df = filtered_df()

                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for selected filters.",
                            ha="center", va="center", transform=ax.transAxes)
                        ax.axis("off")
                        return fig

                    df = df.dropna(subset=["Horsepower", "Price_USD"])

                    for fuel, group in df.groupby("Fuel_Type"):
                        ax.scatter(
                            group["Horsepower"],
                            group["Price_USD"],
                            label=fuel,
                            color=FUEL_COLORS.get(fuel, "#999999"),
                            alpha=0.7,
                            edgecolors="white",
                            linewidth=0.5,
                            s=50,
                        )

                    ax.set_xlabel("Horsepower")
                    ax.set_ylabel("Price (USD)")
                    ax.set_title("Horsepower vs Price")
                    ax.legend(title="Fuel Type", fontsize=8, title_fontsize=9)
                    ax.grid(True, alpha=0.3)

                    fig.tight_layout()
                    return fig