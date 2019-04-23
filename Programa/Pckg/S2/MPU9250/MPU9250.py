# coding: utf-8
## @package MPU9250
#  This is a FaBo9Axis_MPU9250 library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import smbus
import time

## MPU9250 Default I2C slave address
SLAVE_ADDRESS        = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID            = 0x71

''' MPU-9250 Register Addresses '''
## sample rate driver
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR   = 0x1E
WOM_THR        = 0x1F
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B
TEMP_OUT       = 0x41
GYRO_OUT       = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A
PWR_MGMT_1         = 0x6B
PWR_MGMT_2         = 0x6C
FIFO_R_W           = 0x74
WHO_AM_I           = 0x75

## Gyro Full Scale Select 250dps
GFS_250  = 0x00
## Gyro Full Scale Select 500dps
GFS_500  = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03
## Accel Full Scale Select 2G
AFS_2G   = 0x00
## Accel Full Scale Select 4G
AFS_4G   = 0x01
## Accel Full Scale Select 8G
AFS_8G   = 0x02
## Accel Full Scale Select 16G
AFS_16G  = 0x03

# AK8963 Register Addresses
AK8963_ST1        = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN   = 0x00
## One shot data output
AK8963_MODE_ONE    = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ   = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

## smbus
bus = smbus.SMBus(1)

