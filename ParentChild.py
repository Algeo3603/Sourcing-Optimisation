from pathlib import Path
from pyvis.network import Network
import json
import os


net = Network(notebook=True, cdn_resources="remote",directed=True)
net.set_options("""
    var options = {
    "physics": {
        "enabled": false
    }
    }
    """)

with open("ntier.json",'r') as file:
    data=json.load(file)
    
a=0
for group,companies in data.items():
    if(len(companies)==1):
        continue
    net.add_node(group,label=group,color='blue',x=a*1000,y=0)
    offset=-((len(companies)/2)*200)
    for company in companies:
        net.add_node(company,color='red',x=a*1000+offset,y=100)
        offset+=200
        net.add_edge(company,group)
    a+=1
        
net.show('templates/ntier.html')
        