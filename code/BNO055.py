"""!
@file BNO055.py
@brief A MicroPython driver for the BNO055 IMU.
@details This program provides an interface for the BNO055 IMU sensor using I2C communication. 
         It supports operations such as setting modes, retrieving calibration data, and reading 
         orientation and angular velocity data. The implementation is inspired by existing drivers 
         like the MicroPython-BNO055 driver by Peter Hinch and the Adafruit CircuitPython driver.
@author Colin Bentley and Jack Maxwell
@date 11/19/2024
"""

# import modules
import machine
import time
import struct

# BNO055 register addresses
dev_addr = 0x28              # Default I2C address for the BNO055
euler_addr = 0x1A            # Register address for Euler angles
gyr_addr = 0x14              # Register address for gyroscope data
cal_status_addr = 0x35       # Register address for calibration status
mode_addr = 0x3D             # Register address for operation mode
acc_offset_addr = 0x55       # Register address for accelerometer offsets
mag_offset_addr = 0x5C       # Register address for magnetometer offsets
gyr_offset_addr = 0x62       # Register address for gyroscope offsets
unit_addr = 0x3B             # Register address for unit selection

# BNO055 mode numbers
imu_modes = {
    'imuplus': 0x08,          # IMU mode without magnetometer
    'compass': 0x09,          # Compass mode
    'm4g': 0x0A,              # Magnetometer with accelerometer mode
    'ndof_fmc_off': 0x0B,     # NDOF mode without fast magnetometer calibration
    'ndof': 0x0C,             # Full NDOF mode
    'config': 0}              # Configuration mode


class BNO055:
    '''!@brief A MicroPython driver for the BNO055 IMU.
    @details This class provides methods for configuring the BNO055 IMU, retrieving
             calibration data, and reading sensor measurements such as Euler angles
             and angular velocity.
    '''

    def __init__(self, i2c):
        '''!@brief Initializes the BNO055 driver with a given I2C interface.
        @details Sets the initial configuration and prepares the IMU for operation.
        @param i2c A pre-configured I2C object for communicating with the IMU.
        '''
        self.imu = i2c
        self.mode_number = imu_modes['config']  # Start in configuration mode

    def set_opr_mode(self, mode):
        '''!@brief Sets the operating mode of the IMU.
        @details Changes the mode of the BNO055 IMU to one of the supported modes, such as NDOF or IMUPLUS.
        @param mode The name of the mode to set (e.g., 'ndof', 'config').
        '''
        self.mode_name = mode
        self.mode_number = imu_modes[mode]     # Get mode number from the dictionary
        buf = bytearray([self.mode_number])    # Create a buffer with the mode number
        self.imu.writeto_mem(dev_addr, mode_addr, buf)  # Write mode to the operation mode register

    def read_cal_status(self):
        '''!@brief Reads the calibration status of the IMU.
        @details Retrieves the calibration levels of the system, gyroscope, accelerometer, and magnetometer.
        '''
        buf = bytearray(1)                     # Initialize a single-byte buffer
        self.imu.readfrom_mem_into(dev_addr, cal_status_addr, buf)  # Read the calibration status byte
        cal_status = buf[0]
        # Parse the status byte to retrieve individual calibration levels
        self.sys_cal_status = (cal_status >> 6) & 0x03
        self.gyr_cal_status = (cal_status >> 4) & 0x03
        self.acc_cal_status = (cal_status >> 2) & 0x03
        self.mag_cal_status = cal_status & 0x03

    def read_cal_coef(self):
        '''!@brief Reads the calibration coefficients from the IMU.
        @details Retrieves calibration offsets and saves them to a binary file.
        '''
        last_mode = self.mode_name              # Save the current mode
        self.set_opr_mode('config')             # Switch to configuration mode
        buf = bytearray(22)                     # Initialize a buffer for calibration data
        self.imu.readfrom_mem_into(dev_addr, acc_offset_addr, buf)  # Read offsets into buffer
        with open('calibration.bin', 'wb') as file:
            file.write(buf)                     # Save calibration data to a binary file
        self.set_opr_mode(last_mode)            # Restore the previous mode

    def set_offsets(self):
        '''!@brief Writes calibration coefficients to the IMU.
        @details Loads calibration offsets from a binary file and writes them to the IMU.
        '''
        last_mode = self.mode_name              # Save the current mode
        self.set_opr_mode('config')             # Switch to configuration mode
        with open('calibration.bin', 'rb') as file:
            buf = bytearray(file.read())        # Read calibration data from the file
        self.imu.writeto_mem(dev_addr, acc_offset_addr, buf)  # Write offsets to the IMU
        self.set_opr_mode(last_mode)            # Restore the previous mode

    def read_euler(self):
        '''!@brief Reads Euler angles from the IMU.
        @details Retrieves the heading, roll, and pitch angles for orientation feedback.
        '''
        buf = bytearray(6)                      # Initialize a buffer for Euler angle data
        self.imu.readfrom_mem_into(dev_addr, euler_addr, buf)  # Read data into the buffer
        # Unpack the data into individual angles
        self.euler_heading, self.euler_roll, self.euler_pitch = struct.unpack('<hhh', buf)
        self.euler_heading /= 16               # Convert heading to degrees

    def read_gyr(self):
        '''!@brief Reads angular velocity from the IMU.
        @details Retrieves the angular velocity in x, y, and z axes.
        '''
        buf = bytearray(6)                      # Initialize a buffer for gyroscope data
        self.imu.readfrom_mem_into(dev_addr, gyr_addr, buf)  # Read data into the buffer
        # Unpack the data into individual axes
        self.gyr_x, self.gyr_y, self.gyr_z = struct.unpack('<hhh', buf)
        self.gyr_z /= 16                        # Convert yaw rate to degrees/second

if __name__ == '__main__':
    i2c1 = machine.I2C(1)  # Configure I2C on pins B8 (SCL) and B9 (SDA)
    IMU = BNO055(i2c1)     # Initialize the IMU
    IMU.set_opr_mode('ndof')  # Set the IMU to NDOF mode
