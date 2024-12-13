"""!
@file main.py 
@author Colin Bentley and Jack Maxwell
@date 11/19/2024

ADD INFO HERE

"""

# Import modules
from pyb import Pin, Timer, UART, repl_uart, ExtInt
import gc
import machine
import cotask
import task_share
from encoder import encoder
from Romi_Motor import Romi_Motor             
from BNO055 import BNO055
from time import ticks_us, ticks_diff, sleep_ms
from math import pi
from line_sensor import line_sensor

# Blue user button function
def user_button_toggle(pressed):
    global user_button_pressed
    user_button_pressed = True

# Bump sensor function
def bump_toggle(pressed):
    global bump_detected
    bump_detected = True
    print('Hey! Who put that there?')

# Create generator functions acting as tasks containing FSMs
def planner(shares):
    """!
    Task which calculates set points needed to drive in a circle and handles starting/stopping the robot
    @param shares A tuple of a share and queue from which this task gets data
    """
    global user_button_pressed, bump_detected, w, r # list global variables
    
    # get references to the shares and queues which have been passed to this task
    my_velocity_setpoint, my_yaw_setpoint, my_control_flag, my_calibration_flag = shares
    
    state = 0          # initialize state
    calibrated = False # initialize calibration
    my_calibration_flag.put(0)

    while True:
        if (state == 0):                        # init state
            V = .10                             # user input robot translational velocity [m/s]
            w = .141                            # robot track width [m]
            r = .035                            # robot wheel radius [m]
            
            # # # TO BYPASS CALIBRATION CHECK
            # calibrated = True
            # print('bypassing calibration')
            
            if calibrated == False:
                state = 4   # set calibration state
            else:
                print('Press blue button to begin driving')
                state = 1   # set wait state
            yield(state)  
            
        elif (state == 1):  # wait and search for bump state state
            if user_button_pressed == True:
                user_button_pressed = False # if so, reset the user button flag
                my_control_flag.put(1)
                my_velocity_setpoint.put(V)
                my_yaw_setpoint.put(0)
            yield(state)
        
        elif (state == 4):                           # calibration state
            
            file_known = False                       # initialize flag
            calibrated = False                       # initialize calibration status
        
            try:                                     # try to open calibration file
                with open('calibration.bin', 'r'):
                    file_known = True                # set flag
            except OSError:                          # if there is no calibration file
                print('Perform manual calibration')  # notify user
        
            if file_known:
                try:
                    IMU.set_offsets()                # calibrate using file data
                    calibrated = True                # set calibrated
                except OSError:                      # if there is an error using the file
                    raise OSError('''Error accessing calibration.bin. Remove calibration.bin from the nucleo and restart program to perform manual calibration''')
                                  
        
            if not calibrated:                       # if still not calibrated
                IMU.read_cal_status()                # read calibration status
                print(f"{IMU.mag_cal_status} {IMU.acc_cal_status} {IMU.gyr_cal_status} {IMU.sys_cal_status}")
                if (IMU.mag_cal_status == 3
                    and IMU.acc_cal_status == 3
                    and IMU.gyr_cal_status == 3
                    and IMU.sys_cal_status == 3):    # if all calibrated
                    calibrated = True                # set calibrated
                    print('IMU Calibrated')          # notify user
                    my_calibration_flag.put(1)
                    
            state = 0                                # set init state
            yield(state)
        
        else: # if state isnt found
            raise ValueError('Invalid state')

