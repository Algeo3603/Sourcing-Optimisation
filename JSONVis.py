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
    
    addedSellers=set()
    addedBuyers=set()
    addedCountries=set()
    a=0
    b=0
    d=0
    e=0
    if selected_buyers and selected_sellers:
        p=Path('TempJSONs/Suppliers')
        for seller in selected_sellers:
            with open(p/f"{seller}.json",'r') as file:
                data=json.load(file)
            sups=data['buyers']
            c=data['Country']
            
            if countries and c not in countries:
                continue
            for temp,freq in sups.items():
                before,sep,after=temp.rpartition(':')
                
                if part_list and after not in part_list:
                    continue
                
                if freq<min_thickness:
                    continue
                
                if before not in selected_buyers:
                    continue
                
                if before not in addedBuyers:
                    net.add_node(before,label=before,color='red',x=-200,y=a*100)
                    addedBuyers.add(before)
                    a+=1
                net.add_node(temp+seller,label=after,x=0,y=b*100,color='black')
                b+=1
                if seller not in addedSellers:
                    net.add_node(seller,label=seller,color='blue',x=200,y=d*100)
                    addedSellers.add(seller)
                    d+=1
                    if c not in addedCountries:
                        net.add_node(c,label=c,color='yellow',x=400,y=e*100)
                        e+=1
                        addedCountries.add(c)
                    net.add_edge(c,seller)
                    
                net.add_edge(temp+seller,before,label=str(freq),width=min(10,freq))
                net.add_edge(seller,temp+seller,label=str(freq),width=min(10,freq))
                
    elif selected_buyers:
        p=Path('TempJSONs/Buyers')
        for buyer in selected_buyers:
            with open(p/f"{buyer}.json",'r') as file:
                data=json.load(file)
            sups=data['suppliers']
            for sup,freq in sups.items():
                seller,sep,part=sup.rpartition(':')
                
                if freq<min_thickness:
                    continue
                
                if part_list and part not in part_list:
                    continue
                
                z=Path('TempJSONs/Suppliers')
                with open(z/f"{seller}.json",'r') as file:
                    seller_data=json.load(file)
                c=seller_data['Country']
                if countries and c not in countries:
                    continue
                
                if buyer not in addedBuyers:
                    net.add_node(buyer,label=buyer,color='red',x=-200,y=a*100)
                    a+=1
                    addedBuyers.add(buyer)
                net.add_node(sup+buyer,label=part,color='black',x=0,y=b*100)
                b+=1
                if seller not in addedSellers:
                    net.add_node(seller,label=seller,color='blue',x=200,y=d*100)
                    addedSellers.add(seller)
                    d+=1
                    if c not in addedCountries:
                        net.add_node(c,label=c,color='yellow',x=400,y=e*100)
                        e+=1
                        addedCountries.add(c)
                    net.add_edge(c,seller)
                net.add_edge(seller,sup+buyer,label=str(freq),width=min(10,freq))
                net.add_edge(sup+buyer,buyer,label=str(freq),width=min(10,freq))
    
    
    elif selected_sellers:
        p=Path('TempJSONs/Suppliers')
        for seller in selected_sellers:
            with open(p/f"{seller}.json",'r') as file:
                data=json.load(file)
            c=data['Country']
            ps=data['buyers']
            if countries and c not in countries:
                continue
            
            for temp,freq in ps.items():
                buyer,sep,part=temp.rpartition(':')
                if part_list and part not in part_list:
                    continue
                if freq<min_thickness:
                    continue
                if buyer not in addedBuyers:
                    net.add_node(buyer,label=buyer,color='red',x=-200,y=a*100)
                    a+=1
                    addedBuyers.add(buyer)
                net.add_node(temp+buyer,label=part,color='black',x=0,y=b*100)
                b+=1
                if seller not in addedSellers:
                    net.add_node(seller,label=seller,color='blue',x=200,y=d*100)
                    addedSellers.add(seller)
                    d+=1
                    if c not in addedCountries:
                        net.add_node(c,label=c,color='yellow',x=400,y=e*100)
                        e+=1
                        addedCountries.add(c)
                    net.add_edge(c,seller)
                net.add_edge(seller,temp+buyer,label=str(freq),width=min(10,freq))
                net.add_edge(temp+buyer,buyer,label=str(freq),width=min(10,freq))
                
            
    elif not selected_buyers and not selected_sellers and countries:
        directory_path=Path('TempJSONs/Suppliers')
        sellers=[f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        
        for seller in sellers:
            with open(directory_path/seller,'r') as file:
                data=json.load(file)
            seller=seller[:-5]
            c=data['Country']
            if countries and c not in countries:
                continue
            ps=data['buyers']
            
            for temp,freq in ps.items():
                buyer,sep,part=temp.rpartition(':')
                print(buyer)
                if part_list and part not in part_list:
                    continue
                if freq<min_thickness:
                    continue
                if buyer not in addedBuyers:
                    net.add_node(buyer,label=buyer,color='red',x=-200,y=a*100)
                    a+=1
                    addedBuyers.add(buyer)
                net.add_node(buyer+seller+part,label=part,color='black',x=0,y=b*100)
                b+=1
                if seller not in addedSellers:
                    net.add_node(seller,label=seller,color='blue',x=200,y=d*100)
                    addedSellers.add(seller)
                    d+=1
                    if c not in addedCountries:
                        net.add_node(c,label=c,color='yellow',x=400,y=e*100)
                        e+=1
                        addedCountries.add(c)
                    net.add_edge(c,seller)
                net.add_edge(seller,buyer+seller+part,label=str(freq),width=min(10,freq))
                net.add_edge(buyer+seller+part,buyer,label=str(freq),width=min(10,freq))
                
    elif part_list:
        directory_path=Path('TempJSONs/Parts')
        parts=[f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        
        for part in parts:
            if part[:-5] not in part_list:
                continue
            net.add_node(part[:-5],label=part[:-5],color='black',x=0,y=a*100)
            a+=1
            with open(directory_path/part,'r') as file:
                data=json.load(file)
            buyers=data['buyer']
            seller=data['supplier']
            
            for buyer,freq in buyers.items():
                if freq<min_thickness:
                    continue
                net.add_node(buyer,label=buyer,x=-200,y=b*100,color='red')
                b+=1
                net.add_edge(part[:-5],buyer,label=str(freq),width=min(10,freq))
            for seller,freq in seller.items():
                if freq<min_thickness:
                    continue
                net.add_node(seller,seller=buyer,x=200,y=d*100,color='blue')
                d+=1
                net.add_edge(part[:-5],seller,label=str(freq),width=min(10,freq))
                
    else:
        net.add_node(1,label="KOI TOH FILTER LAGA DE BHAI",color='black')        
                
            
    net.show('templates/search.html')
    
    
    