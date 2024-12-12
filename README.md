# ME-405-Romi
## Project Overview
![Romi](images/romi.JPG "Romi")
This is the repository for the ME 405 term project that required building and programming a line following robot using Romi. The robot follows a black line from the start box to the finish box and navigates around a wall obstacle along the way. After finishing, the robot drives back to start and prepares for another run.

[Watch Romi complete the course.](https://cpslo-my.sharepoint.com/:v:/g/personal/cobentle_calpoly_edu/EVazc3-Y6zpHkRecavvJRQMB5AY1bCsFI095H2HzwaM4ng?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=TcedAd)

## Hardware
The robot is built off a Romi chassis and controlled using a Nucleo L476RG running MicroPython. An additional circuit board called the Shoe of Brian attaches to the Nucleo. Information about the shoe and general support for the techniques used in this project can be found [here](https://github.com/spluttflob/ME405-Support).

![Romi Front](images/romi-front.JPG "Romi Front")

The Nucleo attaches to standoffs and an acrylic mount as shown in this [model](https://cad.onshape.com/documents/b78783ff999bc8e6a9990234). The IMU and optional Bluetooth module are taped to the sides of the acrylic mount. The bump sensors screw directly to the front of the chassis, and the line sensor is taped to the line sensor mount which taped to the chassis.

![Romi Bottom](images/romi-bottom.JPG "Romi Bottom")

### Wiring

