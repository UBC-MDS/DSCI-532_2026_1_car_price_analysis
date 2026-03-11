"""
charts.py
=========
Pure Python module — no Shiny dependencies.
All functions accept a DataFrame and return a matplotlib Figure.
"""

import sys
from pathlib import Path

# Ensure src/ is on the import path (needed for Posit Connect)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import altair as alt
import pandas as pd

from data_processing import (
    AI_ENGINE_EFFICIENCY_COLORS,
    AI_FUEL_GROUP_COLORS,
    AI_FUEL_PRICE_COLORS,
    EDA_ENGINE_EFFICIENCY_COLORS,
    EDA_FUEL_GROUP_COLORS,
    EDA_HP_PRICE_COLORS,
    FIG_HEIGHT,
    FIG_WIDTH,
    make_currency_formatter,
    PLOT_FALLBACK_COLOR,
    usd_formatter,
)


# ── Shared helper ─────────────────────────────────────────────────
def _empty_fig(message: str = "No data for selected filters.") -> plt.Figure:
    """Return a blank figure with a centred message."""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.axis("off")
    return fig


def _add_fuel_group(df: pd.DataFrame) -> pd.DataFrame:
    """Append a Fuel_Group column (Hybrid vs Standard Fuel)."""
    df = df.copy()
    df["Fuel_Group"] = df["Fuel_Type"].apply(
        lambda x: "Hybrid" if x == "Hybrid" else "Standard Fuel"
    )
    return df


def _empty_altair_fig(message: str = "No data for selected filters.") -> alt.Chart:
    """Return a blank Altair chart with a centred message."""
    return (
        alt.Chart(pd.DataFrame({"message": [message]}))
        .mark_text(align="center", baseline="middle", fontSize=14, color="#4b5563")
        .encode(text="message:N")
        .properties(width=FIG_WIDTH * 80, height=FIG_HEIGHT * 80)
    )


# ════════════════════════════════════════════════════════════════
# EDA Charts
# ════════════════════════════════════════════════════════════════

