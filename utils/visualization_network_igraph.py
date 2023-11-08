"""
visualization.py
--------------------
Visualization routine to plot the input graph and the coarse grained version side by side (using igraph)

author: Vander Freitas
email: vandercomp at gmail dot com
"""

import igraph as ig
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from collections import Counter


def coarse_grained_visualization(g, layout, g_cg, node_dict, figure_name='graphs.png'):
    """
    It generates a visualization of the input graph and the coarse grained version side by side
    
    Parameters
    ----------
    g (Python-igraph): The original input network
    layout (list of lists): Nodes' coordinates of the original input network. If not provided, we use the kk layout
    g_cg (Python-igraph): The coarse grained network (it must contain an attribute named weight for the plot)
    node_dict (Python dict): A dictionary mapping the nodes of the original network to the corresponding supernodes in g_cg
    figure_name (string): The name of the output figure one wants to export 

    Returns
    -------
    It does not return anything but saves a file with the provided figure_name
    """

    # COLOR
    # Get colors from a colormap, one for each community
    cmap = matplotlib.colormaps['magma_r']
    
    N_cg = g_cg.vcount()
    g_cg.vs['color'] = [cmap(i/float(N_cg)) for i in range(N_cg)]
    g.vs['color'] = [cmap(node_dict[v]/float(N_cg)) for v in range(g.vcount())]

    # COORDINATES
    if(not layout): # create the layout in case it is not passed as a parameter
        layout = g.layout("kk")
    coord_supernodes_x = [[] for i in range(N_cg)]
    coord_supernodes_y = [[] for i in range(N_cg)]
    for i in range(g.vcount()):
        coord_supernodes_x[ node_dict[i] ].append(layout[i][0])
        coord_supernodes_y[ node_dict[i] ].append(layout[i][1])
    
    for i in range(N_cg):
        coord_supernodes_x[i] = np.mean(coord_supernodes_x[i])
        coord_supernodes_y[i] = np.mean(coord_supernodes_y[i])
    
    layout_cg = [[coord_supernodes_x[i],coord_supernodes_y[i]] for i in range(N_cg)]


    # NODE SIZE
    node_max_size = 30.0
    node_min_size = 15.0
    list_nodes = list(node_dict.values())
    n_nodes_by_group = Counter(list_nodes)
    max_size_from_data = max(n_nodes_by_group.values())

    for i in range(len(n_nodes_by_group)):
        g_cg.vs[i]['size'] = (float(n_nodes_by_group[i])/float(max_size_from_data))*(node_max_size-node_min_size)+node_min_size
    
    g.vs['size'] = node_min_size

    min_edge_width = 1
    max_edge_width = 5
    max_observed_weigth = max(g_cg.es['weight'])
    for i in range(g_cg.ecount()):
        g_cg.es[i]['width'] = (float(g_cg.es[i]['weight'])/float(max_observed_weigth))*(max_edge_width-min_edge_width)+min_edge_width

    shape = (2, 1)
    colsep, rowsep = 40, 40
    width, height = 500, 500

    # Construct the plot
    plot = ig.Plot(figure_name, bbox=(2*width, 1*height), background="white")

    # ugly code, thinking about future adaptations (including more graphs)
    g_list = [g,g_cg]
    layout_list = [layout, layout_cg]
    idx=0
    # Create the graph and add it to the plot
    for i in range(shape[0]):
        for j in range(shape[1]):
            plot.add(g_list[idx], layout=layout_list[idx], bbox=(colsep/2 + width*i, rowsep/2 + height*j, -colsep/2 + width*(i+1), -rowsep/2 + height*(j+1)))

            # Make the plot draw itself on the Cairo surface
            plot.redraw()

            # If you have cairo installed, that is also possible to plot titles for the graphs
            ## Grab the surface, construct a drawing context, TextDrawer on surface
            # ctx = cairo.Context(plot.surface)
            # ctx.set_font_size(36)
            # drawer = TextDrawer(ctx, f'Graph.GRG({n}, {radius})', halign=TextDrawer.CENTER)
            # drawer.draw_at(width*i, 36 + height*j, width=200)

            idx += 1
                                
    plot.save()



# input: graph (igraph format)
# output: coarse grained graph (igraph format) and a dict relating nodes to groups
def get_coarse_grained_network(g):
    """
    A general routine to 
    
    Parameters
    ----------
    g (Python-igraph): The original input network

    Returns
    -------
    g_cg (Python-igraph): The coarse grained network
    node_dict (Python dict): A dictionary mapping the nodes of the original network to the corresponding supernodes in g_cg
    """

    
    # PLUG THE COARSE GRAINED METHOD HERE, RETURNING A DICT THAT RELATES NODES TO GROUPS
    # This python-ipgrah infomap returns a list of lists. Other methods return different stuff and one
    # might implement this part accordingly
    c = g.community_infomap()
    N_cg = len(c)

    node_dict = {}
    for i in range(len(c)):
        for v_ in c[i]:
            node_dict[v_] = i


    # FROM THIS POINT ON, WE NEED node_dict and g (in igraph format)
    # ----------------------------------------------------------------------------------

    # Creating the coarse grained network
    g_cg = ig.Graph()
    g_cg.add_vertices(N_cg)
    g_cg.es['weight'] = 0.0
    
    # checking for links between communities
    for e in g.es:
        v_src = e.source
        v_tgt = e.target

        c_src = node_dict[v_src]
        c_tgt = node_dict[v_tgt]

        # if nodes do not belong to the same group
        if(c_src != c_tgt):
            # if the edge does not exist, create one
            if(not g_cg.are_connected(c_src,c_tgt)):
                g_cg.add_edges([(c_src,c_tgt)])
                eid = g_cg.get_eid(c_src,c_tgt)
                g_cg.es[eid]['weight'] = 1.0
            else:
                # else update the weight
                eid = g_cg.get_eid(c_src,c_tgt)
                g_cg.es[eid]['weight'] = float(g_cg.es[eid]['weight']) + 1

    return g_cg, node_dict


if __name__ == '__main__':
    ###### MAIN CODE (for testing purposes) ######

    # Building the network
    g_ori = ig.Graph.GRG(100,0.2)
    #g_ori = ig.Graph.Tree(30,3)

    # Generating the coarse grained net
    g_cg, node_dict = get_coarse_grained_network(g_ori)

    # Visualizing
    coarse_grained_visualization(g=g_ori, layout=None, g_cg=g_cg, node_dict=node_dict, figure_name='graphs.png')