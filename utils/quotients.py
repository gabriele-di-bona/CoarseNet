from pynauty import *
import networkx as nx

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

def get_coarse_grained_net(g : nx.Graph):
    """
    Return the coarse grained graph of the graph g
    """
    orbits = get_partition(g)
    label_dic = {v[0]:v[1]['partition'] for v in g.nodes(data=True)}

    coarse_grained_net = nx.relabel_nodes(g,label_dic,copy=True)
    # removing self loops
    self_loops = list(nx.selfloop_edges(coarse_grained_net)).copy()
    coarse_grained_net.remove_edges_from(self_loops)
    return coarse_grained_net
    
