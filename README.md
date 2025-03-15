# GR5243_Project_2
## Project Overview
The web application is built using Shiny for Python and allows users to upload, clean, explore, and visualize datasets interactively. The application supports different file formats and provides a built-in dataset for demonstration.
This repository will contain 3 .py files that have different functionalities:

**[app.py](app.py): Dataset Upload and Exploratory Data Analysis**

**[data_preprocessing.py](data_preprocessing.py): Data Cleaning and preprocessing**

**[feature.py](feature.py): Feature Engineering**

## **Installation Instructions**
To run the application locally, follow these steps in terminal:

### **1. Clone the Repository**
```
git clone https://github.com/johnfeng2023/GR5243_Project_2.git
cd GR5243_Project_2
```
### **2. Create a Virtual Environment (Optional, Recommended)**
For Mac:
```
python -m venv .venv
source .venv/bin/activate
```
For Windows:
```
python -m venv .venv
.venv\Scripts\activate
```

### **3. Install Dependencies**
```
pip install -r requirements.txt
```

### 3.5 .rds File Dependency
**Note**: For reading in .rds files, library `pyreadr` is required. If you encounter the error of `lzma.h` not found, then you need to install `xz` before installing `pyreadr`.

MacOS only:
```
brew install xz
```
Verify Installation:
```
ls /usr/local/include/lzma.h  # For Intel Macs
ls /opt/homebrew/include/lzma.h  # For Apple Silicon (M1/M2)
```
Manually specify library paths and install `pyreadr`:
```
CFLAGS="-I/usr/local/include" LDFLAGS="-L/usr/local/lib" pip install pyreadr # For Intel Macs
CFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install pyreadr # For Apple Silicon (M1/M2)
```
After manually installying pyreadr, install dependencies in requirements.txt again:
```
pip install -r requirements.txt
```

### **4. Run the Application**
**app.py**:
```
shiny run app.py
```
**data_preprocessing.py**
````
shiny run data_preprocessing.py
````
**feature.py**
```
shiny run feature.py
```

Once running, visit http://127.0.0.1:8000 in your web browser.
Ctrl + C in Terminal to quit application.

## Files
- [app.py](app.py) – The main script for running the web application, integrating various functionalities like dataset uploading, preprocessing, feature engineering, and EDA.
- [data_preprocessing.py](data_preprocessing.py) – Contains functions for cleaning and preprocessing datasets, such as handling missing values, outliers, and scaling transformations.
- [feature.py](feature.py) – Implements feature engineering functions, including log transformations, polynomial expansions, and categorical encoding.
- [penguins.csv](penguins.csv) – A sample dataset included for demonstration purposes, allowing users to test the application without uploading their own data.
requirements.txt – Lists all dependencies required to run the application, ensuring easy installation using pip install -r requirements.txt.
- [shared.py](share.py) – Provides shared utility functions used across different scripts, such as file handling, validation, or common preprocessing tasks.
- [styles.css](styles.css) – Defines the styling for the web application, ensuring a clean and user-friendly interface.
---

## Team Contributions

| Task                        | Contributor       |
|-----------------------------|------------------|
| **Data Uploading**        | John Feng       |
| **Data Preprocessing** | Mei Yue       |
| **Feature Engineering**      | Jiaheng Zhang       |
| **Exploratory Data Analysis**     | Zhuoxuan Li     |

