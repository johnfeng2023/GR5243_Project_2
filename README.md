# GR5243_Project_2
## Project Overview
This web application is built using Shiny for Python and allows users to **upload, clean, explore, and visualize datasets interactively**. The application supports different file formats and provides a built-in dataset for demonstration.
The dashboard provides:

**Dataset Upload & Selection**  
**Data Cleaning (Handle Missing Values, Remove Duplicates, etc.)**  
**Feature Engineering (Create New Features, Drop Columns)**  
**Exploratory Data Analysis (Interactive Visualizations & Tables)**  

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
```
shiny run app.py
```
Once running, visit http://127.0.0.1:8000 in your web browser.
Ctrl + C in Terminal to quit application.
