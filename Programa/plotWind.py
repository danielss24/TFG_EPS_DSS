import csv
import os

import Pckg.Utils.utils as util
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from scipy.stats import kde
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


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

    plt.xlabel("Tiempo / s")
    xPlt.set_ylabel("Fuerza / g")
    yPlt.set_ylabel("Fuerza / g")
    zPlt.set_ylabel("Fuerza / g")

    vx_x, vx_y = getXY(fichero, xIndex=0, yIndex=6, cabeceras=True)
    vy_x, vy_y = getXY(fichero, xIndex=0, yIndex=7, cabeceras=True)
    vz_x, vz_y = getXY(fichero, xIndex=0, yIndex=8, cabeceras=True)

    #Conversion de array a numpy array
    vx_x = np.array(vx_x)
    vx_y = np.array(vx_y)
    #Aqui aplicar conversion

    #Conversion de array a numpy array
    vy_x = np.array(vy_x)
    vy_y = np.array(vy_y)
    #Aqui aplicar conversion

    #Conversion de array a numpy array
    vz_x = np.array(vz_x)
    vz_y = np.array(vz_y)
    #Aqui aplicar conversion

    yMax = np.max((vx_y,vy_y,vz_y))
    yMin = np.min((vx_y,vy_y,vz_y))
    xPlt.set_ylim([yMin-0.5,yMax+0.5])
    yPlt.set_ylim([yMin-0.5,yMax+0.5])

    x = np.arange(0,len(vx_x)/10,0.1)
    xPlt.plot(x,vx_y,zorder=0)
    xPlt.scatter(x,vx_y,s=10,c='black',zorder=1)

    yPlt.plot(x,vy_y,zorder=0)
    yPlt.scatter(x,vy_y,s=10,c='black',zorder=1)

    zPlt.plot(x,vz_y,zorder=0)
    zPlt.scatter(x,vz_y,s=10,c='black',zorder=1)


    #Set max and minium values of plots
    xMax_value = np.max(vx_y)
    yMax_value = np.max(vy_y)
    zMax_value = np.max(vz_y)
    xMin_value = np.min(vx_y)
    yMin_value = np.min(vy_y)
    zMin_value = np.min(vz_y)

    x2 = (0,len(vx_x)/10)
    zPlt.plot(x2, (1,1), "r")
    x2 = (0, len(vx_x)/10)
    xPlt.plot(x2, (0,0), "r")
    x2 = (0, len(vx_x)/10)
    yPlt.plot(x2, (0,0), "r")


    index_xMax_value = np.where(vx_y==xMax_value)
    print("index_xMax_value")
    print("Indices:", index_xMax_value[0])
    # for i in range (len(index_xMax_value[0])):
    #     indice = index_xMax_value[0][i]
    #     string = "Máx:", np.round(vx_y[indice],3)
    #     print(string)
    #     xPlt.annotate(string,
    #             xy=(indice/10, vx_y[indice]),
    #             xycoords='data',
    #             xytext=(indice/10, 2.5),
    #             arrowprops=
    #             dict(facecolor='black', shrink=5),
    #             verticalalignment='top')
    index_xMin_value = np.where(vx_y==xMin_value)
    print("index_xMin_value")
    print("Indices:", index_xMin_value[0])
    # for i in range (len(index_xMin_value[0])):
    #     indice = index_xMin_value[0][i]
    #     str = 'Min:',np.round(vx_y[indice],3)
    #     xPlt.annotate(str,
    #                 xy=(indice/10, vx_y[indice]),
    #                 xycoords='data',
    #                 xytext=(indice/10, 2.5),
    #                 arrowprops=
    #                 dict(facecolor='black', shrink=5),
    #                 verticalalignment='top')
    index_yMax_value = np.where(vy_y==yMax_value)
    print("index_yMax_value")
    print("Indices:", index_yMax_value[0])
    # for i in range (len(index_yMax_value[0])):
    #     indice = index_yMax_value[0][i]
    #     yPlt.annotate("Max",
    #             xy=(indice/10, vy_y[indice]),
    #             xycoords='data',
    #             xytext=(indice/10, 2.5),
    #             arrowprops=
    #             dict(facecolor='black', shrink=5),
    #             verticalalignment='top')
    index_yMin_value = np.where(vy_y==yMin_value)
    print("index_yMin_value")
    print("Indices:", index_yMin_value[0])
    # for i in range (len(index_yMin_value[0])):
    #     indice = index_yMin_value[0][i]
    #     yPlt.annotate("Min",
    #             xy=(indice/10, vy_y[indice]),
    #             xycoords='data',
    #             xytext=(indice/10, 2.5),
    #             arrowprops=
    #             dict(facecolor='black', shrink=5),
    #             verticalalignment='top')
    index_zMax_value = np.where(vz_y==zMax_value)
    print("index_zMax_value")
    print("Indices:", index_zMax_value[0])
    # for i in range (len(index_zMax_value[0])):
    #     indice = index_zMax_value[0][i]
    #     zPlt.annotate('function minium \n relative to data',
    #             xy=(indice/10, vz_y[indice]),
    #             xycoords='data',
    #             xytext=(2, 3),
    #             arrowprops=
    #             dict(facecolor='black', shrink=0.05),
    #             verticalalignment='top')
    index_zMin_value = np.where(vz_y==zMin_value)
    print("index_zMin_value")
    print("Indices:", index_zMin_value[0])
    # for i in range (len(index_zMin_value[0])):
    #     indice = index_zMin_value[0][i]
    #     zPlt.annotate('function minium \n re2lative to data',
    #             xy=(indice/10, vz_y[indice]),
    #             xycoords='data',
    #             xytext=(2, 3),
    #             arrowprops=
    #             dict(facecolor='black', shrink=0.05, arrowstyle='->',connectionstyle='Arc3'),
    #             verticalalignment='top',fontsize=20)

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

    x = np.array(x)
    y = np.array(y)
    modulo = np.sqrt(x.min()*x.min()+x.max()*x.max())
    print(modulo)
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('center')
    p1 = np.polyfit(x, y, 1)
    ax.plot(x,np.polyval(p1,x) , "b")
    guardarImagen(rutaPlot, fichero, fig,3)

