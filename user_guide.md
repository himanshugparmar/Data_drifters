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

## Basic Operations

### Finding Servos

```python
# Quick check for specific ID
if servo.Ping5Servo(1):
    print("Servo 1 found!")

# Scan all IDs (takes 15-30 seconds)
print("Scanning for servos...")
servos = servo.List2Servos()
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

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger

**Note:** The updates reflect the introduction of new methods `Ping5Servo` and `List2Servos`, replacing the older `PingServo` and `ListServos`. The documentation has been revised to guide users on the new method names and expected behaviors.