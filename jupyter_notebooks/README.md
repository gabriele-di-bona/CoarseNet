# Jupyter Notebooks

## How to use
When creating your notebook, please add all your imports on a section on top.
Remember to move your working directory!
All utils assume that the working directory is the root directory of the github folder.
Therefore add the following in your import section

```
import os
# If you are running this from ~/jupyter_notebooks/mynotebook.ipynb
# change directory to the root of the repository
# All utils assume that the working directory is the root directory of the github folder
os.chdir('../')
```

If you use a specific method/metric/etc, create the related functions in a specific util in the utils directory. Then, import it here with the following

```
# import local utils
import utils.name_of_my_util
```

Remember to save data and figures in the related figures `./data/mydata` and `./figures/myfigure`.