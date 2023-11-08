"""
visualization_networkx.py
--------------------
Visualization routine to plot the input graph and the coarse grained version side by side (using networkx)

author: Gabriele Di Bona
email: gabriele.dibona.work@gmail.com
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import networkx as nx
import os
from utils.mapping_auxiliary_functions import *

def visualize_micro_macro(
    G_micro, mapping, G_macro,
    min_ns=60, max_ns=300, min_lw=2, max_lw=4, 
    ec='.7', nc='w', nec='steelblue',
    plot_edge_weights = True,
    all_colorful=True, node_cmap='magma_r',
    method_title = None, name_file = None, file_format = 'png',
):
    """
    Visualize microscale and macroscale networks side by side.

    Parameters:
    - G_micro (nx.Graph): Microscale network (a NetworkX graph).
    - G_macro (nx.Graph): Macroscale network (a NetworkX graph).
    - mapping (pd.DataFrame with columns 'micro' and 'macro'): dataframe with the mapping between nodes in the microscale and macroscale (original graph and coarse grained graph)
    - min_ns (int, optional): Minimum lode size for visualization. Default is 50.
    - max_ns (int, optional): Maximum node size for visualization. Default is 200.
    - min_lw (float, optional): Minimum linewidth for edges. Default is 1.5.
    - max_lw (float, optional): Maximum linewidth for edges. Default is 6.
    - ec (str, optional): Edge color. Default is '.5' (gray).
    - nc (str, optional): Node color. Default is 'w' (white).
    - nec (str, optional): Node edge color. Default is 'steelblue'.
    - plot_edge_weights (bool): if False, edge are not plotted with weights, and min_lw is used. Otherwise, it spans from min_lw to max_lw. If all weights are the same, min_lw is used. Default is True.
    - all_colorful (bool, optional): Whether to color all macroscale nodes (True)
        or only those that combine multiple nodes in the microscale network (False).
    - node_cmap (string): a matplotlib cmap. Default is 'Set2'.
    - method_title (string): title of the method to be printed on top of the figure. Default is None.
    - name_file (string): filename of the figure to be saved. Default is None (i.e., not saved)
    - file_format (string): format of the file of the figure to be saved. Default is 'png'.

    Returns:
    - None: This function plots and displays the microscale
            and macroscale networks side by side.
    """
    # Create a figure with two subplots for microscale and macroscale networks
    fig, ax = plt.subplots(1,2,figsize=(10,4.5),dpi=200)
    if method_title is not None:
        fig.suptitle(method_title, fontsize=16, va='top')
    
    # get the mapping from pd dataframe to dictionary
    micro2macro_dict = get_micro2macro_dict_from_pd_df(mapping)
    # get the inverse mapping from macronodes to the list of its corresponding micronodes
    macro2microlist_dict = get_macro2microlist_dict_from_micro2macro_dict(micro2macro_dict)
    
    # check if edges have weight attribute. If not, add it to 1
    for G in G_micro, G_macro:
        if len(G.edges) > 0 and 'weight' not in G[list(G.edges)[0][0]][list(G.edges)[0][1]]:
            nx.set_edge_attributes(G, 1, 'weight')
    
    # Position the nodes of the microscale network using a spring layout
    pos_micro = nx.spring_layout(G_micro)
    
    # for positioning the macroscale network, we assign the center of mass of the microscale network
    pos_macro = {}
    for macro_node, micro_nodes in macro2microlist_dict.items():
        pos_macro[macro_node] = np.mean([pos_micro[micro_node] for micro_node in micro_nodes],axis=0)

    # define a different color for each macro_node
    if all_colorful == True:
        macro_colors = mpl.colormaps[node_cmap](np.linspace(0,1,G_macro.number_of_nodes()))
        macro_colors_dict = {}
        for i,macro_node in enumerate(pos_macro.keys()):
            macro_colors_dict[macro_node] = macro_colors[i]
    else:
        number_of_big_macro_nodes = len([_ for _ in macro2microlist_dict.values() if len(_) > 1])
        macro_colors = mpl.colormaps[node_cmap](np.linspace(0,1,number_of_big_macro_nodes))
        macro_colors_dict = {}
        index_color = 0
        for macro_node in pos_macro.keys():
            if len(macro2microlist_dict[macro_node]) > 1:
                macro_colors_dict[macro_node] = macro_colors[index_color]
                index_color += 1
            else:
                macro_colors_dict[macro_node] = nc
        
    # define the color of micro nodes based on the corresponding macro_node
    micro_colors_dict = {}
    for micro_node in pos_micro.keys():
        micro_colors_dict[micro_node] = macro_colors_dict[micro2macro_dict[micro_node]]
    
    # PLOT MICROSCALE NETWORK
    nx.draw_networkx_nodes(G_micro, pos_micro,
            ax=ax[0],
            node_size=min_ns,
            node_color=[micro_colors_dict[node] for node in G_micro],
            edgecolors=nec
           )
    if plot_edge_weights == True:
        # get minimum and maximum edge weight
        min_weight_micro = 1000000000
        max_weight_micro = -1000000000
        for edge in G_micro.edges(data='weight'):
            min_weight_micro = min(min_weight_micro, edge[2])
            max_weight_micro = max(max_weight_micro, edge[2])
        # rescale edge_weight
        def rescale_weight(
            weight, 
            min_weight=min_weight_micro, 
            max_weight=max_weight_micro,
            min_size=min_lw, 
            max_size=max_lw,
        ):
            if max_weight == min_weight:
                return min_size
            else:
                return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)

        for edge in G_micro.edges(data='weight'):
            nx.draw_networkx_edges(G_micro,pos_micro,
                                   ax=ax[0],
                                   edgelist=[edge], 
                                   width=rescale_weight(edge[2]),
                                   edge_color=ec,
                                  )
    else:
        nx.draw_networkx_edges(G_micro,pos_micro,
                                   ax=ax[1],
                                   edgelist=G_micro.edges(), 
                                   width=min_lw,
                                   edge_color=ec,
                                  )
    # PLOT MACROSCALE NETWORK
    # rescale node_weight
    min_weight_macro = 1
    max_weight_macro = max([len(_) for _ in macro2microlist_dict.values()])
    def rescale_weight(
        weight, 
        min_weight=min_weight_macro, 
        max_weight=max_weight_macro,
        min_size=min_ns, 
        max_size=max_ns,
    ):
        if max_weight == min_weight:
            return min_size
        else:
            return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)
        
    # plot macroscale network
    nx.draw_networkx_nodes(G_macro, pos_macro,
            ax=ax[1],
            node_size=[rescale_weight(len(macro2microlist_dict[node])) for node in G_macro],
            node_color=[macro_colors_dict[node] for node in G_macro],
            edgecolors=nec
           )
    
    
    if plot_edge_weights == True:
        # get minimum and maximum edge weight
        min_weight_macro = 1000000000
        max_weight_macro = -1000000000
        for edge in G_macro.edges(data='weight'):
            min_weight_macro = min(min_weight_macro, edge[2])
            max_weight_macro = max(max_weight_macro, edge[2])
        # rescale edge_weight
        def rescale_weight(
            weight, 
            min_weight=min_weight_macro, 
            max_weight=max_weight_macro,
            min_size=min_lw, 
            max_size=max_lw,
        ):
            if max_weight == min_weight:
                return min_size
            else:
                return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)
        for edge in G_macro.edges(data='weight'):
            nx.draw_networkx_edges(G_macro,pos_macro,
                                   ax=ax[1],
                                   edgelist=[edge], 
                                   width=rescale_weight(edge[2]),
                                   edge_color=ec,
                                  )
    else:
        nx.draw_networkx_edges(G_macro,pos_macro,
                                   ax=ax[1],
                                   edgelist=G_macro.edges(), 
                                   width=min_lw,
                                   edge_color=ec,
                                  )

    ax[0].set_title('Original network')
    ax[1].set_title('Coarse-grained network')
    
    # remove box from axes
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[1].spines['top'].set_visible(False)
    ax[1].spines['right'].set_visible(False)
    ax[1].spines['bottom'].set_visible(False)
    ax[1].spines['left'].set_visible(False)

    plt.show()
    plt.tight_layout()
    
    if name_file is not None:
        os.makedirs('./figures/network_micro_macro_side_by_side/', exist_ok = True)
        fig.savefig(os.path.join('figures', 'network_micro_macro_side_by_side', f'{name_file}.{file_format}'))