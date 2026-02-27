# ST3215 Servo Control Library - User Manual

Complete API reference and technical documentation for the ST3215 Python library.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Class Initialization](#class-initialization)
4. [Servo Discovery Methods](#servo-discovery-methods)
5. [Read Methods](#read-methods)
6. [Write Methods](#write-methods)
7. [Motion Control Methods](#motion-control-methods)
8. [Configuration Methods](#configuration-methods)
9. [Advanced Methods](#advanced-methods)
10. [Constants and Register Values](#constants-and-register-values)
11. [Error Handling](#error-handling)
12. [Communication Protocol Details](#communication-protocol-details)

---

## Introduction

The ST3215 library provides a comprehensive Python interface for controlling ST3215 serial bus servo motors. This library implements the ST3215 communication protocol over UART/RS485 serial connections.

### Key Features

- Full control over servo position, speed, and acceleration
- Multiple operation modes (Position, Speed, PWM, Step)
- Real-time monitoring of voltage, current, temperature, and load
- Servo calibration and position correction
- Configuration management (ID, baudrate, limits)
- Synchronous group operations for multiple servos
- Thread-safe operations with mutex locking

### Supported Platforms

- Linux (Raspberry Pi, Ubuntu, Debian)
- Windows (with appropriate serial drivers)
- macOS

---

## Installation

### Prerequisites

```bash
# System requirements
Python >= 3.10
pyserial library
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/Mickael-Roger/python-st3215
cd python-st3215

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Install Dependencies Only

```bash
pip install pyserial
```

---

## Class Initialization

### ST3215(device)

Initialize the ST3215 servo controller.

**Parameters:**
- `device` (str): Serial port device path
  - Linux: `/dev/ttyUSB0`, `/dev/ttyAMA0`
  - Windows: `COM3`, `COM4`
  - macOS: `/dev/cu.usbserial-*`

**Raises:**
- `ValueError`: If the serial port cannot be opened

**Example:**

```python
from st3215 import ST3215

# Linux
servo = ST3215("/dev/ttyUSB0")

# Windows
servo = ST3215("COM3")

# Raspberry Pi GPIO UART
servo = ST3215("/dev/ttyAMA0")
```

**Notes:**
- Default baudrate: 1,000,000 bps (1M)
- Serial parameters: 8N1 (8 data bits, no parity, 1 stop bit)
- Port automatically opens on initialization
- Initializes GroupSyncWrite for bulk operations

---

## Servo Discovery Methods

### LinkServo(sts_id)

Check if a servo is present and responding on the bus.

**Parameters:**
- `sts_id` (int): Servo ID (0-253)

**Returns:**
- `bool`: `True` if servo responds, `False` otherwise

**Example:**

```python
if servo.LinkServo(1):
    print("Servo ID 1 detected")
else:
    print("No response from servo ID 1")
```

**Use Cases:**
- Verify servo connection before operations
- Check if servo is powered and functioning
- Validate servo ID before configuration changes

---

### ListServos()

Scan the entire bus to discover all connected servos.

**Parameters:**
- None

**Returns:**
- `list[int]`: List of detected servo IDs

**Example:**

```python
servos = servo.ListServos()
print(f"Found servos: {servos}")
# Output: Found servos: [1, 2, 3, 5]
```

**Warning:**
- This method scans IDs 0-253, which can take 10-30 seconds
- Only use during initialization or diagnosis
- For production use, maintain a list of known servo IDs

---

## Read Methods

### ReadLoad(sts_id)

Read the current load on the servo motor.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `float`: Load percentage (0.0-100.0%)
- `None`: Communication error

**Example:**

```python
load = servo.ReadLoad(1)
if load is not None:
    print(f"Servo load: {load:.1f}%")
    if load > 80:
        print("Warning: High load detected!")
```

**Notes:**
- Load is calculated from motor control duty cycle
- High loads (>80%) may indicate mechanical resistance
- Unit: Percentage of maximum rated load

---

### ReadVoltage(sts_id)

Read the current supply voltage of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `float`: Voltage in volts (V)
- `None`: Communication error

**Example:**

```python
voltage = servo.ReadVoltage(1)
if voltage is not None:
    print(f"Supply voltage: {voltage:.1f}V")
    if voltage < 6.0:
        print("Warning: Low voltage!")
```

**Notes:**
- Recommended operating voltage: 6V-12.6V
- Resolution: 0.1V
- Low voltage may cause erratic behavior

---

### ReadCurrent(sts_id)

Read the current consumption of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `float`: Current in milliamps (mA)
- `None`: Communication error

**Example:**

```python
current = servo.ReadCurrent(1)
if current is not None:
    print(f"Current draw: {current:.1f}mA")
    if current > 2000:
        print("Warning: High current draw!")
```

**Notes:**
- Resolution: 6.5mA
- Normal operation: 100-500mA
- High current may indicate mechanical obstruction

---

### ReadTemperature(sts_id)

Read the internal temperature of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Temperature in degrees Celsius (°C)
- `None`: Communication error

**Example:**

```python
temp = servo.ReadTemperature(1)
if temp is not None:
    print(f"Temperature: {temp}°C")
    if temp > 70:
        print("Warning: Overheating!")
```

**Notes:**
- Operating range: -20°C to 80°C
- Automatic shutdown at 85°C
- Prolonged operation above 70°C reduces lifespan

---

### ReadAccelaration(sts_id)

Read the current acceleration setting.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Acceleration value (0-254)
- `None`: Communication error

**Example:**

```python
acc = servo.ReadAccelaration(1)
if acc is not None:
    print(f"Acceleration: {acc} (x100 step/s²)")
    print(f"Actual: {acc * 100} step/s²")
```

**Notes:**
- Unit: 100 step/s²
- Range: 0-254 (0-25,400 step/s²)
- Higher values = faster acceleration

---

### ReadMode(sts_id)

Read the current operational mode of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Mode value
  - `0`: Position control mode
  - `1`: Constant speed (rotation) mode
  - `2`: PWM mode
  - `3`: Step servo mode
- `None`: Communication error

**Example:**

```python
mode = servo.ReadMode(1)
mode_names = {0: "Position", 1: "Speed", 2: "PWM", 3: "Step"}
if mode is not None:
    print(f"Current mode: {mode_names.get(mode, 'Unknown')}")
```

---

### ReadCorrection(sts_id)

Read the current position correction offset.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Correction value in steps (-2047 to +2047)
- `None`: Communication error

**Example:**

```python
correction = servo.ReadCorrection(1)
if correction is not None:
    print(f"Position correction: {correction} steps")
```

**Notes:**
- Used for mechanical calibration
- Persisted in EEPROM
- Applied automatically to all position commands

---

### ReadStatus(sts_id)

Read the status of all servo diagnostic sensors.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `dict`: Dictionary of status flags
  - `"Voltage"`: Voltage status OK
  - `"Sensor"`: Position sensor status OK
  - `"Temperature"`: Temperature status OK
  - `"Current"`: Current status OK
  - `"Angle"`: Angle limit status OK
  - `"Overload"`: Overload status OK
- `None`: Communication error

**Example:**

```python
status = servo.ReadStatus(1)
if status:
    for sensor, ok in status.items():
        status_str = "✓" if ok else "✗"
        print(f"{sensor}: {status_str}")
    
    if not status["Temperature"]:
        print("Alert: Temperature fault!")
```

**Notes:**
- `True` = Normal operation
- `False` = Fault detected
- Check this regularly during operation

---

### ReadPosition(sts_id)

Read the current position of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Position value (0-4095)
- `None`: Communication error

**Example:**

```python
position = servo.ReadPosition(1)
if position is not None:
    print(f"Current position: {position}")
    
    # Convert to degrees (360° / 4096 steps)
    degrees = (position / 4095) * 360
    print(f"Position: {degrees:.1f}°")
```

**Notes:**
- Resolution: 4096 steps per revolution
- Position 2048 is typically the center position
- 0° = 0, 180° = 2048, 360° = 4095

---

### ReadSpeed(sts_id)

Read the current speed of the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `tuple`: (speed, comm_result, error)
  - `speed` (int): Speed in steps/second (signed)
  - `comm_result` (int): Communication result code
  - `error` (int): Error code
- Negative speed indicates counter-clockwise rotation

**Example:**

```python
speed, comm, error = servo.ReadSpeed(1)
if comm == 0 and error == 0:
    direction = "CW" if speed >= 0 else "CCW"
    print(f"Speed: {abs(speed)} step/s ({direction})")
```

---

### IsMoving(sts_id)

Check if the servo is currently moving.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `bool`: `True` if moving, `False` if stopped
- `None`: Communication error

**Example:**

```python
# Start movement
servo.MoveTo(1, 3000)

# Wait for completion
import time
while servo.IsMoving(1):
    print("Moving...")
    time.sleep(0.1)
print("Movement complete!")
```

---

## Write Methods

### SetAcceleration(sts_id, acc)

Configure the acceleration for servo movements.

**Parameters:**
- `sts_id` (int): Servo ID
- `acc` (int): Acceleration value (0-254)
  - Unit: 100 step/s²
  - Range: 0-25,400 step/s²

**Returns:**
- `True`: Success
- `None`: Communication error

**Example:**

```python
# Set moderate acceleration
servo.SetAcceleration(1, 50)  # 5,000 step/s²

# Set high acceleration for fast response
servo.SetAcceleration(1, 200)  # 20,000 step/s²

# Set low acceleration for smooth motion
servo.SetAcceleration(1, 20)  # 2,000 step/s²
```

**Notes:**
- Higher values = faster acceleration, more mechanical stress
- Lower values = smoother motion, longer movement time
- Affects all subsequent movements

---

### SetSpeed(sts_id, speed)

Configure the maximum speed for servo movements.

**Parameters:**
- `sts_id` (int): Servo ID
- `speed` (int): Speed value (0-3400)
  - Unit: steps/second
  - Maximum: 3400 step/s

**Returns:**
- `True`: Success
- `None`: Communication error

**Example:**

```python
# Set moderate speed
servo.SetSpeed(1, 2400)  # Default speed

# Set slow speed for precision
servo.SetSpeed(1, 500)

# Set maximum speed
servo.SetSpeed(1, 3400)
```

**Notes:**
- Only affects position mode movements
- Does not apply to rotation mode

---

### StopServo(sts_id)

Stop the servo immediately by disabling torque.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `True`: Success
- `None`: Communication error

**Example:**

```python
# Emergency stop
servo.StopServo(1)

# Servo can now be moved freely by hand
```

**Warning:**
- Servo loses holding torque
- Position may drift under load
- Use `StartServo()` to re-enable

---

### StartServo(sts_id)

Enable torque on the servo.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- Communication result tuple
- `None`: Communication error

**Example:**

```python
# Enable servo
servo.StartServo(1)

# Servo now maintains position with torque
```

**Notes:**
- Must be called after `StopServo()` to resume control
- Servo will hold current position

---

### SetMode(sts_id, mode)

Set the operational mode of the servo.

**Parameters:**
- `sts_id` (int): Servo ID
- `mode` (int): Mode value
  - `0`: Position control mode
  - `1`: Constant speed mode (continuous rotation)
  - `2`: PWM mode (direct motor control)
  - `3`: Step servo mode

**Returns:**
- Communication result tuple
- `None`: Communication error

**Example:**

```python
# Position mode (default)
servo.SetMode(1, 0)
servo.MoveTo(1, 2048)

# Rotation mode
servo.SetMode(1, 1)
servo.Rotate(1, 500)  # Rotate at 500 step/s
```

**Notes:**
- Mode change takes effect immediately
- Position limits ignored in rotation mode

---

### CorrectPosition(sts_id, correction)

Apply a permanent position correction offset.

**Parameters:**
- `sts_id` (int): Servo ID
- `correction` (int): Correction in steps (-2047 to +2047)

**Returns:**
- Communication result tuple
- `None`: Communication error

**Example:**

```python
# Correct for mechanical offset
servo.CorrectPosition(1, 100)  # Shift +100 steps

# Remove correction
servo.CorrectPosition(1, 0)

# Negative correction
servo.CorrectPosition(1, -50)
```

**Notes:**
- Correction is persistent (stored in EEPROM)
- Applied to all position commands
- Useful for mechanical calibration

---

## Motion Control Methods

### MoveTo(sts_id, position, speed=2400, acc=50, wait=False)

Move servo to a target position with specified speed and acceleration.

**Parameters:**
- `sts_id` (int): Servo ID
- `position` (int): Target position (0-4095)
- `speed` (int, optional): Movement speed in step/s (default: 2400)
- `acc` (int, optional): Acceleration value (default: 50)
- `wait` (bool, optional): Block until movement completes (default: False)

**Returns:**
- `True`: Command sent successfully
- `None`: Communication error

**Example:**

```python
# Simple move
servo.MoveTo(1, 2048)

# Move with custom speed and acceleration
servo.MoveTo(1, 3000, speed=3400, acc=100)

# Blocking move (wait for completion)
servo.MoveTo(1, 1000, speed=2400, acc=50, wait=True)
print("Movement complete!")

# Move multiple servos simultaneously
servo.MoveTo(1, 2048)
servo.MoveTo(2, 2048)
servo.MoveTo(3, 2048)
```

**Notes:**
- Automatically switches to position mode (mode 0)
- Wait time is calculated based on distance, speed, and acceleration
- Non-blocking by default for concurrent movement

---

### WritePosition(sts_id, position)

Directly write target position (low-level method).

**Parameters:**
- `sts_id` (int): Servo ID
- `position` (int): Target position (0-4095)

**Returns:**
- `True`: Success
- `None`: Communication error

**Example:**

```python
# Direct position write (no speed/acceleration setup)
servo.WritePosition(1, 2048)
```

**Notes:**
- Uses existing speed and acceleration settings
- `MoveTo()` is recommended for most use cases

---

### Rotate(sts_id, speed)

Rotate servo continuously at specified speed.

**Parameters:**
- `sts_id` (int): Servo ID
- `speed` (int): Rotation speed (-3400 to +3400 step/s)
  - Positive: Clockwise
  - Negative: Counter-clockwise

**Returns:**
- Communication result tuple
- `None`: Communication error

**Example:**

```python
# Rotate clockwise at moderate speed
servo.Rotate(1, 500)

# Rotate counter-clockwise
servo.Rotate(1, -500)

# Maximum speed rotation
servo.Rotate(1, 3400)

# Stop rotation
servo.Rotate(1, 0)
```

**Notes:**
- Automatically switches to rotation mode (mode 1)
- Position limits are ignored
- Servo rotates indefinitely until speed changed or stopped

---

### getBlockPosition(sts_id)

Wait for servo to reach a blocking position (mechanical limit).

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Final position when blocked
- `None`: Error or timeout

**Example:**

```python
# Find mechanical limit
servo.Rotate(1, -500)  # Rotate toward limit
limit_pos = servo.getBlockPosition(1)
if limit_pos is not None:
    print(f"Mechanical limit at position: {limit_pos}")
```

**Warning:**
- Only use with servos that have mechanical stops
- Can cause mechanical wear if used excessively
- Servo is stopped and returned to position mode

---

### DefineMiddle(sts_id)

Set the current position as the middle point (position 2048).

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `True`: Success
- `None`: Communication error

**Example:**

```python
# Manually position servo to desired center
input("Position servo to center, then press Enter...")

# Set current position as center
servo.DefineMiddle(1)
```

**Notes:**
- Sets torque to 128 (moderate holding force)
- Useful for initial calibration

---

### TareServo(sts_id)

Automatic servo calibration by finding mechanical limits.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `tuple`: (min_position, max_position)
- `(None, None)`: Error or timeout

**Example:**

```python
# Automatic calibration
print("Calibrating servo (ensure no obstructions)...")
min_pos, max_pos = servo.TareServo(1)

if min_pos is not None:
    print(f"Calibration complete!")
    print(f"Range: {min_pos} to {max_pos}")
    print(f"Total range: {max_pos - min_pos} steps")
else:
    print("Calibration failed!")
```

**Warning:**
- **Only use with servos that have mechanical stops**
- **Never use with continuous rotation servos**
- Servo will rotate to find both limits
- Process takes 5-10 seconds
- Ensure adequate clearance before running

**Process:**
1. Clears any existing correction
2. Rotates counter-clockwise to find min limit
3. Rotates clockwise to find max limit
4. Sets center of range as position 2048
5. Applies correction offset

---

## Configuration Methods

### LockEprom(sts_id)

Lock the servo EEPROM to prevent accidental configuration changes.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Communication result code
- `0` (COMM_SUCCESS): Success

**Example:**

```python
# Lock configuration
result = servo.LockEprom(1)
if result == 0:
    print("EEPROM locked")
```

**Notes:**
- Must be locked before removing power to save changes
- Prevents accidental ID or baudrate changes

---

### UnLockEprom(sts_id)

Unlock the servo EEPROM to allow configuration changes.

**Parameters:**
- `sts_id` (int): Servo ID

**Returns:**
- `int`: Communication result code
- `0` (COMM_SUCCESS): Success

**Example:**

```python
# Unlock for configuration
result = servo.UnLockEprom(1)
if result == 0:
    print("EEPROM unlocked")
    # Can now change ID, baudrate, limits, etc.
```

---

### ChangeId(sts_id, new_id)

Change the ID of a servo.

**Parameters:**
- `sts_id` (int): Current servo ID
- `new_id` (int): New ID (0-253)

**Returns:**
- `None`: Success
- `str`: Error message if failed

**Example:**

```python
# Change ID from 1 to 5
error = servo.ChangeId(1, 5)
if error is None:
    print("ID changed successfully!")
    # Must now use ID 5 to communicate
else:
    print(f"Failed: {error}")
```

**Warning:**
- Ensure new ID is not already in use
- Cannot ping servo with old ID after change
- New servos typically have ID 1 by default

---

### ChangeBaudrate(sts_id, new_baudrate)

Change the communication baudrate of a servo.

**Parameters:**
- `sts_id` (int): Servo ID
- `new_baudrate` (int): Baudrate code (0-7)
  - `0`: 1M bps (1,000,000)
  - `1`: 0.5M bps (500,000)
  - `2`: 250K bps (250,000)
  - `3`: 128K bps (128,000)
  - `4`: 115.2K bps (115,200)
  - `5`: 76.8K bps (76,800)
  - `6`: 57.6K bps (57,600)
  - `7`: 38.4K bps (38,400)

**Returns:**
- `None`: Success
- `str`: Error message if failed

**Example:**

```python
# Change to 115200 bps
error = servo.ChangeBaudrate(1, 4)
if error is None:
    print("Baudrate changed!")
    # Must reinitialize with new baudrate
else:
    print(f"Failed: {error}")
```

**Warning:**
- Must close and reopen connection with new baudrate
- All servos on bus must use same baudrate
- Lower baudrates more reliable over long distances

---

## Advanced Methods

### Group Sync Write

The library includes `GroupSyncWrite` for efficient bulk operations.

**Example:**

```python
# Move multiple servos simultaneously with one command
from st3215.group_sync_write import GroupSyncWrite

gsw = GroupSyncWrite(servo, START_ADDRESS, DATA_LENGTH)
gsw.addParam(1, [data1])
gsw.addParam(2, [data2])
result = gsw.txPacket()
```

**Use Cases:**
- Coordinated multi-servo movements
- Synchronized robot arm control
- Reduced bus communication overhead

---

### Group Sync Read

The library includes `GroupSyncRead` for efficient bulk reads.

**Example:**

```python
# Read positions from multiple servos simultaneously
from st3215.group_sync_read import GroupSyncRead

gsr = GroupSyncRead(servo, START_ADDRESS, DATA_LENGTH)
gsr.addParam(1)
gsr.addParam(2)
result = gsr.txRxPacket()
```

---

## Constants and Register Values

### Position Constants

```python
MIN_POSITION = 0
MAX_POSITION = 4095
```

### Speed Constants

```python
MAX_SPEED = 3400  # steps per second
```

### Correction Constants

```python
MAX_CORRECTION = 2047  # ±2047 steps
```

### Baudrate Codes

```python
STS_1M = 0       # 1,000,000 bps (default)
STS_0_5M = 1     # 500,000 bps
STS_250K = 2     # 250,000 bps
STS_128K = 3     # 128,000 bps
STS_115200 = 4   # 115,200 bps
STS_76800 = 5    # 76,800 bps
STS_57600 = 6    # 57,600 bps
STS_38400 = 7    # 38,400 bps
```

### Communication Result Codes

```python
COMM_SUCCESS = 0        # Success
COMM_PORT_BUSY = -1     # Port in use
COMM_TX_FAIL = -2       # Transmit failed
COMM_RX_FAIL = -3       # Receive failed
COMM_TX_ERROR = -4      # Incorrect packet
COMM_RX_WAITING = -5    # Receiving
COMM_RX_TIMEOUT = -6    # No response
COMM_RX_CORRUPT = -7    # Corrupt packet
COMM_NOT_AVAILABLE = -9 # Not available
```

### Operation Modes

```python
MODE_POSITION = 0  # Position control
MODE_SPEED = 1     # Constant speed (rotation)
MODE_PWM = 2       # PWM direct control
MODE_STEP = 3      # Step servo mode
```

### EEPROM Registers

```python
STS_ID = 5                # Servo ID
STS_BAUD_RATE = 6         # Baudrate setting
STS_MIN_ANGLE_LIMIT_L = 9 # Min angle limit (low byte)
STS_MAX_ANGLE_LIMIT_L = 11 # Max angle limit (low byte)
STS_OFS_L = 31            # Position correction offset
STS_MODE = 33             # Operation mode
```

### SRAM Registers (Volatile)

```python
STS_TORQUE_ENABLE = 40      # Torque enable/disable
STS_ACC = 41                # Acceleration
STS_GOAL_POSITION_L = 42    # Target position
STS_GOAL_SPEED_L = 46       # Target speed
STS_PRESENT_POSITION_L = 56 # Current position
STS_PRESENT_SPEED_L = 58    # Current speed
STS_PRESENT_LOAD_L = 60     # Current load
STS_PRESENT_VOLTAGE = 62    # Current voltage
STS_PRESENT_TEMPERATURE = 63 # Temperature
STS_PRESENT_CURRENT_L = 69  # Current draw
STS_STATUS = 65             # Status flags
STS_MOVING = 66             # Moving flag
```

---

## Error Handling

### Communication Errors

All read/write methods return `None` on communication failure.

**Example:**

```python
position = servo.ReadPosition(1)
if position is None:
    print("Communication error!")
    # Check connection
    # Verify servo ID
    # Check power supply
else:
    print(f"Position: {position}")
```

### Timeout Handling

```python
import time

max_retries = 3
for attempt in range(max_retries):
    result = servo.LinkServo(1)
    if result:
        break
    print(f"Retry {attempt + 1}/{max_retries}")
    time.sleep(0.5)
else:
    print("Servo not responding after retries")
```

### Status Check Pattern

```python
status = servo.ReadStatus(1)
if status:
    errors = [k for k, v in status.items() if not v]
    if errors:
        print(f"Faults detected: {', '.join(errors)}")
    else:
        print("All systems normal")
```

---

## Communication Protocol Details

### Packet Structure

```
[Header0][Header1][ID][Length][Instruction][Param...][Checksum]
```

### Instruction Types

```python
INST_PING = 1        # Check servo presence
INST_READ = 2        # Read data
INST_WRITE = 3       # Write data
INST_REG_WRITE = 4   # Registered write
INST_ACTION = 5      # Execute registered write
INST_SYNC_WRITE = 131 # Synchronous write
INST_SYNC_READ = 130  # Synchronous read
```

### Thread Safety

The library uses threading locks for safe concurrent access:

```python
# Thread-safe operation
import threading

def move_servo_1():
    servo.MoveTo(1, 2048)

def move_servo_2():
    servo.MoveTo(2, 2048)

t1 = threading.Thread(target=move_servo_1)
t2 = threading.Thread(target=move_servo_2)
t1.start()
t2.start()
t1.join()
t2.join()
```

---

## Best Practices

1. **Always check return values**
   ```python
   if servo.MoveTo(1, 2048) is None:
       print("Move command failed!")
   ```

2. **Initialize with error handling**
   ```python
   try:
       servo = ST3215("/dev/ttyUSB0")
   except ValueError as e:
       print(f"Cannot open port: {e}")
       exit(1)
   ```

3. **Monitor servo health**
   ```python
   temp = servo.ReadTemperature(1)
   voltage = servo.ReadVoltage(1)
   if temp and temp > 70:
       print("Warning: High temperature!")
   if voltage and voltage < 6.0:
       print("Warning: Low voltage!")
   ```

4. **Use appropriate acceleration**
   ```python
   # Smooth motion for delicate operations
   servo.SetAcceleration(1, 20)
   
   # Fast response for quick movements
   servo.SetAcceleration(1, 150)
   ```

5. **Clean shutdown**
   ```python
   # Stop all servos before exit
   for servo_id in [1, 2, 3]:
       servo.StopServo(servo_id)
   ```

---

## Related Documentation

- [User Guide](user_guide.md) - Step-by-step tutorials
- [Troubleshooting](troubleshooting.md) - Common issues
- [FAQ](FAQ.md) - Frequently asked questions

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
