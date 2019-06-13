import serial
from time import sleep
import os

from Pckg.S1 import FSIA6B
from Pckg.S2.MPU9250 import MPU9250
from Pckg.S2 import mpl3115
from Pckg.S3 import PWM_PCA9685
from Pckg.S2.MPU9250 import MPU6050

if __name__ == '__main__':
    
    #Comunicaciones
    port = serial.Serial("/dev/ttyS0", parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,  baudrate=115200)
    s1_fsia6b = FSIA6B.FSIA6B(port)
    
    #Sensores
    mpu9250 = MPU9250_lib.MPU9250()

    #Motores
    #Establecemos la frecuencia del pwm a 2000Hz (1560Hz en output)
    pwm = PWM_PCA9685.PWM_PCA9685(2000)

    mpu6050Sensor = MPU6050.MPU6050(1,0x68)

    mpu6050Sensor.dmp_initialize()
    mpu6050Sensor.set_DMP_enabled(True)

    entrada = input("Desea calibrar el gyroscopio[1] o cargar la anterior configuración[2]?\nTenga en cuenta que la orientación puede cambiar: ")
    if entrada == '1':
        calibracion = mpu6050Sensor.calibrarGyro()
    elif entrada == '2':
        mpu6050Sensor.setGyroOffset(0.5238688792890147, 2.561511257439358 ,-6.6875060365656696)
    
    barometer = mpl3115.MPL3115()
    barometer.config(True,102200)

    print("Open:", port.is_open)
    port.reset_input_buffer()
    error = 0
    while True:
        try:
            channels = s1_fsia6b.getChannelsFromReceiver()
        except:
            print("ERROR CHANNELS", channels)
            print("Error en Comunicacion                                        COMUNICACION!!!!!!")
            print("Settings:", port.get_settings())

            channels = [1500, 1500, 1000, 1500, 1000, 1000]
            sleep(5)
            error = 1
        
        altimetro = barometer.read_data()
        # Cambiar lectura de mpu9250
        # sensores = mpu9250.readSensoresConCalibracion()
        sensores = mpu6050Sensor.readSensoresConCalibracion()
        pwm.setDutyPWM_Dron(channels,sensores,altimetro['alt'])
        try:
            port.reset_input_buffer()
        except:
            pass