def robot_control(shares):
    """!
    Controller task which calculates omega setpoints for the motors using translationa velocity and yaw data.
    Comment out this task and follow other instructions in the code to bypass the robot control.
    @param shares A tuple of a share and queue from which this task gets data
    """
    global w, r # list global variables
    
    # get references to the shares and queues which have been passed to this task
    my_velocity_setpoint, my_yaw_setpoint, my_control_flag, my_omega_L_setpoint, my_omega_R_setpoint, my_omega_L_actual, my_omega_R_actual = shares
    
    V_err = 0       # zero error
    yaw_err = 0     # zero error
    V_err_sum = 0   # zero error sum
    yaw_err_sum = 0 # zero error sum
    
    state = 0       # initialize state
    
    # set proportional and integral gains for translational velocity and yaw rate
    Kp_V = .8
    Kp_yaw = .7
    Ki_V = .87
    Ki_yaw = .95
    
    while True:
        control_on = my_control_flag.get() # get control flag
        
        if state == 0:            # State 0: Robot Control off
            time_old = ticks_us() # continuously update old time while off
            if control_on == 0:   # set to control state if flag raised
                pass
            else:
                state = 1         # set control state
            yield(state)                   
            
        elif state == 1: # State 1: Apply control     

            # get values from shares
            V_ref = my_velocity_setpoint.get()
            yaw_ref = my_yaw_setpoint.get()
            omega_L_act = my_omega_L_actual.get()
            omega_R_act = my_omega_R_actual.get()
            
            # perform time calculations
            time_new = ticks_us()                         # update time
            dt = ticks_diff(time_new, time_old)/1_000_000 # calculate time difference in seconds
            time_old = time_new                           # reset the old time for next pass 
        
            # calculate actual translational velocity based on current wheel velocity
            V_act = (r/2)*(omega_L_act + omega_R_act)     
            
            # read actual yaw rate from IMU
            IMU.read_gyr()              
            yaw_act = IMU.gyr_z*0.01745 # [rad/s] convert yaw rate from deg/s to rad/s
      
            # calculate errors
            V_err = V_ref - V_act
            yaw_err = yaw_ref - yaw_act
            
            # calculate error sums
            V_err_sum += V_err*dt
            yaw_err_sum += yaw_err*dt
            
            # calculate robot requests by applying proportional and integral control
            V_request = Kp_V*V_err + Ki_V*V_err_sum
            yaw_request = Kp_yaw*yaw_err + Ki_yaw*yaw_err_sum
            
            # calculate wheel velocity requests from robot requests
            omega_L_request = (V_request/r) - (w*yaw_request/(2*r))
            omega_R_request = (V_request/r) + (w*yaw_request/(2*r))
            
            # add wheel velocities to shares
            my_omega_L_setpoint.put(omega_L_request)
            my_omega_R_setpoint.put(omega_R_request)
            
            if control_on == 1: # set to control off state if flag lowered
                pass
            else:
                V_err = 0       # zero velocity error
                yaw_err = 0     # zero yaw rate error
                V_err_sum = 0   # zero velocity error sum
                yaw_err_sum = 0 # zero yaw rate error sum

                state = 0       # set off state
            yield(state)
           
        else:                   # if state isnt found
            raise ValueError('Invalid state')

def motor_L_control(shares):
    """!
    Task which controls the velocity of the left motor by applying proportional and integral control to the velocity error
    @param shares is a tuple of a share and queue from which this task gets data
    """
    # get references to the shares and queues which have been passed to this task
    my_omega_L_setpoint, my_omega_L_actual, my_control_flag = shares
    
    state = 0       # initialize state
    mot_L.disable() # disable motor
    Kp = 7          # set proportional gain
    Ki = 8          # set integral gain
    err_sum = 0     # initialize error sum
    
    while True:
        motor_on = my_control_flag.get() # get control flag from shares
        
        if state == 0:        # State 0: Motor Off
        
            enc_L.update()    # continuously update encoder while off
            if motor_on == 0: # set to control state if flag raised
                pass
            else:
                mot_L.set_duty(0) # clear duty cycle
                mot_L.enable()    # enable motor
                state = 1         # set control state
            yield(state)
        
        elif state == 1: # State 1: Apply Motor Control
            
        # get wheel velocity from shares
            Omega_L_ref = my_omega_L_setpoint.get()
            
            # update encoder and get dt
            enc_L.update()
            dt = enc_L.get_dt()/1_000_000 # [s]
            
            # calculate omega actual
            Omega_act = enc_L.get_speed()*-4363 # [rad/s], multiplier is speed count/us * 10^6 us/s * 1/1440 rev/count * 2pi rad/rev
            my_omega_L_actual.put(Omega_act)    # add to wheel velocity share

            # Apply motor control
            err = Omega_L_ref - Omega_act # calculate error
            err_sum += err*dt             # calculate error sum
            L = Kp*err + Ki*err_sum       # calculate duty cycle
            mot_L.set_duty(L)             # set duty cycle
            
            if motor_on == 1:     # set to off state if flag lowered
                pass
            else:
                mot_L.set_duty(0) # clear duty cycle
                mot_L.disable()   # disable motor
                err_sum = 0       # clear error sum
                state = 0         # set off state
            yield(state)

