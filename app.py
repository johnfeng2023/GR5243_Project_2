import seaborn as sns
from faicons import icon_svg  # Import FontAwesome icons for UI elements
from shared import app_dir, load_dataset  # Import dataset loader function
import pandas as pd
import numpy as np
import plotly.express as px  # Import Plotly Express for interactive plots
import plotly.graph_objects as go
from shiny import reactive, req  # Import reactive utilities for interactivity
from shiny.express import input, render, ui  # Import Shiny Express for UI and rendering
from shinywidgets import render_widget  # Import render_widget for Plotly plots

# Constants for performance optimization
MAX_POINTS_SCATTER = 1000  # Maximum number of points to plot in scatter
MAX_BINS_HIST = 50  # Maximum number of bins for histogram

ui.page_opts(title="Data Analysis Dashboard", fillable=True)  # Set the title of the dashboard

# Sidebar for dataset upload and filters
with ui.sidebar(title="Dataset Upload & Filters"):
    # File Upload Input
    ui.input_file("uploaded_file", "Upload a Dataset", accept=[".csv", ".xlsx", ".json", ".rds"])

# **Reactive function to load dataset**
@reactive.calc
def dataset():
    """Loads the dataset reactively when a new file is uploaded."""
    uploaded_file = input.uploaded_file()
    if uploaded_file:
        path = uploaded_file[0]["datapath"]
        if path.endswith('.csv'):
            return pd.read_csv(path)
        elif path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(path)
        return load_dataset(path)  # Load user-uploaded file
    return load_dataset()  # Use default dataset if no file is uploaded

# **Creates a responsive layout for value boxes**
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("earlybirds")):
        "Number of rows in dataset"

        @render.text
        def count():
            return dataset().shape[0]  # Displays the number of rows in the dataset

    with ui.value_box(showcase=icon_svg("ruler-horizontal")):
        "Number of columns"

        @render.text
        def column_count():
            return dataset().shape[1]  # Displays the number of columns

# **Column layout for plots and data tables**
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Data Preview")

        @render.data_frame
        def data_preview():
            df = dataset()  # Load dataset
            df.columns = df.columns.astype(str)  # Ensure column names are strings
            return render.DataGrid(df, filters=False, selection_mode="none")

