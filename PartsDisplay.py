from flask import Flask, render_template,redirect,url_for
import pandas as pd
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('index',partName="Brake Line"))

@app.route('/partDisp/<partName>')
def index(partName):
    # Path to the Excel file on the server
    excel_file_path = Path(partName+'.csv')
    
    # Read the Excel file
    df = pd.read_csv(excel_file_path)
    
    # Convert DataFrame to HTML
    table_html = df.to_html(classes='data', header="true",index=False)
    
    return render_template('display.html', tables=[table_html])

if __name__ == '__main__':
    app.run(debug=True)
