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
                
                if selected_sellers and before not in selected_sellers:
                    continue
                
                if countries:
                    z=Path('TempJSONs/Suppliers')
                    seller=before
                    with open(z/f"{seller}.json",'r') as file:
                        d=json.load(file)
                    if d['Country'] not in countries:
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
        if countries and data['Country'] not in countries:
            continue
        #print(countries)
        #print(data['Country'])
        
        
        if seller in added:
            net.node_map[seller]['color']='purple'
        else:
            net.add_node(seller,label=seller,color='purple',x=200,y=b*100)
            added.add(seller)
            b+=1
        for sup,freq in sups.items():
            before, sep, after = sup.rpartition(':')
            if part_list and after not in part_list:
                continue
            if(freq<min_thickness):
                continue
            if selected_buyers and before not in selected_buyers:
                continue
            if seller in selected_sellers and before in selected_buyers:
                continue
                
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
        
    if not selected_buyers and not selected_sellers and countries:
        directory_path=Path('TempJSONs/Suppliers')
        sellers=[f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        a=0
        b=0
        d=0
        
        if part_list:
            for part in part_list:
                net.add_node(part,label=part,color='red',x=200,y=d*100)
                d+=1
        for seller in sellers:
            with open(directory_path/seller, 'r') as file:
                data=json.load(file)
            c=data['Country']
            ps=data['parts_sold']
            flag=False
            
            if part_list:
                intersec=[part for part in part_list if part in ps]
                if not intersec:
                    continue
            
            for part,freq in ps.items():
                if part not in intersec:
                    continue
                if freq>=min_thickness:
                    flag=True
                    break
            
            if not flag:
                continue
            if c not in countries:
                continue
                
            
            net.add_node(c,label=c,color='yellow',x=-200,y=a*100)
            a+=1
            net.add_node(seller[:-5],label=seller[:-5],color='blue',x=0,y=b*100)
            b+=1
            net.add_edge(seller[:-5],c)
            
            if not part_list:
                for item,freq in ps.items():
                    if(freq<min_thickness):
                        continue
                    net.add_node(item,label=item,color='red',x=200,y=d*100)
                    d+=1
                    net.add_edge(item,seller[:-5],label=str(freq),width=min(10,freq))
            else:
                for part in intersec:
                    if(ps[part]<min_thickness):
                        continue
                    net.add_edge(part,seller[:-5],width=min(10,ps[part]),label=str(ps[part]))
                    
            
            
    net.show('templates/search.html')
    
    
    