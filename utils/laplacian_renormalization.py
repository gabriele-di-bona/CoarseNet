"""
laplacian_renormalization.py
--------------------
Coarse graining technique based on the laplacian renormalization procedure
introduced and discussed in the following paper:

Pablo Villegas, Tommaso Gili, Guido Caldarelli & Andrea Gabrielli (2023)
Laplacian renormalization group for heterogeneous networks.
https://www.nature.com/articles/s41567-022-01866-8.

author: Harrison Hartle
email: hthartle1 at gmail dot com
"""

from collections import Counter
import numpy as np
import networkx as nx
from scipy.linalg import expm, sinm, cosm
import matplotlib.pyplot as plt
import pandas as pd
import scipy.linalg as li


def laplacian_renormalization(G, tau, dev=False):
    '''
    Coarsen a networkx graph by collapsing nodes based on a parameter tau.

    Parameters:
    ----------
    G : networkx.Graph
        The input graph to be coarsened.
    tau : float
        The parameter used for coarsening.

    Returns:
    -------
    networkx.Graph
        The coarsened graph.

    '''
    # Get the number of nodes in the input graph
    n = G.number_of_nodes()

    # Calculate the Laplacian matrix of the input graph
    L = nx.laplacian_matrix(G)
    L1 = L.todense()

    # Compute e^(-tau * L) and normalize it
    num = expm((-tau * L1))
    den = np.trace(num)
    rho = num / den

    # Build the metagraph G1 based on the rho values
    adj2 = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if ((rho[i][j] >= rho[j][j]) or (rho[i][j] >= rho[i][i])):
                adj2[i][j] = 1
    G1 = nx.from_numpy_array(adj2)
    unique_macro_ids = [idx for idx, comp in enumerate(list(nx.connected_components(G)))]

    macro_label_dict = {i:-1 for i in G.nodes()}

    # Contract nodes in the input graph based on connected components in G1
    for macro_idx, supernode in enumerate(list(nx.connected_components(G1))):
        nodes = sorted(list(supernode))
        if len(nodes)>1:
            macro_idx = macro_idx + n
            macro_label_dict[nodes[0]] = macro_idx
            for node in nodes[1:]:
                G = nx.contracted_nodes(G, nodes[0], node, self_loops=False)
                macro_label_dict[node] = macro_idx
        else:
            macro_label_dict[nodes[0]] = nodes[0]

    macro_nodes_wrong_label = np.unique([i for i,j in
                                         dict(Counter(list(macro_label_dict.values()))).items()
                                         if j>1])
    relabel_macro_nodes = {i:idx+n for idx,i in enumerate(macro_nodes_wrong_label)}
    for i,j in macro_label_dict.items():
        if j in list(relabel_macro_nodes.keys()):
            macro_label_dict[i] = relabel_macro_nodes[j]


    G = nx.relabel_nodes(G, macro_label_dict).copy()
    nx.set_edge_attributes(G, 1.0, 'weight')


    if dev:
        return G

    else:
        wel = nx.to_pandas_edgelist(G)
        if 'weight' not in wel.columns:
            wel['weight'] = 1.0
        wel = wel[['source','target','weight']].copy()
        mapping_df = pd.DataFrame({"micro":list(macro_label_dict.keys()),
                                   "macro":list(macro_label_dict.values())})

        return mapping_df, wel
