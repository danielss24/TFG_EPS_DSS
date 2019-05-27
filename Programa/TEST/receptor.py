import serial
from time import sleep
import os

from Programa.Pckg.S1 import FSIA6B

if __name__ == '__main__':
    
    #Comunicaciones
    port = serial.Serial("/dev/ttyS0", parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,  baudrate=115200, timeout=7.0)
    s1_fsia6b = FSIA6B.FSIA6B(port)
    
    while True:
        try:
            port.reset_input_buffer()
        except:
            pass
        
        try:
            channels = s1_fsia6b.getChannelsFromReceiver(32)
        except:
            print("Error en Comunicacion")
            channels = [1500, 1500, 1000, 1500, 1000, 1000]
            error = 1

        print(channels)
        
    