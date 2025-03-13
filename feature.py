from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tempfile

# Define UI
app_ui = ui.page_fluid(
    ui.input_file("file", "Upload CSV File", multiple=False, accept=[".csv"]),
    ui.output_ui("column_selector"),
    ui.input_select("transformation", "Choose Transformation:", 
                    {
                        "none": "None",
                        "log": "Log Transform",
                        "square": "Square",
                        "standard": "Standardize",
                        "one_hot": "One-Hot Encoding",
                        "minmax": "Min-Max Scaling",
                        "poly2": "Polynomial (x²)",
                        "poly3": "Polynomial (x³)",
                        "binning": "Binning (Convert to Categories)"
                    }, selected="none"),
    ui.output_plot("plot_output"),
    ui.output_table("preview_data"),
    ui.output_table("transformed_data"),
    ui.download_button("download_csv", "Download Transformed Data")  # New download button
)

# Server Logic
def server(input, output, session):
    df = reactive.Value(None)
    transformed_df = reactive.Value(None)  # Store transformed dataset

    @reactive.effect
    def update_df():
        file_info = input.file()
        if file_info and len(file_info) > 0:
            df.set(pd.read_csv(file_info[0]["datapath"]))
            transformed_df.set(df.get().copy())  # Initialize transformed dataset

    @output
    @render.ui
    def column_selector():
        if df.get() is not None:
            all_columns = df.get().columns
            return ui.input_select("column", "Select Column:", {col: col for col in all_columns})
        return None

    @output
    @render.table
    def preview_data():
        if df.get() is not None:
            return df.get().head()
        return None

    @output
    @render.table
    def transformed_data():
        if df.get() is None or input.column() is None or input.column() not in df.get().columns:
            return None
        
        column_data = df.get()[input.column()].dropna()  
        new_df = df.get().copy()  

        is_numeric = np.issubdtype(column_data.dtype, np.number)
        transformed_data = column_data.copy()

        if input.transformation() == "log" and is_numeric:
            column_data = column_data[column_data > 0]  
            transformed_data = np.log1p(column_data)
        elif input.transformation() == "square" and is_numeric:
            transformed_data = column_data ** 2
        elif input.transformation() == "standard" and is_numeric:
            transformed_data = (column_data - column_data.mean()) / column_data.std()
        elif input.transformation() == "one_hot" and not is_numeric:
            one_hot_encoded = pd.get_dummies(column_data, prefix=input.column())
            new_df = new_df.drop(columns=[input.column()])  
            new_df = pd.concat([new_df, one_hot_encoded], axis=1)
        elif input.transformation() == "minmax" and is_numeric:
            transformed_data = (column_data - column_data.min()) / (column_data.max() - column_data.min())
        elif input.transformation() == "poly2" and is_numeric:
            transformed_data = column_data ** 2
        elif input.transformation() == "poly3" and is_numeric:
            transformed_data = column_data ** 3
        elif input.transformation() == "binning" and is_numeric:
            transformed_data = pd.cut(column_data, bins=5, labels=["Very Low", "Low", "Medium", "High", "Very High"])

        if input.transformation() == "one_hot":
            transformed_df.set(new_df)  
            return new_df.head()
        
        
        new_df[input.column() + "_transformed"] = transformed_data
        transformed_df.set(new_df)
        return new_df[[input.column(), input.column() + "_transformed"]].head()

    @output
    @render.plot
    def plot_output():
        if df.get() is None or input.column() is None or input.column() not in df.get().columns:
            return None
        
        column_data = df.get()[input.column()].dropna() 
        is_numeric = np.issubdtype(column_data.dtype, np.number)
        transformed_data = column_data.copy()

        if input.transformation() == "log" and is_numeric:
            column_data = column_data[column_data > 0]  
            transformed_data = np.log1p(column_data)
        elif input.transformation() == "square" and is_numeric:
            transformed_data = column_data ** 2
        elif input.transformation() == "standard" and is_numeric:
            transformed_data = (column_data - column_data.mean()) / column_data.std()
        elif input.transformation() == "minmax" and is_numeric:
            transformed_data = (column_data - column_data.min()) / (column_data.max() - column_data.min())
        elif input.transformation() == "poly2" and is_numeric:
            transformed_data = column_data ** 2
        elif input.transformation() == "poly3" and is_numeric:
            transformed_data = column_data ** 3
        elif input.transformation() == "binning" and is_numeric:
            transformed_data = pd.cut(column_data, bins=5, labels=[1, 2, 3, 4, 5])

        if input.transformation() == "one_hot":
            return None

        fig, ax = plt.subplots()
        ax.hist(column_data, alpha=0.5, label="Original", bins=20)
        ax.hist(transformed_data, alpha=0.5, label="Transformed", bins=20)
        ax.legend()
        ax.set_title(f"Feature Transformation Impact: {input.transformation().capitalize()}")
        return fig

 
    @session.download(filename="transformed_data.csv")
    def download_csv():
        if transformed_df.get() is not None:
            # Create a temporary CSV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
                transformed_df.get().to_csv(tmpfile.name, index=False)
                return tmpfile.name


app = App(app_ui, server)
