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
import myutil
```

Remember to save data and figures in the related figures `./data/mydata` and `./figures/myfigure`.

## Documentation

Please write a documentation of the functions you are using, using the format:

```
def my_func(parameter1, parameter2, ...):
    '''
    Description:
        Your description of the function.
    
    Input:
        - parameter1: description of parameter1 (type of parameter1)
        - parameter2: description of parameter2 (type of parameter2)
        - ...
    
    Output:
        - output1: description of the output variable output1 (type of output1)
    '''
```