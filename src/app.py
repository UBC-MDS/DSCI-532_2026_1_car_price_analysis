from functools import partial
from pathlib import Path
import os
import sys

# Ensure src/ is on the import path (needed for Posit Connect)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

querychat = None
try:
    import querychat
except ModuleNotFoundError:
    pass
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import page_navbar
from shinywidgets import reactive_read, render_altair

from charts import (
    ai_chart_engine_efficiency_scatter,
    ai_chart_fuel_avg_price,
    ai_chart_fuel_group_efficiency,
    chart_brand_avg_price_interactive,
    chart_engine_efficiency_scatter_interactive,
    chart_fuel_avg_price_interactive,
    chart_fuel_group_efficiency_interactive,
    chart_hp_price_scatter_interactive,
)
from data_processing import (
    as_selection as _as_selection,
    build_choices,
    build_defaults,
    compute_kpis,
    CURRENCY_RATES,
    CURRENCY_SYMBOLS,
    filter_dataframe,
    load_data,
    selection_label as _selection_label,
    AI_TEST_PROMPTS,
)

# ── Environment & Data ──────────────────────────────────────────
_dotenv_loaded = load_dotenv(Path(__file__).resolve().parents[1] / ".env")
github_model = os.getenv("GITHUB_MODEL", "gpt-4.1-mini")

data = load_data()
choices = build_choices(data)
defaults = build_defaults(choices)

brand_choices = choices["brand_choices"]
body_type_choices = choices["body_type_choices"]
fuel_type_choices = choices["fuel_type_choices"]
price_min = choices["price_min"]
price_max = choices["price_max"]

UBER_BODY_TYPE_DEFAULTS = defaults["body_type_defaults"]
UBER_FUEL_TYPE_DEFAULTS = defaults["fuel_type_defaults"]
UBER_PRICE_DEFAULT_RANGE = defaults["price_default_range"]


qc = None
if querychat is not None:
    qc = querychat.QueryChat(
        data,
        "global_cars_enhanced",
        client=f"github/{github_model}",
        greeting=(
            "Hello! I can help you explore the car price dataset. "
            "Try asking things like:\n"
            '- <span class="suggestion">Show only hybrid and electric vehicles under $35,000 with efficiency score above 0.6</span>\n'
            '- <span class="suggestion">Which brands have the highest average price?</span>\n'
            '- <span class="suggestion">Filter to cars under $30,000 with efficiency score above 0.5</span>'
        ),
    )
# qc.server() is called inside the AI Assistant tab (within active Shiny session)

# ── Page Setup ──────────────────────────────────────────────────
ui.page_opts(
    title="Car Prices",
    page_fn=partial(page_navbar, id="page"),
)

ui.head_content(
    ui.tags.style("""
    body {
        background-color: #f7f9fc;
        color: #243b53;
    }

    .navbar {
        background-color: #16324f !important;
        border-bottom: none !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }

    .navbar-brand,
    .navbar-nav .nav-link {
        color: #f8fafc !important;
        font-weight: 500;
    }

    .navbar-nav .nav-link.active,
    .navbar-nav .nav-link:hover {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.12);
        border-radius: 8px;
    }

    .container-fluid {
        padding-top: 1.25rem;
        padding-bottom: 1.5rem;
    }

    h1 {
        font-size: 2.4rem;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 0.25rem;
    }

    h2 {
        font-size: 1.4rem;
        font-weight: 600;
        color: #243b53;
        margin-bottom: 1rem;
    }

    .card {
        border: none !important;
        border-radius: 16px !important;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.06);
        background-color: #ffffff;
    }

    .card-header {
        background-color: transparent !important;
        border-bottom: none !important;
        font-weight: 600;
        color: #243b53;
    }

    .card-body {
        border: none !important;
    }

    .value-box {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    .sidebar {
        background-color: #ffffff;
        border: none !important;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.06);
        border-radius: 16px;
    }

    p, li, label {
        color: #334e68;
    }

    .btn {
        border-radius: 10px;
    }
    """)
)

# ════════════════════════════════════════════════════════════════
# Tab 1: Overview
# ════════════════════════════════════════════════════════════════
with ui.nav_panel("Overview"):
    ui.h1("Car Prices")
    ui.h2("Overview")

    with ui.layout_columns(col_widths=(6, 6), gap="1rem", equal_height=True):
        with ui.card():
            ui.card_header("Project focus")
            ui.p("Explore car pricing patterns across brands and countries.")
            ui.tags.ul(
                ui.tags.li("Target (regression): Price_USD"),
                ui.tags.li("Label (classification): Price_Category"),
            )

        with ui.card():
            ui.card_header("Dataset quick stats")
            ui.p(
                "Price range uses display currency from EDA tab. Rates are approximate.",
                style="font-size:0.8rem;color:#6b7280;",
            )

            @render.ui
            def overview_dataset_stats():
                n_records = len(data)
                n_brands = data["Brand"].nunique()
                n_countries = data["Manufacturing_Country"].nunique()
                year_min = int(data["Manufacture_Year"].min())
                year_max = int(data["Manufacture_Year"].max())
                p_min = int(data["Price_USD"].min())
                p_max = int(data["Price_USD"].max())
                currency = input.input_currency()
                rate = CURRENCY_RATES[currency]
                sym = CURRENCY_SYMBOLS[currency]
                p_min_disp = int(p_min * rate)
                p_max_disp = int(p_max * rate)
                return ui.tags.ul(
                    ui.tags.li(f"Records: {n_records:,}"),
                    ui.tags.li(f"Brands: {n_brands}"),
                    ui.tags.li(f"Countries: {n_countries}"),
                    ui.tags.li(f"Years: {year_min}–{year_max}"),
                    ui.tags.li(f"Price range: {sym}{p_min_disp:,}–{sym}{p_max_disp:,}"),
                )


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
                selected=UBER_BODY_TYPE_DEFAULTS,
                multiple=True,
                options={"placeholder": "All body types"},
            )
            ui.input_slider(
                "input_price_range",
                "Price range (USD)",
                min=price_min,
                max=price_max,
                value=UBER_PRICE_DEFAULT_RANGE,
                pre="$",
            )
            ui.input_selectize(
                "input_fuel_type",
                "Fuel Type",
                choices=fuel_type_choices,
                selected=UBER_FUEL_TYPE_DEFAULTS,
                multiple=True,
                options={"placeholder": "All fuel types"},
            )
            ui.input_radio_buttons(
                "input_currency",
                "Display currency",
                choices={"USD": "USD", "CAD": "CAD", "EUR": "EUR"},
                selected="USD",
            )
            ui.p("Rates are approximate.", class_="text-muted", style="font-size:0.85rem;")
            ui.input_action_button("reset_btn", "Reset Filters")

        @reactive.calc
        def brand_chart_selection():
            try:
                selection = reactive_read(plot_brand_price.widget.selections, "brand_pick")
            except Exception:
                return []

            if selection is None or selection.value is None:
                return []

            return [item["Brand"] for item in selection.value if "Brand" in item]

        @reactive.calc
        def fuel_chart_selection():
            try:
                selection = reactive_read(fuel_eff_plot.widget.selections, "fuel_pick")
            except Exception:
                return []

            if selection is None or selection.value is None:
                return []

            return [item["Fuel_Type"] for item in selection.value if "Fuel_Type" in item]

        @reactive.calc
        def sidebar_filtered_df():
            selected_brands = _as_selection(input.input_brand())

            return filter_dataframe(
                data,
                brands=selected_brands,
                body_types=_as_selection(input.input_body_type()),
                fuel_types=_as_selection(input.input_fuel_type()),
                price_range=input.input_price_range(),
            )

        @reactive.calc
        def filtered_df():
            clicked_brands = brand_chart_selection()
            clicked_fuels = fuel_chart_selection()

            df = sidebar_filtered_df()
            if clicked_brands:
                df = df[df["Brand"].isin(clicked_brands)]
            if clicked_fuels:
                df = df[df["Fuel_Type"].isin(clicked_fuels)]
            return df

        @reactive.calc
        def filter_state_values():
            selected_brands = brand_chart_selection() or _as_selection(input.input_brand())
            brand_label = _selection_label(selected_brands, brand_choices)
            body_type_label = _selection_label(input.input_body_type(), body_type_choices)
            selected_fuels = fuel_chart_selection() or _as_selection(input.input_fuel_type())
            fuel_type_label = _selection_label(selected_fuels, fuel_type_choices)
            price_low, price_high = input.input_price_range()
            currency = input.input_currency()
            rate = CURRENCY_RATES[currency]
            sym = CURRENCY_SYMBOLS[currency]
            count = len(filtered_df())
            return {
                "brand": brand_label,
                "body_type": body_type_label,
                "fuel_type": fuel_type_label,
                "price": f"{sym}{price_low * rate:,.0f} to {sym}{price_high * rate:,.0f}",
                "vehicles": f"{count:,}",
            }

        @reactive.calc
        def summary_kpis():
            currency = input.input_currency()
            rate = CURRENCY_RATES[currency]
            return compute_kpis(filtered_df(), currency_rate=rate)

        @reactive.effect
        @reactive.event(input.reset_btn)
        def _reset_filters():
            ui.update_selectize("input_brand", selected=[])
            ui.update_selectize("input_body_type", selected=UBER_BODY_TYPE_DEFAULTS)
            ui.update_selectize("input_fuel_type", selected=UBER_FUEL_TYPE_DEFAULTS)
            ui.update_slider(
                "input_price_range",
                value=UBER_PRICE_DEFAULT_RANGE,
            )

        with ui.card():
            ui.card_header("Current filter state")

            @render.ui
            def current_filter_state():
                state = filter_state_values()

                def pill(label, value):
                    return ui.tags.div(
                        ui.tags.span(label, style="font-size:0.75rem;font-weight:600;color:#4b5563;"),
                        ui.tags.span(value, style="font-size:0.9rem;color:#111827;"),
                        style=(
                            "display:flex;flex-direction:column;gap:0.2rem;padding:0.6rem 0.8rem;"
                            "border:1px solid #dbe2ea;border-radius:0.65rem;background:#f8fafc;"
                        ),
                    )

                return ui.tags.div(
                    ui.tags.div(
                        pill("Brand", state["brand"]),
                        pill("Body Type", state["body_type"]),
                        pill("Fuel Type", state["fuel_type"]),
                        pill("Price", state["price"]),
                        pill("Vehicles", state["vehicles"]),
                        style=(
                            "display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));"
                            "gap:0.6rem;"
                        ),
                    ),
                    style="padding:0.25rem 0;",
                )

        # KPI value boxes
        with ui.layout_columns(col_widths=(6, 6), gap="1rem", equal_height=True):
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
                    sym = CURRENCY_SYMBOLS[input.input_currency()]
                    value = "—" if k["avg_price"] is None else f"{sym}{k['avg_price']:,.0f}"
                    return ui.value_box(
                        title=f"Avg Price ({input.input_currency()})",
                        value=value,
                    )

        with ui.layout_columns(col_widths=(6, 6), gap="1rem", equal_height=True):
            with ui.card():
                ui.card_header("Average Price by Fuel Type")

                ui.p(
                    "Click bars to filter the EDA view by fuel type. Click again to clear.",
                    class_="text-muted",
                    style="font-size:0.85rem;",
                )

                @render_altair
                def fuel_eff_plot():
                    return chart_fuel_avg_price_interactive(
                        sidebar_filtered_df(),
                        currency_sym=CURRENCY_SYMBOLS[input.input_currency()],
                        currency_rate=CURRENCY_RATES[input.input_currency()],
                    )

            with ui.card():
                ui.card_header("Average Price by Brand")

                ui.p(
                    "Click bars to filter the EDA view by brand. Clear the selection by clicking the active bar again or clicking empty space.",
                    class_="text-muted",
                    style="font-size:0.85rem;",
                )

                @render_altair
                def plot_brand_price():
                    return chart_brand_avg_price_interactive(
                        sidebar_filtered_df(),
                        currency_sym=CURRENCY_SYMBOLS[input.input_currency()],
                        currency_rate=CURRENCY_RATES[input.input_currency()],
                    )

        with ui.layout_columns(col_widths=(6, 6), gap="1rem", equal_height=True):
            with ui.card():
                ui.card_header("Engine Size vs. Performance Efficiency")

                ui.p(
                    "Hover for details. Click the legend to highlight by fuel type.",
                    class_="text-muted",
                    style="font-size:0.85rem;",
                )

                @render_altair
                def scatter_engine_efficiency():
                    return chart_engine_efficiency_scatter_interactive(filtered_df())

            with ui.card():
                ui.card_header("Average Performance Efficiency by Fuel Type")

                @render_altair
                def bar_fuel_efficiency():
                    return chart_fuel_group_efficiency_interactive(filtered_df())

        with ui.layout_columns(col_widths=(6, 6), gap="1rem", equal_height=True):
            with ui.card():
                ui.card_header("Horsepower vs Price")

                ui.p(
                    "Hover for details. Click the legend to highlight by fuel type.",
                    class_="text-muted",
                    style="font-size:0.85rem;",
                )

                @render_altair
                def plot_hp_price():
                    return chart_hp_price_scatter_interactive(
                        filtered_df(),
                        currency_sym=CURRENCY_SYMBOLS[input.input_currency()],
                        currency_rate=CURRENCY_RATES[input.input_currency()],
                    )

            with ui.card():
                ui.card_header("Manufacture Year vs. Mileage")
                ui.p("Placeholder — future chart")


with ui.nav_panel("AI Assistant"):
    ui.h2("AI Assistant")

    if qc is None:
        ui.p("Install the querychat package to enable the AI Assistant (e.g. conda env: car_price_analysis_env).")
    else:
        chat = qc.server()

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
                    return ai_chart_engine_efficiency_scatter(chat.df())

            with ui.card():
                ui.card_header("Avg Efficiency: Hybrid vs Standard (AI Filtered)")

                @render.plot
                def ai_bar_efficiency():
                    return ai_chart_fuel_group_efficiency(chat.df())

        with ui.card():
            ui.card_header("Average Price by Fuel Type (AI Filtered)")

            @render.plot
            def ai_fuel_price_plot():
                return ai_chart_fuel_avg_price(
                    chat.df(),
                    currency_sym=CURRENCY_SYMBOLS[input.input_currency()],
                    currency_rate=CURRENCY_RATES[input.input_currency()],
                )
