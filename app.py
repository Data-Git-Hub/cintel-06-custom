from shiny import App, ui, render, reactive
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

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
        ui.h3("Graph 2"),  # Title for Graph 2 selectize
        ui.input_selectize(
            "graph_2_options",  # Input ID
            "Select categories for Graph 2:",
            choices=[
                "Meats",
                "Beef and veal",
                "Pork",
                "Other meats",
                "Poultry",
                "Fish and seafood",
            ],
            multiple=True,
        ),
        ui.h3("Graph 3"),  # Title for Graph 3
        ui.input_numeric(
            "graph_3_numeric", "Enter a number:", 1, min=1, max=10
        ),  # Numeric input box
    ),
    ui.navset_tab(
        ui.nav_panel(
            "Graph 1",
            ui.h3("Graph 1: Food Price Trends"),  # Static header
            ui.output_ui("line_graph_1_output"),
        ),
        ui.nav_panel(
            "Graph 2",
            ui.h3("Graph 2: Meats, Poultry, and Fish Price Trends"),  # Static header
            ui.output_ui("line_graph_2_output"),
        ),
        ui.nav_panel(
            "Graph 3",
            ui.h3("Graph 3: Eggs Price Trends"),  # Static header
            ui.output_ui("line_graph_3_output"),
        ),
        ui.nav_panel("Table", ui.output_data_frame("frame_output")),
    ),
)


# Define server logic
def server(input, output, session):
    @reactive.Calc
    def dat():
        # Load data from the CSV file and normalize column names
        infile = Path(__file__).parent / "USDA_75_23_CPI.csv"
        try:
            df = pd.read_csv(infile)
            df.columns = df.columns.str.strip()  # Normalize column names
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error

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
            xaxis_title="Date",
            yaxis_title="Price Index",
            yaxis=dict(range=[-25, 55]),
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

        # Always display "Meats poultry and fish"
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

        # Add lines dynamically based on selected options
        selected_categories = input.graph_2_options()
        for category in selected_categories:
            if category in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data[category],
                        mode="lines+markers",
                        name=category,
                        marker=dict(size=8),
                        hovertemplate=f"Date: %{{x}}<br>{category}: %{{y}}<extra></extra>",
                    )
                )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price Index",
            yaxis=dict(range=[-25, 55]),
            template="plotly_white",
            hovermode="closest",
        )

        # Render the Plotly graph
        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    @output
    @render.ui
    def line_graph_3_output():
        data = dat()
        if data.empty:
            print("No data available for Graph 3.")
            return ui.HTML("<p>Error: No data available for Graph 3.</p>")

        # Prepare data for linear regression
        X = data["Date"].values.reshape(-1, 1)
        y = data["Eggs"].values
        model = LinearRegression()
        model.fit(X, y)

        # Predict value for 2024
        prediction_2024 = model.predict([[2024]])[0]

        # Create the graph for Graph 3 using Plotly
        fig = go.Figure()

        # Always display "Eggs" data
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["Eggs"],
                mode="lines+markers",
                name="Eggs",
                marker=dict(size=8),
                hovertemplate="Date: %{x}<br>Eggs: %{y}<extra></extra>",
                line=dict(color="purple"),
            )
        )

        # Add trend line
        trend_line = model.predict(X)
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=trend_line,
                mode="lines",
                name="Trend Line",
                line=dict(color="blue", dash="dash"),
            )
        )

        fig.add_annotation(
            x=2024,
            y=prediction_2024,
            text=f"Predicted 2024: {prediction_2024:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=-50,
            ay=-30,
        )

        fig.update_layout(
            title="Graph 3: Eggs Price Trends with Prediction",
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
