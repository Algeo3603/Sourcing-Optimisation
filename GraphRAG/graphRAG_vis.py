import pandas as pd
import networkx as nx
from pyvis.network import Network

df = pd.read_parquet('output/Current/artifacts/create_base_entity_graph.parquet')
graphml_data = df.iloc[0]['clustered_graph']
graph = nx.parse_graphml(graphml_data.encode('utf-8'))

net = Network(notebook=True)
net.from_nx(graph)
net.show('graph.html')
