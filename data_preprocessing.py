from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import tempfile

# Define UI
app_ui = ui.page_fluid(
    ui.input_file("file", "Upload File", multiple=False, accept=[".csv", ".xlsx", ".xls", ".txt", ".json"]),

    # Handle Missing Values
    ui.input_select("missing_values", "Handle Missing Values:",
                    {
                        "none": "Do Nothing",
                        "drop": "Remove Rows with Missing Values",
                        "mean": "Fill with Mean",
                        "median": "Fill with Median",
                        "mode": "Fill with Mode",
                        "remove_columns": "Remove Columns with High Missing Values"
                    }, selected="none"),
    ui.output_ui("missing_threshold_ui"),
    ui.output_ui("missing_columns_ui"),  # Select columns for specific missing value handling

    # Handle Outliers
    ui.input_select("outliers", "Handle Outliers (Non-Leverage Points):",
                    {
                        "none": "Do Nothing",
                        "remove": "Remove Outliers",
                        "mean": "Replace with Mean",
                        "median": "Replace with Median",
                        "clip": "Clip to Threshold"
                    }, selected="none"),
    ui.output_ui("outlier_column_ui"),  # Show columns for outlier handling

    ui.input_select("leverage", "Handle Leverage Points:",
                    {
                        "none": "Do Nothing",
                        "remove": "Remove Leverage Points",
                        "mean": "Replace with Mean",
                        "median": "Replace with Median"
                    }, selected="none"),
    ui.output_ui("leverage_column_ui"),  # Show columns for leverage handling

    # Convert Data Types
    ui.input_select("data_type", "Convert Data Types:",
                    {
                        "none": "Do Nothing",
                        "to_numeric": "Convert to Numeric"
                    }, selected="none"),
    ui.output_ui("convert_column_ui"),  # Column selection for data type conversion

    # Apply Normalization
    ui.input_select("normalization", "Apply Normalization:",
                    {"none": "Do Nothing", "minmax": "Min-Max Scaling", "zscore": "Standardization (Z-score)", "robust": "Robust Scaling"}, selected="none"),
    ui.output_ui("normalization_column_ui"),  # Allow multiple column selection

    # Display Tables
    ui.output_table("data_summary"),
    ui.output_table("preview_data"),
    ui.output_table("processed_data"),
    
    # Download Processed Data
    ui.download_button("download", "Download Processed Data")
)

# Define Server Logic
def server(input, output, session):
    @output
    @render.ui
    def preview_data():
        df = get_data()
        if df is None:
            return ui.HTML("<p>No data uploaded.</p>")

        table_html = df.head(15).to_html(classes="table table-striped", index=False)
        return ui.HTML(f"""
            <div style="max-height: 300px; overflow: auto; border: 1px solid #ddd; padding: 10px; width: 100%;">
                <table class="table table-striped" style="width: 100%; border-collapse: collapse; text-align: left; display: block; overflow: auto;">
                    {table_html}
                </table>
            </div>
        """)


    @reactive.Calc
    def get_data():
        file_info = input.file()
        if not file_info:
            return None
        file_path = file_info[0]["datapath"]
        
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".txt"):
            df = pd.read_csv(file_path, delimiter="\t")
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            return None
        return df

    @output
    @render.table
    def data_summary():
        df = get_data()
        if df is None:
            return pd.DataFrame()
        summary = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Missing %": ((df.isnull().sum() / len(df)) * 100).round(2).astype(str) + "%"
        })
        return summary

    @output
    @render.ui
    def missing_threshold_ui():
        if input.missing_values() == "remove_columns":
            return ui.input_numeric("missing_threshold", "Set Missing Value Threshold (%)", value=50, min=0, max=100)
        return None

    @output
    @render.ui
    def missing_columns_ui():
        """ Show column selection only for fill methods """
        if input.missing_values() in ["mean", "median", "mode"]:
            df = get_data()
            if df is None:
                return None
            return ui.input_select("missing_columns", "Select Columns for Missing Value Handling:", df.columns.tolist(), multiple=True)
        return None

    @output
    @render.ui
    def outlier_column_ui():
        if input.outliers() != "none":
            df = get_data()
            if df is None:
                return None
            return ui.input_select("outlier_column", "Select Column for Outlier Handling:", df.columns.tolist(), multiple=False)
        return None

    @output
    @render.ui
    def leverage_column_ui():
        if input.leverage() != "none":
            df = get_data()
            if df is None:
                return None
            return ui.input_select("leverage_column", "Select Column for Leverage Handling:", df.columns.tolist(), multiple=False)
        return None

    @output
    @render.ui
    def convert_column_ui():
        if input.data_type() != "none":
            df = get_data()
            if df is None:
                return None
            return ui.input_select("column_selector", "Select Column to Convert:", df.columns.tolist(), multiple=False)
        return None

    @output
    @render.ui
    def normalization_column_ui():
        if input.normalization() != "none":
            df = get_data()
            if df is None:
                return None
            return ui.input_select("normalize_columns", "Select Columns for Normalization:", df.columns.tolist(), multiple=True)
        return None

    @reactive.Calc
    def preprocess_data():
        df = get_data()
        if df is None:
            return None
        
        # Handle Missing Values
        if input.missing_values() == "remove_columns":
            threshold = input.missing_threshold() / 100
            df = df.loc[:, (df.isnull().mean() * 100) < threshold]
        elif input.missing_values() in ["mean", "median", "mode"] and input.missing_columns():
            cols = input.missing_columns()
            if input.missing_values() == "mean":
                df[cols] = df[cols].fillna(df[cols].mean())
            elif input.missing_values() == "median":
                df[cols] = df[cols].fillna(df[cols].median())
            elif input.missing_values() == "mode":
                df[cols] = df[cols].fillna(df[cols].mode().iloc[0])

        # Handle Outliers
        if input.outliers() != "none" and input.outlier_column():
            col = input.outlier_column()
            if input.outliers() == "remove":
                df = df[np.abs(df[col] - df[col].mean()) / df[col].std() < 3]
            elif input.outliers() == "mean":
                df[col] = np.where(np.abs(df[col] - df[col].mean()) > 3 * df[col].std(), df[col].mean(), df[col])
            elif input.outliers() == "median":
                df[col] = np.where(np.abs(df[col] - df[col].median()) > 3 * df[col].std(), df[col].median(), df[col])
            elif input.outliers() == "clip":
                df[col] = df[col].clip(df[col].quantile(0.05), df[col].quantile(0.95))

        # Convert Data Type
        if input.data_type() != "none" and input.column_selector():
            column = input.column_selector()
            df[column] = pd.to_numeric(df[column], errors="coerce")

        return df
    
    @output
    @render.ui
    def processed_data():
        df = preprocess_data()
        if df is None:
            return ui.HTML("<p>No processed data available.</p>")
        
        table_html = df.head(15).to_html(classes="table table-striped", index=False)
        return ui.HTML(f"""
            <div style="max-height: 300px; overflow: auto; border: 1px solid #ddd; padding: 10px; width: 100%;">
                <table class="table table-striped" style="width: 100%; border-collapse: collapse; text-align: left; display: block; overflow: auto;">
                    {table_html}
                </table>
            </div>
        """)

    @output
    @render.download
    def download():
        df = preprocess_data()
        if df is None:
            return None
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(temp_file.name, index=False)
        return temp_file.name

# app = App(app_ui, server)


print("Initializing Shiny app...")
app = App(app_ui, server)
print("Shiny app created successfully.")
print("Starting the Shiny app server...")
app.run()
print("Shiny app has stopped.")  # This will print only if the app stops

