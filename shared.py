from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent

def load_dataset(file_path=None):
    """Loads a dataset from a given path. Supports CSV, Excel, JSON, and RDS."""
    if file_path is None:
        return pd.read_csv(app_dir / "penguins.csv")  # Default dataset

    file_ext = file_path.split(".")[-1].lower()

    try:
        if file_ext == "csv":
            return pd.read_csv(file_path)
        elif file_ext in ["xls", "xlsx"]:
            return pd.read_excel(file_path, engine="openpyxl")
        elif file_ext == "json":
            return pd.read_json(file_path)
        elif file_ext == "rds":
            import pyreadr
            return pyreadr.read_r(file_path)[None]  # Extract dataframe from RDS object
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()  # Return empty DataFrame if there's an error

df = load_dataset()  # Default dataset
