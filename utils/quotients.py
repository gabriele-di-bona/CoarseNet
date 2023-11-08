from pynauty import *
import networkx as nx
import numpy as np
import igraph as ig
import pandas as pd

def from_nx_to_pynauty_graph(
    gnx: nx.Graph
    ):
    """
    Convert a networkx graph to a pynauty graph.
    :param gnx: networkx graph
    :return: pynauty graph
    """
    g = Graph(len(gnx.nodes),directed=False)
    for v in gnx.nodes:
        g.connect_vertex(v, list(gnx.neighbors(v)))
    return g

def get_partition(
        gnx: nx.Graph,
):
    """
    Get the partition of a graph.
    :param gnx: networkx graph
    :return: partition of the graph, number of partitions
    """
    g = from_nx_to_pynauty_graph(gnx)
    generators, grpsize1, grpsize2, orbits, numorbits = autgrp(g)
    orb_dict = {v:orbits[v] for v in gnx.nodes}
    nx.set_node_attributes(gnx, orb_dict, name='partition')
    return orbits,numorbits

def get_coarse_grained_net(g : nx.Graph, dev=False):
    """
    Get the coarse-grained network of a graph.
    :param g: networkx graph
    :param dev: if True, return the coarse-grained network. If False, return the label dataframe and the edge dataframe
    """
    orbits, numorbits = get_partition(g)

    df_micro_macro = _get_label_df(g, orbits)
    label_dic = df_micro_macro.set_index('micro').macro.to_dict()

    #label_dic = {v[0]:v[1]['partition'] for v in g.nodes(data=True)}

    coarse_grained_net = nx.relabel_nodes(g,label_dic,copy=True)
    # removing self loops
    self_loops = list(nx.selfloop_edges(coarse_grained_net)).copy()
    coarse_grained_net.remove_edges_from(self_loops)

    edge_df = pd.DataFrame([list(i) for i in coarse_grained_net.edges()], columns=['source', 'target'])
    edge_df['weight'] = 1

    if dev:
            return coarse_grained_net
    else:
        return df_micro_macro, edge_df

def _get_label_df(g, orbits):
    df = pd.DataFrame(orbits, columns=['macro_tmp'])
    df['micro'] = list(g.nodes())
    v=df.macro_tmp.value_counts()
    v=v[v>1].reset_index().reset_index()
    v['index'] += max(list(g.nodes()))+1
    map_dic = v[['index', 'macro_tmp']].set_index('macro_tmp')['index'].to_dict()
    df['macro'] = df.macro_tmp.map(map_dic)
    df.loc[df.macro.isna(), 'macro'] = df.loc[df.macro.isna(), 'macro_tmp']
    df.macro = df.macro.astype(int)
    df.drop(columns=['macro_tmp'], inplace=True)
    #label_dic = df.set_index('micro').macro.to_dict()
    return df
    

def convert_to_igraph(g: nx.Graph, g_cg:nx.Graph):
    """
    Convert to a format compatible with the function 'coarse_grained_visualization'
    """
    ### create node_dict

    label_dict = {v[0]:v[1]['partition'] for v in g.nodes(data=True)}
    vals = np.unique(list(label_dict.values()))
    val_dict = {vals[i]:i for i in range(len(vals))}
    node_dict = {i: val_dict[label_dict[i]] for i in label_dict}

    ### in this method we don't use weights (see s-quotients)
    nx.set_edge_attributes(g, values=1.0, name='weight')
    nx.set_edge_attributes(g_cg, values=1, name='weight')

    ### convert to igraph
    h = ig.Graph.from_networkx(g)
    h_cg = ig.Graph.from_networkx(g_cg)
    ###

    return h,h_cg,node_dict


def partition_from_edge_list(
        edge_list: list
):
    """
    Get the partition of a graph from an edge list.
    :param edge_list: edge list of the graph
    :return: partition of the graph, number of partitions
    """

    g = nx.Graph()
    g.add_edges_from(edge_list)

    coarse_grained_net = get_coarse_grained_net(g)