def motor_R_control(shares):
    """!
    Task which controls the velocity of the right motor by applying proportional and integral control to the velocity error
    @param shares is a tuple of a share and queue from which this task gets data
    """
    # get references to the shares and queues which have been passed to this task
    my_omega_R_setpoint, my_omega_R_actual, my_control_flag = shares
    
    state = 0       # initialize state
    mot_R.disable() # disable motor
    Kp = 7          # set proportional gain
    Ki = 8          # set integral gain
    err_sum = 0     # initialize error sum
    
    while True:
        motor_on = my_control_flag.get() # get control flag from shares
        
        if state == 0:        # State 0: Motor Off
            
            enc_R.update()    # continuously update encoder while off
            if motor_on == 0: # set to control state if flag raised
                pass
            else:
                mot_R.set_duty(0) # clear duty cycle
                mot_R.enable()    # enable motor
                state = 1         # set control state
            yield(state)
        
        elif state == 1: # State 1: Apply Motor Control
            
            # get wheel velocity from shares
            Omega_R_ref = my_omega_R_setpoint.get()
            
            # update encoder and get dt
            enc_R.update()
            dt = enc_R.get_dt()/1_000_000 # [s]
            
            # calculate omega actual
            Omega_act = enc_R.get_speed()*-4363 # [rad/s], multiplier is speed count/us * 10^6 us/s * 1/1440 rev/count * 2pi rad/rev
            my_omega_R_actual.put(Omega_act)    # add to share

            # Apply motor control
            err = Omega_R_ref - Omega_act # calculate error
            err_sum += err*dt             # calculate error sum
            L = Kp*err + Ki*err_sum       # calculate duty cycle
            mot_R.set_duty(L)             # set duty cycle
            
            if motor_on == 1:     # set to off state if flag lowered
                pass
            else:
                mot_R.set_duty(0) # clear duty cycle
                mot_R.disable()   # disable motor
                err_sum = 0       # clear error sum
                state = 0         # set off state
            yield(state)
            
