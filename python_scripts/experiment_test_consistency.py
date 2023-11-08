#!/usr/bin/env python3
''' Testing consistency of method'''


method_title = 'Causal Emergence Coarse Graining'

import os
# If you are running this from ~/python_scripts/mycode.py
# change directory to the root of the repository
# All utils assume that the working directory is the root directory of the github folder
os.chdir('../') # ONLY DO ONCE!!!!

import sys
# Add utils directory in the list of directories to look for packages to import
sys.path.insert(0, os.path.join(os.getcwd(),'utils'))


import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
# local utils
from causal_emergence import effective_information, causal_emergence, causal_emergence_spectral
from mapping_auxiliary_functions import *
from visualization_networkx import *
from test_consistency import *

# make an example network
if True:
    # load karate club graph
    G_micro = G = nx.karate_club_graph()
else:
    # load graph from weighted edge list
    # weighted_edgelist = .......
    # G_micro = nx.from_pandas_edgelist(weighted_edgelist, edge_attr='weight') 
    # OR OTHER, e.g. from Ref [1] Yanghua Xiao, Ben D MacArthur, Hui Wang, Momiao Xiong, and Wei Wang. “Network quotients: Structural skeletons of complex systems”. In: Physical Review E 78.4 (2008), p. 046102. doi: 10.1103/PhysRevE.78.046102.
    G = nx.read_pajek('./data/PhD.paj')
    # some preprocessing
    G = G.to_undirected()
    nx.relabel_nodes(G, mapping={n:i for i,n in enumerate(G.nodes)},copy=False)
    for v in G.nodes:
        del G.nodes[v]['shape']


# the function causal_emergence returns the mapping of the nodes from microscale to macroscale as a table (pandas columns: micro, macro), and the weighted_edgelist as another table (pandas columns: )
mapping, weighted_edgelist = causal_emergence(G)
# CE = causal_emergence(G,dev=True)
G_macro = nx.from_pandas_edgelist(weighted_edgelist, edge_attr='weight')


# --- test
h = networkx_to_gt(G)
b_ = mapping['macro'].values

res = {"AMI": [], "overlap": []}
ngraphs = 100
for i in range(ngraphs):
    print(i+1)
    # synthetic graph
    sb = gen_from_partition(h,b_)
    # partition in the synthetic graph    
    mapping_sb, weighted_edgelist_sb = causal_emergence(gt_to_networkx(sb))
    b_sb = mapping_sb['macro'].values

    res["AMI"].append(adjusted_mutual_info_score(b_,b_sb))
    res["overlap"].append(gt.partition_overlap(b_,b_sb))    
    del sb


# plot
for k,v in res.items():
    fig,ax = plt.subplots(figsize = (5,4))
    bins = int(np.sqrt(len(v)))
    ax.hist(v,bins=bins)
    ax.set_xlabel(k)
    ax.set_ylabel("density")
    fig.tight_layout();    