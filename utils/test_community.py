import graph_tool.all as gt
import numpy as np
from sklearn.metrics import normalized_mutual_info_score
import networkx as nx

def _sbm_community(v_count, edge_list, weights = None, directed = False):
    sources = [edge[0] for edge in edge_list]
    targets = [edge[1] for edge in edge_list]
    sources = np.array(sources)
    targets = np.array(targets)

    if weights != None:
        weights = np.array(weights)
        # g = gt.Graph(v_count, 
        #             np.array([sources, targets, weights]).T, 
        #             eprops=[("weight", "double")], 
        #             directed=directed)
        g = gt.Graph(v_count, directed=directed)
        g.add_edge_list(np.array([sources, targets, weights]).T, eprops=[("weight", "double")])
        # Here, we considered the maximum edge covarite value.
        # Fomr doc.:The parameter list is ["N", "alpha", "beta"], corresponding to the number of trials N and the parameters of the Beta prior distribution. If unspecified, the default is the noninformative choice, alpha = beta = 1.0, and N is taken to be the maximum edge covarite value.
        state = gt.minimize_blockmodel_dl(g, state_args=dict(recs=[g.ep.weight],
                                                 rec_types=["discrete-binomial"]))
        membership = state.b.a
    else:
        g = gt.Graph(v_count, directed=directed)
        g.add_edge_list(np.array([sources, targets]).T)
        state = gt.minimize_blockmodel_dl(g)
        membership = state.b.a

    return list(membership)

def _nmi(v_1, v_2, nG_dict):
    v_2 = [v_2[i] for i in nG_dict.values()]
    return normalized_mutual_info_score(v_1, v_2)


def sbm_comparison(original_graph, graining_graph, graining_graph_dict):
    """
    Compare two graphs using the Stochastic Block Model (SBM) and calculate the Normalized Mutual Information (NMI).

    Parameters
    ----------
    original_graph (NetworkX Graph):
        The original graph to be compared.

    graining_graph (NetworkX Graph):
        The graining graph, a coarser representation of the original graph, to be compared.

    graining_graph_dict (dict):
        A dictionary mapping nodes in the original graph to their corresponding communities in the graining graph.
        The keys are node IDs in the original graph, and the values are community labels in the graining graph.

    Returns
    ----------
    nmi : float
        The Normalized Mutual Information (NMI) score between the community memberships of the original graph and
        the graining graph. NMI measures the similarity of community structures, with higher values indicating
        better agreement.
    """
    edge_list = list(original_graph.edges)
    number_of_nodes = original_graph.number_of_nodes()
    edge_list_g = list(graining_graph.edges)
    number_of_nodes_g = graining_graph.number_of_nodes()
    weights_g = [d["weight"] for (u, v, d) in graining_graph.edges(data=True)]
    membership_1 = _sbm_community(number_of_nodes, edge_list)
    membership_2 = _sbm_community(number_of_nodes_g, edge_list_g, weights = weights_g)
    nmi = _nmi(membership_1, membership_2, graining_graph_dict)
    return nmi