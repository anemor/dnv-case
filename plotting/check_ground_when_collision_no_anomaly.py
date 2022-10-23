import geopandas as gpd
import matplotlib.pyplot as plt
import time
import shapely.geometry as  geom
import geopy
import geopy.distance
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

###   PLOT NORGE   #################################################################################################################################################
####################################################################################################################################################################

print("Loading Norway…")
start_time = time.time()

coast_gdf = gpd.read_file("NOR_SHP/Norway_coast_cropped.shp")#.to_crs('EPSG:4326')
coast_gdf = coast_gdf.clip_by_rect(xmin=10.43, ymin=59.37, xmax=10.7, ymax=59.46)
fig = plt.figure()
coast_ax = fig.add_subplot(autoscale_on=False, xlim=(10.43, 10.7), ylim=(59.37, 59.46))
coast_gdf.plot(ax=coast_ax)
print(f"Finished loading Norway, took {time.time() - start_time}s")

# Date constants
START_DATE = np.datetime64("2022-08-01")
END_DATE = np.datetime64("2022-08-02")

KNOTS_CONVERSION_FACTOR = 1.9438444924406
LOOKAHEAD_TIME = 20*60 # 20 minutes worth of seconds

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
map_df = pd.read_csv("ais_202208_bastovi_2.csv", sep=",")
print("FINISHED LOADING CSV")

# Anomaly
print("\nLoading anomaly CSV")
# anomalies_df = pd.read_csv("anomalies_lat_lon_7d.csv")
anomalies_df = pd.read_csv("anomalies_dag1_fra_dag8.csv")
print("Finished loading anomaly CSV")

print("\nUpdating anomaly timestamp")
anomalies_df["timestamp"] = pd.to_datetime(anomalies_df["timestamp"]).dt.tz_localize(None)
print("Finished updating anomaly timestamp")

# Filter by date
print("\nFiltering by date")
map_df["date_time_utc"] = pd.to_datetime(map_df["date_time_utc"]).dt.tz_localize(None)
mask = (map_df["date_time_utc"] > START_DATE) & (map_df["date_time_utc"] < END_DATE)
map_df = map_df.loc[mask]
print("Finished filtering by date")

# Find collisions
print("\nFinding collisions…")
def find_collision(timestamp, length, lon, lat, sog, head):
    # Get current values
    current = geopy.Point(lon, lat)
    dist_object = geopy.distance.geodesic(kilometers = 0.001 * 5 * length)
    # top_left = dist_object.destination(point=current, bearing=-63-head)
    # top_right = dist_object.destination(point=current, bearing=63-head)
    # bot_left = dist_object.destination(point=current, bearing=116-head)
    # bot_right = dist_object.destination(point=current, bearing=-116-head)
    top_left = dist_object.destination(point=current, bearing=90+116-head)
    top_right = dist_object.destination(point=current, bearing=90-116-head)
    bot_left = dist_object.destination(point=current, bearing=270+116-head)
    bot_right = dist_object.destination(point=current, bearing=270-116-head)

    a = geom.Point(top_left.latitude, top_left.longitude)
    b = geom.Point(top_right.latitude, top_right.longitude)
    c = geom.Point(bot_left.latitude, bot_left.longitude)
    d = geom.Point(bot_right.latitude, bot_right.longitude)
    poly = geom.Polygon([a, b, c, d])
    intersection = coast_gdf.intersects(poly)
    return poly, intersection.bool()
