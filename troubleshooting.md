# ST3215 Servo Control Library - Troubleshooting Guide

Comprehensive troubleshooting guide for common issues with the ST3215 Python library.

---

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Communication Errors](#communication-errors)
3. [Servo Not Responding](#servo-not-responding)
4. [Movement Problems](#movement-problems)
5. [Power and Electrical Issues](#power-and-electrical-issues)
6. [Performance Issues](#performance-issues)
7. [Configuration Problems](#configuration-problems)
8. [Calibration Issues](#calibration-issues)
9. [Multi-Servo Problems](#multi-servo-problems)
10. [Platform-Specific Issues](#platform-specific-issues)
11. [Error Codes Reference](#error-codes-reference)
12. [Diagnostic Tools](#diagnostic-tools)

---

## Connection Issues

### Cannot Open Serial Port

**Error Message:**
```
ValueError: Could not open port: /dev/ttyUSB0
```

**Possible Causes and Solutions:**

#### 1. **Port Does Not Exist**

```bash
# List available serial ports
ls /dev/tty*

# Look for:
# Linux: /dev/ttyUSB*, /dev/ttyACM*
# Raspberry Pi: /dev/ttyAMA0, /dev/ttyS0
# macOS: /dev/cu.usbserial*
```

**Solution:**
- Verify USB adapter is connected
- Check `dmesg | grep tty` for device recognition
- Try different USB port

#### 2. **Permission Denied**

```bash
# Check current user groups
groups

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in, then verify
groups | grep dialout
```

**Quick Fix (temporary):**
```bash
sudo chmod 666 /dev/ttyUSB0
```

**Permanent Fix:**
```bash
# Create udev rule
sudo nano /etc/udev/rules.d/99-serial.rules

# Add line:
SUBSYSTEM=="tty", GROUP="dialout", MODE="0660"

# Reload rules
sudo udevadm control --reload-rules
```

#### 3. **Port Already in Use**

```bash
# Find process using the port
lsof /dev/ttyUSB0

# Kill process if needed
sudo kill -9 <PID>
```

**Python Solution:**
```python
# Close existing connection
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Port: {port.device}")
    print(f"  Description: {port.description}")
    print(f"  HWID: {port.hwid}")
```

#### 4. **Wrong Port Name**

```python
# Auto-detect USB serial ports
import serial.tools.list_ports

def find_usb_serial():
    """Find first USB serial device"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB' in port.device or 'ACM' in port.device:
            return port.device
    return None

device = find_usb_serial()
if device:
    print(f"Found: {device}")
    servo = ST3215(device)
else:
    print("No USB serial device found")
```

---

## Communication Errors

### Servo Returns None

**Symptom:** All read operations return `None`

```python
voltage = servo.ReadVoltage(1)  # Returns None
```

**Diagnostic Steps:**

#### Step 1: Test Basic Communication

```python
# Test ping
result = servo.PingServo(1)
print(f"Ping result: {result}")

if not result:
    print("Communication failed - check:")
    print("  1. Servo power supply")
    print("  2. Data wire connection")
    print("  3. Baudrate match")
    print("  4. Correct servo ID")
```

#### Step 2: Check Physical Connections

```
┌─────────────────────────────────────────────┐
│  Wiring Checklist:                          │
├─────────────────────────────────────────────┤
│  □ GND connected (servo & USB adapter)      │
│  □ VCC connected (6-12V power supply)       │
│  □ DATA connected (servo TX/RX to adapter)  │
│  □ Common ground (power & signal)           │
│  □ No loose connections                     │
│  □ Correct polarity (check colors)          │
└─────────────────────────────────────────────┘
```

#### Step 3: Verify Baudrate

```python
# Try different baudrates
baudrates = [1000000, 500000, 115200, 57600]

for baud in baudrates:
    print(f"Trying {baud} baud...")
    try:
        servo = ST3215("/dev/ttyUSB0")
        servo.portHandler.setBaudRate(baud)
        if servo.PingServo(1):
            print(f"✓ Communication works at {baud}")
            break
    except:
        pass
```

#### Step 4: Test with Different Servo ID

```python
# Scan for any responding servo
print("Scanning for servos...")
for test_id in [1, 2, 3, 5, 10]:  # Common IDs
    if servo.PingServo(test_id):
        print(f"✓ Found servo at ID {test_id}")
```

### Intermittent Communication

**Symptom:** Sometimes works, sometimes returns `None`

**Causes:**
1. **Loose connections** - Re-seat all connectors
2. **Electrical interference** - Use shielded cables
3. **Cable too long** - Keep under 5 meters
4. **Low voltage** - Check power supply
5. **Bus contention** - Multiple devices with same ID

**Solutions:**

```python
# Add retry logic
def read_with_retry(func, *args, max_retries=3):
    """Retry read operation on failure"""
    for attempt in range(max_retries):
        result = func(*args)
        if result is not None:
            return result
        time.sleep(0.05)
    return None

# Usage
voltage = read_with_retry(servo.ReadVoltage, 1)
if voltage is None:
    print("Failed after retries")
```

### Timeout Errors

**Symptom:** Operations take too long or timeout

```python
# Increase timeout (in port_handler.py)
self.ser.timeout = 0.1  # Increase from default

# Or use longer delays
import time
servo.MoveTo(1, 2048)
time.sleep(0.5)  # Wait before next command
```

---

## Servo Not Responding

### Servo ID Unknown

**Problem:** Don't know what ID servo is set to

**Solution:** Full bus scan

```python
#!/usr/bin/env python3
"""Complete bus scan with verbose output"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")

print("Scanning bus (this may take 30 seconds)...")
print("ID   Status")
print("-" * 20)

found = []
for test_id in range 254:
    if servo.PingServo(test_id):
        print(f"{test_id:3d}  ✓ FOUND")
        found.append(test_id)
    else:
        print(f"{test_id:3d}  -", end='\r')
    
    if test_id % 10 == 0:
        time.sleep(0.1)  # Prevent bus overload

print("\n" + "-" * 20)
print(f"Found {len(found)} servo(s): {found}")
```

### Servo Locked Up

**Symptoms:**
- No response to any command
- Heat buildup
- Strange noises

**Solutions:**

#### Emergency Stop

```python
# Disable torque immediately
servo.StopServo(1)

# Or try emergency stop on all possible IDs
for servo_id in range(1, 10):
    try:
        servo.StopServo(servo_id)
    except:
        pass
```

#### Power Cycle

```
1. Disconnect servo power supply
2. Wait 10 seconds
3. Reconnect power
4. Test: servo.PingServo(1)
```

#### Factory Reset (if supported)

```python
# Reset to factory defaults
servo.UnLockEprom(1)
servo.ChangeId(1, 1)  # Back to default ID
servo.ChangeBaudrate(1, 0)  # Back to 1M baud
servo.CorrectPosition(1, 0)  # Clear correction
servo.LockEprom(1)
```

---

## Movement Problems

### Servo Not Moving

**Symptom:** Commands accepted but no movement

**Diagnostic:**

```python
# Check if servo is moving
moving = servo.IsMoving(1)
print(f"IsMoving: {moving}")

# Check position
pos = servo.ReadPosition(1)
print(f"Current position: {pos}")

# Check mode
mode = servo.ReadMode(1)
mode_names = {0: "Position", 1: "Speed", 2: "PWM", 3: "Step"}
print(f"Mode: {mode_names.get(mode, 'Unknown')}")

# Check if torque enabled
# This requires checking STS_TORQUE_ENABLE register
```

**Solutions:**

#### 1. **Enable Torque**

```python
# Torque might be disabled
servo.StartServo(1)
time.sleep(0.2)
servo.MoveTo(1, 2048)
```

#### 2. **Wrong Mode**

```python
# Force position mode
servo.SetMode(1, 0)
time.sleep(0.1)
servo.MoveTo(1, 2048)
```

#### 3. **Already at Target**

```python
# Check if already at position
current = servo.ReadPosition(1)
target = 2048

if abs(current - target) < 10:
    print("Already at target position")
    # Move to different position first
    servo.MoveTo(1, 3000)
    time.sleep(1)
    servo.MoveTo(1, 2048)
```

#### 4. **Mechanical Obstruction**

```python
# Check load
load = servo.ReadLoad(1)
if load and load > 80:
    print("High load - check for obstruction")
    servo.StopServo(1)
```

### Erratic Movement

**Symptoms:**
- Jittery motion
- Overshooting
- Unstable position

**Solutions:**

#### 1. **Reduce Speed and Acceleration**

```python
# Use gentle parameters
servo.SetAcceleration(1, 20)  # Low acceleration
servo.SetSpeed(1, 800)        # Low speed
servo.MoveTo(1, 2048)
```

#### 2. **Check Power Supply**

```python
# Monitor voltage during movement
servo.MoveTo(1, 3000)
time.sleep(0.1)

for _ in range(20):
    voltage = servo.ReadVoltage(1)
    print(f"Voltage: {voltage:.1f}V", end='\r')
    time.sleep(0.1)

# Voltage should remain stable (±0.5V)
```

#### 3. **Mechanical Issues**

```
Check for:
  □ Loose mounting screws
  □ Damaged gears
  □ Worn bearings
  □ Excessive backlash
  □ Binding in mechanism
```

### Slow Movement

**Problem:** Servo moves slower than expected

```python
# Verify speed setting
current_speed = 500  # Example
servo.SetSpeed(1, current_speed)

# Test with maximum speed
servo.SetSpeed(1, 3400)
servo.SetAcceleration(1, 200)
servo.MoveTo(1, 2048)

# If still slow:
#   - Check voltage (should be 6-12V)
#   - Check load (should be <50%)
#   - Check temperature (should be <60°C)
```

---

## Power and Electrical Issues

### Low Voltage Warning

**Symptom:** Voltage below 6V

**Diagnostics:**

```python
voltage = servo.ReadVoltage(1)
current = servo.ReadCurrent(1)

print(f"Voltage: {voltage:.1f}V")
print(f"Current: {current:.0f}mA")

if voltage < 6.0:
    print("⚠ Low voltage detected!")
    print("Causes:")
    print("  - Power supply insufficient")
    print("  - Voltage drop in cables")
    print("  - Multiple servos on same supply")
```

**Solutions:**

1. **Use adequate power supply**
   ```
   Single servo: 6-12V, 2A minimum
   Multiple servos: Add 1.5A per additional servo
   Recommended: 12V, 5A supply for 3-4 servos
   ```

2. **Check cable gauge**
   ```
   Use proper wire gauge:
   - Under 1 meter: 22 AWG minimum
   - 1-3 meters: 20 AWG
   - Over 3 meters: 18 AWG
   ```

3. **Star topology wiring**
   ```
   ┌──[PSU]──┐
   │    │    │
   S1   S2   S3
   
   Not daisy-chain:
   [PSU]──S1──S2──S3  ✗
   ```

### Overheating

**Symptom:** Temperature above 70°C

```python
# Monitor temperature
temp = servo.ReadTemperature(1)
print(f"Temperature: {temp}°C")

if temp > 70:
    print("⚠ OVERHEATING!")
    servo.StopServo(1)
    print("Cooling down...")
```

**Causes and Solutions:**

| Cause | Solution |
|-------|----------|
| Sustained high load | Reduce load or add cooling |
| Poor ventilation | Add heatsink or fan |
| Continuous operation | Add duty cycle breaks |
| Mechanical binding | Fix mechanical issues |
| Excessive speed | Reduce speed/acceleration |

**Cooling Break Pattern:**

```python
# Add periodic cooling breaks
for cycle in range(10):
    # Work for 2 minutes
    servo.MoveTo(1, 3000)
    time.sleep(60)
    servo.MoveTo(1, 1000)
    time.sleep(60)
    
    # Check temperature
    temp = servo.ReadTemperature(1)
    print(f"Cycle {cycle + 1}, Temp: {temp}°C")
    
    if temp > 65:
        print("Cooling break...")
        servo.StopServo(1)
        time.sleep(180)  # 3 minute break
```

### Current Overload

**Symptom:** High current draw (>2000mA)

```python
current = servo.ReadCurrent(1)
if current > 2000:
    print(f"⚠ High current: {current}mA")
    load = servo.ReadLoad(1)
    print(f"Load: {load}%")
    
    # Check status
    status = servo.ReadStatus(1)
    if not status.get('Current', True):
        print("✗ Current fault detected")
```

**Solutions:**
1. Reduce load on servo
2. Check for mechanical binding
3. Lower speed/acceleration
4. Verify adequate power supply capacity

---

## Performance Issues

### Laggy Response

**Problem:** Delay between command and execution

**Causes:**

1. **High system load** - Close unnecessary programs
2. **Slow polling rate** - Reduce sleep time
3. **USB latency** - Set lower latency timer

**Solutions:**

```python
# Reduce USB latency (Linux)
# Set latency timer to 1ms (default 16ms)
import subprocess
subprocess.call(['setserial', '/dev/ttyUSB0', 'low_latency'])

# Or in Python
from st3215.port_handler import LATENCY_TIMER
# Modify LATENCY_TIMER in values.py

# Optimize polling
# BAD: Sleep too long
while servo.IsMoving(1):
    time.sleep(0.5)  # 500ms delay!

# GOOD: Short sleep
while servo.IsMoving(1):
    time.sleep(0.01)  # 10ms
```

### Commands Queuing/Delayed

**Problem:** Commands execute in wrong order

```python
# BAD: Commands sent too fast
for pos in [1000, 2000, 3000, 2000]:
    servo.MoveTo(1, pos)  # No delay!

# GOOD: Wait for completion
for pos in [1000, 2000, 3000, 2000]:
    servo.MoveTo(1, pos, wait=True)

# Or check IsMoving
for pos in [1000, 2000, 3000, 2000]:
    servo.MoveTo(1, pos)
    while servo.IsMoving(1):
        time.sleep(0.05)
```

---

## Configuration Problems

### Cannot Change ID

**Error:** "Could not find servo" or "Could not change ID"

```python
# Verify current ID
old_id = 1
if not servo.PingServo(old_id):
    print("Cannot find servo at ID", old_id)
    
    # Try scanning
    servos = servo.ListServos()
    if servos:
        print(f"Found servos: {servos}")
        old_id = servos[0]
    else:
        print("No servos found on bus")
        exit(1)

# Check EEPROM is unlocked
error = servo.ChangeId(old_id, 5)
if error:
    print(f"Error: {error}")
    
    # Manual unlock and retry
    servo.UnLockEprom(old_id)
    time.sleep(0.2)
    error = servo.ChangeId(old_id, 5)
```

### Lost After Baudrate Change

**Problem:** Cannot communicate after changing baudrate

```python
# YOU MUST reinitialize with new baudrate
# This is a common mistake!

# Wrong:
servo.ChangeBaudrate(1, 4)  # Changed to 115200
servo.PingServo(1)  # Still using 