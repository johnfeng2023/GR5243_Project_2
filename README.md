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
### **4. Run the Applicatoin**
```
shiny run app.py
```
Once running, visit http://127.0.0.1:8000 in your web browser.
Ctrl + C in Terminal to quit application.