def driving_mode(shares):
    """!
    
    @param 
    """
    global bump_detected
    
    # get references to the shares and queues which have been passed to this task
    my_velocity_setpoint, my_yaw_setpoint, my_control_flag, my_calibration_flag = shares
    
    V = .10                             # user input robot translational velocity [m/s]
    w = .141                            # robot track width [m]
    r = .035                            # robot wheel radius [m]
    
    drive_3 = 1440*3*.0254/(2*pi*r)     # distance for robot to drive 3 inches [encoder counts]
    turn_90 = 1440*w/(8*r)              # distance for robot to turn 90 degrees in place [encoder counts]
    
    # init variables
    after_wall = False
    state = 0
    
    while True:
        if state == 0:                             # starting state
            control_on = my_control_flag.get()     # get control flag
            calibrated = my_calibration_flag.get() # get calibration flag
            if calibrated == 0:                    # ignore bump detection before calibration
                bump_detected = False
            if control_on == 1:                    # set to control state if flag raised
                IMU.read_euler()
                starting_heading = IMU.euler_heading
                enc_R.zero()                       # clear encoder position
                state = 3                          # set leave box
            yield(state)                   
        
        elif state == 1:                                        # line follow state
            if bump_detected:                                   # if there is a bump
                my_control_flag.put(0)                          # turn off motors
                enc_R.zero()                                    # clear encoder
                section_complete = False                        # Initialize square section completion flag
                square_idx = 1                                  # Init square index
                state = 2                                       # set square driving state
            elif after_wall == True and qtr.full_black == True: # if robot crosses black line after bumping wall
                my_velocity_setpoint.put(V)                     # set velocity
                my_yaw_setpoint.put(0)                          # set yaw
                enc_R.zero()                                    # clear encoder
                after_wall = False
                return_idx = 1
                state = 4                                       # set turn around state
            else:                                               # otherwise
                yaw = qtr.read_line()/1500                      # read line and scale measurement
                if qtr.full_black:
                    my_yaw_setpoint.put(0)
                else:
                    my_yaw_setpoint.put(yaw)                        # Set yaw based on line reading
            yield(state)   
            
        elif state == 2:                          # square state
            enc_R.update()                        # Update encoder position
            position = abs(enc_R.get_position())  # Get position magnitude
            
            if square_idx == 1 and not section_complete:  # Step 1: Back up
                my_velocity_setpoint.put(-V)  # Set reverse velocity
                my_yaw_setpoint.put(0)        # No yaw change
                my_control_flag.put(1)        # Start movement
                if position > drive_3 / 2:    # Condition to finish backing up
                    my_control_flag.put(0)
                    square_idx += 1
                    enc_R.zero()
                    section_complete = True
            
            elif square_idx in [2, 4] and not section_complete:  # Steps 2 and 4: Turn 90 degrees
                turn_speed = -pi/2 if square_idx == 2 else pi/2
                my_velocity_setpoint.put(0)      # No forward motion
                my_yaw_setpoint.put(turn_speed)  # Set yaw rate
                my_control_flag.put(1)           # Start turn
                if position > turn_90:           # Condition to finish turn
                    my_control_flag.put(0)
                    square_idx += 1
                    enc_R.zero()
                    section_complete = True
            
            elif square_idx == 3 and not section_complete:  # Steps 3: Drive forward short distance
                my_velocity_setpoint.put(V)  # Forward velocity
                my_yaw_setpoint.put(0)       # No yaw change
                my_control_flag.put(1)       # Start forward motion
                if position > drive_3 * 3:   # Condition to finish drive
                    my_control_flag.put(0)
                    square_idx += 1
                    enc_R.zero()
                    section_complete = True
            
            elif square_idx == 5 and not section_complete:  # Step 5: Drive forward longer distance
                my_velocity_setpoint.put(V)
                my_yaw_setpoint.put(0)
                my_control_flag.put(1)
                if position > drive_3 * 6:
                    my_control_flag.put(0)
                    square_idx += 1
                    enc_R.zero()
                    section_complete = True
                    
            elif square_idx == 6 and not section_complete:  # Step 6: Turn slightly less than 90 degrees
                my_velocity_setpoint.put(0)
                my_yaw_setpoint.put(pi/2)
                my_control_flag.put(1)
                if position > turn_90 * 0.65:
                    my_control_flag.put(0)
                    square_idx += 1
                    enc_R.zero()
                    section_complete = True
                    
            elif square_idx == 7 and not section_complete:  # Step 7: Drive forward longer distance
                my_velocity_setpoint.put(V)
                my_yaw_setpoint.put(0)
                my_control_flag.put(1)
                if position > drive_3 * 4:
                    # my_control_flag.put(1)
                    # my_velocity_setpoint.put(V)
                    # my_yaw_setpoint.put(0)
                    enc_R.zero()
                    square_idx = 0          # Reset for future operations
                    bump_detected = False   # reset the flag
                    after_wall = True
                    state = 1
            
            # elif square_idx == 9 and not section_complete:  # Final step: Stop and reset
            #     my_control_flag.put(1)
            #     my_velocity_setpoint.put(V)
            #     my_yaw_setpoint.put(0)
            #     enc_R.zero()
            #     square_idx = 0          # Reset for future operations
            #     bump_detected = False   # reset the flag
            #     after_wall = True
            #     state = 1
                
            if section_complete:
                section_complete = False
            yield(state)
            
        elif state == 3:                          # Leave box state
            enc_R.update()                        # Update encoder position
            position = abs(enc_R.get_position())  # Get position magnitude
            if position > drive_3 * 2:            # After driving 3 inches
                state = 1                         # Set to line follow state
            yield(state)
            
        elif state == 4:                         # turn around state
            enc_R.update()                       # Update encoder position
            position = abs(enc_R.get_position()) # Get position magnitude
            
            
            if return_idx == 1:              # Step 1: drive forward
                my_control_flag.put(1)       # Start movement
                if position > drive_3 *2:    # After driving correct distance
                    my_velocity_setpoint.put(0) # Set velocity
                    my_yaw_setpoint.put(pi/4)       # Set yaw
                    my_control_flag.put(0)   # Turn off control
                    return_idx += 1          # increment index
                    enc_R.zero()             # Clear encoder position
    
            elif return_idx == 2:              # Step 2: adjust heading
                my_control_flag.put(1)         # Start movement
                IMU.read_euler()
                if IMU.euler_heading > (starting_heading - 1):    # After driving correct distance
                    my_velocity_setpoint.put(-V) # Set reverse velocity
                    my_yaw_setpoint.put(0)       # No yaw change
                    my_control_flag.put(0)   # Turn off control
                    return_idx += 1          # increment index
                    enc_R.zero()             # Clear encoder position
    
            else:                            # Step 3: drive backwards
                my_control_flag.put(1)       # Start movement
                if position > drive_3 *3:    # After driving correct distance
                    
                    return_idx = 1
                    enc_R.zero()
                    state = 5
            yield(state)
            
        elif state == 5:                    # end state
            qtr.read_line()
            if qtr.full_black == True:
                enc_R.zero()
                state = 6
            yield(state)
            
        elif state == 6:
            enc_R.update()                        # Update encoder position
            position = abs(enc_R.get_position())  # Current position magnitude
            if position > drive_3 *1.5:             # Condition to finish backing up
                my_velocity_setpoint.put(0)
                my_yaw_setpoint.put(pi/2)         # Set yaw
                my_control_flag.put(0)
                enc_R.zero()
                state = 7
            yield(state)
              
        elif state == 7:
            my_control_flag.put(1)
            enc_R.update()                        # Update encoder position
            position = abs(enc_R.get_position())  # Current position magnitude
            if position > turn_90*2:              # Condition to finish turn
                my_control_flag.put(0)
                enc_R.zero()
                state = 0
            yield(state)
            
        else:                   # if state isnt found
            raise ValueError('Invalid state')

