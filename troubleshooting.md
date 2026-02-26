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
for test_id in range(254):
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
servo.PingServo(1)  # Still using 1M - Won't work!

# Correct:
servo.ChangeBaudrate(1, 4)
# Close and reopen with new baudrate
del servo
time.sleep(1)

# Reinitialize - but baudrate is in port_handler!
# You need to modify port_handler or use custom initialization
```

**Recovery:**

```python
# Try all baudrates to find servo
def find_servo_baudrate(device, servo_id):
    """Find which baudrate the servo is using"""
    baudrates = [1000000, 500000, 250000, 115200, 57600]
    
    for baud in baudrates:
        print(f"Trying {baud}...")
        try:
            servo = ST3215(device)
            servo.portHandler.setBaudRate(baud)
            if servo.PingServo(servo_id):
                print(f"✓ Found servo at {baud} baud")
                return baud
        except:
            pass
    
    return None

# Usage
baud = find_servo_baudrate("/dev/ttyUSB0", 1)
```

---

## Calibration Issues

### TareServo Fails

**Error:** Returns `(None, None)`

**Causes:**

1. **No mechanical stops**
```python
# Never use TareServo on continuous rotation servos!
# It will run indefinitely
```

2. **Insufficient rotation time**
```python
# Servo might need more time to reach limit
# Edit source if needed or use manual calibration
```

3. **Weak mechanical stops**
```python
# If stops are soft, servo might not detect blocking
# Solution: Manual calibration instead
```

**Alternative: Manual Calibration**

```python
#!/usr/bin/env python3
"""Manual servo calibration"""

from st3215 import ST3215
import time

servo = ST3215("/dev/ttyUSB0")
servo_id = 1

print("Manual Calibration")
print("Move servo to minimum position, press Enter")
input()
min_pos = servo.ReadPosition(servo_id)
print(f"Minimum: {min_pos}")

print("Move servo to maximum position, press Enter")
input()
max_pos = servo.ReadPosition(servo_id)
print(f"Maximum: {max_pos}")

# Calculate center
center = (min_pos + max_pos) // 2
print(f"Center: {center}")

# Apply correction to make center = 2048
correction = center - 2048
servo.CorrectPosition(servo_id, correction)
print(f"Applied correction: {correction}")
```

---

## Multi-Servo Problems

### Servo ID Conflicts

**Symptom:** Multiple servos respond to same ID

```python
# Detect ID conflicts
def check_conflicts():
    """Check for duplicate IDs"""
    for test_id in range(1, 10):
        # Send command and check how many respond
        servo.MoveTo(test_id, 2048)
        time.sleep(0.1)
        
        # If multiple servos move, there's a conflict
        print(f"Check ID {test_id} - inspect for multiple movements")
        time.sleep(2)

# Solution: Change IDs one at a time
# 1. Disconnect all servos
# 2. Connect one servo
# 3. Change its ID
# 4. Disconnect and repeat for next servo
```

### Synchronized Movement Issues

**Problem:** Servos not moving in sync

```python
# BAD: Sequential commands have delays
servo.MoveTo(1, 2048)  # Delay here
servo.MoveTo(2, 2048)  # Delay here
servo.MoveTo(3, 2048)  # Delay here

# GOOD: Quick succession
servo.MoveTo(1, 2048)
servo.MoveTo(2, 2048)
servo.MoveTo(3, 2048)
# All move "simultaneously" (within ms)

# BETTER: Use GroupSyncWrite for true sync
# See User Manual for GroupSyncWrite examples
```

---

## Platform-Specific Issues

### Raspberry Pi

#### GPIO UART Not Working

```bash
# Enable UART
sudo raspi-config
# Interface Options -> Serial Port
# Login shell: NO
# Serial port hardware: YES

# Edit /boot/config.txt
sudo nano /boot/config.txt
# Add:
enable_uart=1
dtoverlay=disable-bt

# Reboot
sudo reboot

# Test
ls -l /dev/ttyAMA0
```

#### Python 2 vs Python 3

```bash
# Use Python 3 explicitly
python3 -m pip install pyserial
python3 your_script.py
```

### Windows

#### COM Port Not Found

```python
import serial.tools.list_ports

# List all COM ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")

# Common on Windows: COM3, COM4, COM5
```

#### Driver Issues

```
Download CH340 or FT232 drivers from manufacturer:
- CH340: http://www.wch-ic.com/downloads/CH341SER_ZIP.html
- FT232: https://ftdichip.com/drivers/vcp-drivers/
```

### macOS

#### Permission Issues

```bash
# Give Terminal/IDE access to USB devices
System Preferences -> Security & Privacy -> Privacy
-> Files and Folders -> Allow access

