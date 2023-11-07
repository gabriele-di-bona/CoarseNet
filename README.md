# Coarse graining in networks

Collaborative repository to analyse various coarse-graining methods for networks.

## Abstract

Coarse-graining is a widespread concept in science, appearing in situations ranging from highly applied, such as in efficient simulation of Earth's climate, to highly abstract, such as in the definition of Boltzmann entropy. In complex systems, coarse graining frequently appears in concepts such as renormalization, causal emergence, critical phenomena, and community detection. Complex networks often exhibit intricate fine-grained structure and multi-scale organization, and hence the choice of an appropriate coarse-graining scheme may be quite subtle. Consequently, over the past few decades, many distinct methods for coarse-graining of networks have emerged. Herein, we study the different coarse-graining methods that have been developed for networks, examining how they work, what their essential properties are, and their major similarities and differences. 

## Repository installation
Clone this directory to your computer in a new folder with the command

```
 git clone https://github.com/gabriele-di-bona/coarse-graining-in-networks
```

In order to ensure that everything is working as intended, create a dedicated environment using the specified requirements file, using:

```
conda env create -f coarse-graining-in-networks.yml
```

ACHTUNG: If you want to specify a specific install path rather than the default for your system, just use the -p flag followed by the required path, e.g.:

```
conda env create -f coarse-graining-in-networks.yml -p /home/user/anaconda3/envs/coarse-graining-in-networks
```

## How to use
In order to avoid problems in this github repository, everything is organised in subfolders. 
Put all functions related to a specific folder in a new util in the `./utils/` folder and use them as you wish in a new script or notebook in `./python_scripts/` `./jupyter_notebooks/`.

Please commit a file only when tested and working, and remember to pull before pushing any changes.

**ACHTUNG**: do not work on the same file as other people at the same time! Otherwise you will get to merge issues and it is going to be a mess hehe :)

**ACHTUNG 2**: Have fun ;)