"""!
@file encoder.py 
@brief An encoder class used for reading the encoders on the Romi robot.
@details This program creates a motor encoder class that is able to create an encoder object based on
         a timer, Channel A pin, and Channel B pin.
         Within the class, there are several methods - the main one is to update the encoder, which
         calculates information like position, change in position, change in time, and speed.
         Other methods allow retrieval of these calculated values or resetting the position.

Classes:
    - encoder: A class to update and read a single motor encoder.

@author Colin Bentley and Jack Maxwell
@date 11/19/2024
"""

# import modules
from pyb import Timer
from time import ticks_us, ticks_diff

class encoder:
    '''!@brief Interface with quadrature encoders.
    @details This class provides methods to track the position, speed, and 
    changes in position of a motor shaft using a quadrature encoder.
    '''

    def __init__(self, enc_tim, CH_A_pin, CH_B_pin):
        '''!@brief Constructs an encoder object.
        @details An encoder is used to measure rotation of a motor by interfacing 
        with hardware timer channels for quadrature decoding.
        @param enc_tim Timer object configured for encoder mode.
        @param CH_A_pin Pin object connected to Channel A of the encoder.
        @param CH_B_pin Pin object connected to Channel B of the encoder.
        '''
        # Configure timer channels for encoder instance
        self.enc_tim = enc_tim
        self.enc_tim.channel(1, pin=CH_A_pin, mode=Timer.ENC_AB)
        self.enc_tim.channel(2, pin=CH_B_pin, mode=Timer.ENC_AB)
        
        # Initialize variables
        self.counter_old = enc_tim.counter()
        self.time_old = ticks_us()
        self.delta = 0
        self.position = 0
        self.counter_new = 0

    def update(self):
        '''!@brief Updates encoder position, delta, and speed.
        @details Reads the encoder count, calculates the difference since 
        the last update (delta), accounts for timer overflow, and updates 
        the encoder speed, position, and time difference.
        '''
        # Read encoder
        self.counter_new = self.enc_tim.counter()
        
        # Calculate the difference in encoder counts
        self.delta = self.counter_new - self.counter_old
        
        # Account for timer rollover
        if self.delta > 32768:
            self.delta -= 65536
        elif self.delta < -32768:
            self.delta += 65536
        
        # Update time and calculate speed
        time_new = ticks_us()
        self.dt = ticks_diff(time_new, self.time_old)
        self.time_old = time_new
        
        # Calculate speed in encoder counts per microsecond
        self.speed = self.delta / self.dt
        
        # Update position
        self.position += self.delta
        
        # Store the current counter value for the next calculation
        self.counter_old = self.counter_new

    def get_position(self):
        '''!@brief Gets the most recent encoder position.
        @details The position is calculated cumulatively and considers
        the convention that counter-clockwise rotation is positive.
        @return The current encoder position in counts (int).
        '''
        return -self.position  # Negated for CCW convention

    def get_delta(self):
        '''!@brief Gets the most recent change in encoder counts.
        @details Represents the difference in encoder counts between the 
        last two updates.
        @return The change in encoder counts (int).
        '''
        return -self.delta  # Negated for CCW convention
    
    def get_speed(self):
        '''!@brief Gets the speed of the encoder.
        @details Speed is calculated as the change in encoder counts divided 
        by the elapsed time since the last update.
        @return The current speed in counts per microsecond (float).
        '''
        return -self.speed  # Negated for CCW convention
    
    def get_dt(self):
        '''!@brief Gets the time difference between updates.
        @details The time difference is measured in microseconds using 
        the ticks_us() and ticks_diff() functions.
        @return The time difference between the last two updates (int).
        '''
        return self.dt 

    def zero(self):
        '''!@brief Resets the encoder position to zero.
        @details This method sets the encoder position and counter reference
        value to zero, effectively resetting the accumulated position.
        '''
        self.counter_old = self.enc_tim.counter()
        self.position = 0