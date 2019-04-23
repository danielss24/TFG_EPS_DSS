__author__ = 'Geir Istad'
"""
MPU6050 Python I2C Class
Copyright (c) 2015 Geir Istad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Code based on
I2Cdev library collection - MPU6050 I2C device class
by Jeff Rowberg <jeff@rowberg.net>
============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2012 Jeff Rowberg
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
"""

import math
import ctypes
import time
import smbus
import csv
from Pckg.S2.MPU9250.MPUConstants import MPUConstants as C
from Pckg.S2.MPU9250.Quaternion import Quaternion as Q
from Pckg.S2.MPU9250.Quaternion import XYZVector as V
# from MPUConstants import MPUConstants as C
# from Quaternion import Quaternion as Q
# from Quaternion import XYZVector as V


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


class MPU6050:
    __buffer = [0] * 14
    __debug = False
    __DMP_packet_size = 0
    __dev_id = 0
    __bus = None

    x_gyro_offset = 0
    y_gyro_offset = 0
    z_gyro_offset = 0

    mres = 0
    magXcoef = 0
    magYcoef = 0
    magZcoef = 0

    address=0x68

    def __init__(self, a_bus=1, a_address=C.MPU6050_DEFAULT_ADDRESS,
                 a_xAOff=None, a_yAOff=None, a_zAOff=None, a_xGOff=None,
                 a_yGOff=None, a_zGOff=None, a_debug=False):
        self.__dev_id = a_address
        # Connect to num 1 SMBus
        self.__bus = smbus.SMBus(a_bus)
        # Set clock source to gyro
        self.set_clock_source(C.MPU6050_CLOCK_PLL_XGYRO)
        # # Set accelerometer range
        self.set_full_scale_accel_range(C.MPU6050_ACCEL_FS_2)
        # # Set gyro range
        self.set_full_scale_gyro_range(C.MPU6050_GYRO_FS_250)
        # # Take the MPU out of time.sleep mode
        self.wake_up()

        self.gres = 250.0/32768.0
        self.ares = 2.0/32768.0

        self.dmp_initialize()
        self.set_DMP_enabled(True)

        # self.configMPU9250(GFS_250, AFS_2G)
        # self.configAK8963(AK8963_MODE_C8HZ, AK8963_BIT_16)


        # Set offsets
        # if a_xAOff:
        #     self.set_x_accel_offset(a_xAOff)
        # if a_yAOff:
        #     self.set_y_accel_offset(a_yAOff)
        # if a_zAOff:
        #     self.set_z_accel_offset(a_zAOff)
        # if a_xGOff:
        #     self.set_x_gyro_offset(a_xGOff)
        # if a_yGOff:
        #     self.set_y_gyro_offset(a_yGOff)
        # if a_zGOff:
        #     self.set_z_gyro_offset(a_zGOff)
        self.__debug = a_debug

    ## Configure AK8963
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self, mode, mfs):
        if mfs == AK8963_BIT_14:
            self.mres = 4912.0/8190.0
        else: #  mfs == AK8963_BIT_16:
            self.mres = 4912.0/32760.0

        self.__bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        self.__bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = self.__bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        self.__bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        self.__bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs<<4|mode))
        time.sleep(0.01)

    # Core bit and byte operations
    def read_bit(self, a_reg_add, a_bit_position):
        return self.read_bits(a_reg_add, a_bit_position, 1)

    def write_bit(self, a_reg_add, a_bit_num, a_bit):
        byte = self.__bus.read_byte_data(self.__dev_id, a_reg_add)
        if a_bit:
            byte |= 1 << a_bit_num
        else:
            byte &= ~(1 << a_bit_num)
        self.__bus.write_byte_data(
            self.__dev_id, a_reg_add, ctypes.c_int8(byte).value)

    def read_bits(self, a_reg_add, a_bit_start, a_length):
        byte = self.__bus.read_byte_data(self.__dev_id, a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        byte &= mask
        byte >>= a_bit_start - a_length + 1
        return byte

    def write_bits(self, a_reg_add, a_bit_start, a_length, a_data):
        byte = self.__bus.read_byte_data(self.__dev_id, a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        # Get data in position and zero all non-important bits in data
        a_data <<= a_bit_start - a_length + 1
        a_data &= mask
        # Clear all important bits in read byte and combine with data
        byte &= ~mask
        byte = byte | a_data
        # Write the data to the I2C device
        self.__bus.write_byte_data(
            self.__dev_id, a_reg_add, ctypes.c_int8(byte).value)

    def read_memory_byte(self):
        return self.__bus.read_byte_data(self.__dev_id, C.MPU6050_RA_MEM_R_W)

    def read_bytes(self, a_data_list, a_address, a_length):
        if a_length > len(a_data_list):
            print('read_bytes, length of passed list too short')
            return a_data_list
        # Attempt to use the built in read bytes function in the adafruit lib
        # a_data_list = self.__bus.read_i2c_block_data(self.__dev_id, a_address,
        #                                             a_length)
        # Attempt to bypass adafruit lib
        #a_data_list = self.__mpu.__bus.read_i2c_block_data(0x68, a_address, a_length)
        #print('data' + str(a_data_list))
        for x in range(0, a_length):
            a_data_list[x] = self.__bus.read_byte_data(self.__dev_id,
                                                       a_address + x)
        return a_data_list

    def write_memory_block(self, a_data_list, a_data_size, a_bank, a_address,
                           a_verify):
        success = True
        self.set_memory_bank(a_bank)
        self.set_memory_start_address(a_address)

        # For each a_data_item we want to write it to the board to a certain
        # memory bank and address
        for i in range(0, a_data_size):
            # Write each data to memory
            self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_MEM_R_W,
                                       a_data_list[i])

            if a_verify:
                self.set_memory_bank(a_bank)
                self.set_memory_start_address(a_address)
                verify_data = self.__bus.read_byte_data(self.__dev_id,
                                                        C.MPU6050_RA_MEM_R_W)
                if verify_data != a_data_list[i]:
                    success = False

            # If we've filled the bank, change the memory bank
            if a_address == 255:
                a_address = 0
                a_bank += 1
                self.set_memory_bank(a_bank)
            else:
                a_address += 1

            # Either way update the memory address
            self.set_memory_start_address(a_address)

        return success

    def wake_up(self):
        self.write_bit(
            C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_SLEEP_BIT, 0)

    def set_clock_source(self, a_source):
        self.write_bits(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_CLKSEL_BIT,
                        C.MPU6050_PWR1_CLKSEL_LENGTH, a_source)

    def set_full_scale_gyro_range(self, a_data):
        self.write_bits(C.MPU6050_RA_GYRO_CONFIG,
                        C.MPU6050_GCONFIG_FS_SEL_BIT,
                        C.MPU6050_GCONFIG_FS_SEL_LENGTH, a_data)

    def set_full_scale_accel_range(self, a_data):
        self.write_bits(C.MPU6050_RA_ACCEL_CONFIG,
                        C.MPU6050_ACONFIG_AFS_SEL_BIT,
                        C.MPU6050_ACONFIG_AFS_SEL_LENGTH, a_data)

    def reset(self):
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1,
                       C.MPU6050_PWR1_DEVICE_RESET_BIT, 1)

    def set_sleep_enabled(self, a_enabled):
        set_bit = 0
        if a_enabled:
            set_bit = 1
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1,
                       C.MPU6050_PWR1_SLEEP_BIT, set_bit)

    def set_memory_bank(self, a_bank, a_prefetch_enabled=False,
                        a_user_bank=False):
        a_bank &= 0x1F
        if a_user_bank:
            a_bank |= 0x20
        if a_prefetch_enabled:
            a_bank |= 0x20
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_BANK_SEL, a_bank)

    def set_memory_start_address(self, a_address):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_MEM_START_ADDR, a_address)

    def get_x_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_XG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_x_gyro_offset_TC(self, a_offset):
        self.write_bits(C.MPU6050_RA_XG_OFFS_TC,
                        C.MPU6050_TC_OFFSET_BIT,
                        C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def get_y_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_YG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_y_gyro_offset_TC(self, a_offset):
        self.write_bits(C.MPU6050_RA_YG_OFFS_TC,
                        C.MPU6050_TC_OFFSET_BIT,
                        C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def get_z_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_ZG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_z_gyro_offset_TC(self, a_offset):
        self.write_bits(C.MPU6050_RA_ZG_OFFS_TC,
                        C.MPU6050_TC_OFFSET_BIT,
                        C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def set_slave_address(self, a_num, a_address):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_I2C_SLV0_ADDR + a_num * 3, a_address)

    def set_I2C_master_mode_enabled(self, a_enabled):
        bit = 0
        if a_enabled:
            bit = 1
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_I2C_MST_EN_BIT, bit)

    def reset_I2C_master(self):
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_I2C_MST_RESET_BIT, 1)

    def write_prog_memory_block(self, a_data_list, a_data_size, a_bank=0,
                                a_address=0, a_verify=True):
        return self.write_memory_block(a_data_list, a_data_size, a_bank,
                                       a_address, a_verify)

    def write_DMP_configuration_set(self, a_data_list, a_data_size):
        index = 0
        while index < a_data_size:
            bank = a_data_list[index]
            offset = a_data_list[index + 1]
            length = a_data_list[index + 2]
            index += 3
            success = False

            # Normal case
            if length > 0:
                data_selection = list()
                for subindex in range(0, length):
                    data_selection.append(a_data_list[index + subindex])
                success = self.write_memory_block(data_selection, length, bank,
                                                  offset, True)
                index += length
            # Special undocumented case
            else:
                special = a_data_list[index]
                index += 1
                if special == 0x01:
                    # TODO Figure out if write8 can return True/False
                    success = self.__bus.write_byte_data(
                        self.__dev_id, C.MPU6050_RA_INT_ENABLE, 0x32)

            if success == False:
                # TODO implement error messagemajigger
                return False
                pass
        return True

    def write_prog_dmp_configuration(self, a_data_list, a_data_size):
        return self.write_DMP_configuration_set(a_data_list, a_data_size)

    def set_int_enable(self, a_enabled):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_INT_ENABLE, a_enabled)

    def set_rate(self, a_rate):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_SMPLRT_DIV, a_rate)

    def set_external_frame_sync(self, a_sync):
        self.write_bits(C.MPU6050_RA_CONFIG,
                        C.MPU6050_CFG_EXT_SYNC_SET_BIT,
                        C.MPU6050_CFG_EXT_SYNC_SET_LENGTH, a_sync)

    def set_DLF_mode(self, a_mode):
        self.write_bits(C.MPU6050_RA_CONFIG, C.MPU6050_CFG_DLPF_CFG_BIT,
                        C.MPU6050_CFG_DLPF_CFG_LENGTH, a_mode)

    def get_DMP_config_1(self):
        return self.__bus.read_byte_data(self.__dev_id, C.MPU6050_RA_DMP_CFG_1)

    def set_DMP_config_1(self, a_config):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_DMP_CFG_1, a_config)

    def get_DMP_config_2(self):
        return self.__bus.read_byte_data(self.__dev_id, C.MPU6050_RA_DMP_CFG_2)

    def set_DMP_config_2(self, a_config):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_DMP_CFG_2, a_config)

    def set_OTP_bank_valid(self, a_enabled):
        bit = 0
        if a_enabled:
            bit = 1
        self.write_bit(C.MPU6050_RA_XG_OFFS_TC,
                       C.MPU6050_TC_OTP_BNK_VLD_BIT, bit)

    def get_OTP_bank_valid(self):
        return self.read_bit(C.MPU6050_RA_XG_OFFS_TC,
                             C.MPU6050_TC_OTP_BNK_VLD_BIT)

    def set_motion_detection_threshold(self, a_threshold):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_MOT_THR, a_threshold)

    def set_zero_motion_detection_threshold(self, a_threshold):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_ZRMOT_THR, a_threshold)

    def set_motion_detection_duration(self, a_duration):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_MOT_DUR, a_duration)

    def set_zero_motion_detection_duration(self, a_duration):
        self.__bus.write_byte_data(
            self.__dev_id, C.MPU6050_RA_ZRMOT_DUR, a_duration)

    def set_FIFO_enabled(self, a_enabled):
        bit = 0
        if a_enabled:
            bit = 1
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_FIFO_EN_BIT, bit)

    def set_DMP_enabled(self, a_enabled):
        bit = 0
        if a_enabled:
            bit = 1
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_DMP_EN_BIT, bit)

    def reset_DMP(self):
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_DMP_RESET_BIT, True)

    def dmp_initialize(self):
        # Reset the MPU
        self.reset()
        # time.Sleep a bit while resetting
        time.sleep(50 / 1000)
        # Disable time.sleep mode
        self.set_sleep_enabled(0)

        # get MPU hardware revision
        if self.__debug:
            print('Selecting user bank 16')
        self.set_memory_bank(0x10, True, True)

        if self.__debug:
            print('Selecting memory byte 6')
        self.set_memory_start_address(0x6)

        if self.__debug:
            print('Checking hardware revision')
        HW_revision = self.read_memory_byte()
        if self.__debug:
            print('Revision @ user[16][6] = ' + hex(HW_revision))

        if self.__debug:
            print('Resetting memory bank selection to 0')
        self.set_memory_bank(0)

        # check OTP bank valid
        # TODO Find out what OTP is
        OTP_valid = self.get_OTP_bank_valid()
        if self.__debug:
            if OTP_valid:
                print('OTP bank is valid')
            else:
                print('OTP bank is invalid')

        # get X/Y/Z gyro offsets
        if self.__debug:
            print('Reading gyro offet TC values')
        x_g_offset_TC = self.get_x_gyro_offset_TC()
        y_g_offset_TC = self.get_y_gyro_offset_TC()
        z_g_offset_TC = self.get_z_gyro_offset_TC()
        if self.__debug:
            print("X gyro offset = ", repr(x_g_offset_TC))
            print("Y gyro offset = ", repr(y_g_offset_TC))
            print("Z gyro offset = ", repr(z_g_offset_TC))

        # setup weird slave stuff (?)
        
        # if self.__debug:
        #     print('Setting slave 0 address to 0x7F')
        # self.set_slave_address(0, 0x7F)
        # if self.__debug:
        #     print('Disabling I2C Master mode')
        # self.set_I2C_master_mode_enabled(True)
        # if self.__debug:
        #     print('Setting slave 0 address to 0x68 (self)')
        # self.set_slave_address(0, 0x68)
        # if self.__debug:
        #     print('Resetting I2C Master control')
        # self.reset_I2C_master()
        # Wait a bit for the device to register the changes
        # time.sleep(20 / 1000)

        # load DMP code into memory banks
        if self.__debug:
            print('Writing DMP code to MPU memory banks ' +
                  repr(C.MPU6050_DMP_CODE_SIZE) + ' bytes')
        if self.write_prog_memory_block(C.dmpMemory, C.MPU6050_DMP_CODE_SIZE):
            # TODO Check if we've actually verified this
            if self.__debug:
                print('Success! DMP code written and verified')

            # Write DMP configuration
            if self.__debug:
                print('Writing DMP configuration to MPU memory banks ' +
                      repr(C.MPU6050_DMP_CONFIG_SIZE) + ' bytes in config')
            if self.write_prog_dmp_configuration(C.dmpConfig,
                                                 C.MPU6050_DMP_CONFIG_SIZE):
                if self.__debug:
                    print('Success! DMP configuration written and verified.')
                    print('Setting clock source to Z gyro')
                self.set_clock_source(C.MPU6050_CLOCK_PLL_ZGYRO)

                if self.__debug:
                    print('Setting DMP and FIFO_OFLOW interrupts enabled')
                self.set_int_enable(0x12)

                if self.__debug:
                    print('Setting sample rate to 200Hz')
                self.set_rate(4)

                if self.__debug:
                    print('Setting external frame sync to TEMP_OUT_L[0]')
                self.set_external_frame_sync(C.MPU6050_EXT_SYNC_TEMP_OUT_L)

                if self.__debug:
                    print('Setting DLPF bandwidth to 42Hz')
                self.set_DLF_mode(C.MPU6050_DLPF_BW_42)

                if self.__debug:
                    print('Setting gyro sensitivity to +/- 2000 deg/sec')
                self.set_full_scale_gyro_range(C.MPU6050_GYRO_FS_2000)

                if self.__debug:
                    print('Setting DMP configuration bytes (function unknown)')
                self.set_DMP_config_1(0x03)
                self.set_DMP_config_2(0x00)

                if self.__debug:
                    print('Clearing OTP Bank flag')
                self.set_OTP_bank_valid(False)

                if self.__debug:
                    print('Setting X/Y/Z gyro offset TCs to previous values')
                self.set_x_gyro_offset_TC(x_g_offset_TC)
                self.set_y_gyro_offset_TC(y_g_offset_TC)
                self.set_z_gyro_offset_TC(z_g_offset_TC)

                # Uncomment this to zero offsets when dmp_initialize is called
                # if self.__debug:
                #    print('Setting X/Y/Z gyro user offsets to zero')
                # self.set_x_gyro_offset(0)
                # self.set_y_gyro_offset(0)
                # self.set_z_gyro_offset(0)

                if self.__debug:
                    print('Writing final memory update 1/7 (function unknown)')
                pos = 0
                j = 0
                dmp_update = [0] * 16
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Writing final memory update 2/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Resetting FIFO')
                self.reset_FIFO()

                if self.__debug:
                    print('Reading FIFO count')
                FIFO_count = self.get_FIFO_count()

                if self.__debug:
                    print('FIFO count: ' + repr(FIFO_count))

                if self.__debug:
                    print('Getting FIFO buffer')
                FIFO_buffer = [0] * 128
                FIFO_buffer = self.get_FIFO_bytes(FIFO_count)

                if self.__debug:
                    print('Setting motion detection threshold to 2')
                self.set_motion_detection_threshold(2)

                if self.__debug:
                    print('Setting zero-motion detection threshold to 156')
                self.set_zero_motion_detection_threshold(156)

                if self.__debug:
                    print('Setting motion detection duration to 80')
                self.set_motion_detection_duration(80)

                if self.__debug:
                    print('Setting zero-motion detection duration to 0')
                self.set_zero_motion_detection_duration(0)

                if self.__debug:
                    print('Resetting FIFO')
                self.reset_FIFO()

                if self.__debug:
                    print('Enabling FIFO')
                self.set_FIFO_enabled(True)

                if self.__debug:
                    print('Enabling DMP')
                self.set_DMP_enabled(True)

                if self.__debug:
                    print('Resetting DMP')
                self.reset_DMP()

                if self.__debug:
                    print('Writing final memory update 3/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Writing final memory update 4/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Writing final memory update 5/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Waiting for FIFO count > 2')
                FIFO_count = self.get_FIFO_count()
                while FIFO_count < 3:
                    FIFO_count = self.get_FIFO_count()

                if self.__debug:
                    print('Current FIFO count = ' + repr(FIFO_count))
                    print('Reading FIFO data')
                FIFO_buffer = self.get_FIFO_bytes(FIFO_count)

                if self.__debug:
                    print('Reading interrupt status')
                MPU_int_status = self.get_int_status()

                if self.__debug:
                    print('Current interrupt status = ' + hex(MPU_int_status))
                    print('Writing final memory update 6/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('Waiting for FIFO count > 2')
                FIFO_count = self.get_FIFO_count()
                while FIFO_count < 3:
                    FIFO_count = self.get_FIFO_count()

                if self.__debug:
                    print('Current FIFO count = ' + repr(FIFO_count))
                    print('Reading FIFO count')
                FIFO_buffer = self.get_FIFO_bytes(FIFO_count)

                if self.__debug:
                    print('Reading interrupt status')
                MPU_int_status = self.get_int_status()

                if self.__debug:
                    print('Current interrupt status = ' + hex(MPU_int_status))
                    print('Writing final memory update 7/7 (function unknown)')
                j = 0
                while (j < 4) or (j < dmp_update[2] + 3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j += 1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1], True)

                if self.__debug:
                    print('DMP is good to go! Finally.')
                    print('Disabling DMP (you turn it on later)')
                self.set_DMP_enabled(False)

                if self.__debug:
                    print('Setting up internal 42 byte DMP packet buffer')
                self.__DMP_packet_size = 42

                if self.__debug:
                    print(
                        'Resetting FIFO and clearing INT status one last time')
                self.reset_FIFO()
                self.get_int_status()

            else:
                if self.__debug:
                    print('Configuration block loading failed')
                return 2

        else:
            if self.__debug:
                print('Main binary block loading failed')
            return 1

        if self.__debug:
            print('DMP initialization was successful')
        return 0

    # Acceleration and gyro offset setters and getters
    def set_x_accel_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_XA_OFFS_H,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_XA_OFFS_L_TC,
                                   ctypes.c_int8(a_offset).value)

    def set_y_accel_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_YA_OFFS_H,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_YA_OFFS_L_TC,
                                   ctypes.c_int8(a_offset).value)

    def set_z_accel_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_ZA_OFFS_H,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_ZA_OFFS_L_TC,
                                   ctypes.c_int8(a_offset).value)

    def set_x_gyro_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_XG_OFFS_USRH,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_XG_OFFS_USRL,
                                   ctypes.c_int8(a_offset).value)

    def set_y_gyro_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_YG_OFFS_USRH,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_YG_OFFS_USRL,
                                   ctypes.c_int8(a_offset).value)

    def set_z_gyro_offset(self, a_offset):
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_ZG_OFFS_USRH,
                                   ctypes.c_int8(a_offset >> 8).value)
        self.__bus.write_byte_data(self.__dev_id, C.MPU6050_RA_ZG_OFFS_USRL,
                                   ctypes.c_int8(a_offset).value)

    # Main interfacing functions to get raw data from MPU
    def get_acceleration(self):
        raw_data = self.__bus.read_i2c_block_data(self.__dev_id,
                                                  C.MPU6050_RA_ACCEL_XOUT_H, 6)
        accel = [0] * 3
        accel[0] = ctypes.c_int16(raw_data[0] << 8 | raw_data[1]).value
        accel[1] = ctypes.c_int16(raw_data[2] << 8 | raw_data[3]).value
        accel[2] = ctypes.c_int16(raw_data[4] << 8 | raw_data[5]).value
        return accel

    def get_accelerationV2(self):
        raw_data = self.__bus.read_i2c_block_data(self.__dev_id,C.MPU6050_RA_ACCEL_XOUT_H, 6)
        accel = [0] * 3
        accel[0] = self.dataConv(raw_data[1],raw_data[0]) * self.ares
        accel[1] = self.dataConv(raw_data[3],raw_data[2]) * self.ares
        accel[2] = self.dataConv(raw_data[5],raw_data[4]) * self.ares
        return accel

    def get_rotation(self):
        raw_data = self.__bus.read_i2c_block_data(self.__dev_id,
                                                  C.MPU6050_RA_GYRO_XOUT_H, 6)
        gyro = [0] * 3
        gyro[0] = ctypes.c_int16(raw_data[0] << 8 | raw_data[1]).value
        gyro[1] = ctypes.c_int16(raw_data[2] << 8 | raw_data[3]).value
        gyro[2] = ctypes.c_int16(raw_data[4] << 8 | raw_data[5]).value
        return gyro

    def get_rotationV2(self):
        raw_data = self.__bus.read_i2c_block_data(self.__dev_id,
                                                  C.MPU6050_RA_GYRO_XOUT_H, 6)
        gyro = [0] * 3
        gyro[0] = self.dataConv(raw_data[0],raw_data[1]) * self.gres
        gyro[1] = self.dataConv(raw_data[2],raw_data[3]) * self.gres
        gyro[2] = self.dataConv(raw_data[4],raw_data[5]) * self.gres
        return gyro


    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

    # Interfacing functions to get data from FIFO buffer
    def DMP_get_FIFO_packet_size(self):
        return self.__DMP_packet_size

    def reset_FIFO(self):
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_FIFO_RESET_BIT, True)

    def get_FIFO_count(self):
        data = [0] * 2
        data = self.read_bytes(data, C.MPU6050_RA_FIFO_COUNTH, 2)
        return (data[0] << 8) | data[1]

    def get_FIFO_bytes(self, a_FIFO_count):
        return_list = list()
        for index in range(0, a_FIFO_count):
            return_list.append(self.__bus.read_byte_data(self.__dev_id,C.MPU6050_RA_FIFO_R_W))
        return return_list

    def get_int_status(self):
        return self.__bus.read_byte_data(self.__dev_id,
                                         C.MPU6050_RA_INT_STATUS)

    # Data retrieval from received FIFO buffer
    def DMP_get_quaternion_int16(self, a_FIFO_buffer):
        w = ctypes.c_int16((a_FIFO_buffer[0] << 8) | a_FIFO_buffer[1]).value
        x = ctypes.c_int16((a_FIFO_buffer[4] << 8) | a_FIFO_buffer[5]).value
        y = ctypes.c_int16((a_FIFO_buffer[8] << 8) | a_FIFO_buffer[9]).value
        z = ctypes.c_int16((a_FIFO_buffer[12] << 8) | a_FIFO_buffer[13]).value
        return Q(w, x, y, z)

    def DMP_get_quaternion(self, a_FIFO_buffer):
        quat = self.DMP_get_quaternion_int16(a_FIFO_buffer)
        w = quat.w / 16384.0
        x = quat.x / 16384.0
        y = quat.y / 16384.0
        z = quat.z / 16384.0
        return Q(w, x, y, z)

    def DMP_get_acceleration_int16(self, a_FIFO_buffer):
        x = ctypes.c_int16(a_FIFO_buffer[28] << 8 | a_FIFO_buffer[29]).value
        y = ctypes.c_int16(a_FIFO_buffer[32] << 8 | a_FIFO_buffer[33]).value
        z = ctypes.c_int16(a_FIFO_buffer[36] << 8 | a_FIFO_buffer[37]).value
        return V(x, y, z)

    def DMP_get_gravity(self, a_quat):
        x = 2.0 * (a_quat.x * a_quat.z - a_quat.w * a_quat.y)
        y = 2.0 * (a_quat.w * a_quat.x + a_quat.y * a_quat.z)
        z = 1.0 * (a_quat.w * a_quat.w - a_quat.x * a_quat.x -
                   a_quat.y * a_quat.y + a_quat.z * a_quat.z)
        return V(x, y, z)

    def DMP_get_linear_accel_int16(self, a_v_raw, a_grav):
        x = ctypes.c_int16(a_v_raw.x - (a_grav.x*8192)).value
        y = ctypes.c_int16(a_v_raw.y - (a_grav.y*8192)).value
        y = ctypes.c_int16(a_v_raw.y - (a_grav.y*8192)).value
        return V(x, y, z)

    def DMP_get_euler(self, a_quat):
        psi = math.atan2(2*a_quat.x*a_quat.y - 2*a_quat.w*a_quat.z,2*a_quat.w*a_quat.w + 2*a_quat.x*a_quat.x - 1)
        theta = -asin(2*a_quat.x*a_quat.z + 2*a_quat.w*a_quat.y)
        phi = math.atan2(2*a_quat.y*a_quat.z - 2*a_quat.w*a_quat.x,2*a_quat.w*a_quat.w + 2*a_quat.z*a_quat.z - 1)
        return V(psi, theta, phi)

    def DMP_get_roll_pitch_yaw(self, a_quat, a_grav_vect):
        # roll: (tilt left/right, about X axis)
        roll = math.atan(a_grav_vect.y /
                         math.sqrt(a_grav_vect.x*a_grav_vect.x +
                              a_grav_vect.z*a_grav_vect.z))
        # pitch: (nose up/down, about Y axis)
        pitch = math.atan(a_grav_vect.x /
                          math.sqrt(a_grav_vect.y*a_grav_vect.y +
                               a_grav_vect.z*a_grav_vect.z))
        # yaw: (about Z axis)
        yaw = math.atan2(2*a_quat.x*a_quat.y - 2*a_quat.w*a_quat.z,
                         2*a_quat.w*a_quat.w + 2*a_quat.x*a_quat.x - 1)
        return V(roll, pitch, yaw)

    def DMP_get_euler_roll_pitch_yaw(self, a_quat, a_grav_vect):
        rad_ypr = self.DMP_get_roll_pitch_yaw(a_quat, a_grav_vect)
        roll = rad_ypr.x * (180.0/math.pi)
        pitch = rad_ypr.y * (180.0/math.pi)
        yaw = rad_ypr.z * (180.0/math.pi)
        return V(roll, pitch, yaw)

    def DMP_get_linear_accel(self, a_vector_raw, a_vect_grav):
        x = a_vector_raw.x - a_vect_grav.x*8192
        y = a_vector_raw.y - a_vect_grav.y*8192
        z = a_vector_raw.z - a_vect_grav.z*8192
        return V(x, y, z)


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
                # print("ACCEL",accel.x,accel.y,accel.z)
                quat = self.DMP_get_quaternion_int16(FIFO_buffer)
                # print("QUAT",quat.w,quat.x,quat.y,quat.z)
                grav = self.DMP_get_gravity(quat)
                # print("GRAV",grav.x,grav.y,grav.z)
                roll_pitch_yaw = self.DMP_get_euler_roll_pitch_yaw(quat, grav)
                roll_pitch_yaw.x -= self.x_gyro_offset
                roll_pitch_yaw.y -= self.y_gyro_offset
                roll_pitch_yaw.z -= self.z_gyro_offset
                return roll_pitch_yaw

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    ## Read accelerometer
    #  @param [in] self The object pointer.
    #  @retval x : x-axis data
    #  @retval y : y-axis data
    #  @retval z : z-axis data
    def readAccel(self):
        data = self.__bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        # x = round(x*self.ares, 3)
        # y = round(y*self.ares, 3)
        # z = round(z*self.ares, 3)

        return {"x":x, "y":y, "z":z}

    ## Read gyro
    #  @param [in] self The object pointer.
    #  @retval x : x-gyro data
    #  @retval y : y-gyro data
    #  @retval z : z-gyro data
    def readGyro(self):
        data = self.__bus.read_i2c_block_data(self.address, GYRO_OUT, 6)

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
        drdy = self.__bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01 :
            data = self.__bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08)!=0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])
                print(self.mres)
                print(self.magXcoef)
                print(self.magYcoef)
                print(self.magZcoef)
                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)
            else:
                print("NOVAAQUI")
        else:
            print("NOVA")
        return {"x":x, "y":y, "z":z}

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
        self.__bus.write_byte_data(0x68, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        self.__bus.write_byte_data(0x68, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # DLPF_CFG
        self.__bus.write_byte_data(0x68, CONFIG, 0x03)
        # sample rate divider
        self.__bus.write_byte_data(0x68, SMPLRT_DIV, 0x04)
        # gyro full scale select
        self.__bus.write_byte_data(0x68, GYRO_CONFIG, gfs << 3)
        # accel full scale select
        self.__bus.write_byte_data(0x68, ACCEL_CONFIG, afs << 3)
        # A_DLPFCFG
        self.__bus.write_byte_data(0x68, ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        self.__bus.write_byte_data(0x68, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    def readMagnet(self):
        x=0
        y=0
        z=0

        # check data ready
        drdy = self.__bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01 :
            data = self.__bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08)!=0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])

                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)

        return {"x":x, "y":y, "z":z}

