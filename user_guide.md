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
    if servo.LinkServo(SERVO_ID):
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
if servo.LinkServo(1):
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

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Start rotation
servo.Rotate(servo_id, 800)

print("Rotating with load monitoring...")
print("Press Ctrl+C to stop")

try:
    while True:
        load = servo.ReadLoad(servo_id)
        current = servo.ReadCurrent(servo_id)
        
        print(f"Load: {load:.1f}%  Current: {current:.0f}mA", end='\r')
        
        # Safety check
        if load and load > 80:
            print("\n⚠️ High load detected! Stopping...")
            servo.Rotate(servo_id, 0)
            break
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nStopping...")
    servo.Rotate(servo_id, 0)
```

---

## Multi-Servo Control

### Sequential Control

```python
#!/usr/bin/env python3
"""Control multiple servos sequentially"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")

# Configure all servos
servo_ids = [1, 2, 3, 4]
for servo_id in servo_ids:
    servo.SetAcceleration(servo_id, 50)
    servo.SetSpeed(servo_id, 2400)

# Move all to center
print("Moving all servos to center...")
for servo_id in servo_ids:
    servo.MoveTo(servo_id, 2048)
time.sleep(2)

# Create a wave pattern
print("Creating wave pattern...")
positions = [1000, 2000, 3000, 2000]
for i, servo_id in enumerate(servo_ids):
    servo.MoveTo(servo_id, positions[i])
    time.sleep(0.5)  # Stagger movements

time.sleep(2)

# Return all to center
for servo_id in servo_ids:
    servo.MoveTo(servo_id, 2048)
```

### Simultaneous Control

```python
#!/usr/bin/env python3
"""Control multiple servos simultaneously"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_ids = [1, 2, 3, 4]

# Move all servos at the same time (non-blocking)
print("Moving all servos simultaneously...")
servo.MoveTo(1, 3000)
servo.MoveTo(2, 2500)
servo.MoveTo(3, 1500)
servo.MoveTo(4, 1000)

# Wait for all to complete
print("Waiting for all movements to complete...")
while True:
    moving = [servo.IsMoving(sid) for sid in servo_ids]
    if not any(moving):
        break
    time.sleep(0.1)

print("All servos reached target positions!")
```

### Synchronized Movement Pattern

```python
#!/usr/bin/env python3
"""Create synchronized servo choreography"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")

def wait_all_stopped(servo_ids):
    """Wait for all servos to stop moving"""
    while True:
        if not any(servo.IsMoving(sid) for sid in servo_ids):
            break
        time.sleep(0.05)

# Robot arm example: 4 servos
BASE = 1      # Base rotation
SHOULDER = 2  # Shoulder joint
ELBOW = 3     # Elbow joint
WRIST = 4     # Wrist rotation

# Initialize position
print("Moving to home position...")
servo.MoveTo(BASE, 2048)
servo.MoveTo(SHOULDER, 2048)
servo.MoveTo(ELBOW, 2048)
servo.MoveTo(WRIST, 2048)
wait_all_stopped([BASE, SHOULDER, ELBOW, WRIST])

# Movement sequence 1: Reach forward
print("Reaching forward...")
servo.MoveTo(SHOULDER, 1500)
servo.MoveTo(ELBOW, 3000)
wait_all_stopped([SHOULDER, ELBOW])

# Movement sequence 2: Rotate base
print("Rotating base...")
servo.MoveTo(BASE, 3000)
wait_all_stopped([BASE])

# Movement sequence 3: Return home
print("Returning home...")
servo.MoveTo(BASE, 2048)
servo.MoveTo(SHOULDER, 2048)
servo.MoveTo(ELBOW, 2048)
servo.MoveTo(WRIST, 2048)
wait_all_stopped([BASE, SHOULDER, ELBOW, WRIST])

print("Choreography complete!")
```

---

## Servo Calibration

### Finding Mechanical Limits

```python
#!/usr/bin/env python3
"""Find mechanical limits manually"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

print("Finding mechanical limits...")
print("⚠️ Ensure servo has mechanical stops!")
input("Press Enter to continue...")

# Find minimum position
print("\nFinding minimum position...")
servo.SetAcceleration(servo_id, 100)
servo.Rotate(servo_id, -250)
time.sleep(0.5)
min_pos = servo.getBlockPosition(servo_id)

if min_pos is None:
    print("Failed to find minimum position")
    exit(1)

print(f"Minimum position: {min_pos}")

