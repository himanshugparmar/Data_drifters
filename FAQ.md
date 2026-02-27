```markdown
# ST3215 Servo Control Library - FAQ

Frequently Asked Questions about the ST3215 Python library.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Hardware Questions](#hardware-questions)
3. [Software Questions](#software-questions)
4. [Usage Questions](#usage-questions)
5. [Performance Questions](#performance-questions)
6. [Troubleshooting Questions](#troubleshooting-questions)
7. [Advanced Questions](#advanced-questions)

---

## General Questions

### What is ST3215?

ST3215 is a serial bus servo motor with built-in controller. It communicates via UART/RS485 protocol and provides position, speed, and PWM control modes. Common in robotics applications.

**Key Specifications:**
- Position resolution: 4096 steps (12-bit)
- Operating voltage: 6-12.6V
- Operating current: 100-2000mA typical
- Torque: ~15 kg·cm @ 12V
- Speed: Up to 3400 steps/second
- Communication: UART (half-duplex)
- Default baudrate: 1M bps

---

### What's the difference between ST3215 and other servos (like Dynamixel)?

| Feature | ST3215 | Dynamixel AX-12 | Standard RC Servo |
|---------|--------|-----------------|-------------------|
| Protocol | ST3215/SCS | Dynamixel | PWM |
| Communication | UART/RS485 | UART/RS485 | PWM (1-2ms) |
| Addressability | Yes (ID 0-253) | Yes (ID 0-253) | No |
| Position feedback | Yes (digital) | Yes (digital) | Some models |
| Speed control | Yes | Yes | No |
| Multi-turn | No | Some models | No |
| Cost | Low | Medium-High | Low |
| Library support | Limited | Excellent | Universal |

**ST3215 Advantages:**
- Lower cost than Dynamixel
- Digital control (better than PWM)
- Multiple operation modes
- Good torque for price

**Disadvantages:**
- Less documentation than Dynamixel
- Fewer library options
- Smaller community

---

### Is this library compatible with other servo models?

**Compatible:** Other Feetech/SCS series servos using the same protocol:
- STS3215
- STS3032
- SCS115
- SCS15 (with limitations)

**Not Compatible:**
- Dynamixel servos (different protocol)
- Herkulex servos (different protocol)
- Standard RC PWM servos (different control method)

**Testing compatibility:**
```python
# Try basic ping
servo = ST3215("/dev/ttyUSB0")
if servo.LinkServo(1):
    print("Compatible servo detected!")
else:
    print("Servo not responding - might be different protocol")
```

---

### Can I use this with Arduino or Raspberry Pi?

**Yes, both!**

#### Raspberry Pi (Recommended)
```python
# GPIO UART (pins 8/10)
servo = ST3215("/dev/ttyAMA0")

# USB adapter
servo = ST3215("/dev/ttyUSB0")
```

**Pros:** Native Python support, this library works directly

#### Arduino
**Note:** This is a Python library. For Arduino, you need:
- SCServo library (Arduino C++)
- Available at: https://github.com/ftservo/SCServo

**Bridge solution:** Use Arduino for servo control, Raspberry Pi for main logic

---

### What's the maximum number of servos I can control?

**Theoretical:** 253 servos (ID 0-253, ID 254 is broadcast)

**Practical limits:**

| Factor | Typical Limit | Notes |
|--------|---------------|-------|
| Power supply | 4-8 servos | 2A per servo needed |
| Bus speed | 20-30 servos | Communication bandwidth |
| Update rate | 10-20 servos | If polling all servos frequently |
| Cable length | 5 meters | Signal degradation |

**Recommendations:**
- **1-4 servos:** Simple daisy-chain, single power supply
- **5-10 servos:** Star topology power, may need RS485 repeater
- **10+ servos:** Multiple buses (multiple USB adapters), robust power distribution

---

## Software Questions

### What Python version is required?

**Minimum:** Python 3.10

**Recommended:** Python 3.11 or 3.12

**Check your version:**
```bash
python3 --version
```

**Not supported:**
- Python 2.x (deprecated)
- Python 3.9 and earlier

**Reason:** Library uses modern Python features (type hints, match statements, etc.)

---

### What dependencies are needed?

**Only one:** `pyserial`

```bash
pip install pyserial
```

**Full installation:**
```bash
# Clone repository
git clone https://github.com/Mickael-Roger/python-st3215
cd python-st3215

# Install dependencies
pip install -r requirements.txt

# Install library
pip install -e .
```

**Verify installation:**
```python
python3 -c "from st3215 import ST3215; print('OK')"
```

---

### Does this work on Windows/macOS/Linux?

**Yes, all three!**

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✓ Excellent | Native support, dev/ttyUSB* |
| Raspberry Pi | ✓ Excellent | GPIO UART available |
| Windows | ✓ Good | Use COM ports, need drivers |
| macOS | ✓ Good | Use /dev/cu.*, may need permissions |

**Platform-specific:**

```python
import platform

if platform.system() == 'Windows':
    device = 'COM3'
elif platform.system() == 'Darwin':  # macOS
    device = '/dev/cu.usbserial-1420'