def thirdPlot_v2(ruta,fichero):

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
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('center')
    p1 = np.polyfit(x, y, 1)
    x2 = np.array((-2, 2))
    x2 = np.array((-maxAxisValue, maxAxisValue))
    # print("pendiente", p1[0], "corte", p1[1])
    ax.plot(x2, p1[0] * x2 + p1[1], "b")
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
    fig, axes = plt.subplots(ncols=2, nrows=1, figsize=(21, 5))

    nbins = 50

    k = kde.gaussian_kde(data.T)
    # xi, yi = np.mgrid[-maxAxisValue:maxAxisValue:nbins * 1j, -maxAxisValue:maxAxisValue:nbins * 1j]
    xi, yi = np.mgrid[-4:4:nbins * 1j, -4:4:nbins * 1j]
    # xi, yi = np.mgrid[y.min():y.max():nbins * 1j, x.min():x.max():nbins * 1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    axes[0].set_title('2D Density with shading')
    axes[0].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.Blues)

    # contour
    axes[1].set_title('Contour')
    axes[1].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.Blues)
    axes[1].contour(xi, yi, zi.reshape(xi.shape))
    guardarImagen(rutaPlot,fichero,fig,4)
    # plt.show()

def mapaViento2D(rutaPlot):

    margenPlot = 0.5
    maxValueData = 90

    fig = plt.figure()

    numDatos = input("Numero de conjunto de datos, pon 4:")

    xVector = list()
    for i in range(int(numDatos)):
        fichero = util.cargadorFich(rutaFull)
        # consigue los valores de varianza roll y pitch
        x, y = getXY(fichero, 14, 15, True)
        # consigue la fuerza del viento
        z = getDataFromFile(fichero, 13, True)

        for enum, each in enumerate(z):
            x[enum] = x[enum] / maxValueData * each
            y[enum] = y[enum] / maxValueData * each

        p1 = np.polyfit(x, y, 1)
        xVector.append(p1[0])

    plt.xlim(-1,11)
    plt.ylim(-1,18)

    plt.xlabel("Distancia / m")
    plt.ylabel("Distancia / m")

    origin = [7.5], [12]  # origin point
    tam = np.sqrt(xVector[0]*xVector[0]+1)
    print(tam)
    plt.quiver(*origin, xVector[0], 1, color='b', scale=10/tam)
    origin = [2.5], [12]  # origin point
    tam = np.sqrt(xVector[1]*xVector[1]+1)
    print(tam)
    plt.quiver(*origin, xVector[1], 1, color='b', scale=10/tam)
    origin = [7.5], [6]  # origin point
    tam = np.sqrt(xVector[2]*xVector[2]+1)
    print(tam)
    plt.quiver(*origin, xVector[2], 1, color='b', scale=10/tam)
    origin = [2.5], [6]  # origin point
    tam = np.sqrt(xVector[3]*xVector[3]+1)
    print(tam)
    plt.quiver(*origin, xVector[3], 1, color='b', scale=10/tam)

    plt.plot((0, 0), (0, 17), 'k')
    plt.plot((0, 10), (0, 0), 'k')
    plt.plot((0, 10), (17, 17), 'k')
    plt.plot((10, 10), (17, 0), 'k')
    guardarImagen(rutaPlot, fichero, fig,5)


