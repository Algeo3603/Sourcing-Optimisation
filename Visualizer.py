from pyvis.network import Network
import csv

def Visualizer(search_list,minThickness,map):
    net = Network(notebook=True, cdn_resources="remote",directed=True)

    net.set_options("""
    var options = {
    "physics": {
        "enabled": false
    }
    }
    """)

    buyers = set()
    suppliers = set()
    relations=set()
    relations2=set()
    dict={}
        
        
    with open('table.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Iterate through each row and add Buyer and Supplier to the respective lists
        for row in reader:
            if row['Buyer'] in search_list or row['Supplier'] in search_list:
                relations.add((row['Buyer'],row['Supplier']))
                buyers.add(row['Buyer'])
                suppliers.add(row['Supplier'])
                # print(row['Buyer'] + " and " + row['Supplier'])
                if (row['Buyer'],row['Supplier']) in dict:
                    dict[(row['Buyer'],row['Supplier'])]=dict[(row['Buyer'],row['Supplier'])]+1
                    continue
                dict[(row['Buyer'],row['Supplier'])]=1

        for relation in relations:
            if(dict[(relation[0],relation[1])]>=minThickness):
                relations2.add(relation)

        relations=relations2
    a=0
    for buyer in buyers:
        net.add_node(buyer,label=buyer,color='red',x=-200,y=a*100)
        a=a+1
        
    a=0
    for supplier in suppliers:
        net.add_node(supplier,label=supplier,color='blue',x=200,y=a*100)
        a=a+1
    
    for company in search_list:
        net.node_map[company]['color']='purple'

    a=0
    for relation in relations:
        net.add_node(str(relation),label="Brake Line",color='black',x=0,y=a*100)
        a=a+1
        net.add_edge(relation[1],str(relation),color='blue',width=dict[(relation[0],relation[1])],label=str(dict[(relation[0],relation[1])]),title="Brake Lines")
        net.add_edge(str(relation),relation[0],color='blue',width=dict[(relation[0],relation[1])],label=str(dict[(relation[0],relation[1])]),title="Brake Lines")

    for element in map:
        net.add_node(map[element],label=map[element],color='yellow')
        net.add_edge(element,map[element])
    
    net.show('templates/search.html')
    

# search_list=set()    
# a=""
# while True:
#     a=str(input('Enter Company name: '))
#     if a=='search':
#         break
#     search_list.add(a)
# Visualizer(search_list)
