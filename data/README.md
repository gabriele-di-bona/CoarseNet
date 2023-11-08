# Data

## How to use
If you need to save data, save them here with a meaningful namefile. 
Please create a new subfolder for specific purposes.
For example, if you save graphs, create a subfolder graph, i.e., `./data/graphs/`.


## Networks
They are in Pajek format (.paj)
- PhD: from 10.1103/PhysRevE.78.046102
- Balanced tree: N=1093, L=1092 with 3 children per node (branching factor = 3, Height of the tree = 6). Code: g_tree = nx.generators.balanced_tree(3,6)
- Random tree: N=1093, L=1092 with leaves grown randomly. Code: g_tree = nx.generators.random_tree(1093)
- ER_random: N=1000, L=25087. Generated with the Erdos-Renyi ER(N,p) model, for N=1000 and p=0.05. Code: g_rand = nx.erdos_renyi_graph(1000, p = 0.05)
