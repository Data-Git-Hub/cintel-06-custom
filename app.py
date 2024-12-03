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
        ui.hr(),  # Horizontal rule between Graph 1 and Graph 2
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
        ui.hr(),  # Horizontal rule between Graph 2 and Graph 3
        ui.h3("Graph 3"),  # Title for Graph 3
        ui.input_selectize(
            "graph_3_select",  # Input ID
            "Select a category for Graph 3:",
            choices=[
                "Fresh fruits and vegetables",
                "Fresh fruits",
                "Fresh vegetables",
            ],
            multiple=False,
        ),
        ui.hr(),  # Horizontal rule for visual clarity before the GitHub link
        ui.a(
            "Data-Git-Hub",
            href="https://github.com/Data-Git-Hub",
            target="_blank",
        ),  # GitHub link
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
            ui.h3("Graph 3: Fruits and Vegetables Trends"),  # Updated header
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
            return ui.HTML("<p>Error: No data available for Graph 1.</p>")

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
            yaxis=dict(range=[-5, 15]),
            template="plotly_white",
            hovermode="closest",
        )

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    @output
    @render.ui
    def line_graph_2_output():
        data = dat()
        if data.empty:
            return ui.HTML("<p>Error: No data available for Graph 2.</p>")

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
            yaxis=dict(range=[-10, 30]),
            template="plotly_white",
            hovermode="closest",
        )

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    @output
    @render.ui
    def line_graph_3_output():
        data = dat()
        if data.empty:
            return ui.HTML("<p>Error: No data available for Graph 3.</p>")

        fig = go.Figure()

        # Always display "Fruits and vegetables"
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["Fruits and vegetables"],
                mode="lines+markers",
                name="Fruits and Vegetables",
                marker=dict(size=8),
                hovertemplate="Date: %{x}<br>Fruits and Vegetables: %{y}<extra></extra>",
                line=dict(color="purple"),
            )
        )

        selected_column = input.graph_3_select()
        if selected_column and selected_column in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data[selected_column],
                    mode="lines+markers",
                    name=selected_column,
                    marker=dict(size=8),
                    hovertemplate=f"Date: %{{x}}<br>{selected_column}: %{{y}}<extra></extra>",
                    line=dict(color="green"),
                )
            )

        fig.update_layout(
            title="Graph 3: Fruits and Vegetables Trends",
            xaxis_title="Date",
            yaxis_title="Price Index",
            yaxis=dict(range=[-10, 20]),
            template="plotly_white",
            hovermode="closest",
        )

        return ui.HTML(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    @output
    @render.data_frame
    def frame_output():
        data = dat()
        if data.empty:
            return pd.DataFrame({"Error": ["No data available"]})
        return data


# Create the application
app = App(app_ui, server)
