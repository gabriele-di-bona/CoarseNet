# Coarse graining in networks

Collaborative repository to analyse various coarse-graining methods for networks.

## Abstract

Coarse-graining is a widespread concept in science, appearing in situations ranging from highly applied, such as in efficient simulation of Earth's climate, to highly abstract, such as in the definition of Boltzmann entropy. In complex systems, coarse graining frequently appears in concepts such as renormalization, causal emergence, critical phenomena, and community detection. Complex networks often exhibit intricate fine-grained structure and multi-scale organization, and hence the choice of an appropriate coarse-graining scheme may be quite subtle. Consequently, over the past few decades, many distinct methods for coarse-graining of networks have emerged. Herein, we study the different coarse-graining methods that have been developed for networks, examining how they work, what their essential properties are, and their major similarities and differences. 

## Repository installation
Clone this directory to your computer in a new folder with the command

```
 git clone https://github.com/gabriele-di-bona/coarse-graining-in-networks
```

## How to use
In order to avoid problems in this github repository, everything is organised in subfolders. 
Put all functions related to a specific folder in a new util in the `./utils/` folder and use them as you wish in a new script or notebook in `./python_scripts/` `./jupyter_notebooks/`.

When modifying the github folder, create a new branch from the main one.
Please commit a file only when tested and working. When you think the folder is at a good stage, ask to merge the repository through a pull request.

**ACHTUNG**: do not work on the same file as other people at the same time! Otherwise you will get to merge issues and it is going to be a mess hehe :)

**ACHTUNG 2**: Have fun ;)

# RULES
you can use networkx or igraph, but return ...

Coarse graining is a dictionary (output of methods)
{original_node: super_node}

## Creation of the graphs
Return an edge list or adjacency matrix when creating a graph.
Save the adjacency matrix as 
