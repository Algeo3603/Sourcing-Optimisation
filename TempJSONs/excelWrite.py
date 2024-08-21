import json
from pathlib import Path

part="Shock Absorber"
p=Path('Suppliers')
file_names = [f.name for f in p.iterdir() if f.is_file()]

for seller in file_names:
    with open(p/seller,'r') as file:
        data=json.load(file)
    if(data['top500']):
        top="True"
    else:
        top="False"
    with open(part+".csv",'a') as file:
        for key,value in data['buyers'].items():
            buyer,sep,partN=key.rpartition(':')
            if partN==part:
                file.write(buyer.replace(",","")+','+seller[:-5].replace(",","")+","+str(value)+","+data['Country']+","+top+"\n") 
