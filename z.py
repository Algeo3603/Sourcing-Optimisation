from flask import Flask, render_template, request
import pandas as pd
import re
from openai import OpenAI
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
    # excel_file_path = Path(part_name+'.xlsx')
    # df = pd.read_excel(excel_file_path)
    # table_html = df.to_html(classes='data', header="true",index=False)
    marklines_data,insights = getMarklinesData(part_name)
    
    # Zauba 
    india_imports = getZaubaData(part_name, 'india')
    us_imports = getZaubaData(part_name, 'us')

    return render_template("part_details.html", part_name=part_name, india_imports=india_imports, us_imports=us_imports, marklines_data=marklines_data,insights=insights)


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
    client = OpenAI(api_key="")
    MODEL="gpt-4o"
    df = pd.read_excel(f"{part_name}.xlsx")
    df=df.sample(n=400)
    content = df.to_string(index=False)
    
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Derive as many insights as possible from the excel sheet that I am providing regarding suppliers and buyers. Make them as concise as possible."},
            {"role": "user", "content": content}
        ]
    )
    insights=completion.choices[0].message.content
    
    
    data = df.to_dict(orient='records')
    return data,insights

if __name__ == "__main__":
  app.run(debug=True)
