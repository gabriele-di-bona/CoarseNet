import pandas as pd
import random
import networkx as nx
from collections import Counter




def random_burning(graph, r):
    '''
    ::: inputs :::
    - graph: nx network
    - r: distance 

    ::: returs :::
    - Gg: nx coarse_grain graph
    - nG_dict: dictionary keys: node-id  values: group-id

    ref: Self-similarity of complex networks, Song et al (2005) (2nd method)
    '''

    G=graph.copy()
    
    #. a. build the dictionary that maps each node to its group
    nG_dict={}
    _=0
    while len(G.nodes())!=0:
        seed_node= random.choice(list(G.nodes()))
        B = nx.ego_graph(G,seed_node,r)
        G.remove_nodes_from(B.nodes())
        
        g_dict= {b:_ for b in B.nodes()}
        nG_dict = {**g_dict, **nG_dict}

        _+=1

    # b. do the mapping & delate edges among nodes in the same group
    G_edges_df = pd.DataFrame(graph.edges())
    G_edges_df.columns =['from', 'to']
    G_edges_df['from']= G_edges_df['from'].map(nG_dict)
    G_edges_df['to']= G_edges_df['to'].map(nG_dict)
    G_edges_df= G_edges_df[G_edges_df['from']!=G_edges_df['to']]

    # c. handeling duplicats links as weights of the coarse grained edges
    Gg_edges= Counter([tuple(sorted(edge)) for edge in G_edges_df.values])
    Gg_df = pd.DataFrame(Gg_edges.items(), columns=['edge', 'weight'])
    Gg_df['source']=Gg_df['edge'].apply(lambda x: x[0])
    Gg_df['target']=Gg_df['edge'].apply(lambda x: x[1])

    mapping = pd.DataFrame(nG_dict, index=range(1)).T.reset_index()
    mapping.columns= ['micro', 'macro']
    weighted_edgelist=Gg_df[['source','target','weight']]

    return mapping, weighted_edgelist
