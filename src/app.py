from functools import partial
from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import querychat
from dotenv import load_dotenv
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import page_navbar

# ── Environment & Data ──────────────────────────────────────────
_dotenv_loaded = load_dotenv(Path(__file__).resolve().parents[1] / ".env")
github_model = os.getenv("GITHUB_MODEL", "gpt-4.1-mini")

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "global_cars_enhanced.csv"
data = pd.read_csv(DATA_PATH)

brand_choices = sorted(data["Brand"].unique().tolist())
body_type_choices = sorted(data["Body_Type"].unique().tolist())
fuel_type_choices = sorted(data["Fuel_Type"].unique().tolist())
price_min = int(data["Price_USD"].min())
price_max = int(data["Price_USD"].max())

SUSTAINABLE_FUEL_DEFAULTS = [fuel for fuel in ["Hybrid", "Electric"] if fuel in fuel_type_choices]
if not SUSTAINABLE_FUEL_DEFAULTS:
    SUSTAINABLE_FUEL_DEFAULTS = fuel_type_choices

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

PLOT_COLORS = {
    "brand": "#34495e",
    "fallback": "#999999",
}

AI_TEST_PROMPTS = [
    "Show only hybrid and electric vehicles under $35,000 with efficiency score above 0.6",
    "Compare average price by fuel type for SUV body type",
    "Return the top 8 brands by average efficiency score",
]


