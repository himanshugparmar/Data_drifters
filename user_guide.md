# ST3215 Servo Control Library - User Guide

Step-by-step tutorials, examples, and practical applications for the ST3215 Python library.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Operations](#basic-operations)
3. [Position Control Tutorial](#position-control-tutorial)
4. [Speed Control Tutorial](#speed-control-tutorial)
5. [Multi-Servo Control](#multi-servo-control)
6. [Servo Calibration](#servo-calibration)
7. [Monitoring and Diagnostics](#monitoring-and-diagnostics)
8. [Configuration Management](#configuration-management)
9. [Advanced Techniques](#advanced-techniques)
10. [Complete Project Examples](#complete-project-examples)
11. [Testing](#testing)
12. [Performance Optimization](#performance-optimization)
13. [Linking Servos](#linking-servos) **[New Section]**

---

## Getting Started

### Hardware Setup

#### Required Components

1. **ST3215 Servo Motor(s)**
2. **USB to TTL/RS485 Converter**
   - FTDI FT232, CH340, CP2102, etc.
3. **Power Supply**
   - 6V-12.6V DC
   - Minimum 2A per servo
4. **Connection Cables**
   - 3-pin servo connectors or wire harness

#### Wiring Diagram

```
ST3215 Servo      USB-TTL Converter      Computer
┌─────────────┐   ┌─────────────┐      ┌──────────┐
│  GND (Black)├───┤ GND         │      │          │
│  VCC (Red)  ├─┐ │             │      │          │
│  DATA(White)├─┼─┤ TX/RX       ├──USB─┤ /dev/USB0│
└─────────────┘ │ └─────────────┘      └──────────┘
                │
                │ External Power Supply
                │ (6-12.6V, 2A+)
                └─[GND]─[VCC]─
```

**Important Notes:**
- **Never power servos from USB** (insufficient current)
- **Use separate power supply** for servos
- **Share common ground** between power supply and USB converter
- **Check voltage polarity** before connecting

#### Raspberry Pi GPIO UART

```python
# Enable UART on Raspberry Pi
# Edit /boot/config.txt:
# enable_uart=1
# dtoverlay=disable-bt

# Use GPIO 14 (TX) and 15 (RX)
servo = ST3215("/dev/ttyAMA0")
```

### Software Installation

#### Step 1: System Preparation

```bash
# Update system (Linux/Raspberry Pi)
sudo apt update
sudo apt upgrade

# Install Python 3.10+ if needed
python3 --version
```

#### Step 2: Install Dependencies

```bash
# Install pyserial
pip install pyserial

# Or use requirements.txt
pip install -r requirements.txt
```

#### Step 3: Set Permissions (Linux)

```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# Log out and log back in for changes to take effect

# Or use temporary permission (not recommended)
sudo chmod 666 /dev/ttyUSB0
```

#### Step 4: Install ST3215 Library

```bash
# From source
git clone https://github.com/Mickael-Roger/python-st3215
cd python-st3215
pip install -e .

# Verify installation
python3 -c "from st3215 import ST3215; print('Success!')"
```

### First Connection Test

```python
#!/usr/bin/env python3
"""Test basic servo connection"""

from st3215 import ST3215
import sys

# Serial port configuration
DEVICE = "/dev/ttyUSB0"  # Change to your port
SERVO_ID = 1

try:
    # Initialize connection
    print(f"Connecting to {DEVICE}...")
    servo = ST3215(DEVICE)
    print("✓ Connection established")
    
    # Test servo communication
    print(f"\nTesting servo ID {SERVO_ID}...")
    if servo.PingServo(SERVO_ID):
        print(f"✓ Servo {SERVO_ID} responding!")
        
        # Read basic info
        voltage = servo.ReadVoltage(SERVO_ID)
        temp = servo.ReadTemperature(SERVO_ID)
        position = servo.ReadPosition(SERVO_ID)
        
        print(f"\nServo Status:")
        print(f"  Voltage: {voltage:.1f}V")
        print(f"  Temperature: {temp}°C")
        print(f"  Position: {position}")
        
    else:
        print(f"✗ No response from servo {SERVO_ID}")
        print("\nTroubleshooting:")
        print("  1. Check power supply (6-12V)")
        print("  2. Verify wiring connections")
        print("  3. Confirm servo ID is 1")
        print("  4. Try scanning all IDs: servo.ListServos()")
        
except ValueError as e:
    print(f"\n✗ Cannot open serial port: {e}")
    print("\nTroubleshooting:")
    print("  1. Check device path (ls /dev/tty*)")
    print("  2. Verify USB converter is connected")
    print("  3. Check user permissions (groups command)")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

print("\n✓ Setup complete!")
```

**Save as:** `test_connection.py`

**Run:**
```bash
chmod +x test_connection.py
./test_connection.py
```

---

## Basic Operations

### Initializing the Library

```python
from st3215 import ST3215

# Linux/Raspberry Pi
servo = ST3215("/dev/ttyUSB0")

# Windows
servo = ST3215("COM3")

# macOS
servo = ST3215("/dev/cu.usbserial-1420")
```

### Finding Servos

```python
# Quick check for specific ID
if servo.PingServo(1):
    print("Servo 1 found!")

# Scan all IDs (takes 15-30 seconds)
print("Scanning for servos...")
servos = servo.ListServos()
print(f"Found {len(servos)} servos: {servos}")

# Example output: Found 3 servos: [1, 2, 3]
```

### Reading Servo Information

```python
servo_id = 1

# Read all key parameters
voltage = servo.ReadVoltage(servo_id)
current = servo.ReadCurrent(servo_id)
temperature = servo.ReadTemperature(servo_id)
position = servo.ReadPosition(servo_id)
load = servo.ReadLoad(servo_id)

print(f"Servo {servo_id} Status:")
print(f"  Voltage: {voltage:.1f}V")
print(f"  Current: {current:.1f}mA")
print(f"  Temperature: {temperature}°C")
print(f"  Position: {position}")
print(f"  Load: {load:.1f}%")
```

---

## Position Control Tutorial

Position control mode allows precise positioning of the servo.

### Basic Position Movement

```python
#!/usr/bin/env python3
"""Basic position control example"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Ensure servo is in position mode
servo.SetMode(servo_id, 0)

# Set movement parameters
servo.SetAcceleration(servo_id, 50)  # Moderate acceleration
servo.SetSpeed(servo_id, 2400)       # Moderate speed

# Move to center position
print("Moving to center (2048)...")
servo.MoveTo(servo_id, 2048)
time.sleep(2)

# Move to position 3000
print("Moving to 3000...")
servo.MoveTo(servo_id, 3000)
time.sleep(2)

# Move to position 1000
print("Moving to 1000...")
servo.MoveTo(servo_id, 1000)
time.sleep(2)

# Return to center
print("Returning to center...")
servo.MoveTo(servo_id, 2048)

print("Complete!")
```

### Blocking vs Non-Blocking Movement

```python
# NON-BLOCKING (default)
# Commands returns immediately, servo moves in background
servo.MoveTo(1, 2048)
print("Command sent, but servo still moving...")
# Do other work here
time.sleep(0.5)

# BLOCKING (wait=True)
# Function waits until movement completes
print("Starting blocking move...")
servo.MoveTo(1, 3000, wait=True)
print("Movement finished!")

# Manual blocking with IsMoving
servo.MoveTo(1, 1000)
while servo.IsMoving(1):
    print("Moving...")
    time.sleep(0.1)
print("Arrived at target!")
```

### Smooth vs Fast Movement

```python
# SMOOTH, SLOW MOVEMENT
servo.SetAcceleration(1, 20)   # Low acceleration
servo.SetSpeed(1, 800)         # Low speed
servo.MoveTo(1, 2048)
time.sleep(3)

# FAST, AGGRESSIVE MOVEMENT
servo.SetAcceleration(1, 200)  # High acceleration
servo.SetSpeed(1, 3400)        # Maximum speed
servo.MoveTo(1, 3000)
time.sleep(1)

# BALANCED (recommended for most cases)
servo.SetAcceleration(1, 50)   # Moderate
servo.SetSpeed(1, 2400)        # Moderate
servo.MoveTo(1, 2048)
```

### Position Control with Feedback

```python
#!/usr/bin/env python3
"""Position control with real-time feedback"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

target = 3000
servo.MoveTo(servo_id, target)

print(f"Target: {target}")
print("-" * 40)

# Monitor until arrival
while True:
    position = servo.ReadPosition(servo_id)
    error = abs(target - position)
    
    print(f"Position: {position}, Error: {error} steps", end='\r')
    
    if error < 10 and not servo.IsMoving(servo_id):
        print("\n✓ Target reached!")
        break
    
    time.sleep(0.05)
```

### Angle-Based Control

```python
def position_to_degrees(position):
    """Convert position (0-4095) to degrees (0-360)"""
    return (position / 4095) * 360

def degrees_to_position(degrees):
    """Convert degrees (0-360) to position (0-4095)"""
    return int((degrees / 360) * 4095)

# Move to 90 degrees
position_90 = degrees_to_position(90)
servo.MoveTo(1, position_90)
print(f"Moving to 90°: position {position_90}")

# Move to 180 degrees
position_180 = degrees_to_position(180)
servo.MoveTo(1, position_180)
print(f"Moving to 180°: position {position_180}")

# Read current angle
current_pos = servo.ReadPosition(1)
current_angle = position_to_degrees(current_pos)
print(f"Current angle: {current_angle:.1f}°")
```

---

## Speed Control Tutorial

Speed control (rotation) mode allows continuous rotation.

### Basic Rotation

```python
#!/usr/bin/env python3
"""Basic rotation control"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Rotate clockwise at 500 step/s
print("Rotating clockwise...")
servo.Rotate(servo_id, 500)
time.sleep(3)

# Stop
servo.Rotate(servo_id, 0)
time.sleep(1)

# Rotate counter-clockwise at 500 step/s
print("Rotating counter-clockwise...")
servo.Rotate(servo_id, -500)
time.sleep(3)

# Stop
servo.Rotate(servo_id, 0)

# High speed rotation
print("Maximum speed rotation...")
servo.Rotate(servo_id, 3400)
time.sleep(2)

# Stop rotation
servo.Rotate(servo_id, 0)
print("Stopped")
```

### Variable Speed Control

```python
#!/usr/bin/env python3
"""Gradually increase rotation speed"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Ramp up speed
for speed in range(0, 1500, 100):
    print(f"Speed: {speed} step/s")
    servo.Rotate(servo_id, speed)
    time.sleep(0.5)

# Maintain top speed
time.sleep(2)

# Ramp down speed
for speed in range(1500, 0, -100):
    print(f"Speed: {speed} step/s")
    servo.Rotate(servo_id, speed)
    time.sleep(0.5)

# Stop
servo.Rotate(servo_id, 0)
```

### Speed Control with Load Monitoring

```python
#!/usr/bin/env python3
"""Monitor load during rotation"""

from st3215