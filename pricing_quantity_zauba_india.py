import pandas as pd
import statistics
import json

file_path = 'Parts/Zauba/brake_line_imports_india.csv'
df = pd.read_csv(file_path)

stats = {}

for index, row in df.iterrows():
    # print(row['Origin Country'])
    if row['Origin Country'] not in stats:
        stats[row['Origin Country']] = {}
    if row['Unit'] not in stats[row['Origin Country']]:
        stats[row['Origin Country']][row['Unit']] = {
            'ppu': [],
            'average_price': -1,
            'median_price': -1,
            'min_price': -1,
            'max_price': -1,
            'total_quantity': 0
        }

    stats[row['Origin Country']][row['Unit']]['ppu'].append(row['Price Per Unit (USD)'])
    stats[row['Origin Country']][row['Unit']]['average_price'] = statistics.mean(stats[row['Origin Country']][row['Unit']]['ppu'])
    stats[row['Origin Country']][row['Unit']]['median_price'] = statistics.median(stats[row['Origin Country']][row['Unit']]['ppu'])
    stats[row['Origin Country']][row['Unit']]['min_price'] = min(stats[row['Origin Country']][row['Unit']]['ppu'])
    stats[row['Origin Country']][row['Unit']]['max_price'] = max(stats[row['Origin Country']][row['Unit']]['ppu'])
    stats[row['Origin Country']][row['Unit']]['total_quantity'] += row['Quantity']

print(stats)

json_filename = file_path.split('/')[-1].split('.')[0] + '.json'
with open(f'Parts/Pricing_Quantity/Indian_Imports/{json_filename}', 'w') as file:
    json.dump(stats, file, ensure_ascii=False, indent=4)