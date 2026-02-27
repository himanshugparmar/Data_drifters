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
# Note: The ReadVoltage method has been removed.
# Ensure you are using the correct method for voltage reading.
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
# Note: The ReadVoltage method has been removed.
# Ensure you are using the correct method for voltage reading.
```

---

## Power and Electrical Issues

### Low Voltage Warning

**Symptom:** Voltage below 6V

**Diagnostics:**

```python
# Note: The ReadVoltage method has been removed.
# Ensure you are using the correct method for voltage reading.
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

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
```

**Note:** The `ReadVoltage` method has been removed from the library. Ensure you are using the correct method for voltage reading. The `ST3215` method's signature has been modified; please refer to the updated method signature in the library documentation for correct usage.
```