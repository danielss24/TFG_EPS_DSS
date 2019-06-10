import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
x = np.arange(-5,5,1)
y = np.arange(-5,5,1)
X,Y = np.meshgrid(x,y)



fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, projection='3d')
Z = X*0
ax.plot_surface(X, Y, Z,cmap='RdBu',alpha=0.3)
Z += 1
ax.plot_surface(X, Y, Z,cmap='seismic',alpha=0.3)
plt.show()