# Documentation: Spatial and Social Inequalities in Public Transport Complaints: Evidence from the Jerusalem Metropolitan Area

This repository contains the code, data structure, and documentation for Yodfat Ben-Shalom's master's thesis:  
**"Spatial and Social Inequalities in Public Transport Complaints: Evidence from the Jerusalem Metropolitan Area."**
- The repository contains The data analysis process, along with an example of 10 public complaints (the remaining complaints are confidential due to privacy restrictions)
---

## 📘 Contents

### 🧠 Main Notebook
- **`main.ipynb`**  
  The main analysis pipeline.  
  👉 *Run cell by cell to reproduce the full process.*

---

## 📁 Folder Structure

### `external_files/`  
>
- **settlements**:  
  shapefile of settlements (shape file)

### `files saved in zenodo  - https://zenodo.org/records/17778363`  

- **CBS Data**:  
  Socio-economic rankings by statistical area (Excel)

- **NPTA Data**:  
  - Number of passengers per bus line and station  
  - Non-execution data  
  - Public complaints

- **GIS Layers**:
  - Jerusalem city borders  
  - Jerusalem metropolitan borders  
  - West Bank borders  
  - Israeli municipalities borders

### `outputs/`
- Aggregated data per bus line  
- TOBIT regression results

### `graphs/`
- Graphs presented in the thesis article

---

## 🐍 Python Scripts (Data Manipulation)

### `dicts.py`  
- Links to external files  
- Field and layer names

### `general_functions.py`  
- Utility functions used throughout the project

### Used in `main.ipynb`:

- `handler_raw_complaints.py`:  
  Processes raw complaints into an editable table (sample only)

- `handler_GIS_demographic.py`:  
  Merges socio-economic data with GIS layers

- `handler_GIS_buslines_jerusalem.py`:  
  Defines which buses are relevant to the study

- `handler_socioeconomic_ranking.py`:  
  Determines socio-economic ranking of bus lines based on location and ridership

- `handler_service_areas.py`:  
  Determines the service area of each bus line (Jerusalem / metro / settlements)

- `handler_rishui.py`:  
  Analyzes whether lines serve East Jerusalem, how many passengers use them, and system-detected incident percentages

- `handler_complaints.py`:  
  Processes the clean version of complaints and aggregates them per bus line

- `handler_merger_export.py`:  
  Final merging and export of data by bus line

---

## 📊 R Script

- **`tobit_complaints.R`**  
  Runs a TOBIT regression model based on the cleaned and merged data.

---
