import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import folium
import folium.plugins
import datetime
import os
from PIL import Image, ImageDraw, ImageFont

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

# Defini le temps initial
start_time = datetime.datetime.strptime("06:00:00", "%H:%M:%S").time()
end_time = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
delta = datetime.timedelta(minutes=15)

def calculate_bus_trips(stop_id, start_time, end_time):
    stop_times_copy = stop_times_df.loc[stop_times_df['stop_id'] == int(stop_id)].copy()
    
    # Convertir les heures d'arrivée dépassant minuit
    stop_times_copy['arrival_time'] = stop_times_copy['arrival_time'].apply(lambda x: x.replace('24:', '00:'))
    
    # Remplacer les heures d'arrivée supérieures à 24 heures par 23:59:59
    stop_times_copy['arrival_time'] = stop_times_copy['arrival_time'].apply(lambda x: '23:59:59' if x > '23:59:59' else x)
    
    stop_times_copy['arrival_time'] = pd.to_datetime(stop_times_copy['arrival_time'], format="%H:%M:%S").dt.time
    stop_times_copy = stop_times_copy[(stop_times_copy['arrival_time'] >= start_time) &
                                      (stop_times_copy['arrival_time'] <= end_time)]
    
    return len(stop_times_copy['trip_id'].unique())

# Creer un dictionnaire pour stocker les données de la carte thermique
heatmap_data_by_time = {}

while start_time < end_time:
    temp_df = zone_stops_df.copy()

    temp_df['bus_trips'] = 0

    for i, stop in temp_df.iterrows():
        stop_id = stop['stop_id']
        bus_trips = calculate_bus_trips(stop_id, start_time, end_time)
        temp_df.at[i, 'bus_trips'] = bus_trips

    service_quality = temp_df['bus_trips'].sum()

    heatmap_data_by_time[start_time.isoformat()] = [[row['stop_lat'], row['stop_lon'], row['bus_trips']] for i, row in temp_df.iterrows()]

    start_time = (datetime.datetime.combine(datetime.date.today(), start_time) + delta).time()

m = folium.Map(location=[zone_lat, zone_lon], zoom_start=15)

output_dir = 'heatmap_images'
os.makedirs(output_dir, exist_ok=True)

#Creer une image de la carte thermique pour chaque fenetre de temps
for key, data in heatmap_data_by_time.items():
    print("Processing time window:", key, "...")

    heatmap = folium.plugins.HeatMap(
        data=data,
        name=f'Heatmap {key}',
        max_opacity=0.8,
    )

    heatmap.add_to(m)

    key_for_filename = key.replace(':', '_')

    #Exporte la carte thermique byte pour le convertir en image PNG
    bytepng = m._to_png(1)
    png_filename = f'heatmap_images/heatmap_{key_for_filename}.png'
    with open(f'heatmap_images/heatmap_{key_for_filename}.png', 'wb') as f:
        f.write(bytepng)
    
    #Ajoute une étiquette au PNG
    img = Image.open(png_filename)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    label_text = key
    font = ImageFont.truetype("arial.ttf", 24)
    label_width, label_height = draw.textsize(label_text, font=font)
    label_x = (width - label_width) / 2
    label_y = 10
    label_color = (0, 0, 0) #Couleur du texte en RGB
    draw.text((label_x, label_y), label_text, fill=label_color, font=font)
    img.save(png_filename)

    m = folium.Map(location=[zone_lat, zone_lon], zoom_start=15)

print("Heatmap images generated in heatmap_images folder")

input_dir = 'heatmap_images'

# Prendre tous les fichiers PNG dans le dossier d'entrée
png_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.png')]

png_files.sort()

frames = []

for png_file in png_files:
    img = Image.open(png_file)
    frames.append(img)

output_gif = 'heatmap_animation.gif'

frames[0].save(output_gif, save_all=True, append_images=frames[1:], duration=500, loop=0)

print(f'GIF saved as {output_gif}')