
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from itertools import combinations
from tqdm import tqdm

from netrd.distance import NetLSD, GraphDiffusion
import netrd
import os
import sys
sys.path.insert(0,os.path.join(os.getcwd(),'utils'))
#import osos.chdir('..')
print(os.getcwd())

from supernodes import supernodes
from causal_emergence import causal_emergence

FIGURES_DIR = Path('figures')

def load_graphs(dirpath):

    g = nx.read_edgelist(dirpath/'edgelist.txt',nodetype=int)
    sg = nx.read_edgelist(dirpath/'super_edgelist.txt',nodetype=int)
    with open(dirpath/'mapping.json') as f:
        mapping = json.load(f)
    for n in g.nodes():
        g.nodes[n]['label'] = mapping[n]
    return g,sg


def noise(g,epsilon,directed=False):

    """
    Make a random noisy version of a graph in a way
    that preserves edge density. When epsilon =1, we
    get a completely random graph with density M/(N choose 2).
    """

    # calculate graph density
    N = len(g)
    M = g.number_of_edges()
    E_possible = N*(N-1) if directed else N*(N-1)/2
    rho = M / E_possible

    # probability that a removed edge is added to an empty site 
    # (after all edges removed)
    prob_spurious = rho*epsilon / (1 + rho*epsilon - rho) 
    
    # true positive = probability an edge isn't removed 
    #               + probability it is removed and is put back
    true_pos = (1 - epsilon) + prob_spurious
    false_pos = prob_spurious    # ϵ*E/non_E

    # print("number kept edges:",true_pos*M)
    # print("number extra edges:", false_pos*(E_possible - M))
    # print(false_pos*(E_possible - M) + true_pos*M )

    A = nx.to_numpy_array(g)
    R = np.random.random(size=(N,N))

    def f(v,r):
        if v > 0: # edge already exists
            return r < true_pos
        else: # no original edge
            return r < false_pos
    func = np.vectorize(f)
    
    A_new = func(A,R)
    if not directed:
        A_new = np.triu(A_new,k=1)
        
    g_new = nx.from_numpy_array(A_new)
    assert nx.number_of_selfloops(g_new) == 0
    return g_new
         

def get_average_distance(g,epsilon, method_func, num_graph_samples = 100, num_method_samples = 100,dist_kernel = None):


    if dist_kernel is None:
        dist_kernel = NetLSD()

    noisy_Gs = [noise(g,epsilon) for _ in range(num_graph_samples)]

    # true macro g
    macro_gs = [method_func(g) for _ in range(num_method_samples)]

    # compute distances
    distances = []
    for g_ in tqdm(noisy_Gs):
        macro_gs_ = [method_func(g_) for _ in range(num_method_samples)]
        for i in range(num_method_samples):
            g1 = macro_gs[i]
            g2 =  macro_gs_[i]
            try:
                assert len(g1) > 0 and len(g2) > 0 
            except:
                print(distances)
                exit()
            dist_ =  dist_kernel.dist(g1,g2)
            distances.append(dist_)
        distances.append(dist_)

    return np.mean(distances)


def main(g,dist_kernel = None):

    epsilons = np.linspace(0,0.5,5)

    fig, ax = plt.subplots()

    num_graph_samples = 1
    num_method_samples = 5

    # super nodes
    method_func = lambda g: supernodes(g,k=5)[1]
    average_distances = [get_average_distance(g,epsilon,method_func,num_graph_samples = num_graph_samples,num_method_samples=num_method_samples,dist_kernel = dist_kernel) for epsilon in epsilons]
    ax.plot(epsilons,average_distances,  label = "Supernodes")
    ax.set(xlabel = '$\epsilon$',ylabel = "Avg. Network Distance",)

    # causal emergence
    def weighted_edgelist2graph(weighted_edgelist):
        G = nx.Graph()
        df = weighted_edgelist
        edgelist = list(zip(df.source,df.target,df['weight']))
        G.add_weighted_edges_from(edgelist)
        return G
    method_func = lambda g: weighted_edgelist2graph(causal_emergence(g)[1])
    average_distances = [get_average_distance(g,epsilon,method_func,num_graph_samples = num_graph_samples,num_method_samples=num_method_samples,dist_kernel = dist_kernel) for epsilon in epsilons]
    ax.plot(epsilons,average_distances, label = "Causal Emergence")

    plt.legend()
    plt.tight_layout(pad = 0.5)
    plt.savefig(FIGURES_DIR / 'karate_noisy_test.png')        


if __name__ == "__main__":

    #g = nx.erdos_renyi_graph(100,0.2)
    g = nx.karate_club_graph()
    main(g,dist_kernel=netrd.distance.PortraitDivergence())