def chart_fuel_avg_price(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> plt.Figure:
    """Bar chart — average Price_USD by Fuel_Type (EDA tab)."""
    agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean()
    agg["Price_display"] = agg["Price_USD"] * currency_rate

    if agg.empty:
        return _empty_fig()

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.96, bottom=0.20, top=0.92)

    bars = ax.bar(agg["Fuel_Type"], agg["Price_display"])
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{currency_sym}{height:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_xlabel("Fuel Type")
    ax.set_ylabel(f"Average Price ({currency_sym})")
    ax.yaxis.set_major_formatter(make_currency_formatter(currency_sym))
    ax.grid(False)
    return fig


def chart_brand_avg_price(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> plt.Figure:
    """Bar chart — average Price_USD by Brand, sorted descending (EDA tab)."""
    if df.empty:
        return _empty_fig()

    agg = (
        df.groupby("Brand", as_index=False)["Price_USD"]
        .mean()
        .sort_values("Price_USD", ascending=False)
    )
    agg["Price_display"] = agg["Price_USD"] * currency_rate

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.96, bottom=0.20, top=0.92)

    bars = ax.bar(agg["Brand"], agg["Price_display"])
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{currency_sym}{height:,.0f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_xlabel("Brand")
    ax.set_ylabel(f"Average Price ({currency_sym})")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.yaxis.set_major_formatter(make_currency_formatter(currency_sym))
    ax.grid(False)
    return fig


def chart_brand_avg_price_interactive(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> alt.Chart:
    """Interactive bar chart of average Price_USD by Brand for the EDA tab."""
    if df.empty:
        return alt.Chart(pd.DataFrame({"message": ["No data for selected filters."]})).mark_text(
            align="center",
            baseline="middle",
            fontSize=14,
            color="#4b5563",
        ).encode(text="message:N").properties(width=FIG_WIDTH * 80, height=FIG_HEIGHT * 80)

    agg = (
        df.groupby("Brand", as_index=False)["Price_USD"]
        .mean()
        .sort_values("Price_USD", ascending=False)
    )
    agg["Price_display"] = agg["Price_USD"] * currency_rate

    brand_pick = alt.selection_point(name="brand_pick", fields=["Brand"], empty=True)

    return (
        alt.Chart(agg)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Brand:N", sort=None, title="Brand", axis=alt.Axis(labelAngle=-35)),
            y=alt.Y(
                "Price_display:Q",
                title=f"Average Price ({currency_sym})",
                axis=alt.Axis(format=",.0f"),
            ),
            color=alt.condition(
                brand_pick,
                alt.value("#3b82f6"),
                alt.value("#bfd7ea"),
            ),
            tooltip=[
                alt.Tooltip("Brand:N", title="Brand"),
                alt.Tooltip("Price_display:Q", title=f"Average Price ({currency_sym})", format=",.0f"),
            ],
        )
        .add_params(brand_pick)
        .properties(width="container", height=320)
        .configure_view(stroke=None)
    )


def chart_engine_efficiency_scatter(df: pd.DataFrame) -> plt.Figure:
    """Scatter — Engine_CC vs Efficiency_Score, coloured by Fuel_Type (EDA tab)."""
    if df.empty:
        return _empty_fig()

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.78, bottom=0.20, top=0.92)

    for fuel, group in df.groupby("Fuel_Type"):
        ax.scatter(
            group["Engine_CC"],
            group["Efficiency_Score"],
            label=fuel,
            color=EDA_ENGINE_EFFICIENCY_COLORS.get(fuel, PLOT_FALLBACK_COLOR),
            alpha=0.7,
            edgecolors="white",
            linewidth=0.5,
            s=50,
        )

    ax.set_xlabel("Engine Size (CC)")
    ax.set_ylabel("Performance Efficiency")
    ax.legend(
        title="Fuel Type",
        fontsize=8,
        title_fontsize=9,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        frameon=False,
    )
    ax.grid(False)
    return fig


def chart_fuel_group_efficiency(df: pd.DataFrame) -> plt.Figure:
    """Bar chart — avg Efficiency_Score for Hybrid vs Standard Fuel (EDA tab)."""
    if df.empty:
        return _empty_fig()

    df = _add_fuel_group(df)
    agg = df.groupby("Fuel_Group", as_index=False)["Efficiency_Score"].mean()

    order = ["Hybrid", "Standard Fuel"]
    agg["Fuel_Group"] = pd.Categorical(agg["Fuel_Group"], categories=order, ordered=True)
    agg = agg.sort_values("Fuel_Group")

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.96, bottom=0.20, top=0.92)

    bars = ax.bar(
        agg["Fuel_Group"],
        agg["Efficiency_Score"],
        color=[EDA_FUEL_GROUP_COLORS.get(g, PLOT_FALLBACK_COLOR) for g in agg["Fuel_Group"]],
        width=0.5,
        edgecolor="white",
    )
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Avg Performance Efficiency")
    ax.set_ylim(0, 1)
    ax.grid(False)
    return fig


def chart_hp_price_scatter(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> plt.Figure:
    """Scatter — Horsepower vs Price_USD, coloured by Fuel_Type (EDA tab)."""
    if df.empty:
        return _empty_fig()

    df = df.dropna(subset=["Horsepower", "Price_USD"]).copy()
    df["Price_display"] = df["Price_USD"] * currency_rate

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.78, bottom=0.20, top=0.92)

    for fuel, group in df.groupby("Fuel_Type"):
        ax.scatter(
            group["Horsepower"],
            group["Price_display"],
            label=fuel,
            color=EDA_HP_PRICE_COLORS.get(fuel, PLOT_FALLBACK_COLOR),
            alpha=0.7,
            edgecolors="white",
            linewidth=0.5,
            s=50,
        )

    ax.set_xlabel("Horsepower")
    ax.set_ylabel(f"Price ({currency_sym})")
    ax.legend(
        title="Fuel Type",
        fontsize=8,
        title_fontsize=9,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        frameon=False,
    )
    ax.grid(False)
    ax.yaxis.set_major_formatter(make_currency_formatter(currency_sym))
    return fig


# ════════════════════════════════════════════════════════════════
# EDA Interactive Charts  (Altair — tooltips + click-to-filter)
# ════════════════════════════════════════════════════════════════

