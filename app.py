import seaborn as sns  # Import Seaborn for data visualization
from faicons import icon_svg  # Import FontAwesome icons for UI elements
from shared import app_dir, load_dataset  # Import dataset loader function
import pandas as pd
from shiny import reactive  # Import reactive utilities for interactivity
from shiny.express import input, render, ui  # Import Shiny Express for UI and rendering

ui.page_opts(title="Data Analysis Dashboard", fillable=True)  # Set the title of the dashboard

# Sidebar for dataset upload and filters
with ui.sidebar(title="Dataset Upload & Filters"):
    # File Upload Input
    ui.input_file("uploaded_file", "Upload a Dataset", accept=[".csv", ".xlsx", ".json", ".rds"])

    # # Placeholder filters (these will be updated dynamically in future steps)
    # ui.input_slider("mass", "Mass", 2000, 6000, 6000)
    # ui.input_checkbox_group(
    #     "species",
    #     "Species",
    #     ["Adelie", "Gentoo", "Chinstrap"],
    #     selected=["Adelie", "Gentoo", "Chinstrap"],
    # )

# **Reactive function to load dataset**
@reactive.calc
def dataset():
    """Loads the dataset reactively when a new file is uploaded."""
    uploaded_file = input.uploaded_file()
    if uploaded_file:
        return load_dataset(uploaded_file[0]["datapath"])  # Load user-uploaded file
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


# **Load custom CSS file**
ui.include_css(app_dir / "styles.css")