else:  # Linux
    device = '/dev/ttyUSB0'

servo = ST3215(device)
```

---

## Usage Questions

### How do I convert between position and angles?

**Position to degrees:**
```python
def position_to_degrees(position):
    """Convert position (0-4095) to degrees (0-360)"""
    return (position / 4095) * 360

# Example
pos = 2048
degrees = position_to_degrees(pos)
print(f"{pos} = {degrees:.1f}°")  # 2048 = 180.0°
```

**Degrees to position:**
```python
def degrees_to_position(degrees):
    """Convert degrees (0-360) to position (0-4095)"""
    return int((degrees / 360) * 4095)

# Example
angle = 90
pos = degrees_to_position(angle)
print(f"{angle}° = {pos}")  # 90° = 1024
```

**Radians:**
```python
import math

def position_to_radians(position):
    """Convert position to radians"""
    return (position / 4095) * 2 * math.pi

def radians_to_position(radians):
    """Convert radians to position"""
    return int((radians / (2 * math.pi)) * 4095)
```

**Using a class:**
```python
class PositionConverter:
    MAX_POS = 4095
    
    @staticmethod
    def to_degrees(position):
        return (position / PositionConverter.MAX_POS) * 360
    
    @staticmethod
    def to_radians(position):
        return (position / PositionConverter.MAX_POS) * 2 * math.pi
    
    @staticmethod
    def from_degrees(degrees):
        return int((degrees / 360) * PositionConverter.MAX_POS)
    
    @staticmethod
    def from_radians(radians):
        return int((radians / (2 * math.pi)) * PositionConverter.MAX_POS)
```

---

### What's the difference between MoveTo and WritePosition?

| Feature | MoveTo() | WritePosition() |
|---------|----------|-----------------|
| **Sets mode** | Yes (position mode) | No |
| **Sets speed** | Yes (if provided) | No (uses existing) |
| **Sets acceleration** | Yes (if provided) | No (uses existing) |
| **Wait option** | Yes | No |
| **High-level** | Yes | No (low-level) |
| **Recommended** | **YES** | Only for advanced use |

**Example:**

```python
# MoveTo (recommended) - complete control
servo.MoveTo(1, 2048, speed=2400, acc=50, wait=False)

# WritePosition - just sets target
servo.SetMode(1, 0)  # Must set mode
servo.SetSpeed(1, 2400)  # Must set speed
servo.SetAcceleration(1, 50)  # Must set acceleration
servo.WritePosition(1, 2048)  # Then write position
```

**Use MoveTo() unless:**
- You need maximum performance (skip redundant mode/speed/acc sets)
- You're implementing custom motion control
- You're using group sync operations

---

### How fast can I send commands?

**Limits:**

| Operation | Max Rate | Notes |
|-----------|----------|-------|
| Read single parameter | ~100 Hz | 10ms interval |
| Write single parameter | ~100 Hz | 10ms interval |
| MoveTo command | ~50 Hz | 20ms interval |
| Scan all servos | ~0.03 Hz | 30 seconds total |

**Practical example:**
```python
import time

# GOOD: Control loop at 50-100 Hz
while True:
    position = servo.ReadPosition(1)
    # Process...
    servo.MoveTo(1, new_target)
    time.sleep(0.02)  # 50 Hz

# TOO FAST: Commands may collide
while True:
    servo.MoveTo(1, target)  # No delay!
```

**Optimize with batch operations:**
```python
# Instead of reading each servo individually
for sid in [1, 2, 3, 4]:
    pos = servo.ReadPosition(sid)  # 4 × 10ms = 40ms

# Consider GroupSyncRead for better performance
# See User Manual for details
```

---

### Can I control servo speed directly in rotation mode?

**Yes! That's what rotation mode is for:**

```python
# Switch to rotation mode
servo.SetMode(1, 1)

# Set rotation speed (-3400 to +3400 step/s)
servo.Rotate(1, 1000)  # CW at 1000 step/s
servo.Rotate(1, -500)  # CCW at 500 step/s
servo.Rotate(1, 0)     # Stop

# Or use the Rotate method which sets mode automatically
servo.Rotate(1, 1000)  # Automatically switches to mode 1
```

**Rotation mode vs Position mode:**
- **Position mode:** Go to specific angle, speed is max speed
- **Rotation mode:** Continuous rotation at specified speed

---

### How do I make smooth movements?

**Several approaches:**

#### 1. **Adjust acceleration**
```python
# Smooth (gradual)
servo.SetAcceleration(1, 20)
servo.MoveTo(1, 3000)

# Aggressive (fast but jerky)
servo.SetAcceleration(1, 200)
servo.MoveTo(1, 3000)
```

#### 2. **Reduce speed**
```python
# Slow, smooth
servo.SetSpeed(1, 800)

# Fast
servo.SetSpeed(1, 3400)
```

#### 3. **Trajectory with waypoints**
```python
# Move through intermediate positions
waypoints = [2048, 2200, 2500, 2900, 3000]
for wp in waypoints:
    servo.MoveTo(1, wp, wait=True)
    time.sleep(0.1)  # Pause at each waypoint
