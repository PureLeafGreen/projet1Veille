import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import folium
import folium.plugins
from tkinter import *
import datetime

stops_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/stops.txt')
routes_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/routes.txt')
trips_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/trips.txt')
stop_times_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/stop_times.txt')
calendar_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/calendar.txt')
calendar_dates_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/calendar_dates.txt')
shapes_df = pd.read_csv('F:/session_9/veille_techno/projet1Veille/gtfs_stm/shapes.txt')

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

# Define the time window (t to t + 15 minutes)
start_time = datetime.datetime.strptime("06:00:00", "%H:%M:%S")
end_time = datetime.datetime.strptime("06:15:00", "%H:%M:%S")

# Create a function to calculate the number of bus trips for a given stop and time window
def calculate_bus_trips(stop_id, start_time, end_time):
    stop_times = stop_times_df.loc[stop_times_df['stop_id'] == int(stop_id)]
    
    # Convertir les heures d'arrivée dépassant minuit
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(lambda x: x.replace('24:', '00:'))
    
    # Remplacer les heures d'arrivée supérieures à 24 heures par 23:59:59
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(lambda x: '23:59:59' if x > '23:59:59' else x)
    
    stop_times['arrival_time'] = pd.to_datetime(stop_times['arrival_time'], format="%H:%M:%S").dt.time
    stop_times = stop_times[(stop_times['arrival_time'] >= start_time.time()) &
                            (stop_times['arrival_time'] <= end_time.time())]
    return len(stop_times['trip_id'].unique())

# Calculate the number of bus trips for each stop in the time window
for i, stop in zone_stops_df.iterrows():
    stop_id = stop['stop_id']
    bus_trips = calculate_bus_trips(stop_id, start_time, end_time)
    zone_stops_df.at[i, 'service_quality'] = bus_trips

# Calculate the total service quality using the formula you provided

print(zone_stops_df)

# Create a map centered on the specified zone
m = folium.Map(location=[zone_lat, zone_lon], zoom_start=15)

# Add a heatmap layer to the map using the morning_peak column of zone_stops_df
heat_data = [[row['stop_lat'], row['stop_lon'], row['service_quality']] for i, row in zone_stops_df.iterrows()]
m.add_child(folium.plugins.HeatMap(heat_data))

# Save the map as an HTML file
m.save('heatmap.html')