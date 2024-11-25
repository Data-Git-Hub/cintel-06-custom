from pathlib import Path

import pandas

from shiny import reactive
from shiny.express import render, ui


@reactive.calc
def dat():
    infile = Path(__file__).parent / "USDA_75_23_CPI.csv"
    return pandas.read_csv(infile)


with ui.navset_card_underline():

    with ui.nav_panel("Graphics"):

        @render.data_frame
        def frame():
            # Give dat() to render.DataGrid to customize the grid
            return dat()

    with ui.nav_panel("Table"):

        @render.table
        def table():
            return dat()

