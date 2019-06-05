import csv
import os

import Pckg.Utils.utils as util
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from scipy.stats import kde


def getXY(fichero, xIndex=0, yIndex=1, cabeceras = False):
    x = []
    y = []

    line = 0

    with open(fichero, 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter='\t')
        for row in plots:
            if cabeceras == True and line == 0:
                print("Cabeceras:", row)
            if (cabeceras == True and line != 0) or cabeceras == False:
                y.append(float(row[yIndex]))
                x.append(float(row[xIndex]))
            line += 1

    return x,y

def getDataFromFile(fichero, i, cabeceras = False):
    x = []

    line = 0

    with open(fichero, 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter='\t')
        for row in plots:
            if cabeceras == True and line == 0:
                print("Cabeceras:", row)
            if (cabeceras == True and line != 0) or cabeceras == False:
                x.append(float(row[i]))
            line += 1

    return x

def firstPlot(fichero):
    x,y = getXY(fichero,0,13,True)
    plt.plot(x, y, label='Viento (G) - Tiempo')
    plt.xlabel('Tiempo (direccion)')
    plt.ylabel('Viento')
    plt.ylim(0, 4)
    plt.legend()

    #plt.show()


def secondPlot(ruta,fichero):

    fig, (xPlt, yPlt, zPlt) = plt.subplots(3, 1, sharex=True)

    xPlt.set_title("Vx/Tiempo")
    yPlt.set_title("Vy/Tiempo")
    zPlt.set_title("Vz/Tiempo")

    x, y = getXY(fichero, xIndex=0, yIndex=6, cabeceras=True)
    xPlt.plot(x,y)
    x, y = getXY(fichero, xIndex=0, yIndex=7, cabeceras=True)
    yPlt.plot(x,y)
    x, y = getXY(fichero, xIndex=0, yIndex=8, cabeceras=True)
    zPlt.plot(x,y,)
    guardarImagen(rutaPlot,fichero,fig,2)
    #plt.show()

def thirdPlot(ruta,fichero):

    margenPlot = 0.5
    maxValueData = 90

    #consigue los valores de varianza roll y pitch
    x,y = getXY(fichero,14,15,True)
    #consigue la fuerza del viento
    z = getDataFromFile(fichero,13,True)

    for enum,each in enumerate(z):
        x[enum] = x[enum] / maxValueData * each
        y[enum] = y[enum] / maxValueData * each

    maxX = max(x) + margenPlot
    maxY = max(y) + margenPlot

    # x = np.array(x)
    # y = np.array(y)
    #
    # indexX = np.where(x==maxX)
    # indexY = np.where(y==maxY)
    #
    # maxX = x[indexX]
    # maxY = y[indexY]

    maxAxisValue = 0
    if maxX > maxY:
       maxAxisValue = maxX
    else:
       maxAxisValue = maxY

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    plt.scatter(x, y)
    # plt.xlabel('grados')
    # plt.ylabel('grados')
    plt.xlim(-maxAxisValue, maxAxisValue)
    plt.ylim(-maxAxisValue, maxAxisValue)
    # plt.legend()
    # Move left y-axis and bottim x-axis to centre, passing through (0,0)
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('center')
    # nombreFichero = fichero.split("/")[4]
    guardarImagen(rutaPlot, fichero, fig,3)


def heatmap(rutaPlot, fichero):
    margenPlot = 0.5
    maxValueData = 90

    # consigue los valores de varianza roll y pitch
    x, y = getXY(fichero, 14, 15, True)
    # consigue la fuerza del viento
    z = getDataFromFile(fichero, 13, True)

    for enum, each in enumerate(z):
        x[enum] = x[enum] / maxValueData * each
        y[enum] = y[enum] / maxValueData * each

    maxX = max(x) + margenPlot
    maxY = max(y) + margenPlot

    maxAxisValue = 0
    if maxX > maxY:
        maxAxisValue = maxX
    else:
        maxAxisValue = maxY

    x = np.array(x)
    y = np.array(y)
    data = np.stack((x, y), axis=-1)

    # Create a figure with 6 plot areas
    fig, axes = plt.subplots(ncols=3, nrows=1, figsize=(21, 5))

    # Everything sarts with a Scatterplot
    axes[0].set_xlim([-maxAxisValue, maxAxisValue])
    axes[0].set_ylim([-maxAxisValue, maxAxisValue])
    axes[0].set_title('Scatterplot')
    axes[0].plot(x, y, 'ko')
    # # Thus we can cut the plotting window in several hexbins
    nbins = 50

    # Evaluate a gaussian kde on a regular grid of nbins x nbins over data extents
    k = kde.gaussian_kde(data.T)
    # xi, yi = np.mgrid[-maxAxisValue:maxAxisValue:nbins * 1j, -maxAxisValue:maxAxisValue:nbins * 1j]
    # xi, yi = np.mgrid[-4:4:nbins * 1j, -4:4:nbins * 1j]
    xi, yi = np.mgrid[y.min():y.max():nbins * 1j, x.min():x.max():nbins * 1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    axes[1].set_title('2D Density with shading')
    axes[1].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.Blues)

    # contour
    axes[2].set_title('Contour')
    axes[2].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.Blues)
    axes[2].contour(xi, yi, zi.reshape(xi.shape))
    guardarImagen(rutaPlot,fichero,fig,4)
    # plt.show()

def guardarImagen(rutaPlot,fichero,fig,numPlot):
    nombreFichero = fichero.split("/")
    nombreFichero = nombreFichero[-1].replace(".txt", "") + "_Plot" + str(numPlot) + ".png"
    nombreFichero = rutaPlot + nombreFichero
    fig.savefig(nombreFichero)

if __name__ == '__main__':
    ruta = "2019/06/03/"
    rutaFull = "./" + ruta
    fichero = util.cargadorFich(rutaFull)
    rutaPlot = ruta+"Plot/"
    os.makedirs(rutaPlot, exist_ok=True)
    secondPlot(rutaPlot,fichero)
    thirdPlot(rutaPlot,fichero)
    heatmap(rutaPlot,fichero)


    # plt.show()