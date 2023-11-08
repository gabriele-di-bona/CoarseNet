import numpy as np
import networkx as nx
import random
from collections import Counter
import pandas as pd
from scipy.spatial import distance


def spatial_coarse_grain(graph, radius):
    """
    This function calculates supernodes in a spatial network,primarily relying on geometric
    distance among nodes. 
    The network is assumed to be comprised of nodes that have predetermined positions
    Note: The input data should already have a pos attribute, which will 
    be used for distance computations. However, if this attribute is missing, 
    the function will automatically compute it using NetworkX's spring_layout algorithm.

    Parameters
    ----------
    G (nx.Graph): the network in question
    radius: radious

    Returns
    -------
    Gg: nx coarse_grain graph
    nG_dict: dictionary keys: node-id  values: group-id
    """

    G=graph.copy()

    if 'pos' not in G.graph:
        print('NOTE: The nodes of G do not have a spatial position.\n\
        The position has been computed using a spring_layout')
        pos = nx.spring_layout(G)  # Compute positions using the spring layout
        nx.set_node_attributes(G, pos, 'pos')


    nG_dict={}
    _=0
    while len(G.nodes())!=0:

        seed_node= random.choice(list(G.nodes()))
        seed_node_position = G.nodes[seed_node]['pos']

        nodes_df= pd.DataFrame(G.nodes(data='pos'))
        nodes_df.columns =['node_id', 'pos']
        neighbors =nodes_df[nodes_df['pos'].apply(
            lambda x: distance.euclidean(tuple(x), seed_node_position) <= radius )]['node_id'].values
        
        if len(neighbors)== len(G.nodes) and _ ==0:
            print('\nRadius is too large: all the node are in an unique group')

        #neighbors = [node for node in G.nodes() 
        #             if distance.euclidean(G.nodes[node]['pos'], seed_node_position) <= radius ]

        G.remove_nodes_from(neighbors)
        g_dict= {b:_ for b in neighbors}
        nG_dict = {**g_dict, **nG_dict}

        _+=1

    # b. do the mapping delate edges among nodes in the same group
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

    # d. building the coarse grained graph (nx)
    Gg=nx.from_pandas_edgelist(Gg_df, edge_attr='weight')

    # e. adding isolated nodes
    Gg.add_nodes_from(nG_dict.values())

    return Gg, nG_dict
