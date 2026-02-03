from pandas import DataFrame
import pandas as pd
import numpy as np

data = {
    'Site ID': [],
    'Quarter Section': [],
    'Address': [],
    'Street': [],
    'Side': [],
    'Site': [],
    'On Street': [],
    'Species': [],
    'DBH': [],
    'Latitude': [],
    'Longitude': [],
    'Inventory Date': [],
    'Species to Plant': [],
    'Condition': [],
    'Alder': [],
    'Closest Cross Street': [],
    'Crown Width': [],
    'Damage': [],
    'Direction from Cross Street': [],
    'Disease': [],
    'Distance from Cross Street': [],
    'District': [],
    'Growing Space': [],
    'Height': [],
    'Property Type': [],
    'Pruning Cycle': [],
    'Reason to Remove': [],
    'Side of Street': [],
    'Site Type': [],
    'Valuation Total': [],
    'Site Last Changed On': [],
    'Site Comments': [],
    'Census Block: Disadvantaged Area': [],
    'Census Block ID': [],
}

data_types = {
    'Site ID': 'int',
    'Quarter Section': 'category',
    'Address': 'string',
    'Street': 'string',
    'Side': 'category',
    'Site': 'category',
    'On Street': 'string',
    'Species': 'category',
    'DBH': 'float',
    'Latitude': 'float',
    'Longitude': 'float',
    'Inventory Date': 'string',
    'Species to Plant': 'category',
    'Condition': 'category',
    'Alder': 'category',
    'Closest Cross Street': 'string',
    'Crown Width': 'float',
    'Damage': 'category',
    'Direction from Cross Street': 'category',
    'Disease': 'category',
    'Distance from Cross Street': 'float',
    'District': 'category',
    'Growing Space': 'category',
    'Height': 'float',
    'Property Type': 'category',
    'Pruning Cycle': 'category',
    'Reason to Remove': 'category',
    'Side of Street': 'category',
    'Site Type': 'category',
    'Valuation Total': 'float',
    'Site Last Changed On': 'datetime64[ns]',
    'Site Comments': 'string',
    'Census Block: Disadvantaged Area': 'bool',
    'Census Block ID': 'category',
    'Full Name': 'category',
    'Abbreviation': 'category',
    'Scientific Name': 'category',
}

import os
path = os.path.join(os.path.dirname(__file__), '../data/raw/trees.csv')

def load_data() -> DataFrame:
    import csv
    with open(path, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in data.keys():
                if key in row:
                    data[key].append(row[key] if row[key] != '' else None)
    return convert_types()

def convert_types() -> DataFrame:
    df = pd.DataFrame(data)

    # Weird regex pattern to get components of species name
    regex_pattern = r'^(?P<full_name>.*?)\s*\((?P<abbreviation>.*?)\)\s*\((?P<scientific_name>.*?)\)$'
    df[['Full Name', 'Abbreviation', 'Scientific Name']] = df['Species'].str.extract(regex_pattern)
    df['Full Name'] = df['Full Name'].str.strip(', ')
    
    df['Site Last Changed On'] = pd.to_datetime(
        df['Site Last Changed On'], 
        format='%m/%d/%Y, %I:%M:%S %p', 
        errors='coerce'
    )

    df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
    df['Crown Width'] = pd.to_numeric(df['Crown Width'], errors='coerce')

    df.loc[df['Height'] <= 0, 'Height'] = np.nan
    df.loc[df['Crown Width'] <= 0, 'Crown Width'] = np.nan

    for key, dtype in data_types.items():
        if key in df.columns:
            if dtype == 'datetime64[ns]' or dtype == 'datetime':
                continue
            df[key] = df[key].astype(dtype)       
    return df