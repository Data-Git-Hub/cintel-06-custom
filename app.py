from shiny import App, ui, render, reactive
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Define the application UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Graph 1"),  # Title for Graph 1 checkboxes
        ui.input_checkbox_group(
            "graph_1_options",  # Input ID
            None,  # No subtitle
            {
                "food_away": "Food away from Home",
                "food_at_home": "Food at Home",
            },
        ),
        ui.h3("Sidebar Content"),  # Sidebar additional title
        ui.p("Add any additional content here!"),  # Additional sidebar text
    ),
    ui.navset_tab(
        ui.nav_panel("Graph 1", ui.output_ui("line_graph_1_output")),
        ui.nav_panel("Graph 2", ui.output_ui("line_graph_2_output")),
        ui.nav_panel("Table", ui.output_data_frame("frame_output")),
    ),
)


# Define server logic
def server(input, output, session):
    @reactive.Calc
    def dat():
        # Load data from the CSV file
        infile = Path(__file__).parent / "USDA_75_23_CPI.csv"
        try:
            df = pd.read_csv(infile)
            print(df.head())  # Debug: Print first few rows of the data
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error

    def plot_to_base64(fig):
        """Convert Matplotlib figure to Base64 image."""
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        return f"data:image/png;base64,{base64_image}"

    @output
    @render.ui
    def line_graph_1_output():
        data = dat()
        if data.empty:
            print("No data available for Graph 1.")
            return ui.HTML("<p>Error: No data available for Graph 1.</p>")

        # Create the graph
        fig, ax = plt.subplots(figsize=(10, 5))

        # Permanent "All food" line
        ax.plot(
            data["Date"], data["All food"], marker="o", label="All Food", color="red"
        )

        # Add lines based on selected options
        selected_columns = input.graph_1_options()
        for col in selected_columns:
            if col == "food_away":
                ax.plot(
                    data["Date"],
                    data["Food away from home"],
                    marker="s",
                    label="Food away from Home",
                    color="blue",
                )
            elif col == "food_at_home":
                ax.plot(
                    data["Date"],
                    data["Food at home"],
                    marker="^",
                    label="Food at Home",
                    color="green",
                )

        ax.set_title("Graph 1: Food Price Trends Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price Index")
        ax.set_ylim(-5, 20)  # Set the y-axis range
        ax.legend()
        ax.grid(True)

        # Convert the plot to Base64 and embed it as an <img> tag
        img_src = plot_to_base64(fig)
        plt.close(fig)
        return ui.HTML(f'<img src="{img_src}" alt="Graph 1" style="width:100%;">')

    @output
    @render.ui
    def line_graph_2_output():
        data = dat()
        if data.empty:
            print("No data available for Graph 2.")
            return ui.HTML("<p>Error: No data available for Graph 2.</p>")

        # Create the line graph for Graph 2
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            data["Date"],
            data["Meats poultry and fish"],
            marker="s",
            label="Meats, Poultry, and Fish",
            color="orange",
        )
        ax.set_title("Graph 2: Meats, Poultry, and Fish Price Trends Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Meats, Poultry, and Fish")
        ax.set_ylim(-25, 55)  # Adjusted y-axis range for consistency
        ax.legend()
        ax.grid(True)

        # Convert the plot to Base64 and embed it as an <img> tag
        img_src = plot_to_base64(fig)
        plt.close(fig)
        return ui.HTML(f'<img src="{img_src}" alt="Graph 2" style="width:100%;">')

    @output
    @render.data_frame
    def frame_output():
        # Render the data frame output for the "Table" tab
        data = dat()
        if data.empty:
            return pd.DataFrame({"Error": ["No data available"]})
        return data


# Create the application
app = App(app_ui, server)