class MPU6050IRQHandler:
    __mpu = MPU6050
    __FIFO_buffer = list()
    __count = 0
    __packet_size = None
    __detected_error = False
    __logging = False
    __log_file = None
    __csv_writer = None
    __start_time = None
    __debug = None

    # def __init__(self, a_i2c_bus, a_device_address, a_x_accel_offset,
    #             a_y_accel_offset, a_z_accel_offset, a_x_gyro_offset,
    #             a_y_gyro_offset, a_z_gyro_offset, a_enable_debug_output):
    #    self.__mpu = MPU6050(a_i2c_bus, a_device_address, a_x_accel_offset,
    #                         a_y_accel_offset, a_z_accel_offset,
    #                         a_x_gyro_offset, a_y_gyro_offset, a_z_gyro_offset,
    #                         a_enable_debug_output)
    def __init__(self, a_mpu, a_logging=False, a_log_file='log.csv',
                 a_debug=False):
        self.__mpu = a_mpu
        self.__FIFO_buffer = [0]*64
        self.__mpu.dmp_initialize()
        self.__mpu.set_DMP_enabled(True)
        self.__packet_size = self.__mpu.DMP_get_FIFO_packet_size()
        mpu_int_status = self.__mpu.get_int_status()
        if a_logging:
            self.__start_time = time.clock()
            self.__logging = True
            self.__log_file = open(a_log_file, 'ab')
            self.__csv_writer = csv.writer(self.__log_file, delimiter=',',
                                           quotechar='|',
                                           quoting=csv.QUOTE_MINIMAL)
        self.__debug = a_debug

    def action(self, channel):
        if self.__detected_error:
            # Clear FIFO and reset MPU
            mpu_int_status = self.__mpu.get_int_status()
            self.__mpu.reset_FIFO()
            self.__detected_error = False
            return

        try:
            FIFO_count = self.__mpu.get_FIFO_count()
            mpu_int_status = self.__mpu.get_int_status()
        except:
            self.__detected_error = True
            return

        # If overflow is detected by status or fifo count we want to reset
        if (FIFO_count == 1024) or (mpu_int_status & 0x10):
            try:
                self.__mpu.reset_FIFO()
            except:
                self.__detected_error = True
                return

        elif (mpu_int_status & 0x02):
            # Wait until packet_size number of bytes are ready for reading,
            # default is 42 bytes
            while FIFO_count < self.__packet_size:
                try:
                    FIFO_count = self.__mpu.get_FIFO_count()
                except:
                    self.__detected_error = True
                    return

            while FIFO_count > self.__packet_size:

                try:
                    self.__FIFO_buffer = \
                        self.__mpu.get_FIFO_bytes(self.__packet_size)
                except:
                    self.__detected_error = True
                    return
                accel = \
                    self.__mpu.DMP_get_acceleration_int16(self.__FIFO_buffer)
                quat = self.__mpu.DMP_get_quaternion_int16(self.__FIFO_buffer)
                grav = self.__mpu.DMP_get_gravity(quat)
                roll_pitch_yaw = self.__mpu.DMP_get_euler_roll_pitch_yaw(quat,
                                                                         grav)
                if self.__logging:
                    delta_time = time.clock() - self.__start_time
                    data_concat = ['%.4f' % delta_time] + \
                        [accel.x, accel.y, accel.z] + \
                        ['%.3f' % roll_pitch_yaw.x,
                         '%.3f' % roll_pitch_yaw.y,
                         '%.3f' % roll_pitch_yaw.z]
                    self.__csv_writer.writerow(data_concat)

                if (self.__debug) and (self.__count % 100 == 0):
                    print('roll: ' + str(roll_pitch_yaw.x))
                    print('pitch: ' + str(roll_pitch_yaw.y))
                    print('yaw: ' + str(roll_pitch_yaw.z))
                self.__count += 1
                FIFO_count -= self.__packet_size

i2c_bus = 1
device_address = 0x68


if __name__ == "__main__":
    
    mpu = MPU6050(i2c_bus, device_address)

    

    # mpu.calibrarGyro()

    while True:
    
        roll_pitch_yaw = mpu.readSensoresConCalibracion()
        
        print('roll: ' + str(roll_pitch_yaw.x))
        print('pitch: ' + str(roll_pitch_yaw.y))
        print('yaw: ' + str(roll_pitch_yaw.z))
        print()
        # print("Aceleration",mpu.get_accelerationV2()[0],mpu.get_accelerationV2()[1],mpu.get_accelerationV2()[2])
        # print("accel2",mpu.readAccel())
        # print("Rotation",mpu.get_rotationV2()[0],mpu.get_rotationV2()[1],mpu.get_rotationV2()[2])
        # print(mpu.DMP_get_linear_accel)
        # print(mpu.DMP_get_gravity)
        print(mpu.get_rotationV2())
        print(mpu.get_accelerationV2())
        # print(mpu.readMagnet())
        # print(mpu.readMagnet())
        time.sleep(1)