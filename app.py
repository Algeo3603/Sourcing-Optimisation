from flask import Flask, render_template, request, session,jsonify
import pandas as pd
import re
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv
import folium
from geopy.geocoders import Nominatim
import csv
from JSONVis import Visualizer


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


app = Flask(__name__)
app.secret_key="123456"


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/search_parts", methods=["POST"])
def search_parts():
    part_name = request.form["part_name"]
    session["part_name"]=part_name

    # Marklines
    marklines_data,insights = getMarklinesData(part_name)
    
    # Zauba 
    india_imports = getZaubaData(part_name, 'india')
    us_imports = getZaubaData(part_name, 'us')

    return render_template("part_details.html", part_name=part_name, india_imports=india_imports, us_imports=us_imports, marklines_data=marklines_data,insights=insights,query_resp="")


@app.route("/getResp", methods=["POST"])
def getResp():
    data = request.json
    query = data.get('query')
    part_name=session['part_name']
    client = OpenAI(api_key=OPENAI_API_KEY)
    MODEL="gpt-4o"
    df = pd.read_excel(f"{part_name}.xlsx")
    df=df.sample(n=400)
    content = df.to_string(index=False)
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Based on the excel sheet, try to answer the following query. Query:"+query},
            {"role": "user", "content": content}
        ]
    )
    resp=completion.choices[0].message.content
    return jsonify({'query_resp': resp})


@app.route('/us_imports_visualisation', methods=['POST', 'GET'])
def us_imports_visualisation():
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


@app.route('/india_imports_visualisation', methods=['POST', 'GET'])
def india_imports_visualisation():
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


@app.route("/search_suppliers",methods=['POST'])
def search_suppliers():
    part_name=request.form["supplier_name"]
    p=Path("Suppliers")
    with open(p/f"{part_name}.txt",'r') as file:
        info=file.read()
    #print(info)
    return render_template("supplier_details.html",details=info)


@app.route("/visualize",methods=['POST','GET'])
def visualize_relations():
    return render_template('graph.html')


@app.route("/visualize/filter", methods=['GET', 'POST'])
def select():
    directory_path=Path('TempJSONs/Suppliers')
    sellers=[f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    sellers=[f[:-5] for f in sellers]
    sellers.sort()
    
    directory_path=Path('TempJSONs/Buyers')
    buyers = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    buyers = [f[:-5] for f in buyers]
    buyers.sort()
    
    sellers=list(set(sellers))
    sellers.sort()
    selected_companies = []
    parts=['Clutch','Axle','Shock Absorber']
    
    return render_template('VisSelect.html', selected_companies=selected_companies, buyers=sellers , sellers=buyers,parts=parts)


@app.route("/visualize/filtered", methods=['POST'])
def graph_vis():
    sellers=request.form.getlist('buyers')
    buyers=request.form.getlist('sellers')
    minThickness=request.form['minThickness']
    minThickness=int(minThickness)
    parts_list=request.form.getlist('parts')
    print(buyers)
    countries=request.form.getlist('Countries')
    Visualizer(buyers,sellers,parts_list,minThickness,countries)
    
    return render_template('search.html')


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


def getMarklinesData(part_name):
    client = OpenAI(api_key=OPENAI_API_KEY)
    MODEL="gpt-4o"
    df = pd.read_excel(f"{part_name}.xlsx")
    df=df.sample(n=400)
    content = df.to_string(index=False)
    
    prompt="""You are an expert data analyst who specializes in deriving insights from large excel sheets.
    Your task is to identify as many insights as possible regarding industry trends, suppliers, buyers and partnerships between suppliers and buyers from the excel sheet being provided to you as well as any other information that you have access to.
    Divide your response into sections for industry trends, buyers, suppliers, partnerships, and misc.

    When highlighting an insight:
    1) Give it a short title, and follow it up with concise sentence that gives further details on the next line.
    2) There should be no formatting
    3) Do not make the insights too long

    Your goal is to help your client make smarter decisions regarding their business using this data.
    """
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
    )
    insights=completion.choices[0].message.content
    
    
    data = df.to_dict(orient='records')
    return data,insights


def getZaubaData(part_name, country):
    part_name = part_name.strip().lower()
    part_name = re.sub(' +', '_', part_name)
    if country == 'india':
        data = pd.read_csv(f"{part_name}_imports_india.csv")
    else:
        data = pd.read_csv(f"{part_name}_imports_us.csv")
    data = data.to_dict(orient='records')
    return data


def process_india_imports():
    geocoder = Nominatim(user_agent="locator")
    df = pd.read_csv('brake_line_imports_india.csv')

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


if __name__ == "__main__":
  app.run(debug=True)
