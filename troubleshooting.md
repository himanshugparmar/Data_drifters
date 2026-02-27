```markdown
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
result = servo.LinkServo(1)
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
        if servo.LinkServo(1):
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
    if servo.LinkServo(test_id):
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

---

## Configuration Problems

### Cannot Change ID

**Error:** "Could not find servo" or "Could not change ID"

```python
# Verify current ID
old_id = 1
if not servo.LinkServo(old_id):
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
servo.LinkServo(1)  # Still using 1M - Won't work!

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
            if servo.LinkServo(servo_id):
                print(f"✓ Found servo at {baud} baud")
                return baud
        except:
            pass
    
    return None

# Usage
baud = find_servo_baudrate("/dev/ttyUSB0", 1)
```

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
    if not servo.LinkServo(servo_id):
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

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
```

**Note:** The `Ping6Servo` method has been removed, and any references to it have been omitted from this documentation. Users should refer to alternative methods for diagnostics or network-related troubleshooting. The `ST3215` method's signature has been updated, and users should ensure they are using the correct parameters as per the latest library version.
```