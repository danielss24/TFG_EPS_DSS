if __name__ == '__main__':

    confirmacion = "n"

    # while True:
    #     roll_pitch_yaw = wm.get_roll_pitch_yaw()
    #     print(roll_pitch_yaw.x,roll_pitch_yaw.y)
    #     print()
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


    if len(sys.argv) == 2:
        wm = WindMeasure(sys.argv[1])
    else:
        wm = WindMeasure()


    if int(opcion) == 1:
        print("Inicio de toma de medida iniciado ...")
        wm.registrar_medidas()
    elif int(opcion) == 2:
        print("Inicio de toma de medidas iniciado ...")
        for h in range(alturas):
            print("Plano Z =", h)
            for row in range(filas):
                print("Fila:", row)
                for col in range(columnas):
                    print("Columna:", col)
                    wm.registrar_medidas()
                    print(" ---- Medida realizada ---- ")
                    raw_input("(press enter) Continuar columnas ...")
                print("----------------------------------------------")
                print("              FILA ",row," TERMINADA               ")
                print("----------------------------------------------")
                raw_input("(press enter) Continuar filas ...")
            print("----------------------------------------------")
            print("                 PLANO",h," TERMINADO              ")
            print("----------------------------------------------")
            raw_input("(press enter) Continuar planos ...")

    print("Fin de toma de datos")