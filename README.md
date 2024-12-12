# ME-405-Romi
## Project Overview
![Romi](images/romi.JPG "Romi")
**Figure 1:** Complete robot
This is the repository for the ME 405 term project that required building and programming a line following robot using Romi. The robot follows a black line from the start box to the finish box and navigates around a wall obstacle along the way. After finishing, the robot drives back to start and prepares for another run.

[Watch Romi complete the course.](https://cpslo-my.sharepoint.com/:v:/g/personal/cobentle_calpoly_edu/EVazc3-Y6zpHkRecavvJRQMB5AY1bCsFI095H2HzwaM4ng?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=TcedAd)

## Hardware
The robot is built off a Romi chassis and controlled using a Nucleo L476RG running MicroPython. An additional circuit board called the Shoe of Brian attaches to the Nucleo. Information about the shoe and general support for the techniques used in this project can be found [here](https://github.com/spluttflob/ME405-Support).

![Romi Front](images/romi-front.JPG "Romi Front")
**Figure 2:** Romi front with IMU and bluetooth module shown on the sides

The Nucleo attaches to standoffs and an acrylic mount as shown in this [model](https://cad.onshape.com/documents/b78783ff999bc8e6a9990234). The IMU and optional Bluetooth module are taped to the sides of the acrylic mount. The bump sensors screw directly to the front of the chassis, and the line sensor is taped to the line sensor mount which taped to the chassis.

![Romi Bottom](images/romi-bottom.JPG "Romi Bottom")
**Figure 3:** Romi bottom with line sensor

**Table 1:** Complete BOM
| Part                           | Supplier  | P/N    | Additional Info                                                                 |
|--------------------------------|-----------|--------|---------------------------------------------------------------------------------|
| Microcontroller                | Nucleo    | L476RG |                                                                                 |
| Shoe of Brian                  | Custom    | N/A    | [OSH Park Link](https://oshpark.com/shared_projects/e6X6OnYK)                   |
| Romi Chassis Kit               | Pololu    | 3509   |                                                                                 |
| Motor Driver and Power Distribution Board | Pololu | 3543   |                                                                                 |
| Line Sensor                    | Pololu    | 3672   |                                                                                 |
| Right Bumper                   | Pololu    | 3674   |                                                                                 |
| Left Bumper                    | Pololu    | 3673   |                                                                                 |
| IMU                            | Adafruit  | 2472   |                                                                                 |
| Bluetooth Module               |           |        | Optional                                                                       |
| Line Sensor Mount              | Custom    | N/A    | line-sensor-mount.STEP                                                         |
| Misc. mounts and fasteners     | N/A       | N/A    | [Onshape Link](https://cad.onshape.com/documents/b78783ff999bc8e6a9990234)      |

### Wiring