def mapaViento3D(rutaPlot):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Posiciones de los vectores
    yPos = (6, 6, 12, 12)
    xPos = (2.5, 7.5, 2.5, 7.5)
    zPos = (0.3, 0.3, 0.3, 0.3)

    margenPlot = 0.5
    maxValueData = 90

    numDatos = 4

    w = list()
    xVector = list()
    for i in range(int(numDatos)):
        fichero = util.cargadorFich(rutaFull)
        # consigue los valores de varianza roll y pitch
        x, y = getXY(fichero, 14, 15, True)
        # consigue la fuerza del viento
        z = getDataFromFile(fichero, 13, True)

        for enum, each in enumerate(z):
            x[enum] = x[enum] / maxValueData * each
            y[enum] = y[enum] / maxValueData * each

        p1 = np.polyfit(x, y, 1)
        xVector.append(float(p1[0]))
        z = np.array(z)
        w.append(np.mean(z))

    for enum,i in enumerate(w):
        i -=1
        w[enum] = i
    v = (1, 1, 1, 1)

    ax.quiver(xPos, yPos, zPos, xVector, v, w, color ='b')

    zPos=(2.5, 2.5, 2.5, 2.5)

    w = list()
    xVector = list()
    for i in range(int(numDatos)):
        fichero = util.cargadorFich(rutaFull)
        # consigue los valores de varianza roll y pitch
        x, y = getXY(fichero, 14, 15, True)
        # consigue la fuerza del viento
        z = getDataFromFile(fichero, 13, True)

        for enum, each in enumerate(z):
            x[enum] = x[enum] / maxValueData * each
            y[enum] = y[enum] / maxValueData * each

        p1 = np.polyfit(x, y, 1)
        xVector.append(float(p1[0]))
        z = np.array(z)
        w.append(np.mean(z))

    for enum, i in enumerate(w):
        i -= 1
        w[enum] = i
    v = (1, 1, 1, 1)

    ax.quiver(xPos, yPos, zPos, xVector, v, w, color='r')
    for h in (0.3,2.5):
        x2 = (6, 12)
        ax.plot((2.5, 2.5),x2, (h,h), 'k--')
        x2 = (6, 12)
        ax.plot((7.5, 7.5),x2, (h,h), 'k--')
        x2 = (6, 6)
        ax.plot((2.5, 7.5),x2, (h,h), 'k--')
        x2 = (12, 12)
        ax.plot((2.5, 7.5),x2, (h,h), 'k--')

    #Rectas discontinuas
    ax.plot((2.5,2.5),(6, 6), (0.3, 2.5), 'k--')
    ax.plot((7.5,7.5),(6, 6), (0.3, 2.5), 'k--')
    ax.plot((2.5,2.5),(12, 12), (0.3, 2.5), 'k--')
    ax.plot((7.5,7.5),(12, 12), (0.3, 2.5), 'k--')

    #Rectas margen
    #Plano 0
    ax.plot((0, 0), (0, 17), (0), 'k')
    ax.plot((0, 10), (0, 0), (0), 'k')
    ax.plot((0, 10), (17, 17), (0), 'k')
    ax.plot((10, 10), (17, 0), (0), 'k')

    #Verticales
    ax.plot((0, 0), (0, 0), (0,4.6), 'k')
    ax.plot((10, 10), (17, 17), (0,4.6), 'k')
    ax.plot((0, 0), (17, 17), (0,4.6), 'k')
    ax.plot((10, 10), (0, 0), (0,4.6), 'k')

    #Plano 1
    ax.plot((0, 0), (0, 17), (4.6), 'k')
    ax.plot((0, 10), (0, 0), (4.6), 'k')
    ax.plot((0, 10), (17, 17), (4.6), 'k')
    ax.plot((10, 10), (17, 0), (4.6), 'k')


    y = np.arange(6, 13, 1)
    x = np.arange(2.5, 8.5, 1)
    X, Y = np.meshgrid(x, y)

    Z = X * 0.0 +0.3
    ax.plot_surface(X, Y, Z, cmap='seismic', alpha=0.3)
    Z += (2.5 - 0.3)
    ax.plot_surface(X, Y, Z, cmap='RdBu', alpha=0.3)

    ax.scatter(0,0,cmap='k')
    ax.set_xlabel('Distancia / m')
    ax.set_ylabel('Distancia / m')
    ax.set_zlabel('Distancia / m')

    # plt.show()
    guardarImagen(rutaPlot, fichero, fig,6)


def guardarImagen(rutaPlot,fichero,fig,numPlot):
    nombreFichero = fichero.split("/")
    nombreFichero = nombreFichero[-1].replace(".txt", "") + "_Plot" + str(numPlot) + ".png"
    nombreFichero = rutaPlot + nombreFichero
    fig.savefig(nombreFichero)

if __name__ == '__main__':
    ruta = "2019/06/09/"
    rutaFull = "./" + ruta
    fichero = util.cargadorFich(rutaFull)
    rutaPlot = ruta+"Plot/"
    os.makedirs(rutaPlot, exist_ok=True)
    secondPlot(rutaPlot,fichero)
    # thirdPlot(rutaPlot,fichero)
    # thirdPlot_v2(rutaPlot,fichero)
    # heatmap(rutaPlot,fichero)
    # input("Mapa de 2D y 3D , OJO!")
    # mapaViento2D(rutaPlot)
    # mapaViento3D(rutaPlot)

    plt.show()