from flask import Flask, render_template
import folium
from geopy.geocoders import Nominatim
import pandas as pd

app = Flask(__name__)

@app.route('/')
def display_map():
    # display blank centered map 
    m = folium.Map(location=[0, 0], zoom_start=2)

    # call function and get data required for plotting tha map
    source_markers, destination_markers, arrow_coordinates, popup_info = process_us_imports()

    # add source markers
    for coordinates in source_markers:
        marker = folium.Marker(location=[coordinates[0], coordinates[1]], icon=folium.Icon(color='blue', icon='location-crosshairs', prefix='fa'), popup=popup_info[coordinates])
        marker.add_to(m)

    # add destination markers
    for coordinates in destination_markers:
        marker = folium.Marker(location=[coordinates[0], coordinates[1]], icon=folium.Icon(color='red', icon='location-dot', prefix='fa'), popup=popup_info[coordinates])
        marker.add_to(m)
    
    # add lines connecting source and destination
    for points in arrow_coordinates:
        line = folium.PolyLine(locations=points, weight=2, color='green')
        line.add_to(m)

    map_html = m._repr_html_()
    return render_template('map_us_imports.html', map_html=map_html)

def process_us_imports():
    geocoder = Nominatim(user_agent="locator")
    df = pd.read_csv('brake_line_imports_us.csv')

    # these will be returned by this function
    source_markers = set()
    destination_markers = set()
    arrow_coordinates = []
    popup_info = {}

    print('loading', end="")
    for index, row in df.iterrows():
        try:
            # geocode the location names
            source = geocoder.geocode(row['Port of Loading'])
            destination = geocoder.geocode(row['Port of Discharge'])
            # create tuples of the coordinates
            source_coordinate_tuple = (source.latitude, source.longitude)
            destination_coordinate_tuple = (destination.latitude, destination.longitude)
            # save the coordiantes to later plot them on the map
            source_markers.add(source_coordinate_tuple)
            destination_markers.add(destination_coordinate_tuple)
            arrow_coordinates.append([source_coordinate_tuple, destination_coordinate_tuple])
            # save text for the popup card on that location
            if source_coordinate_tuple not in popup_info:
                popup_info[source_coordinate_tuple] = row['Port of Loading']
            popup_info[source_coordinate_tuple] += "\n" + row['Weight'] + ", " + row['Quantity']
            if destination_coordinate_tuple not in popup_info:
                popup_info[destination_coordinate_tuple] = row['Port of Discharge']
            popup_info[destination_coordinate_tuple] += "\n" + row['Weight'] + ", " + row['Quantity']
            print(".", end="")
        except:
            pass
    print("")
    
    return source_markers, destination_markers, arrow_coordinates, popup_info

if __name__ == '__main__':
    app.run(debug=True)