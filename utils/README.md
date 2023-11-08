# Utils

## How to use
Use this folder to create utils that can be used across in the repository. 
Create a new file with your specific functions (for graph creation models, metrics, methods, etc.) so that we can all access and use these.

In order to use a util in your python code, add the following lines

```
import os
# If you are running this from ~/python_scripts/mycode.py
# change directory to the root of the repository
# All utils assume that the working directory is the root directory of the github folder
os.chdir('../')

import sys
# Add utils directory in the list of directories to look for packages to import
sys.path.insert(0, os.path.join(os.getcwd(),'utils'))

# import local utils
import name_of_my_util
```

Remember to save data and figures in the related figures `./data/mydata` and `./figures/myfigure`.

## Documentation

Please write a documentation of the functions you are using, using the format:

```
def my_func(parameter1, parameter2, ...):
    """
    Your description of the function.
    
    Parameters
    ----------
    parameter1 (type1 or type2): description of parameter1
    parameter1 (type3): description of parameter2
    
    Returns
    -------
    output1 (type1 or type2): description of output1
    """
```