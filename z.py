from flask import Flask, render_template, request
import pandas as pd
import re
from pathlib import Path

app = Flask(__name__)

@app.route("/search_suppliers",methods=['POST'])
def search_suppliers():
    part_name=request.form["supplier_name"]
    p=Path("Suppliers")
    with open(p/f"{part_name}.txt",'r') as file:
        info=file.read()
    #print(info)
    return render_template("supplier_details.html",details=info)

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


@app.route("/search_parts", methods=["POST"])
def search_parts():
    part_name = request.form["part_name"]

    # Marklines
    excel_file_path = Path(part_name+'.csv')
    df = pd.read_csv(excel_file_path)
    table_html = df.to_html(classes='data', header="true",index=False)
    marklines_data = getMarklinesData(part_name)
    
    # Zauba 
    india_imports = getZaubaData(part_name, 'india')
    us_imports = getZaubaData(part_name, 'us')

    return render_template("part_details.html", part_name=part_name, india_imports=india_imports, us_imports=us_imports, marklines_data=marklines_data)


def getZaubaData(part_name, country):
    part_name = part_name.strip().lower()
    part_name = re.sub(' +', '_', part_name)
    if country == 'india':
        data = pd.read_csv(f"{part_name}_imports_india.csv")
    else:
        data = pd.read_csv(f"{part_name}_imports_us.csv")
    data = data.to_dict(orient='records')
    return data

def getMarklinesData(part_name):
    data = pd.read_csv(f"{part_name}.csv")
    data = data.to_dict(orient='records')
    return data

if __name__ == "__main__":
  app.run(debug=True)
