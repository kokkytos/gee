import pandas as pd
import numpy as np
import rasterio
import os, re
from pathlib import Path

from rasterio.mask import mask
from shapely.geometry import box, mapping

import geopandas as gpd
import fiona
import argparse

parser = argparse.ArgumentParser(
    description="Process data for a given YEAR and FUA_CODE."
)
parser.add_argument(
    "year",
    type=int,
    help="Year (e.g. 2000, 2001, … 2020)"
)
parser.add_argument(
    "fua_code",
    type=str,
    help="FUA code (e.g. ATH, BER, LON, …)"
)

args = parser.parse_args()

YEAR = int(args.year)
FUA = str(args.fua_code)

print(f"Year: {YEAR}, FUA: {FUA}")

fua_path = './data/FUA_fixed.shp'
tif_path = f'./tiffs/PopVeg_{YEAR}.vrt'

OUT_DIR = Path('./output/')
OUT_DIR.mkdir(parents=True, exist_ok=True)


OUT_CSV = OUT_DIR / f'gini_{FUA}_{YEAR}.csv'

# #Read FUA


# Load the shapefile
gdf = gpd.read_file(fua_path)

# Filter rows where 'fua_code' equal
gdf = gdf[gdf['fua_code'] == FUA]

gdf = gdf.to_crs('EPSG:3035')

# 2. Get bounding box of gdf as a shapely box
bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

# Create a shapely box from the bounds
bbox_geom = box(*bounds)

# Convert the box to GeoJSON format
bbox_geojson = [mapping(bbox_geom)]


    
# Open the raster file
with rasterio.open(tif_path) as src:
    nodata_value = src.nodata
    out_image, out_transform = mask(src, bbox_geojson, crop=True, nodata=nodata_value, filled=True)
    
    if nodata_value is not None:
        out_image = np.ma.masked_equal(out_image, nodata_value)

    fcover = out_image[0]  # First band
    pop = out_image[1]  # Second band
    
    
 

# Combined mask: keep only where both are valid
combined_mask = ~pop.mask & ~fcover.mask

# Apply mask to get valid values
pop_filtered = pop[combined_mask].compressed() 
fcover_filtered = fcover[combined_mask].compressed()

# repeat the values, need it for gini
repeated_fcover = np.repeat(fcover_filtered, pop_filtered)
repeated_pop = np.ones_like(repeated_fcover)

def get_gini(repeated_pop, repeated_fcover):
    try:
        
        # Create a pandas DataFrame
        df_all = pd.DataFrame({'pop': repeated_pop, 'veg': repeated_fcover})


        # Generate all greenspace that consider population distribution
        # green_all = np.repeat(df['veg'].values, df['pop'].values)
        # pop_all = np.ones(green_all.shape[0])

        #df_all = pd.DataFrame({'veg': green_all, 'pop': pop_all})
        df_all = df_all.sort_values(by='veg')

        # Cumulative sum of population
        df_all['cum_pop'] = df_all['pop'].cumsum()
        df_all['cum_veg'] = df_all['veg'].cumsum()


        # Compute percentiles
        percentiles_step =np.arange(0, 1.05, 0.05)
        percentiles = np.quantile(df_all['cum_pop'], percentiles_step)




        final_results = df_all[df_all['cum_pop'].isin(np.floor(percentiles).astype(int))]
        final_results = final_results.set_index(percentiles_step)
        
        final_results = final_results.rename(columns={'cum_pop': 'S_pop', 'cum_veg': 'S_veg'})


        # calculate T10/B10
        t10_b10 = final_results.loc[0.9, 'S_veg'] / final_results.loc[0.1, 'S_veg']


        final_results['Xk'] = final_results['S_pop'] / final_results['S_pop'].max()
        final_results['Yk'] = final_results['S_veg'] / final_results['S_veg'].max()

        # Create and append a new row with Xk = 0 and Yk = 0
        new_row = pd.DataFrame({'percentile_value': [np.nan], 'S_veg': [np.nan], 'S_pop': [np.nan], 'Xk': [0], 'Yk': [0]})
        final_results = pd.concat([new_row, final_results], ignore_index=True)

        # Sort by Xk
        final_results = final_results.sort_values(by='Xk')

        # Create the tabl dataframe
        tabl = pd.DataFrame({
            'b': final_results.loc[final_results['Yk'] < 1, 'Yk'],
            'B': final_results['Yk'].iloc[1:].reset_index(drop=True)  # Shifted Yk
        })

        # Calculate differences
        tabl['y'] = np.diff(final_results['Xk'].fillna(0))

        # Calculate trapezoid areas
        tabl['E'] = 0.5 * tabl['y'] * (tabl['B'] + tabl['b'])

        # Calculate Gini coefficient
        B = tabl['E'].sum()
        A = 0.5 - B
        gini = 2 * A
        gini = round(gini,5)


        # Export the results to CSV
        df_gini = pd.DataFrame({
            'FUA':[FUA],
            'Year': [YEAR],
            'Gini': [gini],
            't10_b10': [round(t10_b10,2)]

        })
    except Exception as e:
        print(f"[ERROR] get_gini failed: {e}")
        print (f"[Sfalma]: {FUA}, {YEAR}")
        df_gini = pd.DataFrame({
            'FUA': [FUA],
            'Year': [YEAR],
            'Gini': [np.nan],
            't10_b10': [np.nan]
        })

    return(df_gini)

df_gini = get_gini(repeated_pop, repeated_fcover)
df_gini.to_csv(OUT_CSV, index=False)


