import tkinter as tk
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

stops_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/stops.txt')
routes_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/routes.txt')
trips_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/trips.txt')
stop_times_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/stop_times.txt')


def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6371  # Earth's radius in kilometers
    distance = radius * c

    return distance

zone_radius = 0.50  # Assuming 100m radius is approximately 0.05 degrees in latitude/longitude

zone_lat = 45.43659691976552
zone_lon = -73.60503713208213
zone_stops = []
for index, stop in stops_df.iterrows():
    distance = haversine(zone_lat, zone_lon, stop['stop_lat'], stop['stop_lon'])
    if distance <= zone_radius:
        zone_stops.append(stop)

zone_stops_df = pd.DataFrame(zone_stops)

print(zone_stops_df)

# Create a heatmap of the zone for the quality of service
def generate_heatmap():
    # Create a new window
    window = tk.Toplevel()
    window.title("Heatmap")

    # Create a canvas
    canvas = tk.Canvas(window, width=800, height=800, bg='white')
    canvas.pack()

    # Draw the zone
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')
    canvas.create_rectangle(0, 0, 800, 800, fill='white')

    # Draw the stops
    for index, stop in zone_stops_df.iterrows():
        x = (stop['stop_lon'] - zone_lon) * 10000 + 400
        y = (stop['stop_lat'] - zone_lat) * 10000 + 400
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='red')
    
    # Draw the routes
    for index, route in routes_df.iterrows():
        route_trips_df = trips_df[trips_df['route_id'] == route['route_id']]
        route_stop_times_df = stop_times_df[stop_times_df['trip_id'].isin(route_trips_df['trip_id'])]
        route_stops_df = stops_df[stops_df['stop_id'].isin(route_stop_times_df['stop_id'])]
        for index, stop in route_stops_df.iterrows():
            x = (stop['stop_lon'] - zone_lon) * 10000 + 400
            y = (stop['stop_lat'] - zone_lat) * 10000 + 400
            canvas.create_oval(x - 1, y - 1, x + 1, y + 1, fill='blue')

generate_heatmap()

