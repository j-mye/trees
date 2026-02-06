# Milwaukee Tree Risk Map - Interactive Frontend

## Overview

This interactive map visualization displays Milwaukee's tree inventory organized by Quarter Sections, with risk-based prioritization for pruning operations.

## Features

- **Quarter Section Visualization**: Each quarter section is displayed as a uniform square on the map
- **Risk-Based Coloring**: Quarter sections are color-coded by risk level:
  - 🔴 Critical (70-100)
  - 🟠 High (50-70)
  - 🟡 Medium (30-50)
  - 🟢 Low (0-30)
- **Interactive Filters**:
  - Risk level (Critical, High, Medium, Low)
  - Risk score range slider
  - District filter
  - Minimum tree count
  - Show/hide tree points
  - Show/hide quarter section labels
- **Statistics Panel**: Real-time statistics about the filtered data
- **Click for Details**: Click any quarter section to see detailed information

## Setup Instructions

1. **Prepare the data** (if not already done):
   ```bash
   cd trees/xander/eda
   python prepare_map_data.py
   ```
   
   This will generate:
   - `../../data/quarter_sections_map.geojson` - Quarter section boundaries
   - `../../data/map_summary.json` - Summary statistics
   - `../../data/tree_points_sample.json` - Sample tree locations

2. **Open the map**:
   
   **Option 1: Direct file open (may have CORS issues)**
   - Simply double-click `map_frontend.html` to open in your browser
   - Note: Some browsers may block loading local JSON files due to CORS
   
   **Option 2: Local web server (recommended)**
   ```bash
   # Navigate to the project root
   cd c:\Users\xande\OneDrive\Desktop\Coding\mke-trees
   
   # Start a simple HTTP server
   # Python 3:
   python -m http.server 8000
   
   # Python 2:
   python -m SimpleHTTPServer 8000
   
   # Then navigate to:
   # http://localhost:8000/trees/xander/eda/map_frontend.html
   ```
   
   **Option 3: VS Code Live Server**
   - Install the "Live Server" extension in VS Code
   - Right-click `map_frontend.html` and select "Open with Live Server"

## Data Sources

- **Inventory Data**: `data/Inventory 1-15-26.csv`
- **Service Requests**: `data/10 year service requests.csv`

## How It Works

1. **Data Preparation** (`prepare_map_data.py`):
   - Loads tree inventory data
   - Groups trees by Quarter Section
   - Calculates risk scores based on:
     - Condition (Poor condition trees)
     - Tree size (DBH)
     - Tree density
   - Creates uniform square boundaries for each quarter section
   - Generates GeoJSON for map visualization

2. **Map Frontend** (`map_frontend.html`):
   - Uses Leaflet.js for map rendering
   - Loads GeoJSON data
   - Renders quarter sections as colored polygons
   - Provides interactive filtering and statistics

## Risk Score Calculation

The risk score is calculated as:
- Condition Risk (40%): Percentage of trees in poor condition
- Size Risk (30%): Average DBH normalized to 30 inches
- Density Risk (30%): Number of trees normalized to 100

## Usage Tips

- **Filter by Risk Level**: Uncheck risk levels to hide them from the map
- **Adjust Risk Range**: Use sliders to focus on specific risk score ranges
- **Filter by District**: Select a specific district to focus analysis
- **Tree Count Filter**: Filter out quarter sections with few trees
- **Tree Points**: Toggle to show/hide individual tree locations (may impact performance)

## File Structure

```
trees/
├── data/
│   ├── quarter_sections_map.geojson  # Quarter section boundaries
│   ├── map_summary.json              # Summary statistics
│   └── tree_points_sample.json       # Sample tree points
└── xander/
    └── eda/
        ├── prepare_map_data.py       # Data preparation script
        ├── map_frontend.html         # Interactive map frontend
        └── README_MAP.md             # This file
```

## Future Enhancements

- Integration with actual weighted priority scores from further_analysis.ipynb
- Historical failure data overlay
- Time-based filtering (show changes over time)
- Export filtered data to CSV
- Print-friendly reports
- Mobile-responsive design improvements
