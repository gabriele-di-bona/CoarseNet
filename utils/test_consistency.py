"""
test_consistency.py
--------------------
This is a simple check of consistency for Infomap or Louvain community detection
methods. Although these methods are not generative models, we can use their node
partition and a stochastic block model (SBM) to generate networks having the same
average degree and connectivity between the original groups. Then Infomap or Louvain 
can be applied once again on synthetic networks. The corresponding partitions are 
compared with the original one by the Adjusted Mutual Information (AMI). Low 
values might suggest that the method is inconsistent.

author: Felipe Vaca
email: felipevacar at gmail dot com
"""

import graph_tool.all as gt
import igraph as ig
import networkx as nx
import numpy as np
from sklearn.metrics.cluster import adjusted_mutual_info_score
import matplotlib.pyplot as plt


def gt_to_infomap(g):    
    """
    Convert a graph in .gt format to igraph format.

    Parameters
    ----------
    g (graph_tool.Graph): graph to be used

    Returns
    -------
    h (igraph.Graph): graph in new format    
    """
    
    n_vertices = g.num_vertices()
    edges = [tuple(e) for e in g.get_edges()]
    h = ig.Graph(n_vertices, edges)
    return h

    
def gt_to_networkx(g):
    """
    Convert a graph in .gt format to networkx format.

    Parameters
    ----------
    g (graph_tool.Graph): graph to be used

    Returns
    -------
    h (networkx.Graph): a graph in networkx format
    """

    h = nx.Graph()
    h.add_edges_from([tuple(e) for e in g.get_edges()])
    return h


def networkx_to_gt(G):
    """
    Convert a graph in networkx format to .gt format.

    Parameters
    ----------
    G (networkx.Graph): graph to be used

    Returns
    -------
    h (graph_tool.Graph): a graph in .gt format
    """    
    
    h = gt.Graph(G.number_of_nodes(),directed=False)
    h.add_edge_list(list(G.edges))
    return h


def get_partition_louvain(g):
    """
    Get partition from Louvain algorithm.

    Parameters
    ----------
    g (graph_tool.Graph): graph to be used

    Returns
    -------
    m_ (numpy.array): node memberships
    """

    b_ = nx.community.louvain_communities(gt_to_networkx(g))
    m_ = np.zeros(g.num_vertices(),dtype="int")
    for i,j in enumerate(b_):
        m_[list(j)] = i
    return m_


def gen_from_partition(h,b_):
    """
    Generate a graph from a Stochastic Block Model (SBM) with node memberships b_.

    Parameters
    ----------
    h (graph_tool.Graph): original graph
    b_ (numpy.array): node partition

    Returns
    -------
    sb (graph_tool.Graph): synthetic graph
    
    """
    
    g = h.copy()
    g.vp["b_"] = g.new_vp("int", vals = b_)
    assumed_model = gt.BlockState(g,b=g.vp["b_"])
    sb = assumed_model.sample_graph()
    return sb


def test_consistency(g,b_,ngraphs = 1000, method = "infomap"):
    """
    Generate synthetic networks, obtain partitions, and compute the Adjusted 
    Mutual Information (AMI) between such partitios and original one.
        
    Parameters
    ----------
    g (graph_tool.Graph): original graph.
    b_ (numpy.array): node partition.
    ngraphs (int): number of synthetic graphs to generate and collect indices.
    method (str): method to get partitions, either "infomap" or "louvain".

    Returns
    -------
    res (dict): It contains the Adjusted Mutual Information (AMI)
                between the original partition and the partitions 
                in synthetic graphs. In the case of Infomap, the code length
                (obj) is also collected.
                
    """
    
    res = {"obj":[], "AMI": []}
    for i in range(ngraphs):
        sb = gen_from_partition(g,b_)
        if method == "infomap":
            sb = gt_to_infomap(sb)
            b_sb, cl_sb =ig.GraphBase.community_infomap(sb)
            res["obj"].append(cl_sb)
        else:
            b_sb = get_partition_louvain(sb)            

        res["AMI"].append(adjusted_mutual_info_score(b_,b_sb))
    
        del sb
    return res


if __name__ == '__main__':

    # get a graph using graph-tool
    g = gt.collection.data["dolphins"]
    g = gt.extract_largest_component(g, prune = True)
    gt.remove_parallel_edges(g)
    gt.remove_self_loops(g)
    g.set_directed(False)
    
    # get partition
    method = "infomap"
    # method = "louvain"
    
    if method == "infomap":
        b_, cl  = ig.GraphBase.community_infomap(gt_to_infomap(g))
    else:
        b_ = get_partition_louvain(g)
    
    
    # test
    res = test_consistency(g,b_,ngraphs = 1000, method=method)
    
    # plot
    for k,v in res.items():
        
        if len(v)==0:
            continue
        
        fig,ax = plt.subplots(figsize = (5,4))
        bins = int(np.sqrt(len(v)))
        ax.hist(v,bins=bins)

        if k == "obj":
            vl = cl
        else:
            vl = None
    
        if vl is not None:
            ax.axvline(x = vl, color ="black", ls = "--")        
        ax.set_xlabel(k)
        ax.set_ylabel("density")
        fig.tight_layout();
        plt.savefig("./test-%s.png" % k)
        plt.close()