if __name__ == "__main__":
    
    # configure UART to communicate with Romi using bluetooth
    uart = UART(3, baudrate=115200)
    repl_uart(uart)

    # create timer objects to use with motors
    tim_L = Timer(4, freq = 20_000)
    tim_R = Timer(8, freq = 20_000)

    # create motor driver objects
    mot_L = Romi_Motor(tim_L, Pin.cpu.B6, Pin.cpu.A8, Pin.cpu.A9)
    mot_R = Romi_Motor(tim_R, Pin.cpu.C6, Pin.cpu.C8, Pin.cpu.C9)

    # create timer objects to use with encoders
    enc_tim_L = Timer(3, period = 65535, prescaler = 0)
    enc_tim_R = Timer(2, period = 65535, prescaler = 0)

    # create encoder objects
    enc_L = encoder(enc_tim_L, Pin.cpu.B5, Pin.cpu.B4)
    enc_R = encoder(enc_tim_R, Pin.cpu.A1, Pin.cpu.A0)
    
    # setup blue user button interrupt
    user_button_pressed = False
    button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING,Pin.PULL_NONE, user_button_toggle)
    
    # setup left and right bumper interrupts
    bump_detected = False
    left_int = ExtInt(Pin.cpu.B14, ExtInt.IRQ_FALLING, Pin.PULL_UP, bump_toggle)
    right_int = ExtInt(Pin.cpu.C7, ExtInt.IRQ_FALLING,Pin.PULL_UP, bump_toggle)
    
    # setup IMU
    i2c1 = machine.I2C(1)    # create I2C object on bus 1
    IMU = BNO055(i2c1)       # create BNO055 object using I2C bus
    IMU.set_opr_mode('ndof') # set IMU operating mode
    
    # set up line sensor alternating from left to right
    sensor_pins = [Pin.cpu.C0, Pin.cpu.A6, Pin.cpu.C1, Pin.cpu.A7, 
                   Pin.cpu.B0, Pin.cpu.B1, Pin.cpu.A4, Pin.cpu.C3]
    qtr = line_sensor(sensor_pins) # create line_sensor object

    # create shares and queues for safely using variables in different tasks
    velocity_setpoint = task_share.Share('f', thread_protect=False, name="velocity_setpoint")
    yaw_setpoint = task_share.Share('f', thread_protect=False, name="yaw_setpoint")
    omega_L_setpoint = task_share.Share('f', thread_protect=False, name="omega_L_setpoint")
    omega_R_setpoint = task_share.Share('f', thread_protect=False, name="omega_R_setpoint")
    omega_L_actual = task_share.Share('f', thread_protect=False, name="omega_L_actual")
    omega_R_actual = task_share.Share('f', thread_protect=False, name="omega_R_actual")
    control_flag = task_share.Share('f', thread_protect=False, name="control_flag")
    calibration_flag = task_share.Share('f', thread_protect=False, name='calibration_flag')
    line_reading = task_share.Share('f', thread_protect=False, name="line_reading")

    # Create the tasks. If trace is enabled for any task, memory will be allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for  debugging and set trace to False when it's not needed
    
    # If the program does not seem to be running, try adjusting priorities and periods
    
    task1 = cotask.Task(planner, name="Task_1", priority=4, period=150,
                        profile=True, trace=False, shares=(velocity_setpoint, yaw_setpoint, control_flag, calibration_flag))
    
    task2 = cotask.Task(robot_control, name="Task_2", priority=1, period=5,
                        profile=True, trace=False, shares=(velocity_setpoint, yaw_setpoint, control_flag, omega_L_setpoint, omega_R_setpoint,
                                                           omega_L_actual, omega_R_actual))
    
    task3 = cotask.Task(motor_L_control, name="Task_3", priority=1, period=2,
                        profile=True, trace=False, shares=(omega_L_setpoint, omega_L_actual, control_flag))
    
    task4 = cotask.Task(motor_R_control, name="Task_4", priority=1, period=2,
                        profile=True, trace=False, shares=(omega_R_setpoint, omega_R_actual, control_flag)) 
    
    task5 = cotask.Task(driving_mode, name="Task_5", priority=3, period=25,
                        profile=True, trace=False, shares=(velocity_setpoint, yaw_setpoint, control_flag, calibration_flag)) 
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)

    # Run the memory garbage collector to ensure memory is as defragmented as possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break