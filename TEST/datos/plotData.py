import csv

import matplotlib.pyplot as plt

x = []
y = []

with open('datosPy.txt','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for enum, row in enumerate(plots):
        y.append(float(row[0]))
        x.append(enum)

plt.plot(x,y, label='Loaded from file!')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Interesting Graph\nCheck it out')
plt.legend()
plt.show()