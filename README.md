# ME-405-Romi
## Project Overview and Results
![Romi](images/romi.JPG "Romi")
**Figure 1:** Finished robot

This is the repository for the Cal Poly ME-405 term project that required building and programming a line following differential drive robot. The robot follows a black line from the start box to the finish box and navigates around a wall obstacle along the way. After finishing, the robot drives back to start and prepares for another run. The robot features a line sensor, bump sensors, and a 9-DOF absolute orientation IMU to read heading and yaw. The robot can successfully navigate the course. The line following is accurate, even with challenging shapes like dashes and horizontal lines in the path, and the control system results in smooth driving.

[Watch Romi complete the course](https://cpslo-my.sharepoint.com/:v:/g/personal/cobentle_calpoly_edu/EVazc3-Y6zpHkRecavvJRQMB5AY1bCsFI095H2HzwaM4ng?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=TcedAd)

This project has room for future improvements. Currently, the wall navigation parameters have to be preprogrammed. Having the robot slowly bump around the wall similar to a Roomba could make this program more flexible for unknown obstacles while keeping the same bump sensors. The navigation from start to finish relies on the start box being directly behind the robot when it finishes the course. Adding calculations for the robot's postion while running through the course would allow it to drive back to start even if the start and finish boxes were moved. The program could run faster by using an analog line sensor or by configuring the digital sensor to work with interupts to prevent the program from waiting while reading the line. We noticed that battery voltage has a noticable impact on performance, and the control gains should be tuned to the specific voltage for best results.

## Hardware
The robot is built off a Romi chassis and controlled using a Nucleo L476RG running MicroPython. An additional circuit board called the Shoe of Brian attaches to the Nucleo. Information about the shoe and general support for the techniques used in this project can be found [here](https://github.com/spluttflob/ME405-Support).

![Romi Front](images/romi-front.JPG "Romi Front")
**Figure 2:** Romi front view with IMU and bluetooth module shown on the sides

The Nucleo attaches to standoffs and an acrylic mount as shown in this [model](https://cad.onshape.com/documents/b78783ff999bc8e6a9990234). The IMU and optional Bluetooth module are taped to the sides of the acrylic mount. The bump sensors screw directly to the front of the chassis, and the line sensor is taped to the line sensor mount which taped to the chassis.

![Romi Bottom](images/romi-bottom.JPG "Romi Bottom")
**Figure 3:** Romi bottom view with line sensor

Table 1 lists all of the parts besides the jumper wires used in this project.

**Table 1:** Complete BOM
| Part                           | Supplier  | P/N    | Additional Info                                                                 |
|--------------------------------|-----------|--------|---------------------------------------------------------------------------------|
| Microcontroller                | Nucleo    | L476RG |                                                                                 |
| Shoe of Brian                  | Custom    | N/A    | [OSH Park](https://oshpark.com/shared_projects/e6X6OnYK)                   |
| Romi Chassis Kit               | Pololu    | 3509   |                                                                                 |
| Motor Driver and Power Distribution Board | Pololu | 3543   |                                                                                 |
| Line Sensor                    | Pololu    | 3672   |                                                                                 |
| Right Bumper                   | Pololu    | 3674   |                                                                                 |
| Left Bumper                    | Pololu    | 3673   |                                                                                 |
| IMU                            | Adafruit  | 2472   |                                                                                 |
| Bluetooth Module               |           | HC-05  | Optional                                                                       |
| Line Sensor Mount              | Custom    | N/A    | See line-sensor-mount.STEP                                                         |
| Misc. mounts and fasteners     | N/A       | N/A    | [Onshape](https://cad.onshape.com/documents/b78783ff999bc8e6a9990234)      |

Figure 4 is a wiring diagram for the robot and, Table 2 lists the wire connections used.

**Figure 4:** Wiring diagram

**Table 2:** Wire connections
| Device/Function          | Signal              | Nucleo Pin      | Device Pin |
|--------------------------|---------------------|-----------------|------------|
| Left Encoder (Romi PDB)  | Enc Ch A            | B5 (Tim 3)      | ELA        |
|                          | Enc Ch B            | B4 (Tim 3)      | ELB        |
| Right Encoder (Romi PDB) | Enc Ch A            | A1 (Tim 2)      | ERA        |
|                          | Enc Ch B            | A0 (Tim 2)      | ERB        |
| Left Motor (Romi PDB)    | Enable              | A9              | SLP        |
|                          | Direction           | A8              | DIR        |
|                          | Effort              | B6 (Tim 4)      | PWM        |
| Right Motor (Romi PDB)   | Enable              | C9              | SLP        |
|                          | Direction           | C8              | DIR        |
|                          | Effort              | C6 (Tim 8)      | PWM        |
| Power (Romi PDB)         | Ground              | GND             | GND        |
|                          | Power               | VIN             | VSW        |
| I2C                      | SCL                 | B8              | SCL        |
|                          | SDA                 | B9              | SDA        |
| HC-05 Bluetooth          | RX                  | C4              | RX         |
|                          | TX                  | C5              | TX         |
| Left Bumper              | BMP                 | B14             | BMP 3      |
|                          | GND                 | GND             | GND        |
| Right Bumper             | BMP                 | C7              | BMP 2      |
|                          | GND                 | GND             | GND        |
| Line Sensor              | Power               | 5V              | VIN        |
|                          | GND                 | GND             | GND        |
|                          | Sensor 0            | A4              | S0 (R)     |
|                          | Sensor 1            | B0              | S1         |
|                          | Sensor 2            | C1              | S2         |
|                          | Sensor 3            | A3              | S3         |
|                          | Sensor 4            | A6              | S4         |
|                          | Sensor 5            | B1              | S6         |
|                          | Sensor 7            | C3              | S7 (L)     |

## Code
The code folder contains all of the files that need to be stored on the Nucleo in order to run. This project uses MicroPython, which the nucleo needs to be preconfigured with before adding the other files.

### Task Structure
ADD OVERALL TASK DIAGRAM AND INDIVIDUAL FSMs WITH DISCUSSION SIMILAR TO LAB 3

![Planner Task](images/planner-task.png "Planner Task")
**Figure 5:** Planner Task State Transition Diagram

![Robot Control Task](images/robot-control-task.png "Robot Control Task")
**Figure 5:** Robot Control Task State Transition Diagram

![Motor Control Task](images/motor-control-task.png "Motor Control Task")
**Figure 5:** Motor Control Task State Transition Diagram

![Driving Mode Task](images/driving-mode-task.png "Driving Mode Task")
**Figure 5:** Driving Mode Task State Transition Diagram


### Control System
Figure 5 depicts the overall control system for the robot. We specify velocity and setpoints for the robot control loop either manually or using feedback from devices like the line sensor. . The robot control calculates the actual translational velocity using wheel speed measurements from the motor tasks and gathers yaw measurements from the IMU. Both are fed through PI control to become velocity and yaw requests. Omega setpoints are calculated from these requests using the robot parameters and sent to each of the motor control tasks. The motor control tasks perform PI control of the left and right wheel speeds using omega setpoints from the robot control and real omega measurements calculated from the encoders.

![Control System](images/control-system.png "Control System")
**Figure 5:** Overall control system

## Supporting Calculations

