import csv

import Pckg.Utils.utils as util
import matplotlib.pyplot as plt


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

    x,y = getXY(fichero,14,15,True)
    z = getDataFromFile(fichero,13,True)

    for enum,each in enumerate(z):
        x[enum] = x[enum] / 90 * each
        y[enum] = y[enum] / 90 * each

    # print(min(x))
    # print(max(x))
    # print(min(y))
    # print(max(y))

    plt.scatter(x, y)
    plt.xlabel('grados')
    plt.ylabel('grados')
    #plt.ylim(0, 4)
    # plt.legend()


if __name__ == '__main__':
    fichero = util.cargadorFich("./2019/05/07/")
    firstPlot(fichero)
    secondPlot(fichero)
    thirdPlot(fichero)


    plt.show()