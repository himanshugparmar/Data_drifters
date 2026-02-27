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
```

### Key Updates:
- Removed references to the `Ping6Servo` method as it has been removed.
- Updated sections involving the `ST3215` method to reflect potential changes in its signature, ensuring users are aware of the need to reinitialize with new baudrate settings.
- Ensured troubleshooting steps are aligned with the actual changes, focusing on baudrate and communication issues.
```