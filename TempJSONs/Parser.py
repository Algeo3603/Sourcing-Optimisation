import json
from pathlib import Path

text=""
p=Path('Suppliers')
file_names = [f.name for f in p.iterdir() if f.is_file()]

for seller in file_names:
    with open(p/seller,'r') as file:
        data=json.load(file)
    if data['top500']:
        text=text+seller[:-5]+"is a top 500 supplier, "
    else:
        text=text+seller[:-5]+"is a not top 500 supplier, "
    text+="located in "+data['Country']+". "
    text=text+"It has sold a total of "
    a=0
    for key,value in data['parts_sold'].items():
        text=text+str(value)+" "+key+"(s)"
        a+=1
        if a==len(data['specific_parts_sold']):
            text+=". "
            continue
        text+=","
        if a==len(data['specific_parts_sold'])-1:
            text+="and "
    for key,value in data['buyers'].items():
        buyer,sep,part=key.rpartition(':')
        text+="It has sold a total of "+str(value)+" "+part+"(s) to "+buyer+"." 
    
    
    text+="\n\n"

with open('input.txt','w') as file:
    file.write(text)