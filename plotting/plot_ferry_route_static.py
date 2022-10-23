import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Date constants
START_DATE = np.datetime64("2022-08-01")
END_DATE = np.datetime64("2022-08-02")

# Column constants
COLUMNS = [
    "mmsi", # Ship identifier
    "lon", # Longitude
    "lat", # Latitude
    "date_time_utc", # Timestamp
    "sog", # Speed Over Ground ()
    "true_heading", # Actual direction (not angle)
    "calc_speed", # Calculated direction (from heading and sog)
    "name", # Ship name
    "L5_LloydsTypeCode", # Ship type code
]
PASSENGER_SHIP_TYPES = [
    "A32A2GF",
    "A36A2PR",
    "A36A2PT",
    "A36B2PL",
    "A37B2PS",
    "W12D5PR",
    "W12E5PS",
]

# Load CSV
print("\nLOADING CSV…")
map_df = pd.read_csv("ais_202208_bastovi.csv", sep=",")
print("FINISHED LOADING CSV")

# Filter by date
print("\nFiltering by date")
map_df["date_time_utc"] = pd.to_datetime(map_df["date_time_utc"]).dt.tz_localize(None)
mask = (map_df["date_time_utc"] > START_DATE) & (map_df["date_time_utc"] < END_DATE)
map_df = map_df.loc[mask]
print("Finished filtering by date")

# Output total length
print("\nTotal columns of dataframe")
print(len(map_df))

# Plot ferry route (static)
plt.plot(map_df.lon, map_df.lat, color="red", label="BASTO VI")
plt.show()
