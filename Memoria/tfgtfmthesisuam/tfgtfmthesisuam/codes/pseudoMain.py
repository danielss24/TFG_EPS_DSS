if __name__ == '__main__':

    confirmacion = "n"

    print("Tomar una o varias medidas:\n\t1-Una medida\n\t2-Varias medidas")
    opcion = input("\nOpcion:")
    if int(opcion) == 1:
        print("\nTomar una sola medida seleccionado")
    elif int(opcion) == 2:
        print("\nTomar varias medidas seleccionado")
        while confirmacion == 'n':
            filas = input("Indique el numero de filas:")
            columnas = input("Indique el numero de columnas:")
            alturas = input("Indique el numero de alturas:")

            print("Desea hacer una medicion de:", filas, "x", columnas, "x", alturas, "?")
            confirmacion = raw_input("Yes(Y) - No(n)")
            if confirmacion == 'n' or confirmacion == 'N':
                print("\n\nIndique de nuevo las medidas.")

    tiempo = raw_input("Indique el tiempo de medida (default = 10 s):")
    if tiempo == '':
        tiempo = 10
    print("Tiempo de medicion: ", tiempo , "seg")


    wm = WindMeasure(tiempo)

    if int(opcion) == 1:
        print("Inicio de toma de medida iniciado ...")
        wm.registrar_medidas()
    elif int(opcion) == 2:
        print("Inicio de toma de medidas iniciado ...")
        for h in range(alturas):           
            for row in range(filas):
                for col in range(columnas):
                    wm.registrar_medidas()

    print("Fin de toma de datos")