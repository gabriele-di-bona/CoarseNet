import numpy as np

def get_micro2macro_dict_from_pd_df(mapping):
    """
    Converts the mapping (pandas dataframe) from nodes in the microscale network 
    to the corresponding node in the macroscale network into a dictionary.
    
    Parameters
    ----------
    - mapping (pd.DataFrame with columns 'micro' and 'macro'): dataframe with the mapping between nodes in the microscale and macroscale (original graph and coarse grained graph)
    
    Returns
    -------
    - micro2macro_dict (dict): dictionary with the mapping, where the key is the micro scale node and the value is the macro one
    """
    micro2macro_dict = {}
    mapping_micro = np.array(mapping.micro)
    mapping_macro = np.array(mapping.macro)
    for i in range(len(mapping_micro)):
        micro2macro_dict[mapping_micro[i]] = mapping_macro[i]
    return micro2macro_dict

def get_micro2macro_dict_from_vector(mapping):
    """
    Converts the mapping (pandas dataframe) into a dictionary.
    
    Parameters
    ----------
    - mapping (list or array): list or array with the mapping between nodes in the microscale and macroscale (original graph and coarse grained graph), where the index corresponds to the micro node and the element is the macro node
    
    Returns
    -------
    - micro2macro_dict (dict): dictionary with the mapping, where the key is the micro scale node and the value is the macro one
    """
    micro2macro_dict = {}
    for i,j in enumerate(mapping):
        micro2macro_dict[i] = j
    return micro2macro_dict

def get_macro2microlist_dict_from_micro2macro_dict(micro2macro_dict):
    """
    Get the inverse mapping from macronodes to the list of its corresponding micronodes
    
    Parameters
    ----------
    - micro2macro_dict (dict): dictionary with the mapping, where the key is the micro scale node and the value is the macro one
    
    Returns
    -------
    - macro2microlist_dict (dict): dictionary with the inverse mapping, where the key is the macro scale node and the value is the list of the corresponding micro nodes
    """
    macro2microlist_dict = {}
    for i,j in micro2macro_dict.items():
        try:
            macro2microlist_dict[j].append(i)
        except KeyError:
            macro2microlist_dict[j] = [i]
    return macro2microlist_dict