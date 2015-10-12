readme.txt

Mappy requires JSON and the webcolors module. Both of these modules can be downloaded through the pip package manager (download here: https://pip.pypa.io/en/stable/installing.html) by opening up the command line and typing "pip install json" and "pip install webcolors". 

In order to run Mappy, first install Python 2.7 if it is not already installed. Open a command line interface and navigate to the subfolder "Python", then type the command "python mappy.py" to run the program. 

Alternatively, in order to create an executable file, install the py2exe module through pip (command line --> "pip install py2exe"), then navigate to the "Python" directory in a command line interface and run "python setup.py py2exe". This will create two folders, "build" and "dist". Copy "helpText.txt" and "aboutText.txt" into the "dist" folder, then run "mappy.exe" which is located in the dist folder to run a .exe version of Mappy.

**ABOUT MAPPY**
Mappy is a force-based graph data visualization tool. What this means is it takes any data which can be represented as nodes and edges on a graph, and creates a nice physics-based visualization so that the user can see patterns and groupings in the data. It models nodes as electrons which repel each other, and edges as springs which pull nodes together. One of the main features of Mappy is that it allows the user to specify the size of individual nodes and the thicknesses of edges between nodes. This not only affects the visual drawing of the graph, but also affects the physics (larger nodes have greater repulsion, thicker edges have strong pull), allowing the user to see a clear visualization of which data points are related to each other.


Mappy Version History:
v1.0: Original distribution (submission for 15-112 Term Project)