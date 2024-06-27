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
    query=request.form["query"]
    # Marklines
    marklines_data,insights = getMarklinesData(part_name)
    
    if(query):
        query_resp=getResp(query,part_name)
    else:
        query_resp=""
        
    
    # Zauba 
    india_imports = getZaubaData(part_name, 'india')
    us_imports = getZaubaData(part_name, 'us')

    return render_template("part_details.html", part_name=part_name, india_imports=india_imports, us_imports=us_imports, marklines_data=marklines_data,insights=insights,query_resp=query_resp)


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


def getResp(query,part_name):
    client = OpenAI(api_key="")
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
    return resp


if __name__ == "__main__":
  app.run(debug=True)
