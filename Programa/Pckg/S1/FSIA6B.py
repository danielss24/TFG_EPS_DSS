import sys
import os
import struct


class FSIA6B(object):
    port = 0
    channels = []

    def __init__(self, port):
        self.port = port

    def tratamientoFSIA6B(read):
        # Tratamiento de cadena
        # Input: linea leida
        index = read.find("@")
        cadena = read[index - 1:]
        cadena2 = read[:index - 1]
        cadena += cadena2

        cadena = cadena.replace("\n", "")
        cadena = cadena.replace("'", "")
        cadena = cadena.replace("\\x", "")
        debugPrint(10, 10, cadena)

        channels = []
        [channels.append(cadena[i - 4:i]) for i in range(len(cadena), 4, -4)]
        return channels

    def debugPrint(y, x, text):
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()

    def debugPrintFSIA6B(channels):

        espacio = 0
        for enum, i in enumerate(channels[:8]):
            if enum == 0:
                debugPrint(27, 10, "FS6IA6B")
            else:
                channel = "Channel " + str(enum)
                debugPrint(espacio, 12, channel)
                debugPrint(espacio + 3, 14, i)
                try:
                    debugPrint(espacio + 3, 15, int(i, 16))
                except ValueError:
                    debugPrint(espacio + 3, 16, "error")
                espacio += (len(channel) + 2)
        debugPrint(espacio + 3, 14, channels[-1])

    def getChannelsFromReceiver(self):

        rcv = self.port.readline(32)

        line = repr(rcv)
        line = line.replace("'", "")
        line = line.replace('"', "")

        index = line.find("@")
        cadena = line[index - 1:]
        cadena2 = line[:index - 1]
        cadena += cadena2

        line = cadena

        line = line.replace("\n", "")

        line = line.replace(" ", "\\x20")
        line = line.replace("@", "\\x40")
        line = line.split("\\x")
        cadena = ""
        for enum, i in enumerate(line):
            cadena = cadena + " " + str(len(i))
            if len(i) == 0:
                del line[len(i)]
            tam = 2 - len(i)
            if tam != 2:
                for j in range(tam, 0):
                    line[enum] = line[enum].replace(i[j], "")
                    insertar = hex(ord(i[j]))
                    insertar = insertar.replace("0x", "")
                    line.insert(enum + 1, insertar)

        channels = []

        for i in range(0, len(line) - 1, 2):
            chan = line[i + 1] + line[i]
            channels.append(chan)

        valores = []
        for each in channels[1:7]:
            try:
                if int(each, 16) <= 2500 and int(each, 16) >= 900:
                    valores.append(int(each, 16))
            except ValueError:
                valores.append(0)

        if len(valores) == 6:
            self.channels = valores

        return self.channels

    def printTest(self):
        print("Print test FSIA6B")


def convertChannelsToPercentage(channels, min=1000, max=2000):
    channels = (channels - min)/10
    return channels
