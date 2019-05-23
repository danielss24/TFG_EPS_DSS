import datetime
import os
import sys
import time

import math
from Pckg.S2 import mpl3115
from Pckg.S2.MPU9250 import MPU6050

POSITIVO = 1
NEGATIVO = -1
IGUAL = 0


class WindMeasure():
    file = None
    barometer = None
    gyroscopio = None
    tiempo = 0

    registro_roll_t0 = None
    registro_pitch_t0 = None

    registro_roll_t1 = None
    registro_pitch_t1 = None

    registro_pitch_estado = None
    registro_roll_estado = None

    def __init__(self, tiempo=10):
        self.crearFichero(self.file)
        # self.inicializar_barometro()
        self.inicializar_gyroscopio()
        self.tiempo = tiempo

    def inicializar_gyroscopio(self):

        print("Inicio inicializacion de gyroscopio ... ")
        self.gyroscopio = MPU6050.MPU6050(1, 0x68)
        print("Fin inicializacion de gyroscopio ...")
        # self.gyroscopio = MPU9250.MPU9250()
        # self.gyroscopio.configMPU9250(MPU9250.GFS_250, MPU9250.AFS_2G)
        # self.gyroscopio.configAK8963(MPU9250.AK8963_MODE_C8HZ, MPU9250.AK8963_BIT_16)

    def calibrar_gyro(self):
        entrada = input(
            "Desea calibrar el gyroscopio[1] o cargar la anterior configuración[2]?\nTenga en cuenta que la orientación puede cambiar: ")
        if entrada == '1':
            calibracion = self.gyroscopio.calibrarGyro()
            # f = open("calibracion.out","w")
            # f.write(str(calibracion))
            # f.close()
        elif entrada == '2':
            # f = open("calibracion.out","r")
            # cadenaCalibracion = f.read()
            # f.close()
            self.gyroscopio.setGyroOffset(0.5238688792890147, 2.561511257439358, -6.6875060365656696)

    def inicializar_barometro(self):
        print("Inicio inicializacion de barometro ... ")
        self.barometer = mpl3115.MPL3115()
        self.barometer.config(True, 102200)
        print("Fin inicializacion de barometro ... ")

    def get_barometer_data(self):
        return self.barometer.read_data()

    def crearFichero(self, file):
        print("Inicio creacion fichero ...")
        cabecera = str(datetime.datetime.now())
        diaHora = cabecera.split(".")[0]
        ##################################################################
        # cabecera = (diaHora.split(" ")[0] + "_" + diaHora.split(" ")[1])
        cabecera = diaHora.split(" ")[1]
        ##################################################################
        cabecera = cabecera.replace(":", "")
        filename = cabecera + ".txt"

        fecha = diaHora.split(" ")[0]
        anyo = fecha.split("-")[0]
        mes = fecha.split("-")[1]
        dia = fecha.split("-")[2]
        path = anyo + "/" + mes + "/" + dia + "/"

        os.makedirs(path, exist_ok=True)

        print(filename)
        self.file = open(path + filename, "w+")
        self.put_first_line_fich()
        print("Fin creacion fichero ...")

    def put_first_line_fich(self):
        self.file.write(
            "#\tdia(1)\thora(1)\tgyroX\tgyroY\tgyroZ\taccelX\taccelY\taccelZ\troll\tpitch\tyaw\tbrujula\tvientoFG\tvarianzaRoll\tvarianzaPitch\tdireccion\tgpsLong\tgpsLat\taltime\tmotores(4)\tmotores(4)\tmotores(4)\tmotores(4)\n")

    def get_cabecera(self):
        cabecera = str(datetime.datetime.now())
        diaHora = cabecera.split(".")[0]
        segundos = diaHora[-2:]
        cabecera = (diaHora.split(" ")[0] + "\t" + diaHora.split(" ")[1])
        return cabecera, segundos

    # def get_gyro(self):
    #     return self.gyroscopio.readGyro()

    # def get_acel(self):
    #     return self.gyroscopio.readAccel()

    # def get_magn(self):
    #     while True:
    #         magn = self.gyroscopio.readMagnet()
    #         if magn['x']!=0 and magn['y']!=0 and magn['z']!=0:
    #             return magn

    def get_gyro(self):
        return self.gyroscopio.get_rotationV2()

    def get_acel(self):
        return self.gyroscopio.get_accelerationV2()

    def get_gps(self):
        return None

    def get_motores(self):
        return None

    def get_roll_pitch_yaw(self):
        return self.gyroscopio.readSensoresConCalibracion()

    # def get_pitch(self):
    #     sensoresAccel = self.get_acel()
    #     pitch = 180 * math.atan2(sensoresAccel['x'], math.sqrt(sensoresAccel['y']*sensoresAccel['y'] + sensoresAccel['z']*sensoresAccel['z']))/math.pi
    #     return pitch

    # def get_roll(self):
    #     sensoresAccel = self.get_acel()
    #     roll = 180 * math.atan2(sensoresAccel['y'], math.sqrt(sensoresAccel['x']*sensoresAccel['x'] + sensoresAccel['z']*sensoresAccel['z']))/math.pi
    #     return roll

    # def get_yaw(self):
    #     sensoresMagn = self.get_magn()
    #     pitch = self.get_pitch()
    #     roll = self.get_roll()
    #     mag_x = sensoresMagn['x'] * math.cos(pitch) + sensoresMagn['y']*math.sin(roll)*math.sin(pitch) + sensoresMagn['z']*math.cos(roll)*math.sin(pitch)
    #     mag_y = sensoresMagn['y'] * math.cos(roll) - sensoresMagn['z'] * math.sin(roll)
    #     yaw = 180 * math.atan2(-mag_y,mag_x)/math.pi
    #     return yaw

    def get_NESW_fromDegrees(self, degrees):

        self.conversionRangeDegrees(degrees)

        if 337.5 < degrees or degrees <= 22.5:
            return "N"
        elif 22.5 < degrees <= 67.5:
            return "NE"
        elif 67.5 < degrees <= 112.5:
            return "E"
        elif 112.5 < degrees <= 157.5:
            return "SE"
        elif 157.5 < degrees <= 202.5:
            return "S"
        elif 202.5 < degrees <= 247.5:
            return "SW"
        elif 247.5 < degrees <= 292.5:
            return "W"
        elif 292.5 < degrees <= 337.5:
            return "NW"

    def conversionRangeDegrees(self, degrees):

        degrees *= 2
        if degrees < 0:
            degrees = 360 + degrees

        return degrees

    def fuerzaresultante(self, x, y):
        return math.sqrt(x * x + y * y)

    def calculoViento(self, accel, roll_pitch_yaw):
        vientoFG = self.fuerzaresultante(accel[0], accel[1])

        varianzaRoll = 0
        varianzaPitch = 0

        if self.registro_pitch_t0 == None:
            self.registro_pitch_t0 = roll_pitch_yaw.y
            self.registro_pitch_t1 = roll_pitch_yaw.y
        else:
            self.registro_pitch_t0 = self.registro_pitch_t1
            self.registro_pitch_t1 = roll_pitch_yaw.y
            varianzaPitch = self.registro_pitch_t0 - self.registro_pitch_t1

        if self.registro_roll_t0 == None:
            self.registro_roll_t0 = roll_pitch_yaw.x
            self.registro_roll_t1 = roll_pitch_yaw.x
        else:
            self.registro_roll_t0 = self.registro_roll_t1
            self.registro_roll_t1 = roll_pitch_yaw.x
            varianzaRoll = self.registro_roll_t0 - self.registro_roll_t1

        direccion = self.calculoVientoDireccion(varianzaRoll, varianzaPitch)
     
        return vientoFG, varianzaRoll, varianzaPitch, direccion

    def calculoVientoDireccion(self, varianzaRoll, varianzaPitch):

        margen = 0.10  # margen en porcentaje
        maximoRoll_Pitch = 90

        margenSup = maximoRoll_Pitch * margen / 100
        margenInf = margenSup * -1

        if margenInf < varianzaPitch < margenSup:
            registro_pitch_estado = IGUAL
        elif varianzaPitch > margenSup:
            registro_pitch_estado = POSITIVO
        elif varianzaPitch < margenInf:
            registro_pitch_estado = NEGATIVO

        if margenInf < varianzaRoll < margenSup:
            registro_roll_estado = IGUAL
        elif varianzaRoll > margenSup:
            registro_roll_estado = POSITIVO
        elif varianzaRoll < margenInf:
            registro_roll_estado = NEGATIVO

        if registro_roll_estado == POSITIVO:
            if registro_pitch_estado == NEGATIVO:
                return "W"
            elif registro_pitch_estado == IGUAL:
                return "NW"
            elif registro_roll_estado == POSITIVO:
                return "N"
        elif registro_roll_estado == NEGATIVO:
            if registro_pitch_estado == NEGATIVO:
                return "S"
            elif registro_pitch_estado == IGUAL:
                return "SE"
            elif registro_roll_estado == POSITIVO:
                return "E"
        elif registro_roll_estado == IGUAL:
            if registro_pitch_estado == NEGATIVO:
                return "SW"
            elif registro_roll_estado == POSITIVO:
                return "NE"

    def registrar_medidas(self):
        ini = -1

        factorMedida = 10
        udSeg = 1
        # Esto quiere decir, "factorMedida" medidas tomadas por "udSeg"
        enum = 0
        aux = "null"
        print("Inicio toma de medidas:")
        try:
            while 1:
                cabecera, segundos = self.get_cabecera()
                if self.tiempo != 0:
                    if enum >= (int(self.tiempo) * factorMedida):
                        break
                sensoresGyro = self.get_gyro()
                accel = self.get_acel()
                gyro = self.get_gyro()
                roll_pitch_yaw = self.get_roll_pitch_yaw()
                yaw = self.conversionRangeDegrees(roll_pitch_yaw.z)
                brujula = self.get_NESW_fromDegrees(yaw)
                vientoFG, varianzaRoll, varianzaPitch, direccion = self.calculoViento(accel, roll_pitch_yaw)
                if direccion == None:
                    direccion = aux
                aux = direccion

                self.file.write(str(enum) +
                                "\t" + cabecera +
                                "\t" + str(gyro[0]) + "\t" + str(gyro[1]) + "\t" + str(gyro[2]) +
                                "\t" + str(accel[0]) + "\t" + str(accel[1]) + "\t" + str(accel[2]) +
                                "\t" + str(round(roll_pitch_yaw.x, 3)) + "\t" + str(
                    round(roll_pitch_yaw.y, 3)) + "\t" + str(round(roll_pitch_yaw.z, 3)) +
                                "\t" + str(brujula) +
                                "\t" + str(vientoFG) + "\t" + str(varianzaRoll) + "\t" + str(
                    varianzaPitch) + "\t" + str(direccion) +
                                "\t" + "gpsLong" + "\t" + "gpsLat" +
                                "\t" + "700" +
                                "\t" + "1000" + "\t" + "1000" + "\t" + "1000" + "\t" + "1000" +
                                "\n")

                enum += 1
                time.sleep(udSeg / factorMedida)

        except KeyboardInterrupt as e:
            print("Parada por interrupcion de teclado.\n")
        print("Fin toma de medidas.\n")

    def cerrar_fichero(self):
        self.file.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        wm = WindMeasure(sys.argv[1])
    else:
        wm = WindMeasure()

    # while True:
    #     roll_pitch_yaw = wm.get_roll_pitch_yaw()
    #     print(roll_pitch_yaw.x,roll_pitch_yaw.y)
    #     print()
    wm.registrar_medidas()