def _as_selection(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _selection_label(selected_values, all_values):
    selected = _as_selection(selected_values)
    if not selected or set(selected) == set(all_values):
        return "All"
    return ", ".join(selected)

# ── Querychat Setup (OOP API) ──────────────────────────────────
qc = querychat.QueryChat(
    data,
    "global_cars_enhanced",
    client=f"github/{github_model}",
    greeting=(
        "Hello! I can help you explore the car price dataset. "
        "Try asking things like:\n"
        "- *Show only hybrid and electric vehicles under $35,000 with efficiency score above 0.6*\n"
        "- *Which brands have the highest average price?*\n"
        "- *Filter to cars under $30,000 with efficiency score above 0.5*"
    ),
)

# Initialize querychat server (must be at top level in Express)
chat = qc.server()

# ── Page Setup ──────────────────────────────────────────────────
ui.page_opts(
    title="Car Prices",
    page_fn=partial(page_navbar, id="page"),
)

# ════════════════════════════════════════════════════════════════
# Tab 1: Overview
# ════════════════════════════════════════════════════════════════
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

# ════════════════════════════════════════════════════════════════
# Tab 2: EDA
# ════════════════════════════════════════════════════════════════
with ui.nav_panel("EDA"):
    ui.h2("EDA")

    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_selectize(
                "input_brand",
                "Brand",
                choices=brand_choices,
                selected=[],
                multiple=True,
                options={"placeholder": "All brands"},
            )
            ui.input_selectize(
                "input_body_type",
                "Body Type",
                choices=body_type_choices,
                selected=[],
                multiple=True,
                options={"placeholder": "All body types"},
            )
            ui.input_slider(
                "input_price_range",
                "Price range (USD)",
                min=price_min,
                max=price_max,
                value=(price_min, price_max),
                pre="$",
            )
            ui.input_selectize(
                "input_fuel_type",
                "Fuel Type",
                choices=fuel_type_choices,
                selected=SUSTAINABLE_FUEL_DEFAULTS,
                multiple=True,
                options={"placeholder": "All fuel types"},
            )
            ui.input_action_button("reset_btn", "Reset Filters")

        @reactive.calc
        def filtered_df():
            df = data.copy()

            selected_brands = _as_selection(input.input_brand())
            if selected_brands:
                df = df[df["Brand"].isin(selected_brands)]

            selected_body_types = _as_selection(input.input_body_type())
            if selected_body_types:
                df = df[df["Body_Type"].isin(selected_body_types)]

            price_low, price_high = input.input_price_range()
            df = df[(df["Price_USD"] >= price_low) & (df["Price_USD"] <= price_high)]

            selected_fuels = _as_selection(input.input_fuel_type())
            if selected_fuels:
                df = df[df["Fuel_Type"].isin(selected_fuels)]

            return df

        @reactive.calc
        def filter_state_text():
            brand_label = _selection_label(input.input_brand(), brand_choices)
            body_type_label = _selection_label(input.input_body_type(), body_type_choices)
            fuel_type_label = _selection_label(input.input_fuel_type(), fuel_type_choices)
            price_low, price_high = input.input_price_range()
            count = len(filtered_df())
            return (
                f"Current filters -> Brand: {brand_label} | Body Type: {body_type_label} | "
                f"Fuel Type: {fuel_type_label} | Price: ${price_low:,} to ${price_high:,} | "
                f"Vehicles: {count:,}"
            )

        @reactive.calc
        def summary_kpis():
            df = filtered_df()
            count = int(len(df))
            avg_price = float(df["Price_USD"].mean()) if count > 0 else None
            return {"count": count, "avg_price": avg_price}

        @reactive.effect
        @reactive.event(input.reset_btn)
        def _reset_filters():
            ui.update_selectize("input_brand", selected=[])
            ui.update_selectize("input_body_type", selected=[])
            ui.update_selectize("input_fuel_type", selected=SUSTAINABLE_FUEL_DEFAULTS)
            ui.update_slider(
                "input_price_range",
                value=(price_min, price_max),
            )

        with ui.card():
            ui.card_header("Current filter state")

            @render.text
            def current_filter_state():
                return filter_state_text()

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
                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
                        ax.axis("off")
                        return fig

                    ax.bar(
                        df["Fuel_Type"],
                        df["Price_USD"],
                        color=[FUEL_COLORS.get(fuel, PLOT_COLORS["fallback"]) for fuel in df["Fuel_Type"]],
                        edgecolor="white",
                    )
                    ax.set_xlabel("Fuel Type")
                    ax.set_ylabel("Average Price (USD)")
                    ax.set_title("Average Price by Fuel Type")
                    ax.grid(True, axis="y", alpha=0.3)
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

                    ax.bar(agg["Brand"], agg["Price_USD"], color=PLOT_COLORS["brand"], edgecolor="white")
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
                            color=FUEL_COLORS.get(fuel, PLOT_COLORS["fallback"]),
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

        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
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
                            color=FUEL_COLORS.get(fuel, PLOT_COLORS["fallback"]),
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

            with ui.card():
                ui.card_header("Manufacture Year vs. Mileage")
                ui.p("Placeholder — future chart")

# ════════════════════════════════════════════════════════════════
# Tab 3: AI Assistant (querychat)
# ════════════════════════════════════════════════════════════════
with ui.nav_panel("AI Assistant"):
    ui.h2("AI Assistant")

    with ui.layout_sidebar():
        with ui.sidebar(width=400):
            qc.ui()
            ui.hr()
            ui.p("Prompts tested for AI visuals:")
            ui.tags.ul(*[ui.tags.li(prompt) for prompt in AI_TEST_PROMPTS])

        # Dataframe output
        with ui.card():
            ui.card_header("Filtered Data")

            @render.data_frame
            def ai_data_table():
                return chat.df()

        # Download button
        with ui.card():
            @render.download(label="Download filtered data", filename="filtered_cars.csv")
            def download_filtered():
                yield chat.df().to_csv(index=False)

        with ui.card():
            ui.card_header("AI query result state")

            @render.text
            def ai_filter_state_text():
                df = chat.df()
                return f"Rows: {len(df):,} | Columns: {len(df.columns):,}"

        # 2 charts consuming querychat filtered df
        with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
            with ui.card():
                ui.card_header("Engine Size vs. Efficiency (AI Filtered)")

                @render.plot
                def ai_scatter_engine():
                    df = chat.df()
                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for current query.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    if "Fuel_Type" not in df.columns or "Engine_CC" not in df.columns:
                        ax.text(0.5, 0.5, "Required columns not in query result.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    for fuel, group in df.groupby("Fuel_Type"):
                        ax.scatter(
                            group["Engine_CC"],
                            group["Efficiency_Score"],
                            label=fuel,
                            color=FUEL_COLORS.get(fuel, PLOT_COLORS["fallback"]),
                            alpha=0.7,
                            edgecolors="white",
                            linewidth=0.5,
                            s=50,
                        )

                    ax.set_xlabel("Engine Size (CC)")
                    ax.set_ylabel("Performance Efficiency")
                    ax.set_title("Engine Size vs. Efficiency")
                    ax.legend(title="Fuel Type", fontsize=8, title_fontsize=9)
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    return fig

            with ui.card():
                ui.card_header("Avg Efficiency: Hybrid vs Standard (AI Filtered)")

                @render.plot
                def ai_bar_efficiency():
                    df = chat.df()
                    fig, ax = plt.subplots(figsize=(6, 4))

                    if df.empty:
                        ax.text(0.5, 0.5, "No data for current query.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    if "Fuel_Type" not in df.columns or "Efficiency_Score" not in df.columns:
                        ax.text(0.5, 0.5, "Required columns not in query result.",
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
                    agg = agg.sort_values("Fuel_Group").dropna()

                    if agg.empty:
                        ax.text(0.5, 0.5, "No fuel group data available.",
                                ha="center", va="center", transform=ax.transAxes)
                        return fig

                    bars = ax.bar(
                        agg["Fuel_Group"],
                        agg["Efficiency_Score"],
                        color=[GROUP_COLORS.get(g, PLOT_COLORS["fallback"]) for g in agg["Fuel_Group"]],
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
                    ax.set_title("Hybrid vs Standard Fuel Efficiency")
                    ax.set_ylim(0, 1)
                    ax.grid(True, axis="y", alpha=0.3)
                    fig.tight_layout()
                    return fig

        with ui.card():
            ui.card_header("Average Price by Fuel Type (AI Filtered)")

            @render.plot
            def ai_fuel_price_plot():
                df = chat.df()
                fig, ax = plt.subplots(figsize=(6, 4))

                if df.empty:
                    ax.text(0.5, 0.5, "No data for current query.",
                            ha="center", va="center", transform=ax.transAxes)
                    return fig

                if "Fuel_Type" not in df.columns or "Price_USD" not in df.columns:
                    ax.text(0.5, 0.5, "Required columns not in query result.",
                            ha="center", va="center", transform=ax.transAxes)
                    return fig

                agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean().dropna()
                if agg.empty:
                    ax.text(0.5, 0.5, "No fuel price data available.",
                            ha="center", va="center", transform=ax.transAxes)
                    return fig

                ax.bar(
                    agg["Fuel_Type"],
                    agg["Price_USD"],
                    color=[FUEL_COLORS.get(fuel, PLOT_COLORS["fallback"]) for fuel in agg["Fuel_Type"]],
                    edgecolor="white",
                )
                ax.set_xlabel("Fuel Type")
                ax.set_ylabel("Average Price (USD)")
                ax.set_title("Average Price by Fuel Type")
                ax.grid(True, axis="y", alpha=0.3)
                fig.tight_layout()
                return fig