# Run thing
map_df = map_df.assign(collision=False, polygon=False, anomaly=False)
for i in range(map_df.first_valid_index(), map_df.first_valid_index()+len(map_df)):
    if (i % 1000 == 0):
        print(str(i) + ' collisions checked')
    
    # Get anomaly value where timestamp is same
    ts = map_df.at[i, 'date_time_utc']
    anomaly_index = next(iter(anomalies_df[anomalies_df['timestamp'] == ts].index), None)
    polygon, collision = find_collision(
        map_df.at[i, 'date_time_utc'],
        map_df.at[i, 'LengthOverallLOA'],
        map_df.at[i, 'lon'],
        map_df.at[i, 'lat'],
        map_df.at[i, 'sog'],
        map_df.at[i, 'true_heading'],
    )
    map_df.at[i, 'polygon'] = polygon
    if (collision):
        map_df.at[i, 'collision'] = True
    # if (anomaly_index == None):
    #     continue
    # if (anomalies_df.at[anomaly_index, 'value']):
    #     # print(i)
    #     map_df.at[i, 'anomaly'] = True
    # poly = map_df.polygon
    # print(poly[i])
    # print(polygon)
    # quit()

    # # Get current values
    # current = geopy.Point((map_df.lon)[i], (map_df.lat)[0])
    # v = (map_df.sog)[i]
    # th = (map_df.true_heading)[i]
    # dist_object = geopy.distance.geodesic(kilometers = 0.001 * LOOKAHEAD_TIME * v / KNOTS_CONVERSION_FACTOR)
    # next_point_mid = dist_object.destination(point=current, bearing=90-th)
    # next_point_up = dist_object.destination(point=current, bearing=97.5-th)
    # next_point_down = dist_object.destination(point=current, bearing=82.5-th)

    # # dotp.set_data(current.latitude, current.longitude)
    # # dotu.set_data(next_point_up.latitude, next_point_up.longitude)
    # # dotm.set_data(next_point_mid.latitude, next_point_mid.longitude)
    # # dotd.set_data(next_point_down.latitude, next_point_down.longitude)

    # a = geom.Point(current.latitude, current.longitude)
    # b = geom.Point(next_point_up.latitude, next_point_up.longitude)
    # c = geom.Point(next_point_mid.latitude, next_point_mid.longitude)
    # d = geom.Point(next_point_down.latitude, next_point_down.longitude)
    # poly = geom.Polygon([a, b, c, d])
    # intersection = coast_gdf.intersects(poly)
    # # print(intersection)
    # if (intersection.bool()):
    #     print('Collision found')
    #     map_df.at[i, 'collision'] = True
    # print(intersection.bool())
print("All collisions found")

# Output total length
print("\nTotal columns of dataframe")
print(len(map_df))
print("Printed columns of dataframe")

# Plot ferry route (real time)
from collections import deque
dotp, = coast_ax.plot([], [], 'o', color="orange", lw=2)
poly, = coast_ax.plot([], [], color="green", lw=1)
# dotu, = coast_ax.plot([], [], 'o', color="red", lw=1)
# dotm, = coast_ax.plot([], [], 'o', color="red", lw=1)
# dotd, = coast_ax.plot([], [], 'o', color="red", lw=1)
trace, = coast_ax.plot([], [], '-', lw=1, ms=2)
time_text = coast_ax.text(0.05, 0.9, '', transform=coast_ax.transAxes)
history_x, history_y = deque(maxlen=len(map_df)), deque(maxlen=len(map_df))

# Separate anomaly trace
anomaly_trace, = coast_ax.plot([], [], 'o', color='orange', lw=1, ms=2)
anomaly_collision_trace, = coast_ax.plot([], [], 'o', color='red', lw=1, ms=2)
anomaly_history_x, anomaly_history_y = deque(maxlen=len(map_df)), deque(maxlen=len(map_df))
anomaly_collision_history_x, anomaly_collision_history_y = deque(maxlen=len(map_df)), deque(maxlen=len(map_df))

# x = map_df.lon
# y = map_df.lat
# collisions = map_df.collision
# anomalies = map_df.anomalies
# polygons = map_df.polygon
# heading = map_df.true_heading
# times = map_df.date_time_utc

# For visualization
def animate(i):
    index = i + map_df.first_valid_index()
    if index == 0:
        anomaly_history_x.clear()
        anomaly_history_y.clear()
        history_x.clear()
        history_y.clear()
        anomaly_collision_history_x.clear()
        anomaly_collision_history_y.clear()
    history_x.appendleft(map_df.at[index, 'lon'])
    history_y.appendleft(map_df.at[index, 'lat'])
    # history_x.appendleft(x[index])
    # history_y.appendleft(y[index])

    # Visualise sector
    current = geopy.Point(history_x[0], history_y[0])
    dotp.set_data(current.latitude, current.longitude)
    poly_x, poly_y = map_df.at[index, 'polygon'].exterior.xy
    if (map_df.at[index, 'collision']):
        anomaly_collision_history_x.appendleft(history_x[0])
        anomaly_collision_history_y.appendleft(history_y[0])
        anomaly_collision_trace.set_data(anomaly_collision_history_x, anomaly_collision_history_y)
    poly.set_data(poly_x, poly_y)
    # if (map_df.at[index, 'anomaly']):
    #     else:
    #         anomaly_history_x.appendleft(history_x[0])
    #         anomaly_history_y.appendleft(history_y[0])
    #         anomaly_trace.set_data(anomaly_history_x, anomaly_history_y)
    
    trace.set_data(history_x, history_y)
    time_text.set_text('Time: ' + str(map_df.at[index, 'date_time_utc']))
    return trace, anomaly_trace, anomaly_collision_trace, time_text, dotp, poly


ani = animation.FuncAnimation(fig, animate, len(map_df), interval=1, blit=True)
plt.show()