def chart_fuel_avg_price_interactive(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> alt.Chart:
    """Interactive bar chart — avg Price_USD by Fuel_Type (EDA tab). Click bar to filter."""
    agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean()
    agg["Price_display"] = agg["Price_USD"] * currency_rate

    if agg.empty:
        return _empty_altair_fig()

    fuel_pick = alt.selection_point(name="fuel_pick", fields=["Fuel_Type"], empty=True)

    return (
        alt.Chart(agg)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Fuel_Type:N", title="Fuel Type"),
            y=alt.Y(
                "Price_display:Q",
                title=f"Average Price ({currency_sym})",
                axis=alt.Axis(format=",.0f"),
            ),
            color=alt.condition(
                fuel_pick,
                alt.value("#3b82f6"),
                alt.value("#bfd7ea"),
            ),
            tooltip=[
                alt.Tooltip("Fuel_Type:N", title="Fuel Type"),
                alt.Tooltip("Price_display:Q", title=f"Avg Price ({currency_sym})", format=",.0f"),
            ],
        )
        .add_params(fuel_pick)
        .properties(width="container", height=320)
        .configure_view(stroke=None)
    )


def chart_engine_efficiency_scatter_interactive(df: pd.DataFrame) -> alt.Chart:
    """Scatter — Engine_CC vs Efficiency_Score, coloured by Fuel_Type (EDA tab). Hover + legend click."""
    if df.empty:
        return _empty_altair_fig()

    fuel_sel = alt.selection_point(name="eng_fuel_sel", fields=["Fuel_Type"], bind="legend")

    return (
        alt.Chart(df)
        .mark_circle(size=60, opacity=0.7)
        .encode(
            x=alt.X("Engine_CC:Q", title="Engine Size (CC)"),
            y=alt.Y("Efficiency_Score:Q", title="Performance Efficiency"),
            color=alt.Color("Fuel_Type:N", title="Fuel Type"),
            opacity=alt.condition(fuel_sel, alt.value(0.8), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("Brand:N", title="Brand"),
                alt.Tooltip("Fuel_Type:N", title="Fuel Type"),
                alt.Tooltip("Engine_CC:Q", title="Engine CC", format=","),
                alt.Tooltip("Efficiency_Score:Q", title="Efficiency", format=".2f"),
                alt.Tooltip("Price_USD:Q", title="Price (USD)", format=",.0f"),
            ],
        )
        .add_params(fuel_sel)
        .properties(width="container", height=320)
        .configure_view(stroke=None)
    )


def chart_fuel_group_efficiency_interactive(df: pd.DataFrame) -> alt.Chart:
    """Bar chart — avg Efficiency_Score for Hybrid vs Standard Fuel (EDA tab). Hover tooltip."""
    if df.empty:
        return _empty_altair_fig()

    df = _add_fuel_group(df)
    agg = df.groupby("Fuel_Group", as_index=False)["Efficiency_Score"].mean()

    order = ["Hybrid", "Standard Fuel"]
    agg["Fuel_Group"] = pd.Categorical(agg["Fuel_Group"], categories=order, ordered=True)
    agg = agg.sort_values("Fuel_Group")

    return (
        alt.Chart(agg)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, width=80)
        .encode(
            x=alt.X("Fuel_Group:N", title=None, sort=order),
            y=alt.Y(
                "Efficiency_Score:Q",
                title="Avg Performance Efficiency",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".1f"),
            ),
            color=alt.Color(
                "Fuel_Group:N",
                scale=alt.Scale(
                    domain=["Hybrid", "Standard Fuel"],
                    range=["#5f0f40", "#ff7f51"],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Fuel_Group:N", title="Group"),
                alt.Tooltip("Efficiency_Score:Q", title="Avg Efficiency", format=".2f"),
            ],
        )
        .properties(width="container", height=320)
        .configure_view(stroke=None)
    )


