from functools import partial
from pathlib import Path

from shiny.express import ui
from shiny.ui import page_navbar

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
    ui.h2("EDA placeholders")

    with ui.layout_columns(col_widths=(6, 6), gap="1rem"):
        with ui.card():
            ui.card_header("Plot 1")
            ui.p("Placeholder: plot title")

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
