import sys
from os import listdir
from os.path import isfile


def debugPrint(y, x, text):
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()

def ls1(path):
    return [obj for obj in listdir(path) if isfile(path + obj)]

def cargadorFich(ruta=""):

    if ruta == "":
        print("Indique la ruta de los ficheros desde el directorio actual, tiene que contener un '.' como primero caracter:\n"
                "Ej:\t ./mi/ruta/es/esta/\n")
        ruta = input("Ruta:")

    print("Ruta : ", ruta)


    files = ls1(ruta)
    print("Lista de ficheros:")
    for enum,file in enumerate(files):
        print("\t-",enum,":",file)

    fichIndx = input("Indique el numero de fichero que quiere:")
    fichero = ruta+files[int(fichIndx)]
    print("Fichero: ", fichero, "\n")
    return fichero