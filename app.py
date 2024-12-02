from shiny import App, ui, render, reactive
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Define the application UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Sidebar Content"),  # Sidebar title
        ui.p("Add any additional content here!")  # Additional sidebar text
    ),
    ui.navset_tab(
        ui.nav_panel("Graphics", ui.output_plot("line_graph_output")),
        ui.nav_panel("Table", ui.output_data_frame("frame_output")),
    )
)

# Define server logic
def server(input, output, session):
    @reactive.Calc
    def dat():
        # Load data from the CSV file
        infile = Path(__file__).parent / "USDA_75_23_CPI.csv"
        return pd.read_csv(infile)

    @output
    @render.plot
    def line_graph_output():
        # Create the line graph
        data = dat()
        plt.figure(figsize=(10, 5))
        plt.plot(data["Date"], data["All food"], marker="o", label="All Food")
        plt.title("All Food Price Trends Over Time")
        plt.xlabel("Date")
        plt.ylabel("All Food")
        plt.ylim(-25, 55)  # Set the y-axis range
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

    @output
    @render.data_frame
    def frame_output():
        # Render the data frame output for the "Table" tab
        return dat()

# Create the application
app = App(app_ui, server)
