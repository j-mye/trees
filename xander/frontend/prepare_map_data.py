"""
Prepare data for the interactive map frontend.
Generates quarter section boundaries as squares and aggregates data.
"""
import pandas as pd
import numpy as np
import json
import os

# Load data
print("Loading data...")
inventory_df = pd.read_csv('../../data/Inventory 1-15-26.csv', low_memory=False)

# Convert quarter section to string
inventory_df['Quarter Section'] = inventory_df['Quarter Section'].astype(str).str.replace('.0', '', regex=False)

# Add Species_Simple if it doesn't exist
if 'Species_Simple' not in inventory_df.columns:
    def simplify_species(species):
        if pd.isna(species):
            return 'Unknown'
        species_str = str(species).upper()
        if ',' in species_str:
            return species_str.split(',')[0].strip()
        elif '(' in species_str:
            return species_str.split('(')[0].strip()
        else:
            return species_str.split()[0] if species_str.split() else 'Unknown'
    inventory_df['Species_Simple'] = inventory_df['Species'].apply(simplify_species)

# Filter out invalid coordinates
inventory_df = inventory_df[
    (inventory_df['Latitude'].notna()) & 
    (inventory_df['Longitude'].notna()) &
    (inventory_df['Latitude'] != 0) &
    (inventory_df['Longitude'] != 0)
]

print(f"Trees with valid coordinates: {len(inventory_df):,}")

# Calculate Milwaukee bounds
min_lat = inventory_df['Latitude'].min()
max_lat = inventory_df['Latitude'].max()
min_lon = inventory_df['Longitude'].min()
max_lon = inventory_df['Longitude'].max()

print(f"Milwaukee bounds: Lat [{min_lat:.6f}, {max_lat:.6f}], Lon [{min_lon:.6f}, {max_lon:.6f}]")

# Group by Quarter Section
qs_data = inventory_df.groupby('Quarter Section').agg({
    'Site ID': 'count',
    'Latitude': ['mean', 'min', 'max'],
    'Longitude': ['mean', 'min', 'max'],
    'DBH': 'mean',
    'Condition': lambda x: x.value_counts().to_dict(),
    'Property Type': lambda x: x.value_counts().to_dict(),
    'District': lambda x: x.mode()[0] if len(x.mode()) > 0 else None,
    'Species_Simple': lambda x: x.value_counts().head(3).to_dict() if 'Species_Simple' in inventory_df.columns else {}
}).round(6)

# Flatten column names
qs_data.columns = ['_'.join(col).strip() if col[1] else col[0] for col in qs_data.columns.values]

# Rename columns
qs_data = qs_data.rename(columns={
    'Site ID_count': 'Total_Trees',
    'Latitude_mean': 'Center_Lat',
    'Longitude_mean': 'Center_Lon',
    'Latitude_min': 'Min_Lat',
    'Latitude_max': 'Max_Lat',
    'Longitude_min': 'Min_Lon',
    'Longitude_max': 'Max_Lon',
    'DBH_mean': 'Avg_DBH'
})

# Calculate square size for quarter sections
# Use a fixed size based on the data spread
lat_range = max_lat - min_lat
lon_range = max_lon - min_lon

# Estimate grid size (assuming roughly square grid)
# Calculate how many quarter sections we have
num_qs = len(qs_data)

# Calculate optimal square size to cover all quarter sections uniformly
# Use the larger dimension to ensure coverage
max_range = max(lat_range, lon_range)
grid_size = int(np.ceil(np.sqrt(num_qs * (max_range / min(lat_range, lon_range))))) + 1

# Square size in degrees (make all squares same size)
# Use consistent size for both lat and lon to make true squares
square_size = max_range / grid_size

print(f"Creating {num_qs} quarter section squares...")
print(f"Square size: {square_size:.6f} degrees (uniform)")

# Create square boundaries for each quarter section
qs_features = []

