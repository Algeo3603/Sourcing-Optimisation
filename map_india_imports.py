from flask import Flask, render_template
import folium
from geopy.geocoders import Nominatim
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


app = Flask(__name__)


@app.route('/')
def display_map():
    # display blank centered map 
    m = folium.Map(location=[0, 0], zoom_start=2)

    # call function and get data required for plotting tha map
    source_markers, destination_markers, arrow_coordinates, popup_info = process_india_imports()

    # add source markers
    for coordinates in source_markers:
        marker = folium.Marker(location=[coordinates[0], coordinates[1]], icon=folium.Icon(color='blue', icon='location-crosshairs', prefix='fa'))
        marker.add_to(m)

    # add destination markers
    for coordinates in destination_markers:
        marker = folium.Marker(location=[coordinates[0], coordinates[1]], icon=folium.Icon(color='red', icon='location-dot', prefix='fa'))
        marker.add_to(m)
    
    # add lines connecting source and destination
    for points in arrow_coordinates:
        line = folium.PolyLine(locations=points, weight=2, color='green')
        line.add_to(m)

    map_html = m._repr_html_()
    return render_template('map_india_imports.html', map_html=map_html)


def extract_location_from_llm(detailed_location):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON. Given a deatiled location string, return a JSON with a single field called 'location' which should contain just the name of the city/district. If city/district is unsure, return the state."},
            {"role": "user", "content": f"Return the name of the city/district/state for '{detailed_location}'"}
        ]
    )
    response_json = response.choices[0].message.content
    extracted_location = response.choices[0].message.content.split('"')[-2]
    return extracted_location


def process_india_imports():
    geocoder = Nominatim(user_agent="locator")
    df = pd.read_csv('fuel_hose_imports_india.csv')

    # these will be returned by this function
    source_markers = set()
    destination_markers = set()
    arrow_coordinates = []
    popup_info = {}
    # store locations extracted from llm for consistency
    extracted_destinations = {}

    print('loading', end="")
    for index, row in df.iterrows():
        try:
            # get extracted destination
            detailed_destination = row['Port of Discharge']
            if detailed_destination not in extracted_destinations:
                extracted_destinations[detailed_destination] = extract_location_from_llm(detailed_destination)
            extracted_destination = extracted_destinations[detailed_destination]
            # geocode the location names
            source = geocoder.geocode(row['Origin Country'])
            destination = geocoder.geocode(extracted_destination)
            # create tuples of the coordinates
            source_coordinate_tuple = (source.latitude, source.longitude)
            destination_coordinate_tuple = (destination.latitude, destination.longitude)
            # save the coordiantes to later plot them on the map
            source_markers.add(source_coordinate_tuple)
            destination_markers.add(destination_coordinate_tuple)
            arrow_coordinates.append([source_coordinate_tuple, destination_coordinate_tuple])
            # save text for the popup card on that location
            if source_coordinate_tuple not in popup_info:
                popup_info[source_coordinate_tuple] = row['Origin Country'] + "\nUnit, Quantity, Total Value (USD), Price Per Unit (USD)"
            popup_info[source_coordinate_tuple] += "\n" + row['Unit'] + ", " + row['Quantity'] + ", " + row['Total Value (USD)'] + ", " + row["Price Per Unit (USD)"]
            if destination_coordinate_tuple not in popup_info:
                popup_info[destination_coordinate_tuple] = extracted_destinations[row['Port of Discharge']] + "\nUnit, Quantity, Total Value (USD), Price Per Unit (USD)"
            popup_info[destination_coordinate_tuple] += "\n" + row['Unit'] + ", " + row['Quantity'] + ", " + row['Total Value (USD)'] + ", " + row["Price Per Unit (USD)"]
            print(".", end="")
        except:
            pass
    print("")
    
    return source_markers, destination_markers, arrow_coordinates, popup_info

if __name__ == '__main__':
    app.run(debug=True)
