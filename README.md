# ME-405-Romi


## Wiring
| Connection       | Signal        | Nucleo Pin    | Romi PDB Pin |
|------------------|---------------|---------------|--------------|
| Left Encoder     | Enc Ch A      | B5 (Tim 3)    | ELA          |
|                  | Enc Ch B      | B4 (Tim 3)    | ELB          |
| Right Encoder    | Enc Ch A      | A1 (Tim 2)    | ERA          |
|                  | Enc Ch B      | A0 (Tim 2)    | ERB          |
| Left Motor       | Enable        | A9            | SLP          |
|                  | Direction     | A8            | DIR          |
|                  | Effort        | B6 (Tim 4)    | PWM          |
| Right Motor      | Enable        | C9            | SLP          |
|                  | Direction     | C8            | DIR          |
|                  | Effort        | C6 (Tim 8)    | PWM          |
| Power            | Ground        | GND           | GND          |
|                  | Power         | VIN           | VSW          |
| I2C              | SCL           | B8            | N/A          |
|                  | SDA           | B9            | N/A          |
| HC-05 Bluetooth  | RX            | C4            | N/A          |
|                  | TX            | C5            | N/A          |
| Left Bumper      | BMP           | B14           | N/A          |
|                  | GND           | GND           | N/A          |
| Right Bumper     | BMP           | C7            | N/A          |
|                  | GND           | GND           | N/A          |
| Line Sensor      | VIN           | 5V            | N/A          |
|                  | GND           | GND           | N/A          |
|                  | S0 (R)        | A4            | N/A          |
|                  | S1            | B0            | N/A          |
|                  | S2            | C1            | N/A          |
|                  | S3            | C0            | N/A          |
|                  | S4            | A6            | N/A          |
|                  | S5            | A7            | N/A          |
|                  | S6            | B1            | N/A          |
|                  | S7 (L)        | C3            | N/A          |
