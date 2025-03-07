import seaborn as sns  # Import Seaborn for data visualization
from faicons import icon_svg  # Import FontAwesome icons for UI elements

# Import data from shared.py
from shared import app_dir, df

from shiny import reactive  # Import reactive utilities for interactivity
from shiny.express import input, render, ui  # Import Shiny Express for UI and rendering


ui.page_opts(title="Penguins dashboard", fillable=True) # Set the title of the dashboard

#Creates a sidebar with filters.
with ui.sidebar(title="Filter controls"):
    ui.input_slider("mass", "Mass", 2000, 6000, 6000) #Creates a slider input for filtering by mass (default max 6000g).
    ui.input_checkbox_group(
        "species",
        "Species",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
    )


with ui.layout_column_wrap(fill=False):  # Wraps value boxes in a responsive layout
    with ui.value_box(showcase=icon_svg("earlybirds")):  # Displays an icon with a label
        "Number of penguins"

        @render.text
        def count():
            return filtered_df().shape[0]  # Displays the number of filtered penguins

    with ui.value_box(showcase=icon_svg("ruler-horizontal")):
        "Average bill length"

        @render.text
        def bill_length():
            return f"{filtered_df()['bill_length_mm'].mean():.1f} mm"  # Displays average bill length

    with ui.value_box(showcase=icon_svg("ruler-vertical")):
        "Average bill depth"

        @render.text
        def bill_depth():
            return f"{filtered_df()['bill_depth_mm'].mean():.1f} mm"  # Displays average bill depth



with ui.layout_columns():  # Creates a column layout for plots and data tables
    with ui.card(full_screen=True):  # A card containing a scatter plot
        ui.card_header("Bill length and depth")

        @render.plot
        def length_depth():
            return sns.scatterplot(
                data=filtered_df(),
                x="bill_length_mm",
                y="bill_depth_mm",
                hue="species",
            )

    with ui.card(full_screen=True):  # A card for the data table
        ui.card_header("Penguin data")

        @render.data_frame
        def summary_statistics():
            cols = [
                "species",
                "island",
                "bill_length_mm",
                "bill_depth_mm",
                "body_mass_g",
            ]
            return render.DataGrid(filtered_df()[cols], filters=True)  # Displays a table with filtering enabled

# Loads a custom CSS file (styles.css) to modify the appearance of the dashboard.
ui.include_css(app_dir / "styles.css")


@reactive.calc
def filtered_df():
    filt_df = df[df["species"].isin(input.species())]
    filt_df = filt_df.loc[filt_df["body_mass_g"] < input.mass()]
    return filt_df