# Or use sudo (not recommended)
sudo python3 your_script.py
```

---

## Error Codes Reference

### Communication Result Codes

| Code | Name | Meaning | Solution |
|------|------|---------|----------|
| 0 | COMM_SUCCESS | Success | - |
| -1 | COMM_PORT_BUSY | Port in use | Close other programs |
| -2 | COMM_TX_FAIL | Transmit failed | Check connections |
| -3 | COMM_RX_FAIL | Receive failed | Check wiring |
| -4 | COMM_TX_ERROR | Bad packet | Software issue |
| -5 | COMM_RX_WAITING | Still receiving | Wait longer |
| -6 | COMM_RX_TIMEOUT | No response | Check servo power/ID |
| -7 | COMM_RX_CORRUPT | Corrupt packet | Check for interference |
| -9 | COMM_NOT_AVAILABLE | Not available | Feature unsupported |

### Status Flags

When `ReadStatus()` returns `False` for a flag:

| Flag | Meaning | Action |
|------|---------|--------|
| Voltage | Voltage fault | Check power supply |
| Sensor | Position sensor error | Check servo integrity |
| Temperature | Overheating | Cool down servo |
| Current | Overcurrent | Reduce load |
| Angle | Beyond angle limit | Check position limits |
| Overload | Mechanical overload | Remove obstruction |

---

## Diagnostic Tools

### Complete Diagnostic Script

```python
#!/usr/bin/env python3
"""Complete servo diagnostics"""

from st3215 import ST3215
import sys

def diagnose(device="/dev/ttyUSB0", servo_id=1):
    """Run complete diagnostic"""
    
    print("=" * 60)
    print("ST3215 SERVO DIAGNOSTICS".center(60))
    print("=" * 60)
    
    # Test 1: Connection
    print("\n[1/7] Testing serial connection...")
    try:
        servo = ST3215(device)
        print("✓ Serial port opened")
    except ValueError as e:
        print(f"✗ Cannot open port: {e}")
        return False
    
    # Test 2: Ping
    print(f"\n[2/7] Pinging servo ID {servo_id}...")
    if not servo.PingServo(servo_id):
        print(f"✗ No response from servo {servo_id}")
        print("Scanning bus...")
        found = servo.ListServos()
        if found:
            print(f"Found servos: {found}")
            servo_id = found[0]
        else:
            print("No servos found")
            return False
    else:
        print(f"✓ Servo {servo_id} responding")
    
    # Test 3: Read parameters
    print(f"\n[3/7] Reading servo parameters...")
    voltage = servo.ReadVoltage(servo_id)
    current = servo.ReadCurrent(servo_id)
    temp = servo.ReadTemperature(servo_id)
    position = servo.ReadPosition(servo_id)
    load = servo.ReadLoad(servo_id)
    mode = servo.ReadMode(servo_id)
    
    if None in [voltage, current, temp, position, load, mode]:
        print("✗ Failed to read parameters")
        return False
    
    print(f"✓ Voltage: {voltage:.1f}V")
    print(f"✓ Current: {current:.0f}mA")
    print(f"✓ Temperature: {temp}°C")
    print(f"✓ Position: {position}")
    print(f"✓ Load: {load:.1f}%")
    print(f"✓ Mode: {mode}")
    
    # Test 4: Status flags
    print(f"\n[4/7] Checking status flags...")
    status = servo.ReadStatus(servo_id)
    if status:
        all_ok = True
        for flag, value in status.items():
            symbol = "✓" if value else "✗"
            print(f"{symbol} {flag}: {'OK' if value else 'FAULT'}")
            if not value:
                all_ok = False
        if all_ok:
            print("✓ All status flags OK")
    else:
        print("✗ Failed to read status")
        return False
    
    # Test 5: Health checks
    print(f"\n[5/7] Health checks...")
    issues = []
    
    if voltage < 6.0:
        issues.append(f"Low voltage ({voltage:.1f}V)")
    if current > 2000:
        issues.append(f"High current ({current:.0f}mA)")
    if temp > 70:
        issues.append(f"High temperature ({temp}°C)")
    if load > 80:
        issues.append(f"High load ({load:.1f}%)")
    
    if issues:
        print("⚠ Issues detected:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All health checks passed")
    
    # Test 6: Movement test
    print(f"\n[6/7] Testing movement...")
    print("Moving to position 2048...")
    servo.MoveTo(servo_id, 2048)
    import time
    time.sleep(2)
    
    new_pos = servo.ReadPosition(servo_id)
    error = abs(2048 - new_pos)
    
    if error < 50:
        print(f"✓ Movement OK (error: {error} steps)")
    else:
        print(f"⚠ Large position error: {error} steps")
    
    # Test 7: Summary
    print(f"\n[7/7] Summary...")
    print("-" * 60)
    if len(issues) == 0 and error < 50:
        print("✓ SERVO IS HEALTHY")
    else:
        print("⚠ ISSUES DETECTED - See above")
    print("-" * 60)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        device = sys.argv[1]
    else:
        device = "/dev/ttyUSB0"
    
    if len(sys.argv) > 2:
        servo_id = int(sys.argv[2])
    else:
        servo_id = 1
    
    diagnose(device, servo_id)
```

**Usage:**
```bash
python3 diagnose.py /dev/ttyUSB0 1
```

---

## Getting Help

If you still have issues:

1. **Check FAQ** - [FAQ.md](FAQ.md)
2. **Review User Guide** - [user_guide.md](user_guide.md)
3. **Read User Manual** - [User_manual.md](User_manual.md)
4. **Search GitHub Issues** - [Issues](https://github.com/Mickael-Roger/python-st3215/issues)
5. **Create New Issue** with:
   - Python version
   - Operating system
   - Library version
   - Complete error message
   - Diagnostic script output
   - Wiring diagram/photo

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
