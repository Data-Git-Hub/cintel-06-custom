from shiny import App, ui, render, reactive
from pathlib import Path
import pandas

# Define the application UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Sidebar"),  # Sidebar title
        ui.p("Content goes here"),  # Additional sidebar text
    ),
    ui.navset_tab(
        ui.nav_panel("Graphics", ui.output_table("table_output")),
        ui.nav_panel("Table", ui.output_data_frame("frame_output")),
    ),
)


# Define server logic
def server(input, output, session):
    @reactive.Calc
    def dat():
        # Load data from the CSV file
        infile = Path(__file__).parent / "USDA_75_23_CPI.csv"
        return pandas.read_csv(infile)

    @output
    @render.table
    def table_output():
        # Render table output for the "Graphics" tab
        return dat()

    @output
    @render.data_frame
    def frame_output():
        # Render data frame output for the "Table" tab
        return dat()


# Create the application
app = App(app_ui, server)