# Find maximum position
print("\nFinding maximum position...")
servo.Rotate(servo_id, 250)
time.sleep(0.5)
max_pos = servo.getBlockPosition(servo_id)

if max_pos is None:
    print("Failed to find maximum position")
    exit(1)

print(f"Maximum position: {max_pos}")

# Calculate range
if min_pos < max_pos:
    range_steps = max_pos - min_pos
else:
    range_steps = (4095 - min_pos) + max_pos

print(f"\nRange: {range_steps} steps")
print(f"Range: {(range_steps / 4095) * 360:.1f} degrees")
```

### Automatic Calibration (Taring)

```python
#!/usr/bin/env python3
"""Automatic servo calibration"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

print("=== Automatic Servo Calibration ===")
print("\n⚠️ WARNING:")
print("  - Servo MUST have mechanical stops")
print("  - Ensure adequate clearance")
print("  - Process will take 5-10 seconds")
print("  - Never use on continuous rotation servos")

input("\nPress Enter to start calibration...")

# Perform calibration
print("\nCalibrating...")
min_pos, max_pos = servo.TareServo(servo_id)

if min_pos is None:
    print("✗ Calibration failed!")
    exit(1)

print("✓ Calibration complete!")
print(f"\nResults:")
print(f"  Minimum: {min_pos}")
print(f"  Maximum: {max_pos}")
print(f"  Range: {max_pos - min_pos} steps")
print(f"  Center: {(max_pos - min_pos) / 2:.0f}")

# Test calibration
print("\nTesting calibration...")
center = int((max_pos - min_pos) / 2)

servo.MoveTo(servo_id, 0, wait=True)
print("  At minimum")
time.sleep(1)

servo.MoveTo(servo_id, center, wait=True)
print("  At center")
time.sleep(1)

servo.MoveTo(servo_id, max_pos, wait=True)
print("  At maximum")
time.sleep(1)

servo.MoveTo(servo_id, center, wait=True)
print("  Back to center")

print("\n✓ Calibration verified!")
```

### Manual Position Correction

```python
#!/usr/bin/env python3
"""Manually adjust servo zero position"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

print("=== Manual Position Correction ===")
print("\nInstructions:")
print("1. Servo will move to position 2048")
print("2. Manually adjust if needed (disable torque)")
print("3. Apply correction to set current position as 2048")

# Move to nominal center
servo.MoveTo(servo_id, 2048, wait=True)
print("\nServo at position 2048")

# Get actual position
current_pos = servo.ReadPosition(servo_id)
print(f"Actual position reading: {current_pos}")

# Calculate correction
correction = 2048 - current_pos
print(f"Correction needed: {correction} steps")

if abs(correction) > 10:
    response = input(f"\nApply correction of {correction} steps? (y/n): ")
    if response.lower() == 'y':
        servo.CorrectPosition(servo_id, correction)
        time.sleep(0.5)
        
        # Verify
        new_pos = servo.ReadPosition(servo_id)
        print(f"\nNew position reading: {new_pos}")
        print("✓ Correction applied!")
else:
    print("\nNo correction needed (within tolerance)")
```

---

## Monitoring and Diagnostics

### Health Monitor Dashboard

```python
#!/usr/bin/env python3
"""Real-time servo health monitoring"""

from st3215 import ST3215
import time
import os

servo = ST3215("/dev/ttyUSB0")
servo_ids = [1, 2, 3]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

print("Starting health monitor...")
print("Press Ctrl+C to stop")
time.sleep(2)

try:
    while True:
        clear_screen()
        print("=" * 60)
        print("SERVO HEALTH MONITOR".center(60))
        print("=" * 60)
        
        for servo_id in servo_ids:
            print(f"\n┌─ Servo {servo_id} " + "─" * 48)
            
            voltage = servo.ReadVoltage(servo_id)
            current = servo.ReadCurrent(servo_id)
            temp = servo.ReadTemperature(servo_id)
            load = servo.ReadLoad(servo_id)
            position = servo.ReadPosition(servo_id)
            mode = servo.ReadMode(servo_id)
            moving = servo.IsMoving(servo_id)
            
            if voltage is None:
                print("│ ✗ Communication Error")
                continue
            
            # Voltage
            v_status = "✓" if 6.0 <= voltage <= 12.6 else "⚠"
            print(f"│ {v_status} Voltage:     {voltage:5.1f}V")
            
            # Current
            i_status = "✓" if current < 1500 else "⚠"
            print(f"│ {i_status} Current:     {current:6.0f}mA")
            
            # Temperature
            t_status = "✓" if temp < 60 else ("⚠" if temp < 70 else "✗")
            print(f"│ {t_status} Temperature: {temp:3d}°C")
            
            # Load
            l_status = "✓" if load < 70 else ("⚠" if load < 85 else "✗")
            print(f"│ {l_status} Load:        {load:5.1f}%")
            
            # Position
            print(f"│   Position:    {position:4d}")
            
            # Mode
            mode_names = {0: "Position", 1: "Speed", 2: "PWM", 3: "Step"}
            print(f"│   Mode:        {mode_names.get(mode, 'Unknown')}")
            
            # Moving
            print(f"│   Status:      {'Moving' if moving else 'Stopped'}")
            
            print("└" + "─" * 55)
        
        print("\nPress Ctrl+C to stop")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\nMonitoring stopped")