for qs_id, row in qs_data.iterrows():
    center_lat = row['Center_Lat']
    center_lon = row['Center_Lon']
    
    # Create square around center point (uniform size)
    half_size = square_size / 2
    
    # Square coordinates (4 corners) - uniform square
    square_coords = [
        [center_lat - half_size, center_lon - half_size],  # Bottom-left
        [center_lat - half_size, center_lon + half_size],  # Bottom-right
        [center_lat + half_size, center_lon + half_size],  # Top-right
        [center_lat + half_size, center_lon - half_size],  # Top-left
        [center_lat - half_size, center_lon - half_size]   # Close polygon
    ]
    
    # Calculate risk metrics (simplified - would use actual risk scores if available)
    condition_dist = row.get('Condition_<lambda>', {})
    poor_count = condition_dist.get('Poor', 0) if isinstance(condition_dist, dict) else 0
    condition_risk = (poor_count / row['Total_Trees'] * 100) if row['Total_Trees'] > 0 else 0
    
    # Simple risk score (can be replaced with actual weighted scores)
    risk_score = (
        condition_risk * 0.4 +
        (row['Avg_DBH'] / 30 * 100) * 0.3 +  # Larger trees = higher risk
        min(row['Total_Trees'] / 100 * 100, 100) * 0.3  # More trees = higher risk
    )
    
    # Risk category
    if risk_score >= 70:
        risk_level = 'Critical'
    elif risk_score >= 50:
        risk_level = 'High'
    elif risk_score >= 30:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'
    
    feature = {
        'type': 'Feature',
        'properties': {
            'quarter_section': str(qs_id),
            'total_trees': int(row['Total_Trees']),
            'avg_dbh': float(row['Avg_DBH']) if pd.notna(row['Avg_DBH']) else 0,
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'condition_risk': float(condition_risk),
            'district': str(row.get('District_<lambda>', 'Unknown')),
            'center_lat': float(center_lat),
            'center_lon': float(center_lon)
        },
        'geometry': {
            'type': 'Polygon',
            'coordinates': [square_coords]
        }
    }
    
    qs_features.append(feature)

# Create GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': qs_features
}

# Create data directory if it doesn't exist
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# Save GeoJSON
output_path = os.path.join(data_dir, 'quarter_sections_map.geojson')
with open(output_path, 'w') as f:
    json.dump(geojson, f, indent=2)

print(f"\nSaved GeoJSON to: {output_path}")
print(f"Total quarter sections: {len(qs_features)}")

# Also create a summary JSON with filter options
summary = {
    'bounds': {
        'min_lat': float(min_lat),
        'max_lat': float(max_lat),
        'min_lon': float(min_lon),
        'max_lon': float(max_lon),
        'center_lat': float((min_lat + max_lat) / 2),
        'center_lon': float((min_lon + max_lon) / 2)
    },
    'statistics': {
        'total_quarter_sections': len(qs_features),
        'total_trees': int(inventory_df['Site ID'].nunique()),
        'risk_levels': {
            'Critical': sum(1 for f in qs_features if f['properties']['risk_level'] == 'Critical'),
            'High': sum(1 for f in qs_features if f['properties']['risk_level'] == 'High'),
            'Medium': sum(1 for f in qs_features if f['properties']['risk_level'] == 'Medium'),
            'Low': sum(1 for f in qs_features if f['properties']['risk_level'] == 'Low')
        }
    },
    'districts': sorted(list(set([f['properties']['district'] for f in qs_features if f['properties']['district'] != 'Unknown']))),
    'risk_score_range': {
        'min': float(min(f['properties']['risk_score'] for f in qs_features)),
        'max': float(max(f['properties']['risk_score'] for f in qs_features))
    }
}

summary_path = os.path.join(data_dir, 'map_summary.json')
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"Saved summary to: {summary_path}")

# Create tree points data (sample for performance)
print("\nCreating tree points sample...")
tree_sample = inventory_df.sample(n=(len(inventory_df)), random_state=42)
tree_points = []
for _, row in tree_sample.iterrows():
    tree_points.append({
        'lat': float(row['Latitude']),
        'lon': float(row['Longitude']),
        'dbh': float(row['DBH']) if pd.notna(row['DBH']) else 0,
        'condition': str(row['Condition']) if pd.notna(row['Condition']) else 'Unknown',
        'quarter_section': str(row['Quarter Section'])
    })

tree_points_path = os.path.join(data_dir, 'tree_points_sample.json')
with open(tree_points_path, 'w') as f:
    json.dump(tree_points, f, indent=2)

print(f"Saved tree points sample to: {tree_points_path}")
print(f"Total tree points: {len(tree_points)}")

print("\nData preparation complete!")