# Main content area with tabs
with ui.navset_tab():
    # Summary Statistics Tab
    with ui.nav_panel("Descriptive Statistics"):
        @render.data_frame
        def summary_stats():
            df = dataset()
            numeric_cols = df.select_dtypes(include=np.number).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe().T
                stats = stats.reset_index().rename(columns={'index': 'Variable'})
                return stats
            return pd.DataFrame({"Message": ["No numeric variables found"]})

    # Variable Types Tab
    with ui.nav_panel("Data Structure"):
        @render.data_frame
        def var_types():
            df = dataset()
            var_type_df = pd.DataFrame({
                'Variable': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Unique Values': [df[col].nunique() for col in df.columns],
                'Missing Values': df.isna().sum().values,
                '% Missing': (df.isna().sum().values / len(df) * 100).round(2)
            })
            return var_type_df

    # Distribution Analysis Tab
    with ui.nav_panel("Univariate Analysis"):
        with ui.card():
            ui.h5("Variable Selection")
            ui.input_radio_buttons(
                "var_type_filter", "Variable Type:", 
                choices=["Numeric", "Categorical", "All"],
                selected="All"
            )
            ui.input_select("plot_var", "Select Variable:", choices=[])
        
        @render_widget
        def distribution_plot():
            req(input.plot_var())
            df = dataset()
            var = input.plot_var()
            
            if df[var].dtype.kind in 'ifc':  # If numeric
                return px.histogram(
                    df, 
                    x=var,
                    title=f"Distribution of {var}",
                    nbins=min(MAX_BINS_HIST, len(df[var].unique()))
                )
            else:  # If categorical
                value_counts = df[var].value_counts().nlargest(20)
                return px.bar(
                    x=value_counts.index, 
                    y=value_counts.values,
                    title=f"Distribution of {var} (Top 20 Categories)"
                )

    # Correlation Analysis Tab
    with ui.nav_panel("Bivariate Analysis"):
        with ui.layout_column_wrap(fill=False):
            with ui.card():
                ui.h5("Variable Selection")
                ui.input_select("x_var", "X Variable:", choices=[])
                ui.input_select("y_var", "Y Variable:", choices=[])
            
            with ui.card():
                ui.h5("Plot Customization")
                ui.input_checkbox("show_reg_line", "Show Regression Line", value=True)
                ui.input_select("reg_type", "Regression Type:", 
                    choices=["Linear", "Lowess", "None"],
                    selected="Lowess"
                )
                ui.input_slider("point_size", "Point Size:", min=1, max=10, value=5, step=1)
                ui.input_checkbox("show_outliers", "Highlight Outliers", value=False)
                ui.input_select("color_by", "Color By:", choices=[])
        
        @render_widget
        def scatter_plot():
            req(input.x_var(), input.y_var())
            df = dataset()
            
            if len(df) > MAX_POINTS_SCATTER:
                df = df.sample(n=MAX_POINTS_SCATTER, random_state=42)
            
            # Calculate outliers if requested
            if input.show_outliers():
                z_scores = np.abs((df[input.x_var()] - df[input.x_var()].mean()) / df[input.x_var()].std())
                z_scores_y = np.abs((df[input.y_var()] - df[input.y_var()].mean()) / df[input.y_var()].std())
                df['is_outlier'] = (z_scores > 3) | (z_scores_y > 3)
                color_col = 'is_outlier'
            elif input.color_by() and input.color_by() != "None":
                color_col = input.color_by()
            else:
                color_col = None
            
            fig = px.scatter(
                df,
                x=input.x_var(),
                y=input.y_var(),
                color=color_col,
                title=f"{input.x_var()} vs {input.y_var()}",
                size=[input.point_size()] * len(df),
                trendline="ols" if input.reg_type() == "Linear" else "lowess" if input.reg_type() == "Lowess" else None
            )
            
            if input.show_outliers():
                fig.update_traces(
                    marker=dict(
                        size=[input.point_size() * 1.5 if x else input.point_size() for x in df['is_outlier']],
                        color=['red' if x else 'blue' for x in df['is_outlier']]
                    )
                )
            
            return fig

        @render.text
        def correlation_stats():
            req(input.x_var(), input.y_var())
            df = dataset()
            corr = df[[input.x_var(), input.y_var()]].corr().iloc[0, 1]
            return f"Pearson correlation coefficient: {corr:.4f}"

    # Correlation Matrix Tab
    with ui.nav_panel("Multivariate Correlation"):
        ui.input_slider("corr_threshold", "Correlation Threshold:", min=0.0, max=1.0, value=0.0, step=0.05)
        ui.input_checkbox("show_corr_values", "Show Correlation Values", value=True)
        ui.input_select("corr_method", "Correlation Method:", 
            choices={"pearson": "Pearson", "spearman": "Spearman", "kendall": "Kendall"},
            selected="pearson"
        )
        
        @render_widget
        def correlation_matrix():
            df = dataset()
            numeric_df = df.select_dtypes(include=np.number)
            
            # Only include columns with sufficient non-NA values
            valid_cols = [col for col in numeric_df.columns if numeric_df[col].count() > 10]
            
            if len(valid_cols) < 2:
                return px.imshow([[0]], title="Not enough numeric variables for correlation analysis")
            
            # Calculate correlation matrix
            corr_matrix = numeric_df[valid_cols].corr(method=input.corr_method())
            
            # Apply threshold filter
            threshold = input.corr_threshold()
            if threshold > 0:
                # Convert to numpy array to avoid DataFrame.flat error
                corr_array = corr_matrix.values.copy()
                mask = np.abs(corr_array) < threshold
                np.fill_diagonal(mask, False)  # Keep diagonal
                corr_array[mask] = 0  # Apply mask
                
                # Convert back to DataFrame
                corr_matrix = pd.DataFrame(
                    corr_array, 
                    index=corr_matrix.index,
                    columns=corr_matrix.columns
                )
            
            return px.imshow(
                corr_matrix,
                text_auto=input.show_corr_values(),
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                title=f"{input.corr_method().capitalize()} Correlation Matrix"
            )

# Update UI elements based on dataset
@reactive.effect
def _():
    df = dataset()
    
    # Update variable selections for distribution plot
    if hasattr(input, 'var_type_filter') and input.var_type_filter() == "Numeric":
        var_choices = df.select_dtypes(include=np.number).columns.tolist()
    elif hasattr(input, 'var_type_filter') and input.var_type_filter() == "Categorical":
        var_choices = df.select_dtypes(exclude=np.number).columns.tolist()
    else:  # All variables
        var_choices = df.columns.tolist()
        
    ui.update_select("plot_var", choices=var_choices, selected=var_choices[0] if var_choices else None)
    
    # Update variable selections for correlation plot
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    ui.update_select("x_var", choices=numeric_cols, selected=numeric_cols[0] if numeric_cols else None)
    ui.update_select("y_var", choices=numeric_cols, selected=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0] if numeric_cols else None)
    
    # Update color_by choices for scatter plot
    all_cols = ["None"] + df.columns.tolist()
    ui.update_select("color_by", choices=all_cols, selected="None")

# **Load custom CSS file**
ui.include_css(app_dir / "styles.css")