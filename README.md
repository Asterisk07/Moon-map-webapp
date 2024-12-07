# Moon Elemental Abundance Map

This project visualizes the elemental abundance on the surface of the Moon using an interactive web-based globe. Users can explore the distribution of various elements and compounds, view histograms of data, and save favorite configurations for quick access.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Data Preparation](#data-preparation)
- [Running the Server](#running-the-server)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Additional Notes](#additional-notes)

## Features

- Interactive 3D globe visualization using [Globe.gl](https://globe.gl/)
- Display of elemental and compound abundances on the lunar surface
- Histogram visualization for data distribution
- Support for multiple dates and elements
- Ability to save and load favorite configurations

## Prerequisites

### Required Tools

- **Python 3.x**
- **Node.js and npm** (optional, for frontend dependencies if needed)

### Python Packages

Install the following Python packages:

- Flask
- pandas
- numpy
- scikit-learn
- sqlite3 (standard library)
- json (standard library)

You can install the required packages using:

```bash
pip install flask pandas numpy scikit-learn
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/moon-elemental-abundance-map.git
```

### 2. Navigate to the Project Directory

Ensure you are in the root directory of the project:

```bash
cd moon-elemental-abundance-map
```

## Data Preparation

Before running the application, you need to preprocess the data and generate the necessary files.

### 1. Place Data Files

Make sure the following files are placed in the `data/` directory:

- `data/compound_data.csv`
- `data/element_data.csv`

### 2. Run Preprocessing Script

Navigate to the `scripts/` directory and run the preprocessing script to merge the data:

```bash
cd scripts
python 00_preprocess_data.ipynb
```

This script will generate `merged_data.csv` in the `data/` directory.

### 3. Generate Abundances Database

Run the data generation script to create the `abundances.db` SQLite database:

```bash
python 01_data_generation.py
```

The database will be created in the `database/` directory.

### 4. Perform Clustering

Run the clustering script to generate the JSON files required by the web application:

```bash
python 02_clustering.py
```

This will create the following files in the `static/` directory:

- `clusters.json`
- `dates.json`
- `histograms.json`

After completing the data preparation, navigate back to the root directory:

```bash
cd ..
```

## Running the Server

Now you can run the Flask server to start the web application.

```bash
python server.py
```

The server will start running on [http://127.0.0.1:1234/](http://127.0.0.1:1234/) by default, as specified in `server.py`.

## Usage

### Access the Web Application

Open your web browser and navigate to:

[http://127.0.0.1:1234/](http://127.0.0.1:1234/)

### Explore the Moon Map

- Use your mouse to rotate, zoom, and interact with the 3D globe.
- Select elements or compounds from the dropdown menus to visualize their abundance.
- Adjust visualization settings using the controls on the left.
- View the histogram to understand the distribution of the selected data.
- Save your favorite configurations for easy access later.

### Controls and Features

- **Favorite Configurations**: Save and load your preferred visualization settings.
- **Element Selection**: Choose primary and secondary elements to display abundance or ratios.
- **Date Selector**: Filter data based on the available dates.
- **Histogram**: View the distribution of abundances for the selected element(s).
- **Info Panel**: Get real-time information about the globe's state and data points.

## Project Structure

```
.
├── data
│   ├── compound_data.csv
│   ├── element_data.csv
│   └── merged_data.csv
├── database
│   └── abundances.db
├── documentation
│   └── outline.txt
├── notebooks
│   ├── clustering.ipynb
│   └── data_generation.ipynb
├── plan.txt
├── README.md
├── scripts
│   ├── 00_preprocess_data.ipynb
│   ├── 01_data_generation.py
│   └── 02_clustering.py
├── server.py
├── static
│   ├── clusters.json
│   ├── dates.json
│   ├── histograms.json
│   ├── lunar_bumpmap.jpg
│   ├── lunar_surface.jpg
│   └── style.css
└── templates
    └── index.html
```

### Directory Overview

- `data/`: Contains raw and merged data files.
- `database/`: Stores the SQLite database file `abundances.db`.
- `documentation/`: Includes project outlines and notes.
- `notebooks/`: Jupyter notebooks for data exploration and development.
- `scripts/`: Python scripts for data preprocessing and clustering.
- `static/`: Static files including images, stylesheets, and generated JSON data.
- `templates/`: HTML templates used by Flask.
- `server.py`: The main Flask application server.

## Additional Notes

### Data Files

Ensure that `compound_data.csv` and `element_data.csv` are properly formatted and placed in the `data/` directory before running the scripts.

### Python Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Dependencies

If a `requirements.txt` file is provided, install dependencies using:

```bash
pip install -r requirements.txt
```

### Port Configuration

The server runs on port `1234` by default. You can change this in `server.py` if needed.

### Troubleshooting

If you encounter any issues, ensure all dependencies are installed and check for any error messages in the console.

