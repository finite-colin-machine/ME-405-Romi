"""!
@file line_sensor.py 
@brief A class used for reading a line using the Pololu 8-Channel QTRX Sensor Array
@author Colin Bentley and Jack Maxwell
@date 12/07/2024
"""

# import modules
import pyb
from pyb import Pin, UART, repl_uart
from time import ticks_us, ticks_diff

class line_sensor:
    '''!@brief A class used for reading a line using the Pololu 8-Channel QTRX Sensor Array
    '''
    def __init__(self, sensor_pins):
        '''!@brief Constructs an line sensor object.
        @param pins that connect to the sensor array
        '''
        self.sensors = [Pin(pin, mode=Pin.OUT_PP) for pin in sensor_pins] # initialize pins
    
    def read_line(self):
        '''!@brief Reads the sensor and outputs a weighted average of the readings
        '''
        outputs = []                                       # init output list
        scale = [-1.4, 1.4, -2.4, 2.4, -3.75, 3.75, -5, 5] # scale used for calculating weighted average 
        
        for sensor in self.sensors:      # for each sensor
            sensor.init(mode=Pin.OUT_PP) # set pin to output
            sensor.value(1)              # drive it high
            pyb.udelay(10)               # wait 10 us for output to rise
            sensor.init(mode=Pin.IN)     # set pin to input
            time_start = ticks_us()      # keep track of start time
            state = sensor.value()       # read pin
            
            # keep reading pin until it goes low or timesout
            while state > 0 and ticks_diff(ticks_us(), time_start) < 2000:
                state = sensor.value() # read pin
                
            decay = ticks_diff(ticks_us(), time_start) # calculate length of decay
            outputs.append(decay)                      # add measurement to list

        # raise full_black flag if the total outputs are above a certain threshold
        abs_reading = sum(outputs)
        if abs_reading > 12000:     # if all measurements are above a threshold
            self.full_black = True  # raise flag
        else:                       # otherwise
            self.full_black = False # lower flag
        
        # scale outputs by multiplying each measurement by a weight
        for instance in range(8):
            outputs[instance] *= scale [instance]
        
        reading = sum(outputs) # add all outputs
        
        return reading

if __name__ == "__main__":
    
    # configure UART to communicate with Romi using bluetooth
    uart = UART(3, baudrate=115200)
    repl_uart(uart)
    
    # in order across 
    sensor_pins = [Pin.cpu.A4, Pin.cpu.B0, Pin.cpu.C1, Pin.cpu.C0, 
                   Pin.cpu.A6, Pin.cpu.A7, Pin.cpu.B1, Pin.cpu.C3]
    # # skipping order 
    # sensor_pins = [Pin.cpu.C0, Pin.cpu.A6, Pin.cpu.C1, Pin.cpu.A7, 
    #                Pin.cpu.B0, Pin.cpu.B1, Pin.cpu.A4, Pin.cpu.C3]
    
    qtr = line_sensor(sensor_pins)
    
    while True:
        qtr.read_line()
        print(qtr.full_black)
