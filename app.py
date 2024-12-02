from shiny import App, ui, render, reactive
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

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
        ui.nav_panel(
            "Graph 1",
            ui.h3(ui.output_text("graph_1_header")),  # Dynamic header
            ui.output_ui("line_graph_1_output"),
        ),
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

    @output
    @render.text
    def graph_1_header():
        selected_columns = input.graph_1_options()
        if not selected_columns:
            return (
                "Please select an option from the sidebar to display additional data."
            )
        return "Graph 1: Food Price Trends Over Time"

    @output
    @render.ui
    def line_graph_1_output():
        data = dat()
        if data.empty:
            print("No data available for Graph 1.")
            return ui.HTML("<p>Error: No data available for Graph 1.</p>")

        # Create the graph using Plotly
        fig = go.Figure()

        # Always display "All food" data
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["All food"],
                mode="lines+markers",
                name="All Food",
                marker=dict(size=8),
                hovertemplate="Date: %{x}<br>All Food: %{y}<extra></extra>",
                line=dict(color="red"),
            )
        )

        # Add lines dynamically based on selected options
        selected_columns = input.graph_1_options()
        for col in selected_columns:
            if col == "food_away":
                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data["Food away from home"],
                        mode="lines+markers",
                        name="Food away from Home",
                        marker=dict(size=8),
                        hovertemplate="Date: %{x}<br>Food away from Home: %{y}<extra></extra>",
                        line=dict(color="blue"),
                    )
                )
            elif col == "food_at_home":
                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data["Food at home"],
                        mode="lines+markers",
                        name="Food at Home",
                        marker=dict(size=8),
                        hovertemplate="Date: %{x}<br>Food at Home: %{y}<extra></extra>",
                        line=dict(color="green"),
                    )
                )

        fig.update_layout(
            title=None,  # Title removed as the header is dynamic
            xaxis_title="Date",
            yaxis_title="Price Index",
            yaxis=dict(range=[-5, 15]),
            template="plotly_white",
            hovermode="closest",
        )

        # Render the Plotly graph
        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    @output
    @render.ui
    def line_graph_2_output():
        data = dat()
        if data.empty:
            print("No data available for Graph 2.")
            return ui.HTML("<p>Error: No data available for Graph 2.</p>")

        # Create the graph for Graph 2 using Plotly
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["Meats poultry and fish"],
                mode="lines+markers",
                name="Meats, Poultry, and Fish",
                marker=dict(size=8),
                hovertemplate="Date: %{x}<br>Meats, Poultry, and Fish: %{y}<extra></extra>",
                line=dict(color="orange"),
            )
        )

        fig.update_layout(
            title="Graph 2: Meats, Poultry, and Fish Price Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Price Index",
            yaxis=dict(range=[-25, 55]),
            template="plotly_white",
            hovermode="closest",
        )

        # Render the Plotly graph
        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

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