```

#### 4. **Interpolation**
```python
import time

def smooth_move(servo, servo_id, start, end, duration):
    """Move smoothly over specified duration"""
    steps = 50
    delay = duration / steps
    
    for i in range(steps + 1):
        # Linear interpolation
        pos = int(start + (end - start) * (i / steps))
        servo.MoveTo(servo_id, pos)
        time.sleep(delay)

# Move from 1000 to 3000 over 2 seconds
smooth_move(servo, 1, 1000, 3000, 2.0)
```

---

## Troubleshooting Questions

### Why does servo.ListServos() take so long?

**Reason:** Scans all 254 possible IDs

**Duration:** 15-30 seconds typical

**Solutions:**

1. **Scan specific range**
```python
# Custom scan function
def scan_range(servo, start, end):
    found = []
    for sid in range(start, end + 1):
        if servo.LinkServo(sid):
            found.append(sid)
    return found

# Scan IDs 1-10 only
servos = scan_range(servo, 1, 10)
```

2. **Track IDs yourself**
```python
# Maintain list of known servos
KNOWN_SERVOS = [1, 2, 3, 4]

# Verify they're present
for sid in KNOWN_SERVOS:
    if not servo.LinkServo(sid):
        print(f"Warning: Servo {sid} not responding")
```

3. **Use only when necessary**
- Initial setup
- Troubleshooting
- User configuration
- NOT in main control loop

---

### Why do I get None from read operations?

**Possible causes:**

1. **Servo not powered**
   - Check power supply connected
   - Verify voltage at servo (6-12V)

2. **Wrong servo ID**
```python
# Verify servo ID
if servo.LinkServo(1):
    print("Servo 1 present")
else:
    print("Check servo ID")
```

3. **Communication error**
   - Check data wire connection
   - Verify common ground
   - Test with shorter cable

4. **Servo in different mode**
   - Some operations mode-dependent
   - Set correct mode first

5. **Electrical interference**
   - Use shielded cable
   - Keep away from power lines
   - Add ferrite bead

**Debug pattern:**
```python
result = servo.ReadVoltage(1)
if result is None:
    # Step 1: Can we ping?
    if servo.LinkServo(1):
        print("Ping OK, but read failed")
        # Retry read
        time.sleep(0.1)
        result = servo.ReadVoltage(1)
    else:
        print("Cannot ping servo")
        # Check power, wiring, ID
```

---

### Servo moves erratically or jitters

**Causes and solutions:**

1. **Insufficient power**
```python
# Check voltage during movement
servo.MoveTo(1, 3000)
time.sleep(0.1)
voltage = servo.ReadVoltage(1)
if voltage < 6.0:
    print("Voltage too low - upgrade power supply")
```

2. **Loose connections**
   - Re-seat all connectors
   - Check for damaged wires

3. **Too fast acceleration/speed**
```python
# Reduce to stable settings
servo.SetAcceleration(1, 30)
servo.SetSpeed(1, 1500)
```

4. **Position correction needed**
```python
# Check and clear correction
corr = servo.ReadCorrection(1)
if abs(corr) > 100:
    servo.CorrectPosition(1, 0)
```

5. **Mechanical issues**
   - Check for binding
   - Verify smooth rotation by hand (torque disabled)
   - Look for damaged gears

---

## Advanced Questions

### How do I synchronize multiple servos precisely?

**Use GroupSyncWrite:**

```python
from st3215.group_sync_write import GroupSyncWrite
from st3215.values import STS_GOAL_POSITION_L

# Create sync write for position
gsw = GroupSyncWrite(servo, STS_GOAL_POSITION_L, 2)  # 2 bytes

# Add servo positions
gsw.addParam(1, [servo.sts_lobyte(2048), servo.sts_hibyte(2048)])
gsw.addParam(2, [servo.sts_lobyte(3000), servo.sts_hibyte(3000)])
gsw.addParam(3, [servo.sts_lobyte(1000), servo.sts_hibyte(1000)])

# Send all at once (single packet)
gsw.txPacket()
```

**Benefits:**
- All servos receive command simultaneously
- Minimal time skew (<1ms)
- Efficient bandwidth usage

---

## Still Have Questions?

### Resources

- **User Manual:** Complete API reference - [User_manual.md](User_manual.md)
- **User Guide:** Tutorials and examples - [user_guide.md](user_guide.md)
- **Troubleshooting:** Common issues - [troubleshooting.md](troubleshooting.md)
- **GitHub:** Issues and discussions - [Repository](https://github.com/Mickael-Roger/python-st3215)

### Getting Help

1. **Check documentation first**
2. **Search GitHub issues**
3. **Create detailed issue** with:
   - Python version
   - OS and platform
   - Complete error message
   - Minimal reproducible example
   - What you've tried

### Contributing

Pull requests welcome!
- Bug fixes
- New features
- Documentation improvements
- Test cases

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
```

**Note:** The "Ping6Servo" method has been removed, and any references to it have been omitted from the documentation. The "ST3215" method signature has been updated to reflect the latest changes, ensuring users have the correct information for implementation.