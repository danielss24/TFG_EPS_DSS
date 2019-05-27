import csv

import Pckg.Utils.utils as util
import matplotlib.pyplot as plt
import numpy as np


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


def secondPlot(fichero):

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
    #plt.show()

def thirdPlot(fichero):

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

def fourthPlot(fichero):

    maxValueData = 90
    # consigue los valores de varianza roll y pitch
    U, V= getXY(fichero, 14, 15, True)
    # consigue la fuerza del viento
    Z = getDataFromFile(fichero, 13, True)

    print(np.sqrt(len(U)))

    X,Y = np.meshgrid(np.arange(0,np.sqrt(len(U)),1),np.arange(0,np.sqrt(len(U)),1))


    for enum, each in enumerate(Z):
        U[enum] = U[enum] / maxValueData * each
        V[enum] = V[enum] / maxValueData * each

    plt.quiver(X,Y,U,V)

if __name__ == '__main__':
    fichero = util.cargadorFich("./2019/05/07/")
    # firstPlot(fichero)
    # secondPlot(fichero)
    # thirdPlot(fichero)
    fourthPlot(fichero)


    plt.show()