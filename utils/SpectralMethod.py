
"""
SpectralMethod.py
--------------------
Implementation of the method developed in the paper:

David Gfeller and Paolo De Los Rios (2007)
Spectral Coarse Graining of Complex Networks
DOI: 10.1103/PhysRevLett.99.038701

author: Miguel A. González-Casado
email: miguelangel.gonzalezc@outlook.es
"""

import scipy as sp 
import networkx as nx
import numpy as np
import pandas as pd

def spectral_method(edgelist,n_relevant_eigenvectors,I):
    '''

    A function that takes the edgelist of a weighted, CONNECTED and 
    UNDIRECTED network and produces its Coarse Grained version along 
    with the mapping between nodes in both networks

    Parameters
    ----------
    edgelist (pd.DataFrame): edgelist of the original network with columns 
    'source', 'target' and 'weight'. The algorithm assumes the network to be 
    undirected, so the edgelist requires simply the i->j link, not the j->i
    
    n_relevant_eigenvectors (int): number of left eigenvectors we choose to 
    represent the large-scale behavior of the network. The larger the number, 
    the more fine grained the Coarse-Grained network is
    
    I (int): number of intervals in which we divide the left eigenvectors. The 
    larger this number is, the more fine grained the Coarse-Grained network is
    
    TAKE INTO ACCOUNT THAT BOTH PARAMETERS NEED TO BE TUNED DEPENDING ON THE SIZE 
    OF THE NETWORK, AND THE CHOICE WILL DIRECTLY DETERMINE THE TOTAL NUMBER OF 
    SUPER NODES. 
    
    Returns
    -------
    mapping (pd.DataFrame): mapping between the original nodes (micro) and the 
    Super Nodes (macro)
    
    edgelist (pd.DataFrame): edgelist of the original network with columns 
    'source', 'target' and 'weight'. This output provides both the i->j and the 
    j->i links
    
    '''

    # We construct the Adjacency Matrix from the Edgelist
    G = nx.from_pandas_edgelist(edgelist, source='source', target='target',edge_attr='weight')
    A = nx.to_numpy_array(G)
    # We store the number of nodes in the network
    number_of_nodes = A.shape[0]
    # We build the Stochastic Random Walks Matrix W
    W = A/np.sum(A, axis=0)
    
    # We compute the left/right eigenvectors of W
    eigenvalues, left_eigenvectors, right_eigenvectors = sp.linalg.eig(W, 
                                                                       left = True,
                                                                       right = True)
    eigenvalues, left_eigenvectors, right_eigenvectors = eigenvalues.real, left_eigenvectors.real, right_eigenvectors.real
    
    
    #The normalized left eigenvector corresponding to the eigenvalue eigenvalues[i] is the column left_eigenvectors[:,i]
    #The normalized right eigenvector corresponding to the eigenvalue eigenvalues[i] is the column right_eigenvectors[:,i]
    
    # Eigenvalues are not ordered, so we extract the indices of the ordered eigenvalues (decreasing order)
    ordered_eigenvalue_indices = np.argsort(-eigenvalues)
    
    # We define arrays to store the number N of relevant eigenvectors and their associated eigenvalues
    relevant_eigenvectors_l = np.zeros((left_eigenvectors.shape[0],n_relevant_eigenvectors))
    relevant_eigenvectors_r = np.zeros((right_eigenvectors.shape[0],n_relevant_eigenvectors))
    relevant_eigenvalues = np.zeros(n_relevant_eigenvectors)
    # We store only N NON-TRIVIAL eigenvectors (we are only interested in eigenvectors in which entries are different among them) 
    j = 0
    for i in range(n_relevant_eigenvectors):
        # Extract the left eigenvector associated with the next largest eigenvalue
        left_eigenvector = left_eigenvectors[:,ordered_eigenvalue_indices[j]]
        # We check if the eigenvector is trivial
        while sum(np.round(left_eigenvector,4)==np.round(left_eigenvector,4)[0])==len(left_eigenvector):
            j = j+1
            left_eigenvector = left_eigenvectors[:,ordered_eigenvalue_indices[j]]
        
        # We store the data
        relevant_eigenvectors_l[:,i] = left_eigenvector
        relevant_eigenvectors_r[:,i] = right_eigenvectors[:,ordered_eigenvalue_indices[j]]
        relevant_eigenvalues[i] = eigenvalues[ordered_eigenvalue_indices[j]]
        
        j = j+1
    
    # We divide the left eigenvector in I equal-size intervals   
    # We store the lengths of these intervals
    widths = (np.max(relevant_eigenvectors_l,axis=0) - np.min(relevant_eigenvectors_l,axis=0))/I
    # We store the left limit of the first interval
    priors = np.min(relevant_eigenvectors_l,axis=0)
    # We store the right limit of the first interval
    posteriors = priors + widths
    # Labels to store the interval to which each node belongs
    labels = np.zeros((number_of_nodes,n_relevant_eigenvectors))
    for n_eig in range(n_relevant_eigenvectors):
        label = 1 
        # We don't stop until all nodes are assigned an interval
        while sum(labels[:,n_eig]==0)!=0:
            # We assign nodes belonging to the same interval to the same label
            interval = (relevant_eigenvectors_l[:,n_eig]>=priors[n_eig])*(relevant_eigenvectors_l[:,n_eig]<=posteriors[n_eig])
            labels[interval,n_eig] = label
            label = label+1
            # We go for the next interval
            priors[n_eig] = posteriors[n_eig]
            posteriors[n_eig] = priors[n_eig] + widths[n_eig]
    
    # We construct a dataframe with the labels
    # In summary, each columns contains a label identifying nodes belonging to the same interval for each left eigenvector
    labels = pd.DataFrame(labels)
    # No we are interested in groupìng nodes that belong to the same interval for the N eigenvectors
    # We define the Super Node labels
    unique_labels = labels.drop_duplicates().reset_index(drop=True)
    unique_labels['identifier'] = np.arange(0,unique_labels.shape[0])
    identified_labels = pd.DataFrame(index = labels.index, columns = ['Super Node'])
    for row in unique_labels.index:
        super_node = unique_labels.loc[row,'identifier']
        row_labels = unique_labels.loc[row,labels.columns]
        identified_labels[(labels == row_labels).all(1)] = super_node
    
    # The output identified_labels contains the belonging of each node to each super node
        
    # Finally, with this info we construct the Coarse-Grained adjacency matrix
    # To do so, we aggregate the links belonging to each of the members of the super node
    A_tilde = A.copy()
    super_nodes = np.unique(np.array(identified_labels['Super Node']))
    stay = np.array([])
    for super_node in super_nodes: 
        sub_nodes = identified_labels[identified_labels['Super Node']==super_node].index
        if len(sub_nodes)>1:
            stays = sub_nodes[0]
            stay = np.append(stay,stays)
            leave = sub_nodes[1:]
            for leaves in leave:
                A_tilde[stays] = A_tilde[stays]+A_tilde[leaves]
                A_tilde[:,stays] = A_tilde[:,stays]+A_tilde[:,leaves]
                A_tilde[stays,stays] = 0
        else: 
            stays = sub_nodes[0]
            stay = np.append(stay,stays)
    A_tilde = A_tilde[stay.astype(int),:][:,stay.astype(int)]  
    
    # Uncomment this if you want an unweighted version of the network
    # A_tilde[A_tilde>1] = 1 
    
    G_tilde = nx.from_numpy_array(A_tilde,create_using=nx.DiGraph)
    coarse_grained_edgelist = nx.to_pandas_edgelist(G_tilde)
    
    # We extract the mapping in the correct output
    identified_labels.reset_index(inplace=True)    
    mapping = identified_labels.copy()
    mapping.columns = ['micro','macro']
    
    
    return mapping, coarse_grained_edgelist

def spectral_save(A, path): 
    G = nx.from_numpy_array(A)
    edgelist = nx.to_pandas_edgelist(G)
    mapping, coarse_edgelist = spectral_method(edgelist,
                                               n_relevant_eigenvectors=3,
                                               I=2)
    res = mapping.macro.tolist()
    np.savetxt(path,res)
    
