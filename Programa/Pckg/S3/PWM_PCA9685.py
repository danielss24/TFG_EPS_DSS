
from __future__ import division
import time
import math

FACTOR_AJUSTE = 50

# Import the PCA9685 module.
import Adafruit_PCA9685

class PWM_PCA9685(object):
    # Initialise the PCA9685 using the default address (0x40).
    pwm = None
    altura = -1
    activoControlAltura = False
    def __init__(self, frec = 0):
        self.pwm = Adafruit_PCA9685.PCA9685(0x44)
        if frec != 0:
            self.pwm.set_pwm_freq(frec)

    def setFrecuencia(self, frec=2000):
        """
        Establece la frecuencia al pwm

        Args:
            frec: frecuencia a establecer, por defecto a 2000
        """
        self.pwm.set_pwm_freq(frec)

    def getDutyPWMPercentage_single(self,frec):
        """
        Devuelve el porcentaje de la señal del mando recibida

        Args:
            frec: señal recibida del mando (entre 1000 y 2000)

        Return:
            Devuelve el porcentaje de la señal
        """
        return ((frec - 1000)/10)

    def getRealInputPWM_single(self,frec,min=3296):
        """
        Recibe la señal del mando, comprendida entre 1000 y 2000 y devuelve la señal a establecer en el pwm

        Args:
            frec: señal del mando
            min: señal minima de pwm para 0%, por defecto en su minimo valor
        """
        return int((min-(frec - 1000)*798/1000))

    def getRealInputPWM_multiple(self,channel,min):
        """
        Devuelve el valor a introducir en el PWM a partir de una lista de señales del mando

        Args:
            channel: señales recibidas del mando
            min: valor minimo de pwm

        Return:
            Devuelve la frecuencia de cada canal
        """
        channelFrec = []
        for each in channel:
            channelFrec.append(self.getRealInputPWM_single(each,min))
        return channelFrec

    def setDutyPWM_singleChannel(self,channel, frec, max=4095):
        """
        Not used yet
        """
        self.pwm.set_pwm(channel, frec, max)

    def setDutyPWM_multipleChannel(self,channels, frec, max=4095):
        """
        Establece la señal de los PWM

        Args:

            channels: canales donde establecer el pwm                                                                                                                                                                                                                                                                                                                                                                                                                                                   
            frec: frecuencia de los canales
        """

        # for enum, each in enumerate(channels):
        #     self.pwm.set_pwm(each, frec[enum], max)

        for enum, each in enumerate(channels):
            self.pwm.set_pwm(each, frec[enum], max)

    def setDutyPWM_Dron(self,channelsFrec, sensores, altimetro, min = 3296):

        multChannel=[0,1,2,3]

        self.diagnosticateMotorsFrec(multChannel,channelsFrec, sensores, altimetro)
    
    def isArmed(self,frec):
        
        try:
            if frec[5]>=1500:
                return True
            else:
                return False
        except:
            return False

    def apagarPWM(self,min=3296,max=4095):

        for each in [0,1,2,3,4,5,6,7]:
            self.pwm.set_pwm(each, min, max)

    def controllerMotor(self,channelsFrec):
        potenciaMotores = [100,100,100,100]
        channelsFrecCPY = channelsFrec
        for i, each in enumerate(channelsFrecCPY[:4]):
            each = ((each-1000)/10 -50)
            # print("Con i:", i ,each)
            if i == 0:
                #Modificador giratorio
                # print("ANULADO")
                if each < -0.5:
                    each *= 2
                # elif each > -0.5 and each < 0.5:
                #     print("No hace nada")
                elif each > 0.5:
                    each = (each-50)*2

            elif i == 1: #Modificador desplazamiento hacia delante/atras

                if each < -0.5: #Detras
                    each = math.fabs(each*2)
                    modificador = (100 - each)/100
                    potenciaMotores[1] *= modificador
                    potenciaMotores[2] *= modificador
                # elif each > -0.5 and each < 0.5:
                #     print("No hace nada")
                elif each > 0.5: #Delante
                    each = math.fabs(each*2)
                    modificador = (100 - each)/100
                    potenciaMotores[0] *= modificador
                    potenciaMotores[3] *= modificador
                
                # print("Modificador delante/detras", potenciaMotores)
            elif i == 2:
                each = (each+50)/100
                for i in range(len(potenciaMotores)):
                    potenciaMotores[i]*=each
            elif i == 3:
                #Modificador desplazamiento hacia izq/drch
                if each < -0.5:
                    each = math.fabs(each*2)
                    modificador = (100 - each)/100
                    potenciaMotores[2] *= modificador
                    potenciaMotores[3] *= modificador
                # elif each > -0.5 and each < 0.5:
                #     print("No hace nada")
                elif each > 0.5:
                    each = math.fabs(each*2)
                    modificador = (100 - each)/100
                    potenciaMotores[0] *= modificador
                    potenciaMotores[1] *= modificador
                # print("Modificador izq/drch", potenciaMotores)  
                
        return potenciaMotores
    
    def powerMotorSensors(self,potenciaMotores, sensores, altimetro):

        print("potenciaMotores", potenciaMotores)
        # print("ROLL",sensores.x)
        # print("PITCH",sensores.y)

        potencia = potenciaMotores
        
        if sensores.x > 0:
            ajuste = math.fabs(sensores.x) * 100/90 / FACTOR_AJUSTE
            ajuste0 = potencia[0]+ajuste
            ajuste1 = potencia[1]+ajuste
            if ajuste0 > 100 or ajuste1 > 100:
                minimo = min(ajuste0,ajuste1)
                ajusteContrario = ajuste - minimo

                potencia[0] += minimo
                potencia[1] += minimo

                potencia[2] -= ajusteContrario
                potencia[3] -= ajusteContrario


            else:
                potencia[0] += ajuste
                potencia[1] += ajuste

        else:
            ajuste = math.fabs(sensores.x) * 100/90 / FACTOR_AJUSTE
            ajuste0 = potencia[2]+ajuste
            ajuste1 = potencia[3]+ajuste
            if ajuste0 > 100 or ajuste1 > 100:
                minimo = min(ajuste0,ajuste1)
                ajusteContrario = ajuste - minimo

                potencia[2] += minimo
                potencia[3] += minimo

                potencia[0] -= ajusteContrario
                potencia[1] -= ajusteContrario


            else:
                potencia[2] += ajuste
                potencia[3] += ajuste

        if sensores.y > 0:
            ajuste = math.fabs(sensores.y) * 100/90 / FACTOR_AJUSTE
            ajuste0 = potencia[1]+ajuste
            ajuste1 = potencia[2]+ajuste
            if ajuste0 > 100 or ajuste1 > 100:
                minimo = min(ajuste0,ajuste1)
                ajusteContrario = ajuste - minimo

                potencia[1] += minimo
                potencia[2] += minimo

                potencia[0] -= ajusteContrario
                potencia[3] -= ajusteContrario


            else:
                potencia[1] += ajuste
                potencia[2] += ajuste

        else:
            ajuste = math.fabs(sensores.y) * 100/90 / FACTOR_AJUSTE
            ajuste0 = potencia[0]+ajuste
            ajuste1 = potencia[3]+ajuste
            if ajuste0 > 100 or ajuste1 > 100:
                minimo = min(ajuste0,ajuste1)
                ajusteContrario = ajuste - minimo

                potencia[0] += minimo
                potencia[3] += minimo

                potencia[1] -= ajusteContrario
                potencia[2] -= ajusteContrario


            else:
                potencia[0] += ajuste
                potencia[3] += ajuste

        # print("altimetro",altimetro)
        if self.altura != -1:
            ajuste = (altimetro - self.altura)/100
            potencia[0] = potencia[0] + potencia[0]*ajuste
            potencia[1] = potencia[1] + potencia[1]*ajuste
            potencia[2] = potencia[2] + potencia[2]*ajuste
            potencia[3] = potencia[3] + potencia[3]*ajuste

        potencia[0] = round(potencia[0],3)
        potencia[1] = round(potencia[1],3)
        potencia[2] = round(potencia[2],3)
        potencia[3] = round(potencia[3],3)
        print("potencia",potencia)

        return potencia
        

    def diagnosticateMotorsFrec(self,multChannel,channelsFrec,sensores, altimetro):

        # print(channelsFrec)
        if self.isArmed(channelsFrec) == True:
                              
            if channelsFrec[4]==2000:
                if self.activoControlAltura == False:
                    self.altura = altimetro
                    self.activoControlAltura = True
            else:
                self.altura = -1
                self.activoControlAltura = False

            # print("Altura",self.altura)
            potenciaMotores = self.controllerMotor(channelsFrec)
            potenciaMotoresSensores = self.powerMotorSensors(potenciaMotores,sensores, altimetro)                       
            frecs = self.potenciaToFrec(potenciaMotoresSensores)
            self.setDutyPWM_multipleChannel(multChannel,frecs)
        else:
            self.apagarPWM()

    def potenciaToFrec(self,potencia):

        frecs = []
        for i,each in enumerate(potencia):
            if each < 0:
                each = 0
            elif each > 100:
                each = 100
            frecs.append(int(self.getRealInputPWM_single(int((1000*each/100)+1000))))
        
        return frecs

    
