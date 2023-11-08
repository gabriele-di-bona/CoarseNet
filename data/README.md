# Data

## How to use
If you need to save data, save them here with a meaningful namefile. 
Please create a new subfolder for specific purposes.
For example, if you save graphs, create a subfolder graph, i.e., `./data/graphs/`.


## Networks
They are in Pajek format (.paj)
- PhD: from 10.1103/PhysRevE.78.046102
- Tree: N=1000, L=999 with 3 children per node. Code: g_tree = ig.Graph.Tree(1000,3)
- Random: N=1000, L=25067. Generated with the regular G(N,p) model, for N=1000 and p=0.05. Code: g_rand = ig.Graph.Erdos_Renyi(n=1000,p=0.05)
