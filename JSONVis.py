from pathlib import Path
from pyvis.network import Network
import json
import os

def Visualizer(selected_buyers,selected_sellers,part_list,min_thickness,countries):
    
    net = Network(notebook=True, cdn_resources="remote",directed=True)
    net.set_options("""
    var options = {
    "physics": {
        "enabled": false
    }
    }
    """)
    added=set()
    addedB=set()
    a=0
    b=0
    c=0
    p=Path('TempJSONs/Buyers')
    for buyer in selected_buyers:
        net.add_node(buyer,label=buyer,color='purple',x=-200,y=a*100)
        a+=1
        addedB.add(buyer)
        with open(p/f"{buyer}.json",'r') as file:
            data=json.load(file)
            sups=data['suppliers']
            for sup,freq in sups.items():
                before, sep, after = sup.rpartition(':')
                if part_list and after not in part_list:
                    continue
                
                if(freq<min_thickness):
                    continue
                
                if before not in added:
                    net.add_node(before,color='blue',label=before,x=200,y=b*100)
                    b+=1
                    added.add(before)
                net.add_node(sup,label=after,color='black',x=0,y=c*100)
                c+=1
                net.add_edge(before,sup,width=min(freq,10),label=str(freq))
                net.add_edge(sup,buyer,width=min(freq,10),label=str(freq))
    
    p=Path('TempJSONs/Suppliers')           
    for seller in selected_sellers:
        with open(p/f"{seller}.json",'r') as file:
            data=json.load(file)
            sups=data['buyers']
            for sup,freq in sups.items():
                before, sep, after = sup.rpartition(':')
                if part_list and after not in part_list:
                    continue
                if(freq<min_thickness):
                    continue
                
                
                if seller in added:
                    net.node_map[seller]['color']='purple'
                else:
                    net.add_node(seller,label=seller,color='purple',x=200,y=b*100)
                    b+=1
                
                if before not in addedB:
                    net.add_node(before,color='red',label=before,x=-200,y=a*100)
                    a+=1
                    addedB.add(before)
                net.add_node(sup,label=after,color='black',x=0,y=c*100)
                c+=1
                net.add_edge(seller,sup,label=str(freq),width=min(10,freq))
                net.add_edge(sup,before,label=str(freq),width=min(10,freq))
                
                
        
    a=0
    for sup in added:
        p=Path('TempJSONs/Suppliers')
        with open(p/f"{sup}.json",'r') as file:
            data=json.load(file)
        net.add_node(data['Country'],label=data['Country'],x=400,y=a*100,color='yellow')
        a+=1
        net.add_edge(data['Country'],sup)
            
    net.show('templates/search.html')
    
    
    if countries