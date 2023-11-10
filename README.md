# CoarseNet

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
Please commit a file only when tested and working. When you think the folder is at a good stage, ask to merge to the main branch through a pull request.

**ACHTUNG**: do not work on the same file as other people at the same time! Otherwise you will get to merge issues and it is going to be a mess hehe :)

**ACHTUNG 2**: Have fun ;)

# RULES

## Programming language 
This repository is mainly working on Python. 
Since this is a collaborative project, where some methods are already implemented in other programming languages, you might find some of these, like in R or Julia. 
The usage of each method is documented in the related section.

## Usage of coarse-graining methods
Each method is related to a script and, if needed, some utils. 
The purpose of a coarse-graining method is to find the coarse-grained graph $G'(N',M')$ of a graph $G(N,M)$ with $N$ nodes and $M$ edges.
Therefore, a script related to a method needs to take the (pandas columns: source, target, weight) weighted edge list of a graph $G$ as input and return the mapping (pandas columns: node, supernode) from the nodes in $G$ to their respective node in $G'$, as well as the weighted edge list of $G'$.

**ACHTUNG**: If run on Python, please wrap your method in a function to put in the utils, that take into account either the edge list or some other object (specified in the documentation), so that the related method can be imported easily in other scripts and notebooks.
