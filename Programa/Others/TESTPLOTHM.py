# importing libraries 
import random
import matplotlib.pyplot as plt

fig = plt.figure()


# function to get random values for graph
def get_graphs():
    xs = []
    ys = []
    for i in range(10):
        xs.append(i)
        ys.append(random.randrange(10))
    return xs, ys


# defining subplots
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

# hiding the marker on axis
x, y = get_graphs()
# x =(50,51,52,53,54,55,56,57,58,59)
ax1.plot(x, y)
ax1.tick_params(axis='both', which='both', length=0)

# One can also change marker length
# by setting (length = any float value)

# hiding the ticks and markers
# x, y = get_graphs()
x =(50,51,52,53,54,55,56,57,58,59)
ax2.plot(x, y)
ax1.tick_params(axis='both', which='both', length=0)
# ax2.axes.get_xaxis().set_visible(False)
# ax2.axes.get_yaxis().set_visible(False)

# hiding the values and displaying the marker 
x, y = get_graphs()
ax3.plot(x, y)
ax3.yaxis.set_major_formatter(plt.NullFormatter())
ax3.xaxis.set_major_formatter(plt.NullFormatter())

# tilting the ticks (usually needed when 
# the ticks are densely populated) 
x, y = get_graphs()
ax4.plot(x, y)
ax4.tick_params(axis='x', rotation=45)
ax4.tick_params(axis='y', rotation=-45)

plt.show() 
