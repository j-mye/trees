# Milwaukee Tree Risk Map - Frontend

## Quick Start

1. **Prepare the data** (if not already done):
   ```bash
   cd trees/xander/frontend
   python prepare_map_data.py
   ```
   
   This creates the data files in the `data/` directory.

2. **Open the map**:
   - Simply open `map_frontend.html` in your web browser
   - Or use a local web server:
     ```bash
     # From project root
     python -m http.server 8000
     # Then navigate to: http://localhost:8000/trees/xander/frontend/map_frontend.html
     ```

## Files

- `map_frontend.html` - Main interactive map interface
- `prepare_map_data.py` - Script to generate map data from inventory
- `data/` - Generated data files (created by prepare_map_data.py)
  - `quarter_sections_map.geojson` - Quarter section boundaries
  - `map_summary.json` - Summary statistics
  - `tree_points_sample.json` - Sample tree locations

## Features

- **Uniform Square Quarter Sections**: All quarter sections displayed as same-size squares
- **Risk-Based Coloring**: Color-coded by risk level (Critical, High, Medium, Low)
- **Interactive Filters**: Filter by risk level, score range, district, tree count
- **Statistics Panel**: Real-time statistics
- **Click for Details**: Click any quarter section for detailed information

## Data Sources

- Inventory: `../../data/Inventory 1-15-26.csv`
- Service Requests: `../../data/10 year service requests.csv`
