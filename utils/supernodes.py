import networkx as nx
from copy import deepcopy
import random
import pandas as pd


def choose_seeds(g,k):

    """
    Choose seeds according to CoreHD, which works by taking 
    the two-core of the network and choosing the highest-degree
    node. Each successive seed is chosen by in the same way, but
    all seeds are first removed from the network.

    At a certain point, no seeds will be in the two-core, at which
    point the function will return fewer seeds than requested.
    """
    
    seeds = []
    for _ in range(k):

        g_ = deepcopy(g)
        g_.remove_nodes_from(seeds)
        two_core = nx.k_core(g_,2)

        if len(two_core) == 0:
            print(f"No more nodes in the 2-core. Returning fewer than {k} seeds.")
            return seeds
        
        seeds.append(max(two_core.degree(), key=lambda x: x[1])[0])
    
    return seeds


def grow_neighborhoods(g, seeds, o_max=6):

    """
    Grow the supernodes by adding seeds in the regions around each seed.

    This is done iteratively by choosing first the nodes 1-hop away, then
    two hops away, etc. The algorithm is deterministic, so the first seed
    chosen will have priority over subsequent seeds, in the event of a tie.
    """

    nx.set_node_attributes(g,-1,'label')
    
    for s in seeds:
        g.nodes[s]['label'] = s
    
    o = 1
    num_assigned = 0
    num_assigned_diff = 0
    while o < o_max + 1 and num_assigned < len(g) and num_assigned_diff > 0:

        num_assigned_old = num_assigned
        
        node2potentialseeds = {}
        for s in seeds:
            for n in nx.descendants_at_distance(g,s,o):
                if g.nodes[n]['label']>=0 or n in seeds:
                    continue
                if n in node2potentialseeds:
                    node2potentialseeds[n].append(s)
                else:
                    node2potentialseeds[n] = [s]
                num_assigned += 1
        
        # for each node that needs a label this round, choose a seed randomly
        for n, potential_seeds in node2potentialseeds.items():
            g.nodes[n]['label'] = random.choice(potential_seeds)

        # how many assignments made this iteration
        num_assigned_diff = num_assigned - num_assigned_old

    for n in g.nodes:
        if g.nodes[n]['label'] == -1:
            g.nodes[n]['label'] = len(g)
    
def get_supergraph(g):

    """
    The supernode graph is a weighted graph, where an edge r,s 
    connect supernodes iff there is at least one edge in the origina
    graph between a node that maps to supernode r and a node
    that maps to supernode r.
    """

    adjlist = dict()
    for i,j in g.edges():
        
        r = g.nodes[i]['label']
        s = g.nodes[j]['label']

        if (r,s) in adjlist:
            adjlist[(r,s)] += 1
        else:
            adjlist[(r,s)] = 1

    weighted_edgelist = [(r,s,w) for (r,s),w in adjlist.items()]
    weighted_edgelist = [x for x in weighted_edgelist if x[0]!=x[1]]

    s = nx.Graph()
    s.add_weighted_edges_from(weighted_edgelist)
    return s


def supernodes(g,k = 3, o_max = 6, return_edgelist=False):

    """
    Implementation of the method detailed in
    "Compressing graphs with supernodes"

    Note: edge weights are ignored for this method
    """

    if not isinstance(g,(nx.Graph, nx.DiGraph)):
        g_ = nx.Graph()
        g_.add_weighted_edges_from(g)
        g = g_

    # choose seeds
    seeds = choose_seeds(g,k)
    
    # grow neighborhoods
    grow_neighborhoods(g,seeds)

    # get supergraph
    sg = get_supergraph(g)
    
    # assemble output
    mapping = {n:g.nodes[n]['label'] for n in g.nodes()}
    df = pd.DataFrame()
    df['micro'] = list(g.nodes())
    df['macro'] = df.micro.apply(lambda f: mapping[f])
    mapping = df
    
    if return_edgelist:
        macro_edgelist = [(i,j,v) for (i,j),v in nx.get_edge_attributes(sg,'weight').items()]
        return mapping, macro_edgelist
    else:
        return mapping, sg
    
    
if __name__ == "__main__":

    # get networks
    g = nx.karate_club_graph()
    weighted_edgelist = [(i,j,1) for i,j in g.edges()]

    ############### example code ############
    mapping,macro_nx_graph = supernodes(g,k=5,o_max=6)
    mapping,macro_edgelist = supernodes(weighted_edgelist,k=5,return_edgelist=True)
    print(macro_edgelist)