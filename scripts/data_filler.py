import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from pandas import DataFrame

def fill_missing_data(df: DataFrame) -> DataFrame:
    """
    Uses kNN to fill missing Height and Crown Width.
    Steps:
    1. Encode 'Scientific Name' as numeric codes for kNN.
    2. Impute 'Height' using 'DBH' and 'species_code'.
    3. Impute 'Crown Width' using 'DBH', 'Height', and 'species_code'.
    """
    df_filled = df.copy()

    if 'Scientific Name' in df_filled.columns:
        species_col = 'Scientific Name'
    else:
        species_col = 'Full Name'

    dummies = pd.get_dummies(df_filled[species_col], prefix='species', dummy_na=False)
    species_features = dummies.columns.tolist()
    
    df_filled = pd.concat([df_filled, dummies], axis=1)

    height_features = ['DBH'] + species_features
    df_filled = _run_knn_imputation(df_filled, 'Height', height_features)

    width_features = ['DBH', 'Height'] + species_features
    df_filled = _run_knn_imputation(df_filled, 'Crown Width', width_features)

    # Remove temporary columns
    df_filled = df_filled.drop(columns=species_features)
    
    return df_filled

def _run_knn_imputation(df: DataFrame, target: str, features: list) -> DataFrame:
    if target not in df.columns:
        return df

    missing_mask = df[target].isna() & df[features].notna().all(axis=1)
    train_mask = df[target].notna() & df[features].notna().all(axis=1)

    if missing_mask.any() and train_mask.any():
        X_train = df.loc[train_mask, features]
        y_train = df.loc[train_mask, target]
        X_test = df.loc[missing_mask, features]

        # Set n_neighbors to a max of 30 local trees, at minimum 1
        n_samples = train_mask.sum()
        n_neighbors = max(5, min(30, int(np.sqrt(n_samples))))

        knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights='distance')
        knn.fit(X_train, y_train)
        
        df.loc[missing_mask, target] = knn.predict(X_test)
    return df