```

### Status Flag Checker

```python
#!/usr/bin/env python3
"""Check all status flags"""

from st3215 import ST3215

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

status = servo.ReadStatus(servo_id)

if status is None:
    print("Failed to read status")
    exit(1)

print(f"Servo {servo_id} Status Flags:")
print("-" * 40)

all_ok = True
for flag, value in status.items():
    symbol = "✓" if value else "✗"
    print(f"{symbol} {flag:12} : {'OK' if value else 'FAULT'}")
    if not value:
        all_ok = False

print("-" * 40)
if all_ok:
    print("✓ All systems operational")
else:
    print("⚠ Faults detected - check connections and power")
```

---

## Configuration Management

### Changing Servo ID

```python
#!/usr/bin/env python3
"""Change servo ID with verification"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")

old_id = 1
new_id = 5

print(f"Changing servo ID from {old_id} to {new_id}")

# Verify old ID exists
if not servo.LinkServo(old_id):
    print(f"✗ Servo {old_id} not found!")
    exit(1)

print(f"✓ Servo {old_id} found")

# Check new ID is not in use
if servo.LinkServo(new_id):
    print(f"⚠ Warning: Servo {new_id} already exists!")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        exit(0)

# Change ID
print("Changing ID...")
error = servo.ChangeId(old_id, new_id)

if error:
    print(f"✗ Failed: {error}")
    exit(1)

print("✓ ID changed successfully")

# Verify new ID
time.sleep(0.5)
if servo.LinkServo(new_id):
    print(f"✓ Servo {new_id} responding!")
else:
    print(f"⚠ Cannot ping servo {new_id}")
    print("  (May need to power cycle)")
```

### Changing Baudrate

```python
#!/usr/bin/env python3
"""Change servo baudrate"""

from st3215 import ST3215

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Baudrate codes
baudrates = {
    0: "1M (1000000)",
    1: "0.5M (500000)",
    2: "250K (250000)",
    3: "128K (128000)",
    4: "115.2K (115200)",
    5: "76.8K (76800)",
    6: "57.6K (57600)",
    7: "38.4K (38400)"
}

print("Available baudrates:")
for code, desc in baudrates.items():
    print(f"  {code}: {desc}")

new_baudrate = int(input("\nEnter baudrate code: "))

if new_baudrate not in baudrates:
    print("Invalid baudrate code")
    exit(1)

print(f"\n⚠ Warning: Changing to {baudrates[new_baudrate]}")
print("You will need to reinitialize with new baudrate")
response = input("Continue? (y/n): ")

if response.lower() != 'y':
    exit(0)

error = servo.ChangeBaudrate(servo_id, new_baudrate)

if error:
    print(f"✗ Failed: {error}")
else:
    print("✓ Baudrate changed")
    print("\nReconnect using:")
    print(f"  servo = ST3215('{servo.portHandler.port_name}')")
```

---

## Advanced Techniques

### Trajectory Planning

```python
#!/usr/bin/env python3
"""Execute smooth trajectory with waypoints"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Define waypoints
waypoints = [
    {"position": 2048, "speed": 2000, "acc": 50},
    {"position": 3000, "speed": 1500, "acc": 30},
    {"position": 3500, "speed": 1000, "acc": 20},
    {"position": 2500, "speed": 1500, "acc": 40},
    {"position": 2048, "speed": 2000, "acc": 50}
]

print("Executing trajectory...")

for i, wp in enumerate(waypoints, 1):
    print(f"Waypoint {i}/{len(waypoints)}: pos={wp['position']}")
    
    servo.SetAcceleration(servo_id, wp['acc'])
    servo.SetSpeed(servo_id, wp['speed'])
    servo.MoveTo(servo_id, wp['position'], wait=True)
    
    time.sleep(0.5)  # Pause at waypoint