def chart_hp_price_scatter_interactive(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> alt.Chart:
    """Scatter — Horsepower vs Price_USD, coloured by Fuel_Type (EDA tab). Hover + legend click."""
    if df.empty:
        return _empty_altair_fig()

    df = df.dropna(subset=["Horsepower", "Price_USD"]).copy()
    df["Price_display"] = df["Price_USD"] * currency_rate

    fuel_sel = alt.selection_point(name="hp_fuel_sel", fields=["Fuel_Type"], bind="legend")

    return (
        alt.Chart(df)
        .mark_circle(size=60, opacity=0.7)
        .encode(
            x=alt.X("Horsepower:Q", title="Horsepower"),
            y=alt.Y(
                "Price_display:Q",
                title=f"Price ({currency_sym})",
                axis=alt.Axis(format=",.0f"),
            ),
            color=alt.Color("Fuel_Type:N", title="Fuel Type"),
            opacity=alt.condition(fuel_sel, alt.value(0.8), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("Brand:N", title="Brand"),
                alt.Tooltip("Fuel_Type:N", title="Fuel Type"),
                alt.Tooltip("Horsepower:Q", title="Horsepower", format=","),
                alt.Tooltip("Price_display:Q", title=f"Price ({currency_sym})", format=",.0f"),
            ],
        )
        .add_params(fuel_sel)
        .properties(width="container", height=320)
        .configure_view(stroke=None)
    )


# ════════════════════════════════════════════════════════════════
# AI Tab Charts  (consume querychat filtered df)
# ════════════════════════════════════════════════════════════════

def ai_chart_engine_efficiency_scatter(df: pd.DataFrame) -> plt.Figure:
    """Scatter — Engine_CC vs Efficiency_Score, AI tab palette."""
    if df.empty:
        return _empty_fig("No data for current query.")

    required = {"Fuel_Type", "Engine_CC", "Efficiency_Score"}
    if not required.issubset(df.columns):
        return _empty_fig("Required columns not in query result.")

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))

    for fuel, group in df.groupby("Fuel_Type"):
        ax.scatter(
            group["Engine_CC"],
            group["Efficiency_Score"],
            label=fuel,
            color=AI_ENGINE_EFFICIENCY_COLORS.get(fuel, PLOT_FALLBACK_COLOR),
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


def ai_chart_fuel_group_efficiency(df: pd.DataFrame) -> plt.Figure:
    """Bar chart — Hybrid vs Standard Fuel avg efficiency, AI tab palette."""
    if df.empty:
        return _empty_fig("No data for current query.")

    required = {"Fuel_Type", "Efficiency_Score"}
    if not required.issubset(df.columns):
        return _empty_fig("Required columns not in query result.")

    df = _add_fuel_group(df)
    agg = df.groupby("Fuel_Group", as_index=False)["Efficiency_Score"].mean()

    order = ["Hybrid", "Standard Fuel"]
    agg["Fuel_Group"] = pd.Categorical(agg["Fuel_Group"], categories=order, ordered=True)
    agg = agg.sort_values("Fuel_Group").dropna()

    if agg.empty:
        return _empty_fig("No fuel group data available.")

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))

    bars = ax.bar(
        agg["Fuel_Group"],
        agg["Efficiency_Score"],
        color=[AI_FUEL_GROUP_COLORS.get(g, PLOT_FALLBACK_COLOR) for g in agg["Fuel_Group"]],
        width=0.5,
        edgecolor="white",
    )
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Avg Performance Efficiency")
    ax.set_title("Hybrid vs Standard Fuel Efficiency")
    ax.set_ylim(0, 1)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def ai_chart_fuel_avg_price(
    df: pd.DataFrame, currency_sym: str = "$", currency_rate: float = 1.0
) -> plt.Figure:
    """Bar chart — average Price_USD by Fuel_Type, AI tab palette."""
    if df.empty:
        return _empty_fig("No data for current query.")

    required = {"Fuel_Type", "Price_USD"}
    if not required.issubset(df.columns):
        return _empty_fig("Required columns not in query result.")

    agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean().dropna()
    agg["Price_display"] = agg["Price_USD"] * currency_rate

    if agg.empty:
        return _empty_fig("No fuel price data available.")

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))

    ax.bar(
        agg["Fuel_Type"],
        agg["Price_display"],
        color=[
            AI_FUEL_PRICE_COLORS[i % len(AI_FUEL_PRICE_COLORS)]
            for i in range(len(agg))
        ],
        edgecolor="white",
    )
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel(f"Average Price ({currency_sym})")
    ax.set_title("Average Price by Fuel Type")
    ax.yaxis.set_major_formatter(make_currency_formatter(currency_sym))
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig
