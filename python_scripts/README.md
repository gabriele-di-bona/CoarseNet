# Python scripts

## How to use
When creating your script, please add all your imports on a section on top.
Remember to move your working directory!
All utils assume that the working directory is the root directory of the github folder.
Therefore add the following in your import section

```
import os
# If you are running this from ~/python_scripts/mycode.py
# change directory to the root of the repository
# All utils assume that the working directory is the root directory of the github folder
os.chdir('../')
```

If you use a specific method/metric/etc, create the related functions in a specific util in the utils directory. Then, import it here with the following

```
import sys
# Add utils directory in the list of directories to look for packages to import
sys.path.insert(0, os.path.join(os.getcwd(),'utils'))

# import local utils
import name_of_my_util
```

Remember to save data and figures in the related figures `./data/mydata` and `./figures/myfigure`.