print("Trajectory complete!")
```

### Closed-Loop Position Control

```python
#!/usr/bin/env python3
"""Closed-loop control with error correction"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

def move_with_verification(servo_id, target, tolerance=10, max_attempts=3):
    """Move to target with error checking"""
    
    for attempt in range(max_attempts):
        # Send move command
        servo.MoveTo(servo_id, target)
        
        # Wait for movement
        time.sleep(0.5)
        while servo.IsMoving(servo_id):
            time.sleep(0.05)
        
        # Check final position
        position = servo.ReadPosition(servo_id)
        error = abs(target - position)
        
        print(f"Attempt {attempt + 1}: pos={position}, error={error}")
        
        if error <= tolerance:
            print("✓ Target reached within tolerance")
            return True
        else:
            print(f"⚠ Error {error} > tolerance {tolerance}, retrying...")
    
    print("✗ Failed to reach target after retries")
    return False

# Test
target = 3000
print(f"Moving to {target} with verification...")
success = move_with_verification(servo_id, target)
```

### Load-Based Speed Control

```python
#!/usr/bin/env python3
"""Adjust speed based on load"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

# Start rotating
base_speed = 1000
servo.Rotate(servo_id, base_speed)

print("Load-adaptive rotation")
print("Press Ctrl+C to stop")

try:
    while True:
        load = servo.ReadLoad(servo_id)
        
        # Reduce speed if load is high
        if load < 30:
            speed = base_speed
        elif load < 60:
            speed = int(base_speed * 0.7)
        else:
            speed = int(base_speed * 0.4)
        
        servo.Rotate(servo_id, speed)
        print(f"Load: {load:.1f}%  Speed: {speed}", end='\r')
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    servo.Rotate(servo_id, 0)
    print("\nStopped")
```

---

## Complete Project Examples

### Project 1: Pan-Tilt Camera Mount

```python
#!/usr/bin/env python3
"""2-DOF Pan-Tilt camera control"""

from st3215 import ST3215
import time

class PanTilt:
    def __init__(self, device="/dev/ttyUSB0"):
        self.servo = ST3215(device)
        self.PAN_ID = 1
        self.TILT_ID = 2
        
        # Initialize servos
        for servo_id in [self.PAN_ID, self.TILT_ID]:
            self.servo.SetAcceleration(servo_id, 50)
            self.servo.SetSpeed(servo_id, 2400)
        
        # Center position
        self.center()
    
    def center(self):
        """Move to center position"""
        self.servo.MoveTo(self.PAN_ID, 2048)
        self.servo.MoveTo(self.TILT_ID, 2048)
    
    def look_at(self, pan_degrees, tilt_degrees):
        """
        Look at specific angle
        pan: -180 to +180 degrees
        tilt: -90 to +90 degrees
        """
        # Convert degrees to position
        pan_pos = int(2048 + (pan_degrees / 180) * 2048)
        tilt_pos = int(2048 + (tilt_degrees / 90) * 1024)
        
        # Clamp values
        pan_pos = max(0, min(4095, pan_pos))
        tilt_pos = max(0, min(4095, tilt_pos))
        
        self.servo.MoveTo(self.PAN_ID, pan_pos)
        self.servo.MoveTo(self.TILT_ID, tilt_pos)
    
    def scan(self):
        """Perform scanning pattern"""
        # Horizontal scan
        for pan in range(-90, 91, 30):
            self.look_at(pan, 0)
            time.sleep(0.5)
        
        # Return to center
        self.center()

# Usage
pt = PanTilt()

print("Look left")
pt.look_at(-90, 0)
time.sleep(1)

print("Look right")
pt.look_at(90, 0)
time.sleep(1)

print("Look up")
pt.look_at(0, 45)
time.sleep(1)

print("Look down")
pt.look_at(0, -45)
time.sleep(1)

print("Scanning...")
pt.scan()

print("Center")
pt.center()
```

### Project 2: Robotic Gripper

```python
#!/usr/bin/env python3
"""Robotic gripper with force feedback"""

from st3215 import ST3215
import time

class Gripper:
    def __init__(self, device="/dev/ttyUSB0", servo_id=1):
        self.servo = ST3215(device)
        self.id = servo_id
        
        # Gripper positions
        self.OPEN_POS = 1000
        self.CLOSED_POS = 3000
        
        # Initialize
        self.servo.SetAcceleration(self.id, 30)
        self.servo.SetSpeed(self.id, 1500)
        self.open()
    
    def open(self):
        """Open gripper"""
        print("Opening gripper...")
        self.servo.MoveTo(self.id, self.OPEN_POS, wait=True)
    
    def close(self):
        """Close gripper"""
        print("Closing gripper...")
        self.servo.MoveTo(self.id, self.CLOSED_POS, wait=True)
    
    def close_with_force_limit(self, max_load=60):
        """Close gripper until object detected or max load"""
        print("Closing with force feedback...")
        
        # Start closing
        self.servo.MoveTo(self.id, self.CLOSED_POS)
        
        # Monitor load
        while self.servo.IsMoving(self.id):
            load = self.servo.ReadLoad(self.id)
            
            if load and load > max_load:
                # Object detected - stop
                position = self.servo.ReadPosition(self.id)
                self.servo.MoveTo(self.id, position)
                print(f"Object detected at load {load:.1f}%")
                return True
            
            time.sleep(0.05)
        
        print("Gripper fully closed")
        return False
    
    def is_holding(self):
        """Check if gripper is holding object"""
        load = self.servo.ReadLoad(self.id)
        return load and load > 20

# Usage
gripper = Gripper()

# Pick and place
print("\n=== Pick and Place ===")
gripper.open()
time.sleep(1)

input("Position object in gripper, press Enter...")
gripper.close_with_force_limit(max_load=50)
time.sleep(1)

if gripper.is_holding():
    print("✓ Object secured")
    time.sleep(2)
    print("Releasing object...")
    gripper.open()
else:
    print("✗ No object detected")
```

---

## Testing

### Running Test Suite

```bash
# Set device environment variable
export ST3215_DEV=/dev/ttyUSB0

# Run all tests
cd test
for test in test_*.py; do
    echo "Running $test"
    python3 "$test"
    echo ""
done
```

### Individual Tests

```bash
# Test 1: Ping servo
python3 test/test_01_ping_servo.py

# Test 2: List all servos
python3 test/test_02_list_servos.py

# Test 3: Read voltage, current, load
python3 test/test_03_read_load_voltage_current.py

# Test 10: Complete motion control
python3 test/test_10_complete_motion_control.py
```

---

## Performance Optimization

### Minimize Communication Delays

```python
# BAD: Multiple individual reads
voltage = servo.ReadVoltage(1)
current = servo.ReadCurrent(1)
temp = servo.ReadTemperature(1)

# BETTER: Batch reads with minimal delay
data = {}
data['voltage'] = servo.ReadVoltage(1)
data['current'] = servo.ReadCurrent(1)
data['temp'] = servo.ReadTemperature(1)
```

### Use Non-Blocking Movements

```python
# BAD: Sequential blocking movements (slow)
servo.MoveTo(1, 2048, wait=True)
servo.MoveTo(2, 2048, wait=True)
servo.MoveTo(3, 2048, wait=True)

# GOOD: Parallel non-blocking movements (fast)
servo.MoveTo(1, 2048)
servo.MoveTo(2, 2048)
servo.MoveTo(3, 2048)

# Wait for all to complete
while any(servo.IsMoving(i) for i in [1, 2, 3]):
    time.sleep(0.05)
```

### Reduce Polling Frequency

```python
# BAD: Too frequent polling (CPU intensive)
while servo.IsMoving(1):
    time.sleep(0.001)  # 1ms - too fast!

# GOOD: Reasonable polling rate
while servo.IsMoving(1):
    time.sleep(0.05)  # 50ms - balanced
```

---

## Summary

This guide covered:

- ✓ Hardware setup and wiring
- ✓ Software installation
- ✓ Basic position and speed control
- ✓ Multi-servo coordination
- ✓ Servo calibration techniques
- ✓ Health monitoring
- ✓ Configuration management
- ✓ Advanced control techniques
- ✓ Complete project examples
- ✓ Testing procedures
- ✓ Performance optimization

### Next Steps

1. Review the [User Manual](User_manual.md) for complete API reference
2. Check [Troubleshooting](troubleshooting.md) if you encounter issues
3. Read the [FAQ](FAQ.md) for common questions

### Additional Resources

- [ST3215 Datasheet](https://www.waveshare.com/wiki/ST3215_Servo)
- [GitHub Repository](https://github.com/Mickael-Roger/python-st3215)
- [Issue Tracker](https://github.com/Mickael-Roger/python-st3215/issues)

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
