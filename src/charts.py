"""
charts.py
=========
Pure Python module — no Shiny dependencies.
All functions accept a DataFrame and return a matplotlib Figure.
"""

import matplotlib.pyplot as plt
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


# ════════════════════════════════════════════════════════════════
# EDA Charts
# ════════════════════════════════════════════════════════════════

def chart_fuel_avg_price(df: pd.DataFrame) -> plt.Figure:
    """Bar chart — average Price_USD by Fuel_Type (EDA tab)."""
    agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean()

    if agg.empty:
        return _empty_fig()

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.96, bottom=0.20, top=0.92)

    bars = ax.bar(agg["Fuel_Type"], agg["Price_USD"])
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Average Price (USD)")
    ax.yaxis.set_major_formatter(usd_formatter)
    ax.grid(False)
    return fig


def chart_brand_avg_price(df: pd.DataFrame) -> plt.Figure:
    """Bar chart — average Price_USD by Brand, sorted descending (EDA tab)."""
    if df.empty:
        return _empty_fig()

    agg = (
        df.groupby("Brand", as_index=False)["Price_USD"]
        .mean()
        .sort_values("Price_USD", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.96, bottom=0.20, top=0.92)

    bars = ax.bar(agg["Brand"], agg["Price_USD"])
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,.0f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_xlabel("Brand")
    ax.set_ylabel("Average Price (USD)")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.yaxis.set_major_formatter(usd_formatter)
    ax.grid(False)
    return fig


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


def chart_hp_price_scatter(df: pd.DataFrame) -> plt.Figure:
    """Scatter — Horsepower vs Price_USD, coloured by Fuel_Type (EDA tab)."""
    if df.empty:
        return _empty_fig()

    df = df.dropna(subset=["Horsepower", "Price_USD"])

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.subplots_adjust(left=0.14, right=0.78, bottom=0.20, top=0.92)

    for fuel, group in df.groupby("Fuel_Type"):
        ax.scatter(
            group["Horsepower"],
            group["Price_USD"],
            label=fuel,
            color=EDA_HP_PRICE_COLORS.get(fuel, PLOT_FALLBACK_COLOR),
            alpha=0.7,
            edgecolors="white",
            linewidth=0.5,
            s=50,
        )

    ax.set_xlabel("Horsepower")
    ax.set_ylabel("Price (USD)")
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
    ax.yaxis.set_major_formatter(usd_formatter)
    return fig


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


def ai_chart_fuel_avg_price(df: pd.DataFrame) -> plt.Figure:
    """Bar chart — average Price_USD by Fuel_Type, AI tab palette."""
    if df.empty:
        return _empty_fig("No data for current query.")

    required = {"Fuel_Type", "Price_USD"}
    if not required.issubset(df.columns):
        return _empty_fig("Required columns not in query result.")

    agg = df.groupby("Fuel_Type", as_index=False)["Price_USD"].mean().dropna()

    if agg.empty:
        return _empty_fig("No fuel price data available.")

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))

    ax.bar(
        agg["Fuel_Type"],
        agg["Price_USD"],
        color=[
            AI_FUEL_PRICE_COLORS[i % len(AI_FUEL_PRICE_COLORS)]
            for i in range(len(agg))
        ],
        edgecolor="white",
    )
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Average Price (USD)")
    ax.set_title("Average Price by Fuel Type")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig