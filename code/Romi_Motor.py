"""!
@file Romi_Motor.py
@brief A driver class for controlling DC motors on the Romi robot.
@details This file contains the implementation of a motor driver class for the 
         DRV8838 motor driver used in the Pololu Romi robot. The class allows for
         precise control of the motor's speed and direction via PWM signals and 
         provides methods to enable and disable the motor driver.

Classes:
    - Romi_Motor: A class to control a single DC motor using the DRV8838 driver.

@author Colin Bentley and Jack Maxwell
@date 11/19/2024
"""

from pyb import Pin, Timer

class Romi_Motor:
    '''!@brief A driver class for the DRV8838 Motors on Romi.
    @details Objects of this class can be used to control a DRV8838 DC motor
    on the Romi robot by setting the PWM duty cycle, direction, and enabling
    or disabling the motor driver. This driver is designed for the Romi robot
    from Pololu, which uses the DRV8838 motor driver.
    '''

    def __init__(self, PWM_tim, PWM_pin, DIR_pin, EN_pin):
        '''!@brief Initializes and returns an object associated with a DC motor.
        @details This constructor configures the PWM channel, direction pin, and
        enable pin needed to control the motor. It sets default values to ensure
        the motor starts in a known state.
        @param PWM_tim The Timer object used for generating the PWM signal.
        @param PWM_pin The Pin object connected to the PWM input of the motor driver.
        @param DIR_pin The Pin object connected to the direction control pin.
        @param EN_pin The Pin object connected to the enable (not sleep) pin of the motor driver.
        '''
        self.CH = PWM_tim.channel(1, mode=Timer.PWM, pin=PWM_pin, pulse_width_percent=0)  # Configure PWM on CH1
        self.DIR = Pin(DIR_pin, mode=Pin.OUT_PP)  # Configure direction pin
        self.DIR.high()  # Set direction pin high (default to forward)
        self.EN = Pin(EN_pin, mode=Pin.OUT_PP)  # Configure enable pin
        self.EN.low()  # Turn off the enable pin (default to disabled)

    def set_duty(self, duty):
        '''!@brief Sets the PWM duty cycle for the DC motor.
        @details This method adjusts the motor's duty cycle to control its
        speed and direction. Positive values make the motor turn in one direction
        (e.g., forward), while negative values reverse the direction.
        @param duty A signed integer or float specifying the duty cycle
                    of the PWM signal as a percentage (-100 to 100).
        '''
        # Set direction based on duty sign
        if duty >= 0:  # For positive inputs
            self.DIR.low()  # Set direction for forward rotation
        else:  # For negative inputs
            self.DIR.high()  # Set direction for reverse rotation
        
        # Set the PWM duty cycle (absolute value of input)
        self.CH.pulse_width_percent(abs(duty))

    def enable(self):
        '''!@brief Enables the motor driver.
        @details This method sets the enable (not sleep) pin of the motor driver
        high to allow the motor to operate. The motor will respond to PWM and
        direction signals when enabled.
        '''
        self.EN.high()  # Enable the motor driver

    def disable(self):
        '''!@brief Disables the motor driver.
        @details This method sets the enable (not sleep) pin of the motor driver
        low to disable the motor. The motor will not respond to any PWM or
        direction signals while disabled.
        '''
        self.EN.low()  # Disable the motor driver
