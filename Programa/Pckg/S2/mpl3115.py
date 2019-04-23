import smbus
import time
class MPL3115():
    ADDRESS = 0x60
    
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        
        if (self.IIC_Read(0x0c) != 196):
          print("Sensor not detected!")
    def IIC_Read(self,reg):
        return self.i2c.read_byte_data(self.ADDRESS, reg)
    
    def IIC_Write(self,reg,data):
        self.i2c.write_byte_data(self.ADDRESS, reg, data)
            
    def config(self,altitude,barometric_pressure):
        self.altitude = altitude
        if altitude == True:
            self.IIC_Write(0x26, 0xb9)
        else:
            self.IIC_Write(0x26, 0x39)
        
        self.IIC_Write(0x29, 0x80)
        self.IIC_Write(0x13, 0x07)
        
        pressure = barometric_pressure/2
        
        self.IIC_Write(0x14, int(pressure) >> 8)
        self.IIC_Write(0x15, int(pressure) & 0xff)
        
    def read_data(self):
        clock = time.clock()
        out = {'time':time.time()}
        #out={}
        #self.wait_new()
        
        if self.altitude == True:
            m_altitude = self.IIC_Read(0x01)
            c_altitude = self.IIC_Read(0x02)
            l_altitude = float(self.IIC_Read(0x03)>>4)/16.0
            altitude = (m_altitude << 8) | c_altitude
            if altitude > 32768:
                altitude = 0-(65536-altitude)
            out['alt'] = float(altitude) + l_altitude
        else:
            pressure_l = self.IIC_Read(0x03)
            out['pressure']  = self.IIC_Read(0x01) << 10 | self.IIC_Read(0x02) << 2 | pressure_l >> 6
        
        m_temp = self.IIC_Read(0x04) # temp, degrees
        l_temp = float(self.IIC_Read(0x05)>>4)/16.0 #temp, fraction of a degree
        out['temp'] = m_temp + l_temp    
        return out

    def wait_new(self): # todo: add interrupt pin support when we put it in hw.
        while self.IIC_Read(0x12) == False:
            time.sleep(0.5)
 
 
if __name__ == "__main__":
    
    barometer = MPL3115()
    barometer.config(False,102200)
    #while True:
    out = {}
    out = barometer.read_data()
    #barometer.config(True,102200)
    #out2 = {}
    #out2 = barometer.read_data(out2)
    
    print(str(out['time'])+","+str(out['pressure'])+","+str(out['temp'])+ "\n")
        