## MPU9250 I2C Controll class
class MPU9250:

    INIgyroX = 0
    INIgyroY = 0
    INIgyroZ = 0
    gyroX = 0
    gyroY = 0
    gyroZ = 0


    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU9250(GFS_250, AFS_2G)
        self.configAK8963(AK8963_MODE_C8HZ, AK8963_BIT_16)

    ## Search Device
    #  @param [in] self The object pointer.
    #  @retval true device connected
    #  @retval false device error
    def searchDevice(self):
        who_am_i = bus.read_byte_data(self.address, WHO_AM_I)
        if(who_am_i == DEVICE_ID):
            return true
        else:
            return false

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self.gres = 250.0/32768.0
        elif gfs == GFS_500:
            self.gres = 500.0/32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0/32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0/32768.0

        if afs == AFS_2G:
            self.ares = 2.0/32768.0
        elif afs == AFS_4G:
            self.ares = 4.0/32768.0
        elif afs == AFS_8G:
            self.ares = 8.0/32768.0
        else: # afs == AFS_16G:
            self.ares = 16.0/32768.0

        # sleep off
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # DLPF_CFG
        bus.write_byte_data(self.address, CONFIG, 0x03)
        # sample rate divider
        bus.write_byte_data(self.address, SMPLRT_DIV, 0x04)
        # gyro full scale select
        bus.write_byte_data(self.address, GYRO_CONFIG, gfs << 3)
        # accel full scale select
        bus.write_byte_data(self.address, ACCEL_CONFIG, afs << 3)
        # A_DLPFCFG
        bus.write_byte_data(self.address, ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    ## Configure AK8963
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self, mode, mfs):
        if mfs == AK8963_BIT_14:
            self.mres = 4912.0/8190.0
        else: #  mfs == AK8963_BIT_16:
            self.mres = 4912.0/32760.0

        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs<<4|mode))
        time.sleep(0.01)

    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval true data is ready
    #  @retval false data is not ready
    def checkDataReady(self):
        drdy = bus.read_byte_data(self.address, INT_STATUS)
        if drdy & 0x01:
            return True
        else:
            return False

    ## Read accelerometer
    #  @param [in] self The object pointer.
    #  @retval x : x-axis data
    #  @retval y : y-axis data
    #  @retval z : z-axis data
    def readAccel(self):
        data = bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.ares, 3)
        y = round(y*self.ares, 3)
        z = round(z*self.ares, 3)

        return {"x":x, "y":y, "z":z}

    ## Read gyro
    #  @param [in] self The object pointer.
    #  @retval x : x-gyro data
    #  @retval y : y-gyro data
    #  @retval z : z-gyro data
    def readGyro(self):
        data = bus.read_i2c_block_data(self.address, GYRO_OUT, 6)

        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x*self.gres, 3)
        y = round(y*self.gres, 3)
        z = round(z*self.gres, 3)

        return {"x":x, "y":y, "z":z}

    ## Read magneto
    #  @param [in] self The object pointer.
    #  @retval x : X-magneto data
    #  @retval y : y-magneto data
    #  @retval z : Z-magneto data
    def readMagnet(self):
        x=0
        y=0
        z=0

        # check data ready
        drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01 :
            data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08)!=0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])

                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)

        return {"x":x, "y":y, "z":z}

    ## Read temperature
    #  @param [out] temperature temperature(degrees C)
    def readTemperature(self):
        data = bus.read_i2c_block_data(self.address, TEMP_OUT, 2)
        temp = self.dataConv(data[1], data[0])

        temp = round((temp / 333.87 + 21.0), 3)
        return temp

    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

    def calibrarGyro(self):
        gyro = self.readGyro()
        self.INIgyroX = round((gyro['x']),3)
        self.INIgyroY = round((gyro['y']),3)
        self.INIgyroZ = round((gyro['z']),3)
    
    def modifyPositionGyro(self):
        gyro = self.readGyro()
        self.gyroX += (round((gyro['x']),3) - self.INIgyroX)
        self.gyroY += (round((gyro['y']),3) - self.INIgyroY)
        self.gyroZ += (round((gyro['z']),3) - self.INIgyroZ)
        self.printActualGyro()

    def printActualGyro(self):
        print("\n")
        print("X:",self.gyroX)
        print("Y:",self.gyroY)
        print("Z:",self.gyroZ)
        print("\n")

    def readSensores(self):
        sensores = dict()
        accel = self.readAccel()
        gyro = self.readGyro()   
        mag = self.readMagnet()
        
        sensores["gyro"] = gyro
        sensores["accel"] = accel
        sensores["mag"] = mag

        return sensores

    def readSensoresConCalibracion(self):
        sensores = dict()
        accel = self.readAccel()
        gyro = self.readGyro()   
        mag = self.readMagnet()
        
        gyro['x']-=self.INIgyroX
        gyro['y']-=self.INIgyroY
        gyro['z']-=self.INIgyroZ

        sensores["gyro"] = gyro
        sensores["accel"] = accel
        sensores["mag"] = mag

        return sensores

    def get_FIFO_count(self):
        data = [0] * 2
        data = self.read_bytes(data, C.MPU6050_RA_FIFO_COUNTH, 2)
        return (data[0] << 8) | data[1]

    def calibrarGyro(self):

        input("Ponme sobre una superficie plana y presione Enter")

        a_roll = 0
        a_pitch = 0
        a_yaw = 0


        old_roll_pitch_yaw = None
        salir = 0
        firstTime = True
        while salir != 3:
            roll_pitch_yaw = self.readSensoresConCalibracion()

            if (firstTime != True):
                diffx = math.fabs(old_roll_pitch_yaw.x - roll_pitch_yaw.x) 
                diffy = math.fabs(old_roll_pitch_yaw.y - roll_pitch_yaw.y) 
                diffz = math.fabs(old_roll_pitch_yaw.z - roll_pitch_yaw.z) 
                print(diffx)
                print(diffy)
                print(diffz)
                salir = 0
                if diffx < 0.2:
                    salir += 1
                if diffy < 0.2:
                    salir += 1
                if diffz < 0.2:
                    salir += 1
            
            old_roll_pitch_yaw = roll_pitch_yaw
            firstTime = False
            time.sleep(1)

        self.x_gyro_offset = roll_pitch_yaw.x
        self.y_gyro_offset = roll_pitch_yaw.y
        self.z_gyro_offset = roll_pitch_yaw.z

        print("Offset establecido en:\n X=", self.x_gyro_offset, "Y=", self.y_gyro_offset, "Z=", self.z_gyro_offset)
        time.sleep(1)
        return {'x':self.x_gyro_offset,'y':self.y_gyro_offset,'z':self.z_gyro_offset}

    def setGyroOffset(self,x,y,z):
        self.x_gyro_offset = x
        self.y_gyro_offset = y
        self.z_gyro_offset = z

    def readSensoresConCalibracion(self):

        while (True):
            FIFO_count = self.get_FIFO_count()
            mpu_int_status = self.get_int_status()
            packet_size = self.DMP_get_FIFO_packet_size()
            FIFO_buffer = [0]*64

            # If overflow is detected by status or fifo count we want to reset
            if (FIFO_count == 1024) or (mpu_int_status & 0x10):
                self.reset_FIFO()
                # print('overflow!')
            # Check if fifo data is ready
            elif (mpu_int_status & 0x02):
                # Wait until packet_size number of bytes are ready for reading, default
                # is 42 bytes
                FIFO_count = self.get_FIFO_count()
                while FIFO_count < packet_size:
                    FIFO_count = self.get_FIFO_count()
                FIFO_buffer = self.get_FIFO_bytes(packet_size)
                accel = self.DMP_get_acceleration_int16(FIFO_buffer)
                quat = self.DMP_get_quaternion_int16(FIFO_buffer)
                grav = self.DMP_get_gravity(quat)
                roll_pitch_yaw = self.DMP_get_euler_roll_pitch_yaw(quat, grav)
                roll_pitch_yaw.x -= self.x_gyro_offset
                roll_pitch_yaw.y -= self.y_gyro_offset
                roll_pitch_yaw.z -= self.z_gyro_offset
                return roll_pitch_yaw

    def get_int_status(self):
        return self.__bus.read_byte_data(self.__dev_id,
                                         C.MPU6050_RA_INT_STATUS)


    def DMP_get_FIFO_packet_size(self):
        return self.__DMP_packet_size #= 42


if __name__ == "__main__":
    gyroscopioBruteData = MPU9250()

    while True:
        # print(gyroscopioBruteData.readMagnet())
        # print(gyroscopioBruteData.readGyro())
        print(gyroscopioBruteData.readMagnet())
        print()
        time.sleep(1)
